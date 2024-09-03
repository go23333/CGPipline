import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("levelinfo","关卡信息工具",toolTip="",command="from UnrealPipeline.info.LevelInfo.LevelInfo import Start;Start()")
    rootMenu.add_menu_entry("",entry)