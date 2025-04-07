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


    from UnrealPipeline.core.socketHelper import StartSocketServer
    StartSocketServer()
    
    #添加一些右键菜单
    texContextMenu = menus.find_menu("ContentBrowser.AssetContextMenu.StaticMesh")
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("importAssetsToLibrary","将资产添加到库中",toolTip="将选中的资产添加到库中,目前只支持单资产选择",command="from UnrealPipeline.Library.ExportToAssetLibrary.ExportToAssetLibrary import Start;Start()")
    texContextMenu.add_menu_entry("CommonAssetActions",entry)


    menus.refresh_all_widgets()

if __name__ == "__main__":
    pass


