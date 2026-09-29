import unreal



def InstallMenu(rootMenu:unreal.ToolMenu):
    from UnrealPipeline.core.UnrealHelper import MakeEntry
    entry = MakeEntry("FbxDetection","检测动画fbx与Excel完整性工具",toolTip="",command="from UnrealPipeline.pipeline.FbxDetection.FbxDetection import start;start()")
    rootMenu.add_menu_entry("",entry)
