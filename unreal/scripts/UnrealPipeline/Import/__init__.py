import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","ImportTools","导入工具")


    from UnrealPipeline.Import.CameraImporter import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.StaticMeshImporter import InstallMenu
    InstallMenu(submenu)



    entry = MakeEntry("model_import","地编模型导入",toolTip="",command="from UnrealPipeline.songshunjie import ScenesFolder;ScenesFolder.start()")
    submenu.add_menu_entry("",entry)

    entry = MakeEntry("material_model_import","角色材质模型导入",toolTip="",command="from UnrealPipeline.songshunjie import ShadeCreate;ShadeCreate.start()")
    submenu.add_menu_entry("",entry)
