# -*- coding: utf-8 -*-

import maya.cmds as cmds

_COMPONENT_MAP = {
    'uv': ".map[{}]",
    'vertex': ".vtx[{}]",
    'edge': ".e[{}]",
    'face': ".f[{}]",
}


def parse_errors(errors):
    """
    解析诊断错误数据，生成可选的组件路径列表

    依据 result_type 分三种解析方式：
    - "text": 纯文本结果，原样返回字符串列表
    - "node": 自动识别 uuids 为列表（纯节点，text 为空串）
             或字典（节点到错误信息的映射），统一输出 {"node": 路径, "text": msg} 条目
    - "uv"/"vertex"/"edge"/"face": 组件类型，拼出 ".map[i]/.vtx[i]/.e[i]/.f[i]" 路径

    Args:
        errors (dict): 诊断结果，包含 result_type 和 uuids

    Returns:
        list: 解析结果，字符串路径或 {"node": str, "text": str} 条目
    """
    uuids = errors['uuids']
    result_type = errors['result_type']

    if result_type == 'text':
        return uuids

    if result_type == 'node':
        nodes = []
        if isinstance(uuids, dict):
            for node, message in uuids.items():
                nodeName = cmds.ls(node)
                if nodeName:
                    node = nodeName[0]
                nodes.append({'node': node, 'text': message or u''})
        else:
            for node in uuids:
                nodeName = cmds.ls(node)
                if nodeName:
                    node = nodeName[0]
                nodes.append({'node': node, 'text': u''})
        return nodes

    output_errors = []

    if not uuids:
        return {} if result_type in _COMPONENT_MAP.keys() else []
    
    for uuid, components in uuids.items():
        nodeName = cmds.ls(uuid)
        if nodeName:
            for component in components:
                output_errors.append(nodeName[0] + _COMPONENT_MAP[result_type].format(component))
    return output_errors


def get_selectable(parsed):
    """
    从解析结果中提取可被 Maya 选中的路径列表

    Args:
        parsed (list): parse_errors 的解析结果，条目可能是 str 路径或 {"node": 路径, "text": msg}

    Returns:
        list: Maya 可选中的节点/组件路径列表
    """
    selectable = []
    for item in parsed:
        if isinstance(item, dict):
            selectable.append(item.get('node', ''))
        else:
            selectable.append(item)
    return selectable


def count_errors(diagnostics):
    """
    统计通过、失败和待定的检查数量

    Args:
        diagnostics (dict): 诊断结果字典

    Returns:
        tuple: (通过数, 总检查数, 待定数)
    """
    passed = 0
    blocked = 0
    for diag in diagnostics.values():
        status = diag.get('status')
        if status == 'passed':
            passed += 1
        elif status == 'blocked':
            blocked += 1
        elif status is None and not diag.get('uuids'):
            passed += 1
    return passed, len(diagnostics), blocked
