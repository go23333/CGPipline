# -*- coding: utf-8 -*-

import re
import os
import time
from collections import defaultdict

import maya.cmds as cmds
import maya.api.OpenMaya as om

from zynn_check.core.utils import get_node_name
from . import report, preferences
from .collector import StageCollector
from . import environment as env
from .progress import NullProgress
from .registry import get_commands_list, get_check_info, CHECK_REGISTRY


class Engine:
    def __init__(self, stage_name='model', progress=None):
        """
        初始化引擎

        Args:
            stage_name (str): 环节名称，用于隔离设置和命令列表，默认 'model'
            progress (Progress): 进度/光标抽象，GUI 传 MayaProgress，默认 NullProgress（无 UI）
        """
        env.STAGE = stage_name
        self.stage_name = stage_name
        self.progress = progress if progress is not None else NullProgress()
        self._check_registry = CHECK_REGISTRY
        self.commandsList = get_commands_list(self.stage_name)
        self.context = None
        self._results = {}

    def _build_mesh_selection_list(self, nodes):
        """
        从节点列表中筛选mesh节点，构建MSelectionList

        Args:
            nodes (list): 节点UUID列表

        Returns:
            MSelectionList: 网格节点选择列表
        """
        SLMesh = om.MSelectionList()
        for node in nodes:
            nodeName = cmds.ls(node)
            shapes = cmds.listRelatives(nodeName, shapes=True, noIntermediate=True, type='mesh')
            if shapes:
                SLMesh.add(get_node_name(node))
        return SLMesh

    def _collected_mesh_transforms(self, check_data):
        """
        取本次收集到的网格 transform 列表，用于构建 SLMesh

        mesh_face / mesh_edge / mesh_vertex 与 mesh 共用同一个采集函数，
        而收集器只为选中的 check_type 写入键：单条执行 mesh_edge 检查时
        只收集到 'mesh_edge' 一个键。因此这里按族查找，
        否则 SLMesh 为空、组件遍历一次都不执行，检查会被误判为通过。

        Args:
            check_data (dict): 检查数据，包含 collected

        Returns:
            list: mesh transform 的 UUID 列表
        """
        collected = check_data.get('collected', {})
        for key in ['mesh', 'mesh_face', 'mesh_edge', 'mesh_vertex']:
            items = collected.get(key)
            if items:
                return items
        return []

    def _run_vertex_checks(self, SLMesh, check_fns, progress):
        """
        顶点遍历，驱动所有顶点检查的回调函数

        Args:
            SLMesh (MSelectionList): 网格节点选择列表
            check_fns (list): 顶点检查回调函数列表，每项签名为 fn(uuid, vertexIt, vertex_index)
            progress (Progress): 进度抽象
        """
        selIt = om.MItSelectionList(SLMesh)
        while not selIt.isDone():
            dagPath = selIt.getDagPath()
            uuid = om.MFnDependencyNode(dagPath.node()).uuid().asString()
            vertexIt = om.MItMeshVertex(dagPath)
            while not vertexIt.isDone():
                for fn in check_fns:
                    fn(dagPath, uuid, vertexIt, vertexIt.index())
                vertexIt.next()
            selIt.next()
            progress.step()

    def _run_edge_checks(self, SLMesh, check_fns, progress):
        """
        边遍历，驱动所有边检查的回调函数

        Args:
            SLMesh (MSelectionList): 网格节点选择列表
            check_fns (list): 边检查回调函数列表，每项签名为 fn(uuid, edgeIt, edge_index)
            progress (Progress): 进度抽象
        """
        selIt = om.MItSelectionList(SLMesh)
        while not selIt.isDone():
            dagPath = selIt.getDagPath()
            uuid = om.MFnDependencyNode(dagPath.node()).uuid().asString()
            edgeIt = om.MItMeshEdge(dagPath)
            while not edgeIt.isDone():
                for fn in check_fns:
                    fn(dagPath, uuid, edgeIt, edgeIt.index())
                edgeIt.next()
            selIt.next()
            progress.step()

    def _run_face_checks(self, SLMesh, check_fns, progress):
        """
        面遍历，驱动所有面检查的回调函数

        Args:
            SLMesh (MSelectionList): 网格节点选择列表
            check_fns (list): 面检查回调函数列表，每项签名为 fn(uuid, faceIt, face_index)
            progress (Progress): 进度抽象
        """
        selIt = om.MItSelectionList(SLMesh)
        while not selIt.isDone():
            dagPath = selIt.getDagPath()
            uuid = om.MFnDependencyNode(dagPath.node()).uuid().asString()
            faceIt = om.MItMeshPolygon(dagPath)
            while not faceIt.isDone():
                for fn in check_fns:
                    fn(dagPath, uuid, faceIt, faceIt.index())
                # maya2018与maya2023参数不同
                if env.MAYA_VERSION == '2018':
                    faceIt.next(0)
                elif env.MAYA_VERSION == '2023':
                    faceIt.next()
                else:
                    raise KeyError(u'不支持当前maya版本')
            selIt.next()
            progress.step()

    def _run_node_checks(self, nodes, check_fns, progress):
        """
        遍历节点列表，驱动所有节点检查的回调函数

        Args:
            nodes (list): 节点UUID列表
            check_fns (list): 节点检查回调函数列表，每项签名为 fn(node_uuid)
            progress (Progress): 进度抽象
        """
        for node in nodes:
            for fn in check_fns:
                fn(node)
            progress.step()

    def _run_item_checks(self, items, check_fns, progress):
        """
        遍历普通节点名列表，驱动 controller/joint 等检查

        Args:
            items (list): 节点名列表
            check_fns (list): 检查回调函数列表，每项签名为 fn(item)
            progress (Progress): 进度抽象
        """
        for item in items:
            for fn in check_fns:
                fn(item)
            progress.step()

    def _run_scene_checks(self, check_fns, check_data, progress):
        """
        执行场景级检查，通过 check_data 传递 SLMesh 和 nodes 等检查数据

        Args:
            check_fns (list): 场景检查回调函数列表，每项签名为 fn(check_data)
            check_data (dict): 检查数据，包含 SLMesh / nodes 等
            progress (Progress): 进度抽象
        """
        for fn in check_fns:
            fn()
        progress.step()

    def _build_traversers(self):
        """
        构建检查类型到遍历器的映射字典

        新增检查类型只需在此添加一条映射和对应的 _run_* 方法。

        Returns:
            dict: {check_type: lambda(check_fns, check_data, progress)}
        """
        return {
            'mesh_face':   lambda fns, check_data, prog: self._run_face_checks(check_data['SLMesh'], fns, prog),
            'mesh_edge':   lambda fns, check_data, prog: self._run_edge_checks(check_data['SLMesh'], fns, prog),
            'mesh_vertex': lambda fns, check_data, prog: self._run_vertex_checks(check_data['SLMesh'], fns, prog),
            'mesh':        lambda fns, check_data, prog: self._run_node_checks(check_data['collected']['mesh'], fns, prog),
            'transform':   lambda fns, check_data, prog: self._run_node_checks(check_data['collected']['transform'], fns, prog),
            'controller':  lambda fns, check_data, prog: self._run_item_checks(check_data['collected']['controller'], fns, prog),
            'joint':       lambda fns, check_data, prog: self._run_item_checks(check_data['collected']['joint'], fns, prog),
            'material':    lambda fns, check_data, prog: self._run_item_checks(check_data['collected']['material'], fns, prog),
            'texture':     lambda fns, check_data, prog: self._run_item_checks(check_data['collected']['texture'], fns, prog),
            'shading_group': lambda fns, check_data, prog: self._run_item_checks(check_data['collected']['shading_group'], fns, prog),
            'display_layer': lambda fns, check_data, prog: self._run_item_checks(check_data['collected']['display_layer'], fns, prog),
            'anim_layer':  lambda fns, check_data, prog: self._run_item_checks(check_data['collected']['anim_layer'], fns, prog),
            'render_layer': lambda fns, check_data, prog: self._run_item_checks(check_data['collected']['render_layer'], fns, prog),
            'scene':       lambda fns, check_data, prog: self._run_scene_checks(fns, check_data, prog),
        }

    def _items_for_check_type(self, check_data, check_type):
        """
        根据 check_type 返回本次检查需要的已收集数据。

        check_type 即收集器收集的类别键，scene 类型不依赖节点数据。

        Args:
            check_data (dict): 检查数据，包含 collected / nodes 等
            check_type (str): 检查类型

        Returns:
            list or None: 节点列表，scene 类型返回 None
        """
        if check_type == 'scene':
            return None
        return check_data['collected'].get(check_type, [])

    def _check_types_for_commands(self, commands):
        """
        根据本次要执行的命令推导需要收集的 check_type 并集

        scene 检查不参与收集，直接执行。

        Args:
            commands (list): 扩展后的命令名称列表

        Returns:
            set: 需要收集的 check_type 集合
        """
        check_types = set()
        for cmd in commands:
            info = get_check_info(cmd)
            check_type = info.check_type if info else 'transform'
            if check_type != 'scene':
                check_types.add(check_type)
        return check_types

    def _needs_data(self, check_data, check_type):
        """
        判断该 check_type 的数据为空时是否需要提示缺少数据

        只有收集器标记为必需(required)的数据为空才算缺少数据；
        非必需数据为空时检查照常执行（零项遍历），因此结果为通过。
        未在收集器注册的 check_type 视为必需，避免注册错误被静默通过。

        Args:
            check_data (dict): 检查数据，包含 collected / required_keys 等
            check_type (str): 检查类型

        Returns:
            bool: 是否需要提示缺少数据
        """
        if check_type not in check_data.get('collected', {}):
            return True
        return check_type in check_data.get('required_keys', ())

    def _block_empty_data(self, diagnostics, outcomes, cmd, label):
        """
        数据为空时将检查标记为待定(blocked)

        Args:
            diagnostics (dict): 诊断结果字典
            outcomes (dict): 命令到状态的映射
            cmd (str): 命令名称
            label (str): 缺少数据的名称
        """
        info = get_check_info(cmd)
        result_type = info.result_type if info else 'node'
        diagnostics[cmd] = self._make_result(
            result_type, [], 'blocked', blocked_by=[u"缺少 {} 数据".format(label)])
        outcomes[cmd] = 'blocked'

    def command_to_run(self, commands):
        """
        执行指定命令列表的检查

        根据命令的 check_type 分组，通过 _build_traversers 字典自动分发到对应遍历器。
        新增检查类型只需在 _build_traversers 中添加映射。
        支持检查间依赖：requires 声明的前置检查会自动连带运行，
        前置未通过/出错时该检查标记为 "blocked"（待定）而不执行。

        Args:
            commands (list): 要执行的命令名称列表

        Returns:
            tuple: (diagnostics, checked_nodes)
                diagnostics (dict): {command: {'result_type': str, 'uuids': dict/list, 'status': str, ...}}
                checked_nodes (list): 本次实际被检查的节点UUID并集
        """
        traversers = self._build_traversers()

        dependency_graph = self._build_dependency_graph()
        commands = self._expand_requires(commands, dependency_graph)

        collector = StageCollector()
        check_types = self._check_types_for_commands(commands)
        context = collector.collect(check_types)
        context['shared'] = {}
        context['results'] = self._results
        mesh_transforms = self._collected_mesh_transforms(context)
        SLMesh = self._build_mesh_selection_list(mesh_transforms)
        context['SLMesh'] = SLMesh
        self.context = context

        checked_nodes = []
        seen = set()
        for items in context['collected'].values():
            for uuid in items:
                if uuid not in seen:
                    seen.add(uuid)
                    checked_nodes.append(uuid)

        total_steps = 1
        for cmd in commands:
            info = get_check_info(cmd)
            if info:
                total_steps += self._check_step(info, context)
        self.progress.begin(total_steps)

        diagnostics = self._schedule(commands, dependency_graph, context, traversers,
                                     self.progress)

        self.progress.end()
        SLMesh.clear()
        return diagnostics, checked_nodes

    def command_to_run_fix(self, commands):
        """
        运行检查并修复

        Args:
            commands (list): 要执行的命令名称列表

        Returns:
            tuple: (diagnostics, checked_nodes, fix_results)
                diagnostics (dict): 最终诊断（修复后已复检的检查已更新）
                checked_nodes (list): 被检查的节点UUID并集
                fix_results (dict): {cmd: 'fixed' | 'still_failed' | 'error'}，仅含尝试修复的检查
        """
        diagnostics, checked_nodes = self.command_to_run(commands)

        fix_results = {}
        for cmd in list(diagnostics.keys()):
            diag = diagnostics.get(cmd)
            if not diag or diag.get('status') != 'failed':
                continue

            info = get_check_info(cmd)
            if info is None or not hasattr(info, 'fix'):
                continue

            try:
                errors = self._build_fix_errors(diag)
                instance = info(self.context)
                instance.fix(errors)
                fix_results[cmd] = 'fixed'
            except Exception:
                fix_results[cmd] = 'error'

        # 有尝试修复时，整体复检一次，获得修复后的最终状态
        if fix_results:
            try:
                final_diag, _ = self.command_to_run(commands)
            except Exception:
                final_diag = None
            if final_diag:
                for cmd in fix_results:
                    if cmd not in final_diag:
                        continue
                    diagnostics[cmd] = final_diag[cmd]
                    if (fix_results[cmd] == 'fixed'
                            and final_diag[cmd].get('status') == 'failed'):
                        fix_results[cmd] = 'still_failed'

        return diagnostics, checked_nodes, fix_results

    def _fix_name(self, value):
        """若为 UUID 则解析为节点名；否则（本就是名字）原样返回"""
        uuid_re = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')

        if not uuid_re.match(value):
            return value
        try:
            names = cmds.ls(value)
            return names[0] if names else value
        except Exception:
            return value

    def _build_fix_errors(self, diag):
        """从诊断构建 fix 需要的可选路径列表"""
        result_type = diag.get('result_type', 'node')
        uuids = diag.get('uuids') or []

        if result_type == 'text':
            return list(uuids)

        if result_type == 'node':
            if isinstance(uuids, dict):
                return [self._fix_name(node) for node in uuids.keys()]
            return [self._fix_name(node) for node in uuids]

        if isinstance(uuids, dict):
            component_map = {'uv': '.map[{}]', 'vertex': '.vtx[{}]',
                             'edge': '.e[{}]', 'face': '.f[{}]'}
            fmt = component_map.get(result_type)
            parts = []
            for node, indices in uuids.items():
                name = self._fix_name(node)
                for index in indices:
                    parts.append(name + fmt.format(index) if fmt else name)
            return parts

        return list(uuids)

    def _build_dependency_graph(self):
        """
        构建当前环节内的依赖图，仅包含环节内可用的前置检查

        Returns:
            tuple: (requires_of, dependents)
                requires_of: {cmd: [前置检查名称列表]}
                dependents:  {前置检查: [依赖它的检查名称列表]}
        """
        stage_commands = set(self.commandsList.keys())
        requires_of = {}
        dependents = defaultdict(list)
        for cmd in self.commandsList:
            requires_of[cmd] = []
            info = get_check_info(cmd)
            if not info:
                continue
            for required in info.requires:
                if required in stage_commands:
                    requires_of[cmd].append(required)
                    dependents[required].append(cmd)
        return requires_of, dependents

    def _expand_requires(self, commands, dependency_graph):
        """
        将命令列表按 requires 做传递闭包扩展，前置检查自动排在依赖之前

        Args:
            commands (list): 命令名称列表
            dependency_graph (tuple): _build_dependency_graph 的返回值

        Returns:
            list: 扩展后的命令名称列表（前置在前，依赖在后）
        """
        requires_of, _ = dependency_graph
        expanded = []
        seen = set()

        def visit(cmd):
            if cmd in seen:
                return
            seen.add(cmd)
            for required in requires_of.get(cmd, []):
                visit(required)
            expanded.append(cmd)

        for cmd in commands:
            visit(cmd)
        return expanded

    def _schedule(self, commands, dependency_graph, check_data, traversers, progress):
        """
        按依赖关系分轮执行检查命令

        采用待办计数（Kahn）调度：每个命令记录尚未完成的前置数，
        前置归零即可在本轮执行；前置未通过/出错时依赖方标记为 blocked。
        无法再选出就绪命令时说明依赖成环，剩余命令全部标记为 blocked。

        Args:
            commands (list): 扩展后的命令名称列表
            dependency_graph (tuple): _build_dependency_graph 的返回值
            check_data (dict): 检查数据，包含 SLMesh / nodes / shared 等
            traversers (dict): 检查类型到遍历器的映射
            progress (Progress): 进度抽象

        Returns:
            dict: {command: {"result_type": str, "uuids": dict/list, "status": str, ...}}
        """
        requires_of, dependents = dependency_graph
        diagnostics = {}
        outcomes = {}
        pending = {cmd: len(requires_of.get(cmd, [])) for cmd in commands}
        not_done = set(commands)

        while not_done:
            if progress.cancelled():
                self._block_many(diagnostics, outcomes, not_done, [u"用户取消"])
                break

            ready = [cmd for cmd in not_done if pending[cmd] == 0]
            if not ready:
                self._block_many(diagnostics, outcomes, not_done, sorted(not_done))
                break
            not_done.difference_update(ready)

            settled, cancelled = self._run_round(
                ready, requires_of, diagnostics, outcomes, check_data, traversers,
                progress)

            if cancelled:
                unrun = [cmd for cmd in ready if cmd not in settled]
                self._block_many(diagnostics, outcomes, unrun, [u"用户取消"])
                self._block_many(diagnostics, outcomes, not_done, [u"用户取消"])
                break

            for cmd in settled:
                for dependent in dependents.get(cmd, []):
                    if dependent in pending:
                        pending[dependent] -= 1

        return diagnostics

    def _run_round(self, ready, requires_of, diagnostics, outcomes, check_data, traversers,
                   progress):
        """
        执行一轮就绪检查：门控过滤、按检查类型合并遍历、写入结果

        Args:
            ready (list): 本轮就绪的命令名称列表
            requires_of (dict): 命令到前置检查列表的映射
            diagnostics (dict): 诊断结果字典
            outcomes (dict): 命令到状态的映射
            check_data (dict): 检查数据，包含 SLMesh / nodes 等
            traversers (dict): 检查类型到遍历器的映射
            progress (Progress): 进度抽象

        Returns:
            tuple: (settled, cancelled)
                settled (list): 本轮已获得结果的命令名称列表
                cancelled (bool): 本轮遍历是否被用户取消
        """
        settled = []
        groups_by_type = {}
        for cmd in ready:
            failed_requires = [r for r in requires_of.get(cmd, [])
                               if outcomes.get(r) != 'passed']
            if failed_requires:
                self._mark_blocked(diagnostics, outcomes, cmd, failed_requires)
                settled.append(cmd)
                continue

            info = get_check_info(cmd)
            try:
                instance = info(check_data)
                instance.prepare()
            except Exception as exc:
                result_type = info.result_type if info else 'node'
                diagnostics[cmd] = self._make_result(result_type, [], 'failed', error=str(exc))
                outcomes[cmd] = 'failed'
                settled.append(cmd)
                continue

            run_errors = []
            wrapped = self._wrap_runner(instance.run, run_errors)
            check_type = info.check_type if info else 'transform'
            items = self._items_for_check_type(check_data, check_type)
            if items == [] and self._needs_data(check_data, check_type):
                label = check_data.get('empty_required', {}).get(check_type, check_type)
                self._block_empty_data(diagnostics, outcomes, cmd, label)
                settled.append(cmd)
                continue
            groups_by_type.setdefault(check_type, []).append(
                (cmd, wrapped, instance, run_errors))

        cancelled = False
        for check_type, checks in groups_by_type.items():
            if progress.cancelled():
                cancelled = True
                break
            check_fns = [check[1] for check in checks]
            if check_type not in traversers:
                for cmd, _, instance, _ in checks:
                    info = get_check_info(cmd)
                    result_type = info.result_type if info else 'node'
                    diagnostics[cmd] = self._make_result(
                        result_type, [], 'failed',
                        error=u"未知 check_type: {}".format(check_type))
                    outcomes[cmd] = 'failed'
                    settled.append(cmd)
                continue
            traversers[check_type](check_fns, check_data, progress)
            for cmd, _, instance, run_errors in checks:
                info = get_check_info(cmd)
                result_type = info.result_type if info else 'node'
                uuids = dict(instance.errors) if isinstance(instance.errors, dict) else (
                    list(instance.errors) if isinstance(instance.errors, set) else instance.errors
                )
                if run_errors:
                    diag = self._make_result(result_type, uuids, 'failed', error=run_errors[0])
                else:
                    diag = self._make_result(result_type, uuids,
                                             'passed' if not uuids else 'failed')
                diagnostics[cmd] = diag
                outcomes[cmd] = diag['status']
                settled.append(cmd)

        return settled, cancelled

    def _block_many(self, diagnostics, outcomes, commands, blocked_by):
        """
        将多个检查统一标记为待定(blocked)

        Args:
            diagnostics (dict): 诊断结果字典
            outcomes (dict): 命令到状态的映射
            commands (iterable): 命令名称列表
            blocked_by (list): 未通过的前置检查列表
        """
        for cmd in commands:
            self._mark_blocked(diagnostics, outcomes, cmd, blocked_by)

    def _check_step(self, info, check_data):
        """
        估算单条检查的进度步数

        Args:
            info (dict): 检查注册信息
            check_data (dict): 检查数据

        Returns:
            int: 步数
        """
        check_type = info.check_type
        items = self._items_for_check_type(check_data, check_type)
        if items is not None:
            return max(1, len(items))
        return 1

    def _make_result(self, result_type, uuids, status, blocked_by=None, error=None):
        """
        构造检查结果字典

        Args:
            result_type (str): 结果类型，如 "node"/"scene"/"face"
            uuids (list/dict): 错误数据
            status (str): 状态，可选 "passed"/"failed"/"blocked"
            blocked_by (list): 未通过的前置检查列表
            error (Exception): 执行异常

        Returns:
            dict: 检查结果
        """
        result = {'result_type': result_type, 'uuids': uuids, 'status': status}
        if blocked_by:
            result['blocked_by'] = blocked_by
        if error:
            result['error'] = error
        return result

    def _mark_blocked(self, diagnostics, outcomes, cmd, blocked_by):
        """
        将检查标记为待定(blocked)并记录原因

        Args:
            diagnostics (dict): 诊断结果字典
            outcomes (dict): 命令到状态的映射
            cmd (str): 命令名称
            blocked_by (list): 未通过的前置检查列表
        """
        info = get_check_info(cmd)
        result_type = info.result_type if info else 'node'
        diagnostics[cmd] = self._make_result(result_type, [], 'blocked', blocked_by=blocked_by)
        outcomes[cmd] = 'blocked'

    def _wrap_runner(self, runner_fn, run_errors):
        """
        包裹 runner，捕获单次调用异常并记录，保证共享遍历不中断

        Args:
            runner_fn (callable): 原始检查回调
            run_errors (list): 异常记录列表

        Returns:
            callable: 包裹后的回调
        """
        def wrapped(*args, **kwargs):
            try:
                runner_fn(*args, **kwargs)
            except Exception as exc:
                run_errors.append(exc)
        return wrapped

    def parse_errors(self, errors):
        """
        解析诊断错误数据，生成可选的组件路径列表

        Args:
            errors (dict): 诊断结果，包含 result_type 和 uuids

        Returns:
            list: 解析结果，字符串路径或 {"node": str, "text": str} 条目
        """
        return report.parse_errors(errors)

    def get_selectable(self, parsed):
        """
        从解析结果中提取可被 Maya 选中的路径列表

        Args:
            parsed (list): parse_errors 的解析结果，条目可能是 str 路径或 {"node": 路径, "text": msg}

        Returns:
            list: Maya 可选中的节点/组件路径列表
        """
        return report.get_selectable(parsed)

    def count_errors(self, diagnostics):
        """
        统计通过、失败和待定的检查数量

        Args:
            diagnostics (dict): 诊断结果字典

        Returns:
            tuple: (通过数, 总检查数, 待定数)
        """
        return report.count_errors(diagnostics)

    def validation(self, diagnostics):
        """检查通过时把结果写进场景 fileInfo，并保存场景"""
        try:
            cmds.fileInfo(remove='@zynn_check_passed')   # 幂等：先清旧的，避免重复堆积
        except Exception:
            pass

        passed, checks, blocked = self.count_errors(diagnostics)
        if not blocked and passed == checks == len(self.commandsList):
            timestamp = int(time.time())
            file_size = os.path.getsize(cmds.file(query=True, sn=True))
            cmds.fileInfo('@zynn_check_passed', '{}_{}@zynn_check_passed'.format(timestamp, file_size))
            cmds.file(save=True)

            return True

        return False

    def save_preferences(self, checked_commands):
        """
        保存检查设置到Maya optionVar，键名按环节隔离

        Args:
            checked_commands (dict): 命令复选框状态
        """
        preferences.save_preferences(self.stage_name, checked_commands)

    def load_preferences(self):
        """
        从Maya optionVar加载检查设置，键名按环节隔离

        Returns:
            dict or None: 设置字典，不存在则返回None
        """
        return preferences.load_preferences(self.stage_name)
