#coding=utf-8
#Init maya menu

# 将本插件的vendor目录插入到python环境的第一位
import sys
for path in sys.path:
    if "vendor" in path:
        break
sys.path.remove(path)
sys.path.insert(0,path)

import maya.cmds as cmds
from mayaTools import install
cmds.evalDeferred(install)











