


import sys
from UnrealPipeline.core.Log import log
from Qt.QtWidgets import QApplication
import sys
import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


#===================细分插件===================
MY_UNIQUE_OWNER = "MySubdivisionPlugin_Owner"
MY_UNIQUE_ENTRY_NAME = "MySubdivisionPlugin_SubdivideButton"

def open_smooth_plugin():
    path1 = "/Game/Assets/Common/BP/Smooth/Smooth_Plugin"
    path2 = "/Game/AAI/Reference/BP/Smooth/Smooth_Plugin"

    if unreal.EditorAssetLibrary.does_asset_exist(path1):
        asset_path = path1
    elif unreal.EditorAssetLibrary.does_asset_exist(path2):
        asset_path = path2
    else:
        unreal.log_error(f"未找到资源:\n{path1}\n{path2}")
        return

    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    eus = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)
    bp = eus.find_utility_widget_from_blueprint(asset)
    if bp is None:
        bp = eus.spawn_and_register_tab(asset)

unreal.open_smooth_plugin = open_smooth_plugin

def register_smooth_toolbar(menus_handle):
    menus_handle.unregister_owner_by_name(MY_UNIQUE_OWNER)
    entry = unreal.ToolMenuEntry(
        name=MY_UNIQUE_ENTRY_NAME,
        type=unreal.MultiBlockType.TOOL_BAR_BUTTON
    )
    entry.set_label("细分插件")
    entry.set_tool_tip("打开细分插件工具")
    entry.set_icon("EditorStyle", "TextureEditor.RedChannel")
    entry.set_string_command(
        unreal.ToolMenuStringCommandType.PYTHON,
        "",
        "import unreal; unreal.open_smooth_plugin()"
    )
    toolbar = menus_handle.extend_menu("LevelEditor.LevelEditorToolBar.User")
    toolbar.add_menu_entry("Asset", entry)
#===================细分插件===================

def reloadModule(name="UnrealPipeline",*args):
    for mod in sys.modules.copy():
        if mod.startswith(name):
            #log("delete model:{0}".format(mod))
            del sys.modules[mod]


def add_context_menu(menu,context_name,context_name_ch,toolTip,command,category):
    menus = unreal.ToolMenus.get()
    # AssetContextMenu = menus.find_menu(menu)  #扩展菜单
    AssetContextMenu = menus.extend_menu(menu)  #扩展菜单
    print(AssetContextMenu)
    entry = MakeEntry(context_name,context_name_ch,toolTip=toolTip,command=command)
    AssetContextMenu.add_menu_entry(category,entry)

def InstallMenu():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    menus = unreal.ToolMenus.get()
    toolbar = menus.find_menu("LevelEditor.MainMenu")

    from UnrealPipeline.pipeline import InstallMenu
    InstallMenu(toolbar)

    from UnrealPipeline.Tools import InstallMenu
    InstallMenu(toolbar)


    from UnrealPipeline.Import import InstallMenu
    InstallMenu(toolbar)



    from UnrealPipeline.Export import InstallMenu
    InstallMenu(toolbar)

    
    from UnrealPipeline.info import InstallMenu
    InstallMenu(toolbar)


    #开放网路套接字
    from UnrealPipeline.core.socketHelper import StartSocketServer
    StartSocketServer()
    
    #添加一些右键菜单
    #添加资产到库中
    
    add_context_menu(
        "ContentBrowser.AssetContextMenu",
        "importAssetsToLibrary",
        "将资产添加到库中",
        "将选中的资产添加到库中,目前只支持单资产选择",
        "from UnrealPipeline.Library.ExportToAssetLibrary.ExportToAssetLibrary import Start;Start()",
        "CommonAssetActions")
    
    #整理资产
    add_context_menu(
        "ContentBrowser.AssetContextMenu",
        "ArragementAsset",
        "整理资产",
        "整理选中资产,目前只支持单资产选择",
        "from UnrealPipeline.Library.asset_arrangement.gui import show;show();",
        "CommonAssetActions")
    
    #设置毛发插值类型
    add_context_menu(
        "ContentBrowser.AssetContextMenu.GroomAsset",
        "SetAssetInterpolationLodType",
        "设置毛发资产插值类型及lod",
        "设置毛发资产插值类型为距离,lod为手动",
        "from UnrealPipeline.core.UnrealHelper import set_hair_interpolation_type_to_distance;set_hair_interpolation_type_to_distance()",
        "CommonAssetActions")
    #设置毛发插值
    add_context_menu(
        "ContentBrowser.AssetContextMenu.GroomAsset",
        "SetAssetInterpolationType",
        "设置毛发资产插值类型",
        "设置毛发资产插值类型为距离",
        "from UnrealPipeline.core.UnrealHelper import set_hair_interpolation_type_to_distance;set_hair_interpolation_type_to_distance(interpolation_switch=True,lod_switch=False)",
        "CommonAssetActions")
    #设置毛发lod
    add_context_menu(
        "ContentBrowser.AssetContextMenu.GroomAsset",
        "SetAssetLodType",
        "设置毛发资产lod",
        "设置毛发资产lod为手动",
        "from UnrealPipeline.core.UnrealHelper import set_hair_interpolation_type_to_distance;set_hair_interpolation_type_to_distance(interpolation_switch=False,lod_switch=True)",
        "CommonAssetActions")

    
    # #整理特效
    add_context_menu(
        "ContentBrowser.AssetContextMenu",
        "ArrangeEffectLibraryScene",
        "整理特效(NT)",
        "将选中的资产整理到本文件夹",
        "from UnrealPipeline.effectLibrary.asset_arrangement.gui import move_effect;move_effect()",
        "CommonAssetActions")


    #上传到特效库
    add_context_menu(
        "ContentBrowser.AssetContextMenu",
        "UploadToEffectLibrary",
        "上传特效库(NT)",
        "将选中的资产上传到特效库",
        "from UnrealPipeline.effectLibrary.asset_arrangement.gui import show;show()",
        "CommonAssetActions")

    # #整理场景
    # add_context_menu(
    #     "ContentBrowser.AssetContextMenu",
    #     "ArrangeEffectLibraryScene",
    #     "整理场景(测试按钮)",
    #     "将选中的资产整理到场景目录",
    #     "from UnrealPipeline.effectLibrary.asset_arrangement.gui import move_scene;move_scene()",
    #     "CommonAssetActions")
    # #整理场景
    # add_context_menu(
    #     "ContentBrowser.AssetContextMenu",
    #     "ArrangeEffectLibraryScene",
    #     "整理场景(测试按钮)",
    #     "将选中的资产整理到场景目录",
    #     "from UnrealPipeline.effectLibrary.asset_arrangement.gui import move_scene;move_scene()",
    #     "CommonAssetActions")

    register_smooth_toolbar(menus)

    menus.refresh_all_widgets()

if __name__ == "__main__":
    InstallMenu()

