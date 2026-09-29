import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("groomimport","groom导入工具V1",toolTip="",command="from UnrealPipeline.Import.GroomImporter.GroomImporter import start;start()")
    rootMenu.add_menu_entry("",entry)