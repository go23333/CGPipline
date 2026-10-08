# -*- coding: utf-8 -*-

import json

import maya.cmds as cmds


def save_preferences(stage_name, checked_commands):
    """
    保存检查设置到Maya optionVar，键名按环节隔离

    Args:
        stage_name (str): 环节名称
        checked_commands (dict): 命令复选框状态
    """
    settings = {
        'commands': checked_commands,
    }
    cmds.optionVar(sv=('{}CheckerPreferences'.format(stage_name), json.dumps(settings)))


def load_preferences(stage_name):
    """
    从Maya optionVar加载检查设置，键名按环节隔离

    Args:
        stage_name (str): 环节名称

    Returns:
        dict or None: 设置字典，不存在则返回None
    """
    settings = cmds.optionVar(q='{}CheckerPreferences'.format(stage_name))
    if settings:
        return json.loads(settings)
    return None
