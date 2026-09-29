import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("GroomToBP","角色蓝图Groom组件添加工具",toolTip="",command="from UnrealPipeline.pipeline.GroomToBP.GroomToBP import start;start()")
    rootMenu.add_menu_entry("",entry)
