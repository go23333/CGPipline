import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","UsefulTools","实用工具")

    from UnrealPipeline.Tools.LightTools import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Tools.LevelDesignTool import InstallMenu
    InstallMenu(submenu)