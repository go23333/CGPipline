import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    rootMenu.add_section("LightTools","灯光工具")
    entry = MakeEntry("LightTool","灯光常用工具",toolTip="",command="from UnrealPipeline.Tools.LightTools.LightTools import Start;Start()")
    rootMenu.add_menu_entry("LightTools",entry)
