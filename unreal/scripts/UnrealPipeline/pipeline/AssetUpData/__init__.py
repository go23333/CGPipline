import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("AssetUpData","资产批量更新工具",toolTip="",command="from UnrealPipeline.pipeline.AssetUpData.AssetUpData import start;start()")
    rootMenu.add_menu_entry("",entry)
