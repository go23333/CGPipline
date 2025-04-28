import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("groomimport","groom导入工具",toolTip="",command="from UnrealPipeline.Import.GroomImporter.GroomImporter import Start;Start()")
    rootMenu.add_menu_entry("",entry)