import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("animationimport","动画序列导入工具",toolTip="",command="from UnrealPipeline.Import.AnimImporter.AnimImporter import start;start()")
    rootMenu.add_menu_entry("",entry)
