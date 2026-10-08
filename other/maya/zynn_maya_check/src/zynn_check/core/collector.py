# -*- coding: utf-8 -*-

"""
场景数据收集器
"""

import maya.cmds as cmds

from zynn_check.core.config import DEFAULT_CAMERA_LONG_TRANSFORMS
from zynn_check.core.fileinfo import FileInfo
from zynn_check.core.utils import is_node_referenced, names_to_uuids


def _drop_referenced(names):
    """剔除来自引用文件的节点名"""
    return [name for name in names if not is_node_referenced(name)]


def _transforms_with_shapes(shape_type, no_intermediate=False):
    """
    收集含指定 shape 类型子节点的 transform 节点

    Args:
        shape_type (str): shape 节点类型，如 'mesh' / 'nurbsCurve'
        no_intermediate (bool): 是否排除 intermediate 形状

    Returns:
        list: transform 节点 UUID 列表
    """
    parent_names = []
    seen = set()
    for shape in cmds.ls(type=shape_type) or []:
        if is_node_referenced(shape):
            continue

        parents = cmds.listRelatives(shape, parent=True, type='transform', 
                                     fullPath=True, noIntermediate=no_intermediate)
        if not parents:
            continue

        if parents[0] not in seen:
            seen.add(parents[0])
            parent_names.append(parents[0])

    return names_to_uuids(_drop_referenced(parent_names))


def _collect_transforms():
    """收集所有 transform 节点"""
    names = cmds.ls(transforms=True, long=True) or []
    names = [name for name in names if name not in DEFAULT_CAMERA_LONG_TRANSFORMS]
    return names_to_uuids(_drop_referenced(names))


def _collect_mesh():
    """收集 mesh 节点（其 transform 父级）"""
    return _transforms_with_shapes('mesh', no_intermediate=True)


def _collect_controllers():
    """收集控制器节点（nurbsCurve shape 的父级 transform）"""
    return _transforms_with_shapes('nurbsCurve')


def _collect_joints():
    """收集关节节点"""
    return names_to_uuids(_drop_referenced(cmds.ls(type='joint') or []))


def _collect_materials():
    """收集材质球节点（非 DAG 节点）"""
    return names_to_uuids(_drop_referenced(cmds.ls(materials=True) or []))


def _collect_textures():
    """收集贴图节点（非 DAG 节点）"""
    return names_to_uuids(_drop_referenced(cmds.ls(textures=True) or []))


def _collect_shading_groups():
    """收集着色组节点（非 DAG 节点）"""
    return names_to_uuids(_drop_referenced(cmds.ls(type='shadingEngine') or []))


def _collect_display_layers():
    """收集显示层（含 defaultLayer / Norender，由检查自行排除）"""
    return names_to_uuids(_drop_referenced(cmds.ls(type='displayLayer') or []))


def _collect_anim_layers():
    """收集动画层（含 BaseAnimation，由检查自行排除）"""
    return names_to_uuids(_drop_referenced(cmds.ls(type='animLayer') or []))


def _collect_render_layers():
    """收集渲染层（含 defaultRenderLayer，由检查自行排除）"""
    return names_to_uuids(_drop_referenced(cmds.ls(type='renderLayer') or []))


def _collect_file_info():
    """
    收集当前场景文件信息（镜头/资产判别等）

    Returns:
        FileInfo: 场景文件信息对象
    """
    return FileInfo()


class CollectorSpec(object):
    """
    收集器规格

    Args:
        func (callable): 收集函数
        label (str): 数据名称，用于「缺少 {label} 数据」提示
        always (bool): 是否必须收集（True 时无论选中哪些检查都收集）
        required (bool): 是否必须有数据（True 时收集结果为空会提示缺少数据并阻塞检查）
    """
    def __init__(self, func, label='', always=False, required=False):
        self.func = func
        self.label = label
        self.always = always
        self.required = required


COLLECTORS = {
    'file_info': CollectorSpec(_collect_file_info, u'文件信息', always=True, required=True),

    'transform': CollectorSpec(_collect_transforms, u'transform'),
    'mesh': CollectorSpec(_collect_mesh, u'mesh'),
    'mesh_face': CollectorSpec(_collect_mesh, u'mesh'),
    'mesh_edge': CollectorSpec(_collect_mesh, u'mesh'),
    'mesh_vertex': CollectorSpec(_collect_mesh, u'mesh'),

    'controller': CollectorSpec(_collect_controllers, u'controller'),
    'joint': CollectorSpec(_collect_joints, u'joint'),

    'material': CollectorSpec(_collect_materials, u'material'),
    'texture': CollectorSpec(_collect_textures, u'texture'),
    'shading_group': CollectorSpec(_collect_shading_groups, u'shading_group'),

    'display_layer': CollectorSpec(_collect_display_layers, u'display_layer'),
    'anim_layer': CollectorSpec(_collect_anim_layers, u'anim_layer'),
    'render_layer': CollectorSpec(_collect_render_layers, u'render_layer'),
}

# 必须有数据的 data_key 集合，供引擎判断数据为空时是否需要提示缺少数据
REQUIRED_KEYS = frozenset(key for key, spec in COLLECTORS.items() if spec.required)


class StageCollector(object):
    """
    通用数据收集器

    按 check_type 反向驱动收集节点数据（always 类型始终收集），
    file_info 等信息始终收集并可直接被所有检查访问。
    相同的采集函数只执行一次，结果同时填入对应的多个 check_type 键
    （如 mesh_face/mesh_edge/mesh_vertex）。
    """

    def collect(self, check_types):
        """
        收集数据（始终全场景查询）

        Args:
            check_types (set): 需要收集的 check_type 集合

        Returns:
            dict: {
                'collected': {check_type: [UUID...]}（引用节点已剔除）,
                'file_info': FileInfo,
                'empty_required': {check_type: label} 必需数据为空的项,
                'required_keys': 必需数据的 check_type 集合,
            }
        """
        collected = {}
        empty_required = {}
        file_info = None
        results_cache = {}

        for key in self._resolve_keys(check_types):
            spec = COLLECTORS[key]

            # file_info 是对象不是节点列表，单独收集
            if key == 'file_info':
                file_info = spec.func()
                continue

            # 采集函数已自带引用节点过滤，同一函数只跑一次
            if spec.func not in results_cache:
                results_cache[spec.func] = spec.func() or []

            result = results_cache[spec.func]
            collected[key] = result
            if spec.required and not result:
                empty_required[key] = spec.label

        return {
            'collected': collected,
            'file_info': file_info,
            'empty_required': empty_required,
            'required_keys': REQUIRED_KEYS,
        }

    def _resolve_keys(self, check_types):
        """
        计算需要收集的 data_key 集合：always 项 ∪ 反向推导的 check_type

        Args:
            check_types (set): 选中检查的 check_type 集合

        Returns:
            set: 需要收集的 data_key 集合
        """
        keys = set()
        for key, spec in COLLECTORS.items():
            if spec.always or key in check_types:
                keys.add(key)
        return keys
