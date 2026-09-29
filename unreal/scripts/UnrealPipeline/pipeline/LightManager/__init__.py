import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("LightManager","灯光管理工具",toolTip="",command="from UnrealPipeline.pipeline.LightManager.LightManager import start;start()")
    rootMenu.add_menu_entry("",entry)
