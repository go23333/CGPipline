# -*- coding: utf-8 -*-

"""
通用工具函数

原先分散在 core/utils.py（节点标识）与 checks/utils.py（场景查询与拓扑判断）两处，
现合并到本模块：两者都是无状态纯工具，拆分只增加了 import 负担。
"""

import re
from collections import deque

import maya.cmds as cmds
import maya.api.OpenMaya as om

from zynn_check.core.config import (
    DEFAULT_CAMERA_SHAPES,
    DEFAULT_CAMERA_TRANSFORMS,
)


def get_node_name(node):
    """
    根据UUID或节点名获取节点长名

    Args:
        node (str): 节点UUID或节点名称

    Returns:
        str or None: 节点长名，取不到返回None
    """
    names = cmds.ls(node, long=True)
    if names:
        return names[0]
    else:
        return None


def get_node_uuid(name):
    """
    根据节点名称获取UUID

    Args:
        name (str): 节点名称

    Returns:
        str or None: 节点UUID
    """
    sel = om.MSelectionList()
    try:
        sel.add(name)
        return om.MFnDependencyNode(sel.getDependNode(0)).uuid().asString()
    except RuntimeError:
        return None


def names_to_uuids(names):
    """
    将节点名称列表批量转换为UUID（对非DAG节点也可靠）

    Args:
        names (list): 节点名称列表

    Returns:
        list: 节点UUID列表
    """
    uuids = []
    for name in names:
        uuid = get_node_uuid(name)
        if uuid:
            uuids.append(uuid)
    return uuids


def is_node_referenced(node_name):
    """
    判断节点是否来自引用文件

    Args:
        node_name (str): 节点UUID、节点名称或DAG路径

    Returns:
        bool: 是否来自引用文件
    """
    return cmds.referenceQuery(node_name, isNodeReferenced=True)


def get_assemblies():
    """获取除默认相机以外的顶层tarnsform"""
    assemblies = []
    transforms = cmds.ls(assemblies=True)
    for transform in transforms:
        if transform in DEFAULT_CAMERA_TRANSFORMS:
            continue
        assemblies.append(transform)

    return assemblies


def get_camera_shapes():
    """
    获取场景中所有非默认相机的shape节点名称

    Returns:
        list: 相机shape节点名称列表
    """
    camera_shapes = list(set(cmds.ls(type='camera')) - set(DEFAULT_CAMERA_SHAPES))
    return camera_shapes


def verify_camera_name(lens_name, camera_transform):
    """
    校验相机命名是否符合规范

    Args:
        lens_name (str): 镜头名称
        camera_transform (str): 相机transform节点名称

    Returns:
        bool: 命名是否符合规范
    """
    search = re.search('^{}_[0-9]{{3}}_[0-9]{{3}}_cam$'.format(lens_name), camera_transform)
    if search:
        return True
    else:
        return False


def is_node_used(node_name):
    """
    判断节点下游连接链是否被使用

    Args:
        node_name (str): 起始节点名称

    Returns:
        bool: 是否被使用
    """
    visited = set()
    queue = deque([node_name])
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        if cmds.nodeType(current) == 'shadingEngine':
            if cmds.sets(current, query=True):
                return True

        # 如果是毛发节点
        if cmds.nodeType(current) == 'RedshiftHair':
            if cmds.listConnections('{}.outColor'.format(node_name), 
                                    source=True, destination=True, plugs=True):
                return True

        queue.extend(cmds.listConnections(current, source=False, destination=True) or [])

    return False


def get_blend_shape(mesh_shape):
    """
    获取mesh shape上的BlendShape

    Args:
        mesh_shape (str): mesh shape

    Returns:
        list: blend_shapes
    """
    historys = cmds.listHistory(mesh_shape) or []
    blend_shapes = cmds.ls(historys, type='blendShape') or []

    return blend_shapes


def duplicate_attr(src_node, attr_name, target_node):
    """在目标节点上创建相同属性"""
    src = '{}.{}'.format(src_node, attr_name)
    dst = '{}.{}'.format(target_node, attr_name)

    attr_type = cmds.getAttr(src, type=True)
    kwargs = {'longName': attr_name, 'attributeType': attr_type}

    # 默认值
    try:
        kwargs['defaultValue'] = cmds.attributeQuery(attr_name, node=src_node, listDefault=True)[0]
    except:
        pass

    # 最小值
    if cmds.attributeQuery(attr_name, node=src_node, minExists=True):
        kwargs['minValue'] = cmds.attributeQuery(attr_name, node=src_node, minimum=True)[0]

    if cmds.attributeQuery(attr_name, node=src_node, softMinExists=True):
        kwargs['softMinValue'] = cmds.attributeQuery(attr_name, node=src_node, softMin=True)[0]

    # 最大值
    if cmds.attributeQuery(attr_name, node=src_node, maxExists=True):
        kwargs['maxValue'] = cmds.attributeQuery(attr_name, node=src_node, maximum=True)[0]

    if cmds.attributeQuery(attr_name, node=src_node, softMaxExists=True):
        kwargs['softMaxValue'] = cmds.attributeQuery(attr_name, node=src_node, softMax=True)[0]

    cmds.addAttr(target_node, **kwargs)

    # keyable 状态
    if cmds.getAttr(src, keyable=True):
        cmds.setAttr(dst, keyable=True)
    else:
        cmds.setAttr(dst, channelBox=True)

    return dst


def in_group(node_name, groups):
    """判断节点是否属于指定组（按长路径名祖先判断）"""
    if not node_name:
        return False
    parts = node_name.split('|')
    return any(group in parts for group in groups)
