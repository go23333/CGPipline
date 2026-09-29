import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("PreviewCreate","Preview序列创建工具",toolTip="",command="from UnrealPipeline.pipeline.PreviewCreate.PreviewCreate import start;start()")
    rootMenu.add_menu_entry("",entry)
