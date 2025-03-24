#coding=utf-8
from pkgutil import extend_path
import sys

from mayaTools.core.log import log
import pymel.core as pm
# 确保之后导入mayaTools模块时使用__path__作为路径
__path__ = extend_path(__path__, __name__)




def install(menuID="mayaTools"):
    #确保不重复创建
    if pm.menu(menuID, exists=True):
        pm.deleteUI(menuID)
    menuID = pm.menu(menuID,
            parent="MayaWindow",
            tearOff=True,
            allowOptionBoxes=True,
            label=menuID)
    import mayaTools.pipline as pipline
    pipline.install(menuID)
    import mayaTools.lightTools as lightTools
    lightTools.install(menuID)
    import mayaTools.export as export
    export.install(menuID)
    import mayaTools.optimize as optimize
    optimize.install(menuID)
    import mayaTools.editTools as edit
    edit.install(menuID)
    
    

def reloadModule(name="mayaTools",*args):
    for mod in sys.modules.copy():
        if mod.startswith(name):
            log("delete model:{0}".format(mod))
            del sys.modules[mod]

if __name__ == "__main__":
    reloadModule()
