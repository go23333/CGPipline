import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("ClothAbcImport","布料解算导入工具V1",toolTip="",command="from UnrealPipeline.Import.ClothAbcImporter.ClothAbcImport import start;start()")
    rootMenu.add_menu_entry("",entry)