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
    from UnrealPipeline.core.socketHelper import ThreadSocket
    ThreadSocket.StartListening()

    #添加一些右键菜单
    texContextMenu = menus.find_menu("ContentBrowser.AssetContextMenu.Texture2D")
    from UnrealPipeline.core.UnrealHelper import MakeEntry

    entry = MakeEntry("addWaterMark","添加大模型标签",toolTip="",command="from UnrealPipeline.core.UnrealHelper import addWaterMarkToSelectedTextures;addWaterMarkToSelectedTextures()")
    texContextMenu.add_menu_entry("",entry)
    

