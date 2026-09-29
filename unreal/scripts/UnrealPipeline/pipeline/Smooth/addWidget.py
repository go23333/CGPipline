# Copyright Epic Games, Inc. All Rights Reserved.

import unreal

MY_UNIQUE_OWNER = "MySubdivisionPlugin_Owner"
MY_UNIQUE_ENTRY_NAME = "MySubdivisionPlugin_SubdivideButton"
tool_menus = unreal.ToolMenus.get()
owning_menu_name = "LevelEditor.LevelEditorToolBar.User"#插件地址


# 1. 直接定义一个绑定到 unreal 命名空间下的函数，防止 __main__ 找不到
def open_smooth_plugin():
    asset_path = "/Game/Assets/Common/BP/Smooth/Smooth_Plugin"
    if not unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        unreal.log_error(f"找不到资源: {asset_path}")
        return

    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    eus = unreal.get_editor_subsystem(unreal.EditorUtilitySubsystem)

    bp = eus.find_utility_widget_from_blueprint(asset)

    if bp is None:
        bp = eus.spawn_and_register_tab(asset)


# 将函数临时挂载到 unreal 模块上，确保在任何上下文（包括 __main__）中都能被 100% 访问到
unreal.open_smooth_plugin = open_smooth_plugin


def Run():
    # 2. 清理旧的 Owner，防止重复运行冲突
    tool_menus.unregister_owner_by_name(MY_UNIQUE_OWNER)

    # 3. 创建纯数据结构的 ToolMenuEntry
    entry = unreal.ToolMenuEntry(
        name=MY_UNIQUE_ENTRY_NAME,
        type=unreal.MultiBlockType.TOOL_BAR_BUTTON
    )

    entry.set_label("细分插件")
    entry.set_tool_tip("打开细分插件工具")

    # 使用通用的设置图标（这里用红色的材质图标方便在工具栏辨认）
    entry.set_icon("EditorStyle", "TextureEditor.RedChannel")#更改图标，仅限调用ue的图集

    # 4. 【核心修改】通过 unreal 模块直接调用，绕过 __main__ 的限制
    entry.set_string_command(
        unreal.ToolMenuStringCommandType.PYTHON,
        "",
        "import unreal; unreal.open_smooth_plugin()"
    )

    # 5. 延伸菜单并添加
    toolbar = tool_menus.extend_menu(owning_menu_name)
    toolbar.add_menu_entry("Asset", entry)

    # 6. 刷新界面
    tool_menus.refresh_all_widgets()
    #print("【成功】细分插件按钮已注册且绑定！")


Run()