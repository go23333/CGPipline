# -*- coding: utf-8 -*-

import re
from collections import defaultdict

import maya.cmds as cmds

from zynn_check.core.check import Check, register
from zynn_check.core.fileinfo import FileInfo
from zynn_check.core.utils import get_assemblies, is_node_referenced


SHARED_REFERENCE_NODE = 'sharedReferenceNode'


def _reference_nodes():
    """
    获取场景中所有引用节点（排除共享引用节点）

    Returns:
        list: 引用节点名称列表
    """
    refs = []
    for ref_node in cmds.ls(type='reference') or []:
        if SHARED_REFERENCE_NODE in ref_node:
            continue
        refs.append(ref_node)
    return refs


@register
class Reference(Check):
    name = 'reference'
    label = u"引用节点"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model', 'shading', 'rig']

    def run(self):
        ref_nodes = cmds.ls(type='reference')
        if ref_nodes:
            self.errors.extend(ref_nodes)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for ref_node in errors:
            try:
                ref_path = cmds.referenceQuery(ref_node, filename=True)
                cmds.file(ref_path, removeReference=True)
            except RuntimeError:
                if cmds.lockNode(ref_node, query=True, lock=True):
                    cmds.lockNode(ref_node, lock=False)
                cmds.delete(ref_node)


@register
class DamagedReferenceNode(Check):
    name = 'damaged_reference_node'
    label = u"损坏的引用节点"
    category = u"引用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']

    def run(self):
        ref_nodes = _reference_nodes()
        reference_info = {}
        for ref_node in ref_nodes:
            try:
                ref_path = cmds.referenceQuery(ref_node, filename=True)
                reference_info[ref_node] = {
                    'path': ref_path,
                }
            except RuntimeError:
                self.errors.append(ref_node)
                continue

        self.context['shared']['reference_info'] = reference_info

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for ref_node in errors:
            if cmds.lockNode(ref_node, query=True, lock=True):
                cmds.lockNode(ref_node, lock=False)
            cmds.delete(ref_node)


@register
class UnloadReference(Check):
    name = 'unload_reference'
    label = u"未加载的引用文件"
    category = u"引用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['damaged_reference_node']

    def run(self):
        for ref_node in self.context['shared']['reference_info'].keys():
            if not cmds.referenceQuery(ref_node, isLoaded=True):
                self.errors.append(ref_node)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for ref_node in errors:
            cmds.file(removeReference=True, referenceNode=ref_node)


@register
class NonTopLevelReference(Check):
    name = 'non_top_level_reference'
    label = u"非顶层引用"
    category = u"引用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['damaged_reference_node']

    def run(self):
        for ref_node in self.context['shared']['reference_info'].keys():
            if cmds.referenceQuery(ref_node, rfn=True, parent=True):
                self.errors.append(ref_node)


@register
class ReferenceRightDrive(Check):
    name = 'reference_right_drive'
    label = u"引用文件路径正确"
    category = u"引用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['damaged_reference_node']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(str)

    def run(self):
        for ref_node, info in self.context['shared'].get('reference_info', {}).items():
            project = self.file_info.get_project()
            ref_file_path = info['path']

            if 'Y:/{}'.format(project) not in ref_file_path.upper():
                self.errors[ref_node] = ref_file_path


@register
class ReferenceNodeLoadFile(Check):
    name = 'reference_node_load_file'
    label = u"引用节点引用正确文件"
    category = u"引用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['unload_reference']

    def run(self):
        for ref_node, info in self.context['shared'].get('reference_info', {}).items():
            ref_file_info = FileInfo(info['path'])
            ref_name = ref_file_info.get_stem()
            ref_node_search = re.search('^({})[0-9]{{0,2}}RN[0-9]{{0,2}}'.format(ref_name), ref_node)
            if not ref_node_search:
                self.errors.append(ref_node)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for ref_node in errors:
            ref_path = cmds.referenceQuery(ref_node, filename=True)

            ref_file_info = FileInfo(ref_path)
            ref_entity_name = ref_file_info.get_entity_name()

            new_ref_name = ref_node.split('_')[0]
            new_ref_path = ref_path.replace(ref_entity_name, new_ref_name)
            cmds.file(new_ref_path, loadReference=ref_node)


@register
class ReferenceNamespace(Check):
    name = 'reference_namespace'
    label = u"引用命名空间"
    category = u"引用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['unload_reference']

    def run(self):
        for ref_node in self.context['shared'].get('reference_info', {}).keys():
            namespace = cmds.referenceQuery(ref_node, namespace=True).strip(':')
            ref_node_suffix = re.search('[0-9]{0,2}RN[0-9]{0,2}', ref_node).group(0)
            ref_node_name = ref_node.replace(ref_node_suffix, '')
            if not re.search('^{}[0-9]{{0,2}}$'.format(ref_node_name), namespace):
                self.errors.append(ref_node)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for ref_node in errors:
            namespace = cmds.referenceQuery(ref_node, namespace=True).strip(':')
            ref_node_suffix = re.search('[0-9]{0,2}RN[0-9]{0,2}', ref_node).group(0)
            ref_node_name = ref_node.replace(ref_node_suffix, '')

            index = 0
            new_namespace = ref_node_name
            while index < 100:
                try:
                    cmds.namespace(rename=[namespace, new_namespace])
                    break
                except RuntimeError:
                    index += 1
                    new_namespace = ref_node_name + str(index)


@register
class UnreferenceAsset(Check):
    name = 'unreference_asset'
    label = u"非引用资产"
    category = u"通用"
    check_type = 'scene'
    result_type = 'node'
    stages = ['layout', 'animation']
    requires = ['camera_level']

    def run(self):
        top_transforms = get_assemblies()
        for transform in top_transforms:
            if transform.lower() in ['effects_g', 'ly_shiyi', '|effects_g', '|ly_shiyi']:
                continue

            if '_cam' in transform:
                continue

            if is_node_referenced(transform):
                continue

            self.errors.append(transform)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        cmds.delete(errors)
