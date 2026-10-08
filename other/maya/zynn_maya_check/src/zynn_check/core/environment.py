# -*- coding: utf-8 -*-

"""
运行时变量
"""

import sys
import platform

import maya.cmds as cmds


PYTHON_VERSION = sys.version
PYTHON_VERSION_INFO = sys.version_info

MAYA_VERSION = cmds.about(version=True)
MAYA_API_VERSION = cmds.about(apiVersion=True)

OS_NAME = platform.system()
OS_VERSION = platform.version()

STAGE = 'model'
