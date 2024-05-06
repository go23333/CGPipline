#coding=utf-8
#Init maya menu

from mayaTools import reloadModule
reloadModule()

import sys
for path in sys.path:
    if "vendor" in path:
        break
sys.path.remove(path)
sys.path.insert(0,path)

from pymel.core.general import evalDeferred

def installMenu():
    
    import mayaTools.menu
    mayaTools.install()

    import mayaTools.export.menu
    mayaTools.export.menu.install()


    import mayaTools.optimize.menu
    mayaTools.optimize.menu.install()

    import mayaTools.pipline.menu
    mayaTools.pipline.menu.install()

    import mayaTools.thirdpart.menu
    mayaTools.thirdpart.menu.install()
    
evalDeferred(installMenu)










