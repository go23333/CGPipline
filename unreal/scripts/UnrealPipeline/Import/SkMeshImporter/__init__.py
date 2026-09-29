import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("SkMeshImport","骨骼网格体导入工具",toolTip="",command="from UnrealPipeline.Import.SkMeshImporter.SkMeshImport import start;start()")
    rootMenu.add_menu_entry("",entry)
