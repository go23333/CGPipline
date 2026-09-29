import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("LightMatrixAppend","灯光矩阵添加工具",toolTip="",command="from UnrealPipeline.pipeline.LightMatrixAppend.LightMatrixAppend import start;start()")
    rootMenu.add_menu_entry("",entry)
