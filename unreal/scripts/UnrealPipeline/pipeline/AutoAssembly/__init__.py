import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("AutoAssembly","自动化组装",toolTip="",command="from UnrealPipeline.pipeline.AutoAssembly.AutoAssembly import start;start()")
    rootMenu.add_menu_entry("",entry)
