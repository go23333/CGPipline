import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","ExportTools","导出工具")


    from UnrealPipeline.Export.NormalizeExporter import InstallMenu
    InstallMenu(submenu)
    

    
    entry = MakeEntry("group_export","导出关卡序列群集",toolTip="",command="from UnrealPipeline.songshunjie import QunJiSequenceExport;QunJiSequenceExport.start()")
    submenu.add_menu_entry("",entry)





    