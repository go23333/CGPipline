import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("groomimport574","groom导入工具V2",toolTip="",command="from UnrealPipeline.Import.GroomImporter574.GroomImporter574 import start;start()")
    rootMenu.add_menu_entry("",entry)