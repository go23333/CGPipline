# -*- coding: utf-8 -*-

import maya.cmds as cmds

from zynn_check.core.check import Check, register
from zynn_check.core.config import DEFAULT_MATERIALS, DEFAULT_SHADING_GROUPS
from zynn_check.core.utils import (
    get_node_name,
    get_node_uuid,
    is_node_referenced,
    is_node_used,
)


@register
class AbnormalMaterial(Check):
    name = 'abnormal_material'
    label = u"多余材质球"
    category = u"材质"
    check_type = 'material'
    result_type = 'node'
    stages = ['model']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name or node_name in DEFAULT_MATERIALS:
            return

        self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for material in errors:
            cmds.delete(material)


@register
class AbnormalSg(Check):
    name = 'abnormal_sg'
    label = u"多余着色器"
    category = u"材质"
    check_type = 'shading_group'
    result_type = 'node'
    stages = ['model']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if node_name and node_name not in DEFAULT_SHADING_GROUPS:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for sg in errors:
            obj_set = set()
            objs = cmds.sets(sg, query=True) or []
            for obj in objs:
                if cmds.nodeType(obj) == "mesh":
                    if '.' in obj:
                        obj = obj.split('.')[0]
                    obj_set.add(obj)

            for os in obj_set:
                cmds.sets(os, edit=True, forceElement="initialShadingGroup")
                cmds.setAttr('{}.displayColors'.format(os), 0)
            cmds.delete(sg)


@register
class Lambert1(Check):
    name = 'lambert1'
    label = u"lambert1默认材质"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['shading']

    def run(self):
        sgs = cmds.listConnections('lambert1.outColor', type='shadingEngine') or []
        for sg in sgs:
            members = cmds.sets(sg, query=True) or []
            for member in members:
                if cmds.nodeType(member) == 'mesh':
                    self.errors.append(member)


@register
class HasTexture(Check):
    name = 'has_texture'
    label = u"file节点贴图"
    category = u"材质"
    check_type = 'texture'
    result_type = 'node'
    stages = ['shading']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        node_type = cmds.nodeType(node_name)
        if node_type == 'file':
            file_path = cmds.getAttr('{}.fileTextureName'.format(node_name))
        elif node_type == 'RedshiftNormalMap':
            file_path = cmds.getAttr('{}.tex0'.format(node_name))
        else:
            return

        if not file_path:
            self.errors.append(node_uuid)


@register
class IsTexture(Check):
    name = 'is_texture'
    label = u"Texture贴图"
    category = u"材质"
    check_type = 'texture'
    result_type = 'node'
    stages = ['shading', 'rig']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        node_type = cmds.nodeType(node_name)
        if node_type == 'file':
            file_path = cmds.getAttr('{}.fileTextureName'.format(node_name))
        elif node_type == 'RedshiftNormalMap':
            file_path = cmds.getAttr('{}.tex0'.format(node_name))
        else:
            return

        if file_path and 'Texture' not in file_path:
            self.errors.append(node_uuid)


@register
class NonRefMaterialOnRefObject(Check):
    name = 'non_ref_material_on_ref_object'
    label = u"非引用材质赋予引用物体"
    category = u"材质"
    check_type = 'material'
    result_type = 'node'
    stages = ['layout', 'animation']

    def prepare(self):
        self.context['results'][self.name] = {}

    def run(self, node_uuid):
        material = get_node_name(node_uuid)
        if not material or is_node_referenced(material) or material == 'lambert1':
            return
        shading_engines = cmds.listConnections(material, type='shadingEngine') or []
        for shading_engine in shading_engines:
            members = cmds.sets(shading_engine, query=True) or []
            for member in members:
                if '.' in member:
                    member = member.split('.')[0]
                if not is_node_referenced(member):
                    continue
                parents = cmds.listRelatives(member, parent=True, type='transform') or []
                obj = parents[0] if parents else member
                obj_uuid = get_node_uuid(obj)
                if obj_uuid:
                    self.errors[obj_uuid] = material


@register
class UselessTexture(Check):
    name = 'useless_texture'
    label = u"无用贴图"
    category = u"材质"
    check_type = 'texture'
    result_type = 'node'
    stages = ['shading', 'rig', 'layout', 'animation']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return

        if not is_node_used(node_name):
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for texture in errors:
            if cmds.objExists(texture):
                cmds.delete(texture)


@register
class UselessMaterial(Check):
    name = 'useless_material'
    label = u"无用材质球"
    category = u"材质"
    check_type = 'material'
    result_type = 'node'
    stages = ['shading', 'rig', 'layout', 'animation']

    def run(self, node_uuid):
        # 因为制作人员替换文件的操作导致材质球的uuid重复，所以不走统一接口
        node_names = cmds.ls(node_uuid)
        if not node_names:
            return

        for node_name in node_names:
            # 跳过默认材质球
            if node_name in DEFAULT_MATERIALS:
                return

            if not is_node_used(node_name):
                self.errors.append(node_name)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for material in errors:
            if cmds.objExists(material):
                cmds.delete(material)


@register
class UselessShadingGroup(Check):
    name = 'useless_shading_group'
    label = u"无用shading group"
    category = u"材质"
    check_type = 'shading_group'
    result_type = 'node'
    stages = ['shading', 'rig', 'layout', 'animation']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return

        if node_name in DEFAULT_SHADING_GROUPS:
            return

        if not cmds.sets(node_name, query=True):
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for sg in errors:
            if cmds.objExists(sg):
                cmds.delete(sg)
