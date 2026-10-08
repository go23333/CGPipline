# -*- coding: utf-8 -*-

import maya.cmds as cmds

from zynn_check.core.check import Check, register
from zynn_check.core.config import AI_CAMERA_ATTRS, DEFAULT_CAMERA_SHAPES
from zynn_check.core.utils import (
    get_camera_shapes,
    get_node_name,
    verify_camera_name,
)


CAMERA_SHAPE_ATTR_DICT = {
    'horizontalFilmAperture': 1.41732,
    'verticalFilmAperture': 0.94488,
    'lensSqueezeRatio': 1,
    'fStop': 5.6,
    'focusDistance': 5,
    'shutterAngle': 144,
    'motionBlurOverride': 0
}


@register
class AbnormalCamera(Check):
    name = 'abnormal_camera'
    label = u"多余相机"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading', 'rig']

    def run(self):
        for camera in cmds.ls(type='camera'):
            if camera not in DEFAULT_CAMERA_SHAPES:
                self.errors.append(camera)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for camera in errors:
            cmds.delete(camera)


@register
class CameraExist(Check):
    name = 'camera_exist'
    label = u"相机存在"
    category = u"相机"
    check_type = 'scene'
    result_type = 'text'
    stages = ['layout', 'animation']
    requires = ['lens_file_name']

    def run(self):
        lens_name = self.file_info.get_lens_name()
        camera_shapes = get_camera_shapes()
        if not camera_shapes:
            self.errors.append(u"场景中缺少相机")
            return

        if len(camera_shapes) > 1:
            self.errors.append(u"场景中存在多个相机")
            return

        camera_shape = camera_shapes[0]
        camera_transform = cmds.listRelatives(camera_shape, parent=True)[0]
        is_valid = verify_camera_name(lens_name, camera_transform)
        if not is_valid:
            self.errors.append(u"相机命名不符合规范")
            return

        self.context['shared']['main_camera_transform'] = camera_transform
        self.context['shared']['main_camera_shape'] = camera_shape


@register
class CameraPivot(Check):
    name = 'camera_pivot'
    label = u"相机枢轴"
    category = u"相机"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['camera_exist']

    def run(self):
        camera_transform = self.context['shared'].get('main_camera_transform')
        if not camera_transform:
            return
        cam_pos = cmds.xform(camera_transform, q=True, ws=True, t=True)
        pivot_pos = cmds.xform(camera_transform, q=True, ws=True, rp=True)
        distance = sum((cam_pos[i] - pivot_pos[i]) ** 2 for i in range(3)) ** 0.5
        if distance > 0.001:
            self.errors.append(camera_transform)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for camera in errors:
            cam_pos = cmds.xform(camera, q=True, ws=True, t=True)
            cmds.xform(camera, ws=True, rp=cam_pos, sp=cam_pos, p=True)


@register
class CameraLevel(Check):
    name = 'camera_level'
    label = u"相机层级"
    category = u"相机"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['camera_exist']

    def run(self):
        camera_transform = self.context['shared'].get('main_camera_transform')
        if not camera_transform:
            return
        camera_parents = cmds.listRelatives(camera_transform, parent=True)
        camera_children = cmds.listRelatives(camera_transform, children=True, type='transform')
        if camera_parents or camera_children:
            self.errors.append(camera_transform)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors

        camera_transform = errors[0]
        camera_shape = cmds.listRelatives(camera_transform, shapes=True, type='camera')[0]
        new_camera_name = '{}_new'.format(camera_transform)
        new_camera, new_camera_shape = cmds.camera(name=new_camera_name)

        near_clip = cmds.getAttr('{}.nearClipPlane'.format(camera_shape))
        far_clip = cmds.getAttr('{}.farClipPlane'.format(camera_shape))
        hfa = cmds.getAttr('{}.horizontalFilmAperture'.format(camera_shape))
        vfa = cmds.getAttr('{}.verticalFilmAperture'.format(camera_shape))
        film_fit = cmds.getAttr('{}.filmFit'.format(camera_shape))

        cmds.setAttr('{}.nearClipPlane'.format(new_camera_shape), near_clip)
        cmds.setAttr('{}.farClipPlane'.format(new_camera_shape), far_clip)
        cmds.setAttr('{}.horizontalFilmAperture'.format(new_camera_shape), hfa)
        cmds.setAttr('{}.verticalFilmAperture'.format(new_camera_shape), vfa)
        cmds.setAttr('{}.filmFit'.format(new_camera_shape), film_fit)

        cmds.setAttr('{}.displayGateMaskOpacity'.format(new_camera_shape), 1)
        cmds.setAttr('{}.displayGateMaskColor'.format(new_camera_shape), 0, 0, 0, type='double3')

        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)
        for frame in range(int(start_frame), int(end_frame) + 1):
            cmds.currentTime(frame, edit=True)

            pos = cmds.xform(camera_transform, q=True, ws=True, t=True)
            rot = cmds.xform(camera_transform, q=True, ws=True, ro=True)
            scale = cmds.xform(camera_transform, q=True, ws=True, s=True)

            cmds.setAttr('{}.tx'.format(new_camera), pos[0])
            cmds.setAttr('{}.ty'.format(new_camera), pos[1])
            cmds.setAttr('{}.tz'.format(new_camera), pos[2])
            cmds.setAttr('{}.rx'.format(new_camera), rot[0])
            cmds.setAttr('{}.ry'.format(new_camera), rot[1])
            cmds.setAttr('{}.rz'.format(new_camera), rot[2])
            cmds.setAttr('{}.sx'.format(new_camera), scale[0])
            cmds.setAttr('{}.sy'.format(new_camera), scale[1])
            cmds.setAttr('{}.sz'.format(new_camera), scale[2])

            focal_length = cmds.getAttr('{}.focalLength'.format(camera_shape))
            cmds.setAttr('{}.focalLength'.format(new_camera_shape), focal_length)
            cmds.setKeyframe(new_camera, at=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], t=[frame, frame])
            cmds.setKeyframe(new_camera_shape, at=['focalLength'], t=[frame, frame])


        for object in (new_camera, new_camera_shape):
            for attr in cmds.listAttr(object, keyable=True):
                if attr in AI_CAMERA_ATTRS:
                    continue
                cmds.setAttr('{}.{}'.format(object, attr), lock=True)

        self.delete_with_empty_parents(camera_transform)

        cmds.rename(new_camera, camera_transform)

    def delete_with_empty_parents(self, node):
        parent = cmds.listRelatives(node, parent=True, fullPath=True)
        if not parent:
            cmds.delete(node)
            return
        siblings = cmds.listRelatives(parent[0], children=True, type='transform') or []
        if len(siblings) == 1:
            self.delete_with_empty_parents(parent[0])
        else:
            cmds.delete(node)


@register
class CameraDefaultValue(Check):
    name = 'camera_default_value'
    label = u"相机默认属性值"
    category = u"相机"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['camera_exist']

    def run(self):
        camera_shape = self.context['shared'].get('main_camera_shape')
        if not camera_shape:
            return
        for attr, value in CAMERA_SHAPE_ATTR_DICT.items():
            object_attr = '{}.{}'.format(camera_shape, attr)
            current_value = cmds.getAttr(object_attr)
            if current_value != value:
                self.errors.append(object_attr)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for object_attr in errors:
            if cmds.getAttr(object_attr, lock=True):
                cmds.setAttr(object_attr, lock=False)

            attr = object_attr.split('.')[1]
            cmds.setAttr(object_attr, CAMERA_SHAPE_ATTR_DICT[attr], lock=True)


@register
class CameraAttrsLocked(Check):
    name = 'camera_attrs_locked'
    label = u"相机属性锁定"
    category = u"相机"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['camera_exist']

    def run(self):
        objects = []
        for key in ('main_camera_transform', 'main_camera_shape'):
            obj = self.context['shared'].get(key)
            if obj:
                objects.append(obj)
        for obj in objects:
            for attr in cmds.listAttr(obj, keyable=True):
                if attr in AI_CAMERA_ATTRS:
                    continue
                object_attr = '{}.{}'.format(obj, attr)
                if not cmds.getAttr(object_attr, lock=True):
                    self.errors.append(object_attr)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for object_attr in errors:
            cmds.setAttr(object_attr, lock=True)


@register
class DefaultResolution(Check):
    name = 'default_resolution'
    label = u"场景分辨率"
    category = u"相机"
    check_type = 'scene'
    result_type = 'text'
    stages = ['layout', 'animation']

    def run(self):
        width = cmds.getAttr("defaultResolution.width")
        height = cmds.getAttr("defaultResolution.height")

        if width != 2048 or height != 858:
            self.errors.append(u"默认分辨率不正确")

    def fix(self, errors=None):
        cmds.setAttr('defaultResolution.width', 2048)
        cmds.setAttr('defaultResolution.height', 858)


@register
class SceneUnit(Check):
    name = 'scene_unit'
    label = u"场景帧率"
    category = u"相机"
    check_type = 'scene'
    result_type = 'text'
    stages = ['layout', 'animation']

    def run(self):
        if cmds.currentUnit(query=True, time=True) != 'pal':
            self.errors.append(u"场景帧率不正确")

    def fix(self, errors=None):
        cmds.currentUnit(time='pal')


@register
class CameraStartFrame(Check):
    name = 'camera_start_frame'
    label = u"相机起始帧"
    category = u"相机"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['camera_exist', 'scene_unit']

    def prepare(self):
        self.context['results'][self.name] = {}

    def run(self):
        camera_transform = self.context['shared'].get('main_camera_transform')
        if not camera_transform:
            return

        should_start_frame = 1
        if self.file_info.get_project() == u'EMFZ_TWO':
            should_start_frame = 101
        
        camera_start_frame = int(camera_transform.split('_')[3])
        if camera_start_frame!= should_start_frame:
            self.errors[camera_transform] = u'相机命名中起始帧应为{:03d}'.format(should_start_frame)

    def fix(self, errors=None):
        should_start_frame = 1
        if self.file_info.get_project() == u'EMFZ_TWO':
            should_start_frame = 101

        errors = self.selectable() if errors is None else errors
        for camera in errors:
            camera_split = camera.split('_')
            camera_split[3] = '{:03d}'.format(should_start_frame)
            cmds.rename(camera, '_'.join(camera_split))


@register
class SceneFrame(Check):
    name = 'scene_frame'
    label = u"场景帧范围"
    category = u"相机"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['camera_start_frame']

    def prepare(self):
        self.context['results'][self.name] = {}

    def run(self):
        camera_transform = self.context['shared'].get('main_camera_transform')
        if not camera_transform:
            return
        camera_start_frame, camera_end_frame = [int(s) for s in camera_transform.split('_')[3: 5]]

        playback_start_frame = cmds.playbackOptions(q=1, min=1)
        playback_end_frame = cmds.playbackOptions(q=1, max=1)

        animation_start_frame = cmds.playbackOptions(q=True, ast=True)
        animation_end_frame = cmds.playbackOptions(q=True, aet=True)

        if (camera_start_frame != playback_start_frame or
            camera_end_frame != playback_end_frame or
            camera_start_frame != animation_start_frame or
            camera_end_frame != animation_end_frame):
            self.errors[camera_transform] = u'场景时间轴范围与相机时间轴范围不一致'

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for camera in errors:
            camera_start_frame, camera_end_frame = [int(s) for s in camera.split('_')[3: 5]]
            cmds.playbackOptions(ast=camera_start_frame, aet=camera_end_frame)
            cmds.playbackOptions(min=camera_start_frame, max=camera_end_frame)


@register
class FractionalFrame(Check):
    name = 'fractional_frame'
    label = u"小数帧"
    category = u"通用"
    check_type = 'transform'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['scene_frame']

    def prepare(self):
        self.context['results'][self.name] = set()

    def run(self, node_uuid):
        node = get_node_name(node_uuid)
        curves = cmds.listConnections(node, type='animCurve') or []
        for curve in curves:
            times = cmds.keyframe(curve, q=True, tc=True) or []

            for t in times:
                if t % 1 != 0:
                    self.errors.add(curve)
