import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("QunJiSequenceExport","导出关卡序列群集",toolTip="",command="from UnrealPipeline.Export.QunJiSequenceExport.QunJiSequenceExport import start;start()")
    rootMenu.add_menu_entry("",entry)