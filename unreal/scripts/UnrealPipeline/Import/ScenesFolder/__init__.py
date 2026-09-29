import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("ScenesFolder","道具模型导入",toolTip="",command="from UnrealPipeline.Import.ScenesFolder.ScenesFolder import start;start()")
    rootMenu.add_menu_entry("",entry)
