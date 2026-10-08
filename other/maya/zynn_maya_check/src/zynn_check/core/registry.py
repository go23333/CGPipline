# -*- coding: utf-8 -*-

import maya.cmds as cmds

from .config import STAGE_GROUPS


CHECK_REGISTRY = {}


def expand_stage(stage):
    """
    展开环节名称，返回该环节自身及其所属的所有分类

    只向上找分类，不会把分类展开成它下面的环节：
    expand_stage('model-all') 含 'model'，但 expand_stage('model') 只有 'model'。

    Args:
        stage (str): 环节名称，如 'model-all'

    Returns:
        set: 该环节可匹配的环节名称集合，如 {'model-all', 'model'}
    """
    expanded = set()
    pending = [stage]
    while pending:
        name = pending.pop()
        if name in expanded:
            continue
        expanded.add(name)
        groups = STAGE_GROUPS.get(name, ())
        # 容错：配置里误写成 ('model')（字符串）时不应被逐字符拆开
        if not isinstance(groups, (list, tuple)):
            groups = (groups,)
        pending.extend(groups)
    return expanded


def get_commands_list(stage):
    """
    获取指定环节的所有已注册命令

    检查类的 stages 与环节的展开集合存在交集即视为属于该环节，
    因此变体环节会继承上级环节的检查，而声明了变体环节的检查只在变体环节生效。

    Args:
        stage (str): 环节名称，如 'model' / 'model-all' / 'model-half'

    Returns:
        dict: {name: {'label': str, 'category': str}}
    """
    matched_stages = expand_stage(stage)
    commands = {}
    for name, cls in CHECK_REGISTRY.items():
        if matched_stages.intersection(cls.stages):
            commands[name] = {
                'label': cls.label,
                'category': cls.category,
            }
    return commands


def get_check_info(name):
    """
    获取指定命令的检查类

    Args:
        name (str): 命令名称

    Returns:
        type or None: 检查类，未注册返回 None
    """
    return CHECK_REGISTRY.get(name)


def _validate_requires():
    """
    校验所有检查注册信息完整,
    以及声明的 requires 依赖均已注册，否则发出警告
    """
    for name, cls in CHECK_REGISTRY.items():
        if not cls.check_type or not cls.result_type:
            cmds.warning(u"检查 [{}] 缺少 check_type 或 result_type, 二者缺一不可".format(name))
        for required in cls.requires:
            if required not in CHECK_REGISTRY:
                cmds.warning(u"检查 [{}] 声明的依赖 [{}] 未注册".format(name, required))
