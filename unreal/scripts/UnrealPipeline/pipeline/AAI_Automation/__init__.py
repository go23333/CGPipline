import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("AAI_Automation","自动组装关卡资产工具",toolTip="",command="from UnrealPipeline.pipeline.AAI_Automation.AAI_Automation import start;start()")
    rootMenu.add_menu_entry("",entry)
