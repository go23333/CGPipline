import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("ShadeCreate","角色材质模型导入",toolTip="",command="from UnrealPipeline.Import.ShadeCreate.ShadeCreate import start;start()")
    rootMenu.add_menu_entry("",entry)
