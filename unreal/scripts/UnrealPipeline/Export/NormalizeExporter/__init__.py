import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("normalize_export","规范化导出工具",toolTip="",command="from UnrealPipeline.Export.NormalizeExporter.NormalizeExporter import Start;Start()")
    rootMenu.add_menu_entry("",entry)