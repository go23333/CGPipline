import sys
from UnrealPipeline.core.Log import log
from Qt.QtWidgets import QApplication
import sys

def reloadModule(name="UnrealPipeline",*args):
    for mod in sys.modules.copy():
        if mod.startswith(name):
            log("delete model:{0}".format(mod))
            del sys.modules[mod]


def InstallMenu():
    app = QApplication(sys.argv)

    import unreal
    menus = unreal.ToolMenus.get()
    toolbar = menus.find_menu("LevelEditor.MainMenu")

    from UnrealPipeline.pipeline import InstallMenu
    InstallMenu(toolbar)

    from UnrealPipeline.Tools import InstallMenu
    InstallMenu(toolbar)


    from UnrealPipeline.Import import InstallMenu
    InstallMenu(toolbar)



    from UnrealPipeline.Export import InstallMenu
    InstallMenu(toolbar)

    
    from UnrealPipeline.info import InstallMenu
    InstallMenu(toolbar)

    menus.refresh_all_widgets()
    

