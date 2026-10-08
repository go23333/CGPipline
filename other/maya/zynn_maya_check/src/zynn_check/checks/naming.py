# -*- coding: utf-8 -*-

import re
from collections import defaultdict

import maya.cmds as cmds

from zynn_check.core.check import Check, register
from zynn_check.core.config import DEFAULT_CAMERA_LONG_TRANSFORMS, FILE_SUFFIX
from zynn_check.core import environment as env
from zynn_check.core.utils import get_node_name, names_to_uuids


@register
class DuplicatedNames(Check):
    name = 'duplicatedNames'
    label = u"重名"
    category = u"命名"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading', 'rig']

    def run(self):
        names = cmds.ls(transforms=True, long=True) or []
        names = [name for name in names if name not in DEFAULT_CAMERA_LONG_TRANSFORMS]

        nodesByShortName = defaultdict(list)
        for node_name in names:
            name = node_name.rsplit('|', 1)[-1]
            nodesByShortName[name].append(node_name)

        for name, shortNameNodes in nodesByShortName.items():
            if len(shortNameNodes) > 1:
                node_uuids = names_to_uuids(shortNameNodes)
                self.errors.extend(node_uuids)


@register
class Namespaces(Check):
    name = 'namespaces'
    label = u"命名空间"
    category = u"命名"
    check_type = 'scene'
    result_type = 'text'
    stages = ['model', 'shading', 'rig']

    def run(self):
        default_namespaces = [u'UI', u'shared']
        namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
        for namespace in namespaces:
            if namespace in default_namespaces:
                continue
            self.errors.append(namespace)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        # 按层级深度排序，最深的 namespace 优先删除
        namespaces = sorted(errors, key=lambda x: x.count(':'), reverse=True)
        for namespace in namespaces:
            cmds.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)


@register
class PastedNaming(Check):
    name = 'pasted_naming'
    label = u"pasted__命名"
    category = u"命名"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model-all', 'shading-all']

    def run(self):
        pasted_nodes = cmds.ls('pasted__*') or []
        for pasted_node in pasted_nodes:
            if cmds.objectType(pasted_node) == 'shadingEngine':
                continue

            self.errors.append(pasted_node)
    
    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        rename_node = ['lambert', 'RedshiftMaterial', 'hairPhysicalShader', 'file']
        for pasted_node in errors:
            node_type = cmds.objectType(pasted_node)
            if node_type in rename_node:
                cmds.rename(pasted_node, pasted_node.replace('pasted__', ''))
            else:
                cmds.delete(pasted_node)


@register
class ShapeNames(Check):
    name = 'shapeNames'
    label = u"shape命名"
    category = u"命名"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model', 'shading']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return

        node_split = node_name.split('|')
        shapes = cmds.listRelatives(node_name, shapes=True, f=True)
        if not shapes:
            return

        shape_split = shapes[0].split('|')
        shapename = node_split[-1] + 'Shape'
        if shape_split[-1] != shapename:
            self.errors.append(node_uuid)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for node in errors:
            node_split = node.split('|')
            shape = cmds.listRelatives(node, shapes=True, f=True)[0]
            shape_split = shape.split('|')
            shape_name = node_split[-1] + 'Shape'
            if shape_split[-1] != shape_name:
                cmds.rename(shape, shape_name)


@register
class LensFileName(Check):
    name = 'lens_file_name'
    label = u"文件命名"
    category = u"命名"
    check_type = 'scene'
    result_type = 'text'
    stages = ['layout', 'animation']

    def run(self):
        lens_name = self.file_info.get_lens_name()
        if not lens_name:
            self.errors.append(u'文件命名不符合规范')
            return

        suffix = FILE_SUFFIX[env.STAGE]
        if lens_name + suffix != self.file_info.get_name():
            self.errors.append(u'文件命名不符合规范')
            return


@register
class MaterialNameing(Check):
    name = 'material_nameing'
    label = u"材质球命名带数字"
    category = u"命名"
    check_type = 'material'
    result_type = 'node'
    stages = ['shading-all', 'rig-all']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return

        if any(key in node_name for key in  ['lambert', 'TouPi']):
            return

        if node_name in ['particleCloud1', 'standardSurface1', 'asGreen2', 'asBlue2']:
            return

        if cmds.nodeType(node_name) == 'hairPhysicalShader':
            return

        if re.search(r'\d$', node_name):
            self.errors.append(node_name)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for material in errors:
            cmds.rename(material, re.sub(r'\d+$', '', material))


@register
class BodyNaming(Check):
    name = 'body_naming'
    label = u"完整人体命名"
    category = u"命名"
    check_type = 'scene'
    result_type = 'text'
    stages = ['model', 'shading']

    def run(self):
        top_nodes = cmds.ls(assemblies=True)
        for top_node in top_nodes:
            if '_body_1' in top_node:
                return

        self.errors.append(u'缺少完整人体或其命名不符合规范')
