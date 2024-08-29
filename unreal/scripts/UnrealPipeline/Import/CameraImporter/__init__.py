import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("cameraimport","相机导入工具",toolTip="",command="from UnrealPipeline.Import.CameraImporter.camera_importer import Start;Start()")
    rootMenu.add_menu_entry("",entry)