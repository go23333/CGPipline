import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("SemiClothAbcImport","半流程布料解算导入工具",toolTip="",command="from UnrealPipeline.Import.SemiClothAbcImporter.SemiClothAbcImport import start;start()")
    rootMenu.add_menu_entry("",entry)