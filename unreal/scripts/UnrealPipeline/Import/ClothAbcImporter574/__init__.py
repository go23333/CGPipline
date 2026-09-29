import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("ClothAbcImport574","布料解算导入工具V2",toolTip="",command="from UnrealPipeline.Import.ClothAbcImporter574.ClothAbcImport574 import start;start()")
    rootMenu.add_menu_entry("",entry)