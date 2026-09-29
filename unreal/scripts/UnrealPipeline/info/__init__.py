import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","info","统计信息")


    from UnrealPipeline.info.LevelInfo import InstallMenu
    InstallMenu(submenu)

    #查找开启了漫反射增强的关卡
    entry = MakeEntry("find_level_with_diffuse_boost","查找开启了漫反射增强的关卡",toolTip="",command="from UnrealPipeline.core.UnrealHelper import find_all_level_has_diffuse_boost;find_all_level_has_diffuse_boost()")
    submenu.add_menu_entry("",entry)
    




