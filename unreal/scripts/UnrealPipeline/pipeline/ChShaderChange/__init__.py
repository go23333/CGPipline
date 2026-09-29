import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("ChShaderChange","批量材质切换插件",toolTip="",command="from UnrealPipeline.pipeline.ChShaderChange.ChShaderChange import start;start()")
    rootMenu.add_menu_entry("",entry)