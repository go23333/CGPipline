# -*- coding: utf-8 -*-

import maya.mel as mel
import maya.cmds as cmds

from zynn_check.core.check import Check, register
from zynn_check.core.config import AI_CAMERA_ATTRS
from zynn_check.core.utils import get_node_name


def _node_names(nodes):
    """把 UUID 列表还原为节点名（fix 由引擎/界面传入的可能是 UUID，也可能是名称）"""
    return [get_node_name(node) or node for node in nodes]


def _layer_short_name(name):
    """取层的短名，忽略 DAG 路径与命名空间前缀（引用文件里的层会带命名空间）"""
    return name.split('|')[-1].split(':')[-1]


@register
class DisplayLayer(Check):
    name = 'display_layer'
    label = u"显示层"
    category = u"通用"
    check_type = 'display_layer'
    result_type = 'node'
    stages = ['model', 'shading', 'rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if node_name and _layer_short_name(node_name) != 'defaultLayer':
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for layer in errors:
            cmds.delete(layer)


@register
class DisplayLayerLens(Check):
    name = 'display_layer_lens'
    label = u"显示层"
    category = u"通用"
    check_type = 'display_layer'
    result_type = 'node'
    stages = ['layout', 'animation']

    def prepare(self):
        self.context['results'][self.name] = {}

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return

        if _layer_short_name(node_name) == 'Norender':
            if cmds.getAttr('{}.visibility'.format(node_name)):
                self.errors[node_uuid] = u"显示层可见"
            return

        if _layer_short_name(node_name) != 'defaultLayer':
            self.errors[node_uuid] = u""

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for layer in _node_names(errors):
            if _layer_short_name(layer) == 'Norender':
                cmds.setAttr('{}.visibility'.format(layer), False)
                continue
            cmds.delete(layer)


@register
class RenderLayer(Check):
    name = 'render_layer'
    label = u"渲染层"
    category = u"通用"
    check_type = 'render_layer'
    result_type = 'node'
    stages = ['model', 'shading', 'rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if node_name and _layer_short_name(node_name) != 'defaultRenderLayer':
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for render_layer in errors:
            cmds.delete(render_layer)


@register
class AnimLayerAsset(Check):
    name = 'anim_layer_asset'
    label = u"动画层"
    category = u"通用"
    check_type = 'anim_layer'
    result_type = 'node'
    stages = ['model', 'shading', 'rig']

    def run(self, node_uuid):
        self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for anim_layer in errors:
            cmds.delete(anim_layer)


@register
class AnimLayerLens(Check):
    name = 'anim_layer_lens'
    label = u"动画层"
    category = u"通用"
    check_type = 'anim_layer'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['camera_level']

    def run(self, node_uuid):
        self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors

        objects = []
        for key in ('main_camera_transform', 'main_camera_shape'):
            obj = self.context['shared'].get(key)
            if obj:
                objects.append(obj)

        # 解锁相机属性
        for obj in objects:
            for attr in cmds.listAttr(obj, keyable=True):
                if attr in AI_CAMERA_ATTRS:
                    continue
                object_attr = '{}.{}'.format(obj, attr)
                if not cmds.getAttr(object_attr, lock=False):
                    self.errors.append(object_attr)

        # string $layers[] = {"AnimLayer1","BaseAnimation"}; layerEditorMergeAnimLayer($layers, 0);
        layer_names = _node_names(errors)
        if len(layer_names) > 1:
            mel_cmd = 'string $layers[] = {{{}}}; layerEditorMergeAnimLayer($layers, 0);'.format(
                ','.join(['"{}"'.format(l) for l in layer_names])
            )
            mel.eval(mel_cmd)
        cmds.delete('BaseAnimation')

        # 锁定相机属性
        for obj in objects:
            for attr in cmds.listAttr(obj, keyable=True):
                if attr in AI_CAMERA_ATTRS:
                    continue
                object_attr = '{}.{}'.format(obj, attr)
                if not cmds.getAttr(object_attr, lock=True):
                    self.errors.append(object_attr)
