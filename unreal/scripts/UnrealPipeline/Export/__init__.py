import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","ExportTools","导出工具")


    from UnrealPipeline.Export.NormalizeExporter import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.Export.QunJiSequenceExport import InstallMenu
    InstallMenu(submenu)
    

    






    