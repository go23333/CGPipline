import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("AutoAssemblyV2","自动化组装V2",toolTip="",command="from UnrealPipeline.pipeline.AutoAssemblyV2.AutoAssemblyV2 import start;start()")
    rootMenu.add_menu_entry("",entry)
