import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","info","统计信息")


    from UnrealPipeline.info.LevelInfo import InstallMenu
    InstallMenu(submenu)
    




