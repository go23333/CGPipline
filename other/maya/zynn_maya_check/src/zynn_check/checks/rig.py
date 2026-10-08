# -*- coding: utf-8 -*-

import maya.cmds as cmds

from zynn_check.core.check import Check, register
from zynn_check.core.utils import (
    duplicate_attr,
    get_blend_shape,
    get_node_name,
    in_group,
)


TRANSFORM_ATTRS = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']

GLOBAL_ATTR_TEN_DICT = {
    'FKShoulder_L.Global': 10,
    'FKShoulder_R.Global': 10,
    'FKShoulder_L.globalRotate': 10,
    'FKShoulder_R.globalRotate': 10,
}
GLOBAL_ATTR_ZERO_DICT = {
    'FKHead_M.Global': 0,
    'FKScapula_L.Global': 0,
    'FKScapula_R.Global': 0,
    'FKScapula_L.GlobalTranslate': 0,
    'FKScapula_R.GlobalTranslate': 0,
    'FKShoulder_L.GlobalTranslate': 0,
    'FKShoulder_R.GlobalTranslate': 0,
}

IKFK_DICT = {
    'FKIKArm': 0,
    'FKIKLeg': 10,
}


def _obj_exists(name):
    """节点是否存在的安全判断"""
    if not name:
        return False
    return cmds.objExists(name)


def _get_mesh_shapes(node_name):
    """获取transform节点下的mesh shape节点列表"""
    return cmds.listRelatives(node_name, shapes=True, type='mesh', noIntermediate=True) or []


def _get_mesh_deformers(mesh_shape):
    """获取mesh shape上实际变形节点列表"""
    historys = cmds.listHistory(mesh_shape, pruneDagObjects=1) or []
    return cmds.ls(historys, type='geometryFilter') or []


def _fix_sy_mesh_lambert(meshes):
    for mesh in meshes:
        cmds.sets(mesh, edit=True, forceElement='initialShadingGroup')


@register
class ModelSmoothDisplay(Check):
    name = 'model_smooth_display'
    label = u"模型平滑显示"
    category = u"绑定"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Geometry']):
            return

        if cmds.getAttr('{}.displaySmoothMesh'.format(node_name)) != 0:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for mesh in errors:
            cmds.setAttr('{}.displaySmoothMesh'.format(mesh), 0)


@register
class ControllerKeyframe(Check):
    name = 'controller_keyframe'
    label = u"控制器关键帧"
    category = u"绑定"
    check_type = 'controller'
    result_type = 'node'
    stages = ['rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        if cmds.keyframe(node_name, query=True, keyframeCount=True):
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for controller in errors:
            cmds.cutKey(controller, clear=True)


@register
class MeshKeyframe(Check):
    name = 'mesh_keyframe'
    label = u"模型关键帧"
    category = u"绑定"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        if cmds.keyframe(node_name, query=True, keyframeCount=True):
            self.errors.append(node_uuid)


@register
class ModelHidden(Check):
    name = 'model_hidden'
    label = u"模型隐藏"
    category = u"绑定"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig-all']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Geometry']):
            return

        if 'eyeshell' in node_name:
            return
        
        for obj in [node_name] + _get_mesh_shapes(node_name):
            if not cmds.getAttr('{}.visibility'.format(obj)):
                self.errors.append(node_uuid)
                return

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for model in errors:
            for obj in [model] + _get_mesh_shapes(model):
                attr = '{}.visibility'.format(obj)
                locked = cmds.getAttr(attr, lock=True)
                if locked:
                    cmds.setAttr(attr, lock=False)
                cmds.setAttr(attr, 1)
                if locked:
                    cmds.setAttr(attr, lock=True)


@register
class ModelSkinned(Check):
    name = 'model_skinned'
    label = u"模型蒙皮"
    category = u"绑定"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig-all']

    def prepare(self):
        self.context['results'][self.name] = {}

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Geometry']):
            return
        for shape in _get_mesh_shapes(node_name):
            historys = cmds.listHistory(shape) or []
            skinClusters = cmds.ls(historys, type='skinCluster')
            if not skinClusters:
                self.errors[node_uuid] = u"缺少蒙皮"
                return

            for skinCluster in skinClusters:
                skinning_method = cmds.getAttr('{}.skinningMethod'.format(skinCluster))
                if skinning_method != 0:
                    self.errors[skinCluster] = u"蒙皮方法应为经典线性"
                    return

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            if cmds.nodeType(node) == 'skinCluster':
                cmds.setAttr('{}.skinningMethod'.format(node), 0)


@register
class IkfkSwitch(Check):
    name = 'ikfk_switch'
    label = u"手脚IK/FK切换"
    category = u"绑定"
    check_type = 'controller'
    result_type = 'node'
    stages = ['rig']

    def prepare(self):
        self.context['results'][self.name] = {}

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return

        matched_key = next((key for key in IKFK_DICT if key in node_name), None)
        if matched_key is None:
            return

        object_attr = '{}.FKIKBlend'.format(node_name)
        if not cmds.objExists(object_attr):
            self.errors[object_attr] = u"属性不存在"
            return

        expected_value = IKFK_DICT[matched_key]
        actual_value = cmds.getAttr(object_attr)

        if actual_value != expected_value:
            self.errors[object_attr] = u"FKIKBlend值不正确"

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for object_attr in errors:
            if not cmds.objExists(object_attr):
                continue

            node_name, attr_name = object_attr.rsplit('.', 1)
            matched_key = next((key for key in IKFK_DICT if key in node_name), None)
            if matched_key is None:
                continue

            cmds.setAttr(object_attr, IKFK_DICT[matched_key])


@register
class GlobalAttr(Check):
    name = 'global_attr'
    label = u"Global属性值"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig-all']

    def run(self):
        for object_attr, value in GLOBAL_ATTR_TEN_DICT.items():
            if not _obj_exists(object_attr):
                continue
            current_value = cmds.getAttr(object_attr)
            if current_value != value:
                self.errors.append(u"{} 当前值 {}，需要改为 {}".format(object_attr, current_value, value))
        for object_attr, value in GLOBAL_ATTR_ZERO_DICT.items():
            if not _obj_exists(object_attr):
                continue
            current_value = cmds.getAttr(object_attr)
            if current_value != value:
                self.errors.append(u"{} 当前值 {}，需要改为 {}".format(object_attr, current_value, value))

    def fix(self, errors=None):
        for object_attr, value in GLOBAL_ATTR_TEN_DICT.items():
            if _obj_exists(object_attr):
                cmds.setAttr(object_attr, value)
        for object_attr, value in GLOBAL_ATTR_ZERO_DICT.items():
            if _obj_exists(object_attr):
                cmds.setAttr(object_attr, value)


@register
class ChaGroup(Check):
    name = 'cha_group'
    label = u"Cha组"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig']

    def run(self):
        cha_groups = cmds.ls('Cha', long=True)
        if not cha_groups:
            self.errors.append(u"Cha组不存在")

    def fix(self, errors=None):
        cmds.group(em=True, name='Cha', parent='Group')


@register
class SkGroup(Check):
    name = 'sk_group'
    label = u"SK_G解算组"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig']

    def run(self):
        sk_groups = cmds.ls('SK_G', long=True)
        if not sk_groups:
            self.errors.append(u"SK_G解算组不存在")


@register
class JemoGroup(Check):
    name = 'jemo_group'
    label = u"jemo组"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig']
    requires = ['cha_group']

    def run(self):
        jemo_groups = cmds.ls('jemo', long=True)
        if not jemo_groups:
            self.errors.append(u"jemo组不存在")

    def fix(self, errors=None):
        cmds.group(em=True, name='jemo', parent='Cha')


@register
class SyGroup(Check):
    name = 'sy_group'
    label = u"SY_Gro示意组"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig-all']

    def run(self):
        sy_groups = cmds.ls('*_SY_Gro', long=True)
        if not sy_groups:
            self.errors.append(u"SY_Gro示意组不存在")


@register
class JemoMeshLambert(Check):
    name = 'jemo_mesh_lambert'
    label = u"jemo组默认材质"
    category = u"材质"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig']
    requires = ['jemo_group']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['jemo']):
            return

        for shape in _get_mesh_shapes(node_name):
            engines = cmds.listConnections('{}.instObjGroups'.format(shape),
                                           source=False, destination=True, type='shadingEngine') or []
            if not engines:
                self.errors.append(node_uuid)
                return
            for engine in engines:
                shaders = cmds.listConnections('{}.surfaceShader'.format(engine),
                                               source=True, destination=False) or []
                if 'lambert1' not in shaders:
                    self.errors.append(node_uuid)
                    return

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        _fix_sy_mesh_lambert(errors)


@register
class VisulCubeMeshMaterial(Check):
    name = 'visul_cube_mesh_material'
    label = u"脚底板材质"
    category = u"材质"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig-all']
    requires = ['cha_group']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['visulCube_Grp']):
            return

        for shape in _get_mesh_shapes(node_name):
            visul_cube__material_dict = {
                'AVC': 'visulFootCube_A_material',
                'BVC': 'visulFootCube_B_material',
            }
            engines = cmds.listConnections('{}.instObjGroups'.format(shape),
                                            source=False, destination=True, type='shadingEngine') or []
            if not engines:
                self.errors.append(node_uuid)
                return
            for engine in engines:
                shaders = cmds.listConnections('{}.surfaceShader'.format(engine),
                                                source=True, destination=False) or []

                for key, value in visul_cube__material_dict.items():
                    if key in shape:
                        if value not in shaders:
                            self.errors.append(node_uuid)
                            return


@register
class SyMeshLambert(Check):
    name = 'sy_mesh_lambert'
    label = u"示意组默认材质"
    category = u"材质"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig-all']
    requires = ['sy_group']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        sy_groups = cmds.ls('*_SY_Gro')
        if not node_name or not in_group(node_name, sy_groups):
            return

        for shape in _get_mesh_shapes(node_name):
            engines = cmds.listConnections('{}.instObjGroups'.format(shape),
                                           source=False, destination=True, type='shadingEngine') or []
            if not engines:
                self.errors.append(node_uuid)
                return
            for engine in engines:
                shaders = cmds.listConnections('{}.surfaceShader'.format(engine),
                                               source=True, destination=False) or []
                if 'lambert1' not in shaders:
                    self.errors.append(node_uuid)
                    return

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        _fix_sy_mesh_lambert(errors)


@register
class VisulCube(Check):
    name = 'visul_cube'
    label = u"visulCube_Grp"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig']
    requires = ['cha_group']

    def run(self):
        visul_cube_groups = cmds.ls('visulCube_Grp', long=True)
        if not visul_cube_groups:
            self.errors.append(u"visulCube_Grp组不存在")

    def fix(self, errors=None):
        cmds.group(em=True, name='visulCube_Grp', parent='Cha')


@register
class NgNode(Check):
    name = 'ng_node'
    label = u"NG节点"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'node'
    stages = ['rig']

    def run(self):
        ng_nodes = cmds.ls(type='ngst2SkinLayerData') or []
        self.errors.extend(ng_nodes)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            cmds.delete(node)


@register
class ExtraShoulderGroup(Check):
    name = 'extra_shoulder_group'
    label = u"驱动表情后多出两个空组"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'node'
    stages = ['rig']

    extra_shoulder_groups = ['SDKFKExtraShoulder_L', 'SDKFKExtraShoulder_R']

    def run(self):
        for extra_shoulder_group in self.extra_shoulder_groups:
            if cmds.objExists(extra_shoulder_group):
                self.errors.append(extra_shoulder_group)


@register
class SoftNormalHistory(Check):
    name = 'soft_normal_history'
    label = u"软边与法线历史"
    category = u"绑定"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Geometry']):
            return
        for shape in _get_mesh_shapes(node_name):
            historys = cmds.listHistory(shape) or []
            if cmds.ls(historys, type=['polySoftEdge', 'polyNormalPerVertex']):
                self.errors.append(node_uuid)
                return

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        cmds.bakePartialHistory(errors, prePostDeformers=True)


@register
class BsWedigtConnectHeadAttr(Check):
    name = 'bs_wedigt_connect_head_attr'
    label = u"bs关联Head_M"
    category = u"绑定"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig-all']

    def prepare(self):
        self.context['results'][self.name] = {}
        self._checked_weights = set()

    def _is_head_attr_driven(self, weight):
        """
        判断头骨上是否已有该属性且已被连接驱动

        Args:
            weight (str): bs权重属性名

        Returns:
            bool: 头骨上该属性存在且已有输入连接
        """
        try:
            if not cmds.attributeQuery(weight, node='Head_M', exists=True):
                return False
            return bool(cmds.connectionInfo('Head_M.{}'.format(weight),
                                            sourceFromDestination=True))
        except Exception:
            return False

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Geometry']):
            return

        blend_shapes = get_blend_shape(node_name)
        for blend_shape in blend_shapes:
            weights = cmds.listAttr('{}.weight'.format(blend_shape), multi=True) or []
            for weight in weights:
                # 同名属性只检查一次
                if weight in self._checked_weights:
                    continue
                if self._is_head_attr_driven(weight):
                    self._checked_weights.add(weight)
                    continue

                blend_shape_weight = '{}.{}'.format(blend_shape, weight)
                self._checked_weights.add(weight)
                destinations = cmds.connectionInfo(blend_shape_weight, destinationFromSource=True)
                if not destinations:
                    self.errors[blend_shape_weight] = u"没有连接至Head_M"
                elif len(destinations) == 1:
                    try:
                        is_connected = cmds.isConnected(blend_shape_weight,
                                                        'Head_M.{}'.format(weight))
                        if not is_connected:
                            self.errors[blend_shape_weight] = u"没有连接至Head_M"
                    except ValueError:
                        self.errors[blend_shape_weight] = u"Head_M没有属性{}".format(weight)
                elif len(destinations) > 1:
                    self.errors[blend_shape_weight] = u"有多个输出连接"

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for blend_shape_weight in errors:
            blend_shape, weight = blend_shape_weight.split('.')

            connections = cmds.listConnections(blend_shape_weight, source=False, destination=True, plugs=True) or []
            for connection in connections:
                cmds.disconnectAttr(blend_shape_weight, connection)

            if not cmds.attributeQuery(weight, node='Head_M', exists=True):
                duplicate_attr(blend_shape, weight, 'Head_M')

            cmds.connectAttr(blend_shape_weight, 'Head_M.{}'.format(weight), force=True)


@register
class MultiBlendshape(Check):
    name = 'multi_blendshape'
    label = u"多重BS层"
    category = u"绑定"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['SK_G', 'Geometry']):
            return
        for shape in _get_mesh_shapes(node_name):
            deformers = _get_mesh_deformers(shape)
            skin_cluster = cmds.ls(deformers, type='skinCluster')
            if not skin_cluster:
                continue
            skin_cluster_index = deformers.index(skin_cluster[0])
            befor_skin_bs = cmds.ls(deformers[0: skin_cluster_index], type='blendShape') or []
            after_skin_bs = cmds.ls(deformers[skin_cluster_index + 1: ], type='blendShape') or []
            if len(after_skin_bs) > 1:
                self.errors.append(node_uuid)
                continue

            if self.file_info.get_type() == 'CH':
                if befor_skin_bs:
                    self.errors.append(node_uuid)
                    continue
            elif self.file_info.get_type() == 'Dyn':
                if len(befor_skin_bs) > 1:
                    self.errors.append(node_uuid)
                    continue
            else:
                raise TypeError(u'非绑定文件')


@register
class LocgController(Check):
    name = 'locg_controller'
    label = u"LOCG控制器"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig']

    def run(self):
        if not _obj_exists('QieHuan_Con'):
            self.errors.append(u"QieHuan_Con 控制器不存在")


@register
class LocgReferen(Check):
    name = 'locg_referen'
    label = u"LOCG Referen关联"
    category = u"绑定"
    check_type = 'mesh'
    result_type = 'node'
    stages = ['rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Geometry']):
            return

        connection_transform = False
        connection_shape = False

        transform_connections = cmds.listConnections('{}.overrideDisplayType'.format(node_name), source=True, destination=False) or []
        if transform_connections:
            connection_transform = True

        for shape in _get_mesh_shapes(node_name):
            shape_connections = cmds.listConnections('{}.overrideDisplayType'.format(shape), 
                                                     source=True, destination=False) or []
            if shape_connections:
                connection_shape = True
                break

        if not (connection_transform or connection_shape):
            self.errors.append(node_name)


@register
class ControllerTransform(Check):
    name = 'controller_transform'
    label = u"控制器存在位移旋转缩放值"
    category = u"绑定"
    check_type = 'controller'
    result_type = 'node'
    stages = ['rig']

    identity_matrix = (
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0
    )
    transform_attrs = [
        'translateX', 'translateY', 'translateZ',
        'rotateX', 'rotateY', 'rotateZ',
        'scaleX', 'scaleY', 'scaleZ',
    ]

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Cha', 'MotionSystem']):
            return

        # 跳过Transform属性不能K帧的控制器
        has_keyable_transform = any(
            cmds.getAttr(
                '{}.{}'.format(node_name, attr),
                keyable=True
            )
            for attr in self.transform_attrs
        )
        if not has_keyable_transform:
            return

        matrix = cmds.getAttr('{}.matrix'.format(node_name))
        is_identity = all(
            abs(value - default) <= 0.0001
            for value, default in zip(matrix, self.identity_matrix)
        )
        if not is_identity:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for controller in errors:
            cmds.setAttr('{}.translate'.format(controller), 0, 0, 0)
            cmds.setAttr('{}.rotate'.format(controller), 0, 0, 0)
            cmds.setAttr('{}.scale'.format(controller), 1, 1, 1)


@register
class FingerAttr(Check):
    name = 'finger_attr'
    label = u"手指属性归0"
    category = u"绑定"
    check_type = 'controller'
    result_type = 'node'
    stages = ['rig']

    def prepare(self):
        self.context['results'][self.name] = {}

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or 'Fingers' not in node_name:
            return

        warning = ''
        user_attrs = cmds.listAttr(node_name, keyable=True, userDefined=True, scalar=True) or []
        for attr in user_attrs:
            value = cmds.getAttr('{}.{}'.format(node_name, attr))
            if abs(value) > 0.0001:
                warning += u"[{}] = {} ".format(attr, value)
        if warning:
            self.errors[node_uuid] = warning

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for controller in errors:
            user_attrs = cmds.listAttr(controller, keyable=True, userDefined=True, scalar=True) or []
            for attr in user_attrs:
                cmds.setAttr('{}.{}'.format(controller, attr), 0)


@register
class ShapeExpression(Check):
    name = 'shape_expression'
    label = u"Shape表达式清理"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'node'
    # stages = ['rig']

    def run(self):
        asset_nodes = cmds.ls('*AssetGlobals*') or []
        for node in asset_nodes:
            if node not in self.errors:
                self.errors.append(node)

        script_nodes = cmds.ls(type='script') or []
        for script_node in script_nodes:
            before_value = ''
            try:
                before_value = cmds.getAttr('{}.before'.format(script_node))
            except RuntimeError:
                continue
            if before_value and 'SHAPESShapes' in str(before_value):
                if script_node not in self.errors:
                    self.errors.append(script_node)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            try:
                cmds.lockNode(node, lock=0)
            except RuntimeError:
                pass
            cmds.delete(node)


@register
class JointLock(Check):
    name = 'joint_lock'
    label = u"蒙皮骨骼锁定"
    category = u"绑定"
    check_type = 'joint'
    result_type = 'node'
    stages = ['rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['DeformationSystem']):
            return
        for attr in TRANSFORM_ATTRS:
            if cmds.getAttr('{}.{}'.format(node_name, attr), lock=True):
                self.errors.append(node_uuid)
                return

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for joint in errors:
            for attr in TRANSFORM_ATTRS:
                cmds.setAttr('{}.{}'.format(joint, attr), lock=False)


@register
class LockedShadingGroup(Check):
    name = 'locked_shading_group'
    label = u"解决模型创建不显示"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig']

    def run(self):
        if cmds.lockNode('initialShadingGroup', query=True, lock=True)[0]:
            self.errors.append(u"initialShadingGroup被锁定")

    def fix(self, errors=None):
        cmds.lockNode('initialShadingGroup', lock=0, lockUnpublished=0)


@register
class RigEffectGroupExist(Check):
    name = 'rig_effect_group_exist'
    label = u"特效简模组"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'text'
    stages = ['rig-all']

    def run(self):
        groups = cmds.ls('TeXiao_JianMo', type='transform', long=True)
        if not groups:
            self.errors.append(u'特效简模组不存在')
            return

        if len(groups) > 1:
            self.errors.append(u'特效简模组存在多个')
            return

        if not in_group(groups[0], ['Geometry']):
            self.errors.append(u'特效简模组不在Geometry组下')
            return

        if cmds.getAttr('TeXiao_JianMo.visibility'):
            self.errors.append(u'特效组简模组未隐藏')
            return

    def fix(self, errors=None):
        geometry_child = cmds.listRelatives('Geometry', type='transform', children=True)[0]
        if not cmds.objExists('TeXiao_JianMo'):
            cmds.group(em=True, name='TeXiao_JianMo', parent=geometry_child)

        groups = cmds.ls('TeXiao_JianMo', type='transform', long=True)
        if len(groups) > 1:
            cmds.warning(u'特效简模组存在多个，请手动删除多余的组')
            return

        if not in_group(groups[0], [geometry_child]):
            cmds.parent('TeXiao_JianMo', geometry_child)

        if cmds.getAttr('TeXiao_JianMo.visibility'):
            cmds.setAttr('TeXiao_JianMo.visibility', 0)


@register
class LocgEyecrystal(Check):
    name = 'locg_eyecrystal'
    label = u"LOCG眼球晶状体关联"
    category = u"绑定"
    check_type = 'scene'
    result_type = 'node'
    stages = ['rig']
    requires = ['locg_controller']

    def run(self):
        eyecrystals = cmds.ls(['*eyecrystal', 'eyeshell*'], type='transform') or None
        if not eyecrystals:
            return

        for eyecrystal in eyecrystals:
            object_attr = '{}.visibility'.format(eyecrystal)
            source = cmds.connectionInfo(object_attr, sourceFromDestination=True) or None

            if not source and source != 'QieHuan_Con.glasses_eye_Vis':
                self.errors.append(eyecrystal)
                continue

            if cmds.getAttr('QieHuan_Con.glasses_eye_Vis') == 1:
                self.errors.append(eyecrystal)
                continue

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for eyecrystal in errors:
            object_attr = '{}.visibility'.format(eyecrystal)
            source = cmds.connectionInfo(object_attr, sourceFromDestination=True) or None
            if not source:
                cmds.connectAttr('QieHuan_Con.glasses_eye_Vis', object_attr)

            cmds.setAttr('QieHuan_Con.glasses_eye_Vis', 0)


@register
class ExpressionRig(Check):
    name = 'expression_rig'
    label = u"表达式节点"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['rig']

    def run(self):
        expressions = cmds.ls(type='expression')
        if not expressions:
            return

        delete_patterns = ['xgmRefreshPreview']
        for expression in expressions:
            for delete_pattern in delete_patterns:
                if delete_pattern in expression:
                    self.errors.append(expression)
                    break

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for expression in errors:
            try:
                cmds.lockNode(expression, lock=False)
            except RuntimeError:
                pass
            cmds.delete(expression)


@register
class ScriptNodeRig(Check):
    name = 'script_node_rig'
    label = u"脚本节点"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['rig']

    def run(self):
        script_nodes = cmds.ls(type='script')
        if not script_nodes:
            return

        delete_patterns = ['xgenGlobals', 'gsColorShaderStorageNode', 'gsMaterialStorageNode', 'saveClean', 'openClean']
        for script_node in script_nodes:
            for delete_pattern in delete_patterns:
                if delete_pattern in script_node:
                    self.errors.append(script_node)
                    break

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for script_node in errors:
            try:
                cmds.lockNode(script_node, lock=False)
            except RuntimeError:
                pass
            cmds.delete(script_node)


@register
class PastedNamingRig(Check):
    name = 'pasted_naming_rig'
    label = u"模型pasted__命名"
    category = u"命名"
    check_type = 'transform'
    result_type = 'node'
    stages = ['rig-all']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or not in_group(node_name, ['Geometry']):
            return
        
        if 'pasted__' in node_name:
            self.errors.append(node_name)
    
    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for pasted_node in errors:
            cmds.delete(pasted_node)
