import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("AAI_import","手动组装关卡资产工具(AAI)",toolTip="",command="from UnrealPipeline.pipeline.AAI_import.AAI_import import start;start()")
    rootMenu.add_menu_entry("",entry)
