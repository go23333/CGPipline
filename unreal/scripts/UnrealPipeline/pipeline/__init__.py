import unreal
from UnrealPipeline.core.UnrealHelper import MakeEntry


def InstallMenu(rootMenu:unreal.ToolMenu):
    submenu = rootMenu.add_sub_menu(rootMenu.get_name(),"","pipelinetool","流程工具")

    from UnrealPipeline.pipeline.AnimToSeq import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.AAI_import import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.ChuShiHua import InstallMenu
    InstallMenu(submenu)
    from UnrealPipeline.pipeline.ChuShiHua57 import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.GroomToBP import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.AAI_Automation import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.FbxDetection import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.ChShaderChange import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.AutoAssembly import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.AssetUpData import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.PreviewCreate import InstallMenu
    InstallMenu(submenu)

    from UnrealPipeline.pipeline.SeqBindToSpawnable import InstallMenu
    InstallMenu(submenu)






