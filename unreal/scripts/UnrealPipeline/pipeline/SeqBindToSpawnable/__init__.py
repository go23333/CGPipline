import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("SeqBindToSpawnable","镜头actor转为spawnable",toolTip="",command="from UnrealPipeline.pipeline.SeqBindToSpawnable.SeqBindToSpawnable import start;start()")
    rootMenu.add_menu_entry("",entry)
