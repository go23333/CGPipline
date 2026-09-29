import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("ChuShiHua","旧版项目初始化工具",toolTip="",command="from UnrealPipeline.pipeline.ChuShiHua.ChuShiHua import start;start()")
    rootMenu.add_menu_entry("",entry)
