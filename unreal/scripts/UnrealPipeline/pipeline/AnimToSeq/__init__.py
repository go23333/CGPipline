import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("AnimToSequnce","动画导入动画关卡序列工具",toolTip="",command="from UnrealPipeline.pipeline.AnimToSeq.AnimToSeq import start;start()")
    rootMenu.add_menu_entry("",entry)
