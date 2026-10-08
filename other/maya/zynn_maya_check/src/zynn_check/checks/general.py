# -*- coding: utf-8 -*-

import maya.cmds as cmds

from zynn_check.core.check import Check, register
from zynn_check.core.config import ALLOWED_TEXTURE_DIRS, SUPPORTED_MAYA_VERSIONS
from zynn_check.core.utils import get_node_name, in_group, is_node_referenced


def _fix_multiple_shape(nodes):
    for node in nodes:
        shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True)
        for shape in shapes:
            if '{}Shape'.format(node) != shape:
                cmds.delete(shape)


@register
class ConstructionHistory(Check):
    name = 'construction_history'
    label = u"构建历史"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        shape = cmds.listRelatives(node_name, shapes=True, fullPath=True)
        if shape and cmds.nodeType(shape[0]) == 'mesh':
            historys = cmds.listHistory(shape, interestLevel=1, pruneDagObjects=True) or []
            deformers = cmds.findDeformers(shape) or []

            difference = set(historys) - set(deformers)
            if difference:
                self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            shape = cmds.listRelatives(node, shapes=True)[0]
            historys = cmds.listHistory(shape, interestLevel=1, pruneDagObjects=True) or []
            deformers = cmds.findDeformers(shape) or []
            difference = set(historys) - set(deformers)
            for node in difference:
                cmds.delete(node)


@register
class UncenteredPivots(Check):
    name = 'uncenteredPivots'
    label = u"归于原点枢轴"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model', 'shading']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        rotatePivot = cmds.xform(node_name, q=1, ws=1, rp=1)
        # 人体
        if not cmds.listRelatives(node_name, p=True):
            translate = cmds.getAttr('{}.translate'.format(node_name))[0]
            if rotatePivot != [translate[0], translate[1], 0]:
                self.errors.append(node_uuid)
        else:
            if rotatePivot != [0, 0, 0]:
                self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            translate = cmds.getAttr('{}.translate'.format(node))[0]
            cmds.xform(node, ws=True, pivots=(translate[0], translate[1], 0))


@register
class EmptyGroups(Check):
    name = 'emptyGroups'
    label = u"空组"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    # stages = ['model', 'shading']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return

        node_type = cmds.nodeType(node_name)
        all_descendents = cmds.listRelatives(node_name, ad=True)
        if node_type == 'transform' and not all_descendents:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            cmds.delete(node)


@register
class MultipleShapes(Check):
    name = 'multipleShapes'
    label = u"多Shape"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model', 'shading']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        shapes = cmds.listRelatives(node_name, shapes=True, noIntermediate=True)
        if shapes and len(shapes) > 1:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        _fix_multiple_shape(errors)


@register
class RigMultipleShapes(Check):
    name = 'rig_multiple_shapes'
    label = u"Geometry与Cha存在多个形节点"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['rig-all']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Geometry', 'Cha']):
            return

        shapes = cmds.listRelatives(node_name, shapes=True, noIntermediate=True, fullPath=True) or []
        if all(cmds.nodeType(shape) == 'nurbsSurface' for shape in shapes):
            return

        if len(shapes) > 1:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        _fix_multiple_shape(errors)


@register
class LockedTransforms(Check):
    name = 'locked_transforms'
    label = u"锁定变换"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model']

    attrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        if any(cmds.getAttr('{}.{}'.format(node_name, attr), lock=True) for attr in self.attrs):
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            for attr in self.attrs:
                cmds.setAttr('{}.{}'.format(node, attr), lock=False)


@register
class EmptyMesh(Check):
    name = 'empty_mesh'
    label = u"空Mesh"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        if cmds.polyEvaluate(node_name, vertex=True) == 0:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            cmds.delete(node)


@register
class AnimationKey(Check):
    name = 'animation_key'
    label = u"动画关键帧"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model', 'shading']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        if cmds.keyframe(node_name, query=True, keyframeCount=True):
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            cmds.cutKey(node, clear=True)


@register
class DisplaySmoothMesh(Check):
    name = 'display_smooth_mesh'
    label = u"平滑网格预览"
    category = u"通用"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['model']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return

        if cmds.getAttr('{}.displaySmoothMesh'.format(node_name)) != 0:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for mesh in errors:
            cmds.setAttr('{}.displaySmoothMesh'.format(mesh), 0)


@register
class AbnormalNode(Check):
    name = 'abnormal_node'
    label = u"非模型节点"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model']

    def run(self, node_uuid):
        if '_Hair_CV' in self.file_info.get_name():
            return

        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        shapes = cmds.listRelatives(node_name, shapes=True, noIntermediate=True) or []
        for shape in shapes:
            node_type = cmds.nodeType(shape)
            if node_name.endswith('eye') and node_type == 'locator':
                continue
            if node_type != 'mesh':
                self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            cmds.delete(node)


@register
class Constraint(Check):
    name = 'constraint'
    label = u"约束"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading']

    def run(self):
        constraints = cmds.ls(type='constraint')
        if constraints:
            self.errors.extend(constraints)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for constraint in errors:
            cmds.delete(constraint)


@register
class Light(Check):
    name = 'light'
    label = u"灯光节点"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading', 'rig']

    def run(self):
        lights = cmds.ls(type='light')
        if lights:
            self.errors.extend(lights)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for light in errors:
            cmds.delete(light)


@register
class Unknown(Check):
    name = 'unknown'
    label = u"未知节点"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading', 'rig', 'layout', 'animation']

    def run(self):
        unknowns = cmds.ls(type='unknown') or []
        for unknown in unknowns:
            if is_node_referenced(unknown):
                continue
            self.errors.append(unknown)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for unknown in errors:
            if cmds.lockNode(unknown, query=True, lock=True):
                cmds.lockNode(unknown, lock=False)
            cmds.delete(unknown)


@register
class MayaVersion(Check):
    name = 'maya_version'
    label = u"maya版本"
    category = u"通用"
    check_type = 'scene'
    result_type = 'text'
    stages = ['model', 'shading', 'rig', 'layout', 'animation']

    def run(self):
        version = cmds.about(version=True)
        if version not in SUPPORTED_MAYA_VERSIONS:
            self.errors.append(u'maya 版本不正确，当前版本为：{}'.format(version))


@register
class DisplayView(Check):
    name = 'display_view'
    label = u"面板显示"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']

    def run(self):
        if cmds.about(batch=True):
            return

        panels = cmds.getPanel(type='modelPanel')
        for panel in panels:
            mode = cmds.modelEditor(panel, q=True, displayAppearance=True)
            if mode == 'smoothShaded':
                self.errors.append(panel)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for panel in errors:
            cmds.modelEditor(panel, e=True, displayAppearance='wireframe')


@register
class UnnecessaryFile(Check):
    name = 'unnecessary_file'
    label = u"非项目文件"
    category = u"通用"
    check_type = 'scene'
    result_type = 'text'
    stages = ['layout', 'animation']

    def run(self):
        if not self.file_info.file_path:
            return
        current_project = self.file_info.get_project()
        dir_paths = cmds.filePathEditor(query=True, listDirectories='')
        for dir_path in dir_paths:
            if (current_project != dir_path.split('/')[1] and
                    not any(allowed in dir_path for allowed in ALLOWED_TEXTURE_DIRS)):
                self.errors.append(dir_path)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for dir_path in errors:
            files = cmds.filePathEditor(query=True, listFiles=dir_path, withAttribute=True)
            for i in range(0, len(files), 2):
                attr = files[i + 1]
                node = attr.split('.')[0]
                if cmds.objExists(node):
                    cmds.delete(node)


@register
class Expression(Check):
    name = 'expression'
    label = u"表达式节点"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading']

    def run(self):
        expressions = cmds.ls(type='expression')
        if not expressions:
            return

        default_expressions = ['']
        for default_expression in default_expressions:
            if default_expression in expressions:
                expressions.remove(default_expression)
        
        if expressions:
            self.errors.extend(expressions)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for expression in errors:
            try:
                cmds.lockNode(expression, lock=False)
            except RuntimeError:
                pass
            cmds.delete(expression)


@register
class ScriptNode(Check):
    name = 'script_node'
    label = u"脚本节点"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading']

    def run(self):
        script_nodes = cmds.ls(type='script')
        if not script_nodes:
            return

        default_script_nodes = ['sceneConfigurationScriptNode', 'uiConfigurationScriptNode']
        for default_script_node in default_script_nodes:
            if default_script_node in script_nodes:
                script_nodes.remove(default_script_node)
    
        if script_nodes:
            self.errors.extend(script_nodes)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for script_node in errors:
            try:
                cmds.lockNode(script_node, lock=False)
            except RuntimeError:
                pass
            cmds.delete(script_node)


@register
class NodeGraphEditorInfo(Check):
    name = 'node_graph_editor_info'
    label = u"节点图编辑器信息"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading', 'rig']

    def run(self):
        node_graph_editor_infos = cmds.ls(type='nodeGraphEditorInfo')
        if node_graph_editor_infos:
            self.errors.extend(node_graph_editor_infos)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node_graph_editor_info in errors:
            cmds.delete(node_graph_editor_info)


@register
class EffectGroupExist(Check):
    name = 'effect_group_exist'
    label = u"特效简模组"
    category = u"通用"
    check_type = 'scene'
    result_type = 'text'
    stages = ['model', 'shading']

    def run(self):
        groups = cmds.ls('TeXiao_JianMo', type='transform', long=True)
        if not groups:
            self.errors.append(u'特效简模组不存在')
            return

        if len(groups) > 1:
            self.errors.append(u'特效简模组存在多个')
            return
