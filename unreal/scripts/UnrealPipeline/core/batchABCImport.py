
import UnrealPipeline.core.uSTools as ut
import json
import unreal

def BatchAbcImport(root_path:str):
    error_cloth,error_mat_cloth,successful_cloth = ut.clothImportMount(root_path)
    error_groom,successful_groom = ut.CacheImportTool.groomMount(root_path,0)
    result = dict(
        cloth = dict(
            error = error_cloth,
            mat_error = error_mat_cloth,
            successful = successful_cloth
        ),
        groom = dict(
            error = error_groom,
            successful = successful_groom
        )
    )

    over_file_path = "D:\over.file"
    with open(over_file_path,"w+",encoding="utf-8") as file:
        file.write(json.dumps(result))
    unreal.SystemLibrary.quit_editor()
    
    
    
    
