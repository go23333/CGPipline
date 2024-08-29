import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    rootMenu.add_section("EditTools","地编工具")
    entry = MakeEntry("EditTool","地编常用工具",toolTip="",command="from UnrealPipeline.Tools.LevelDesignTool.LevelDesignTool import Start;Start()")
    rootMenu.add_menu_entry("EditTools",entry)
