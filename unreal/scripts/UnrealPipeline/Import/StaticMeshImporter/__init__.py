import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("staticmeshimport","静态网格体导入工具",toolTip="",command="from UnrealPipeline.Import.StaticMeshImporter.staticmesh_importer import Start;Start()")
    rootMenu.add_menu_entry("",entry)
