import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","pipelinetool","流程工具")



    entry = MakeEntry("AAI","整合关卡(AAI)",toolTip="",command="from UnrealPipeline.songshunjie import AAI_import;AAI_import.start()")
    submenu.add_menu_entry("",entry)

    entry = MakeEntry("initProject","项目初始化工具",toolTip="",command="from UnrealPipeline.songshunjie import ChuShiHua;ChuShiHua.start()")
    submenu.add_menu_entry("",entry)

