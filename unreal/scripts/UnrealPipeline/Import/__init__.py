import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","ImportTools","导入工具")


    from UnrealPipeline.Import.CameraImporter import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.StaticMeshImporter import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.AnimImporter import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.ScenesFolder import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.ShadeCreate import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.GroomImporter import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.GroomImporter574 import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.ClothAbcImporter import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.ClothAbcImporter574 import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.SemiClothAbcImporter import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Import.SkMeshImporter import InstallMenu
    InstallMenu(submenu)
    


