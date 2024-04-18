#coding=utf-8
#Init maya menu
from mayaTools import reloadModule
reloadModule()



from pymel.core.general import evalDeferred


def installMenu():
    import mayaTools.menu
    mayaTools.install()

    import mayaTools.export.menu
    mayaTools.export.menu.install()
    
evalDeferred(installMenu)










