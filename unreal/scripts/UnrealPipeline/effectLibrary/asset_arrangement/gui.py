import unreal
import os, shutil
import importlib
import UnrealPipeline.effectLibrary.asset_arrangement.effect_capture as effect_capture
from Qt.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
NIAGARA_RENDERER_REGISTRY_TAGS = (
    "ComponentRenderer",
    "DecalRenderer",
    "GeometryCacheRenderer",
    "LightRenderer",
    "MeshRenderer",
    "RibbonRenderer",
    "SpriteRenderer",
    "VolumeRenderer",
)
SPARSE_VOLUME_TEXTURE_CLASS_NAMES = (
    "SparseVolumeTexture",
    "SparseVolumeTextureFrame",
    "AnimatedSparseVolumeTexture",
)
MOVE_EFFECT_LIBRARY_ROOT = "/Game/VFX/effectsLibrary"
MOVE_EFFECT_CLASS_FOLDER_MAP = {
    "Material": "Material",
    "MaterialInstance": "MI",
    "MaterialInstanceConstant": "MI",
    "MaterialFunction": "MF",
    "MaterialFunctionInstance": "MF",
    "Texture": "Texture",
    "Texture2D": "Texture",
    "TextureCube": "Texture",
    "StaticMesh": "Mesh",
    "SkeletalMesh": "SkeletalMesh",
    "GeometryCache": "GeometryCache",
    "NiagaraSystem": "NS",
    "NiagaraEmitter": "NE",
    "ParticleSystem": "Particle",
    "Blueprint": "BP",
    "BlueprintGeneratedClass": "BP",
    "LevelSequence": "Sequence",
    "World": "Level",
}


class AssetArrangement:

    # 获取引擎版本（仅主版本号，如 5.7.4）
    def _get_engine_version(self):
        full_version = unreal.SystemLibrary.get_engine_version()
        # 取第一个 - 之前的部分
        return full_version.split("-")[0]

    # 生成当前时间戳（毫秒）
    def _get_timestamp(self):
        import time

        return int(time.time() * 1000)

    def _to_abs_file_path(self, file_path: str) -> str:
        return os.path.abspath(os.path.normpath(file_path)).replace("\\", "/")

    def _collect_renderer_tags(self, package_path: str) -> list:
        """从 Asset Registry Tags 中提取 Niagara Renderer 类型。"""
        asset_tag = unreal.EditorAssetLibrary.get_tag_values(package_path)
        tags_dict = {str(k): v for k, v in asset_tag.items()}
        found = []
        for name in NIAGARA_RENDERER_REGISTRY_TAGS:
            value = tags_dict.get(name)
            if value and str(value) not in ("0", "False", "None", "false"):
                found.append(name)
        return found

    def clear_all_in_dir(self, target_dir):
        if not target_dir or not os.path.isdir(target_dir):
            return
        for name in os.listdir(target_dir):
            full_path = os.path.join(target_dir, name)
            try:
                if os.path.isfile(full_path) or os.path.islink(full_path):
                    os.unlink(full_path)
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                print(f"清理完成: {full_path}")
            except Exception as e:
                print(f"清理失败 {full_path}: {e}")

    def __move_Effect(self):
        selected_assets = [
            asset
            for asset in unreal.EditorUtilityLibrary.get_selected_assets()
            if asset is not None
        ]

        if not selected_assets:
            QMessageBox.warning(None, "提示", "请先在内容浏览器中选择要整理的资产")
            return

        target_folder, confirmed = QInputDialog.getText(
            None,
            "整理资产",
            "请输入目标内容路径（例如：/Game/VFX/effectsLibrary/VFX_DT）：",
            text="/Game/VFX/effectsLibrary/VFX_DT",
        )
        if not confirmed:
            return

        target_folder = target_folder.strip().rstrip("/")
        if not target_folder:
            QMessageBox.warning(None, "提示", "目标路径不能为空")
            return
        if not target_folder.startswith("/Game/"):
            QMessageBox.warning(None, "提示", "目标路径必须以 /Game/ 开头")
            return

        for asset in selected_assets:
            level_package_name = asset.get_outermost().get_name()
            print(f"整理资产: {level_package_name} -> {target_folder}")
            unreal.BrowserBridge.sort_asset_to_folder(
                level_package_name,
                target_folder,
            )
        QMessageBox.information(
            None,
            "提示",
            "整理完成",
        )

    def __move_Sence(self):
        
        
       copytext =  unreal.BrowserBridge.copy_selected_actors_and_get_text()
       print(f"copytext: {copytext}")
       return

#         actor_text = r'''Begin Map
#    Begin Level
#       Begin Actor Class=/Script/Engine.Actor Name=Actor_2 Archetype="/Script/Engine.Actor'/Script/Engine.Default__Actor'" ExportPath="/Script/Engine.Actor'/Game/Shots/EP001/sc004/Ep001_sc004_076/NewWorld.NewWorld:PersistentLevel.Actor_2'"
#          Begin Object Class=/Script/Engine.SceneComponent Name="DefaultSceneRoot" ExportPath="/Script/Engine.SceneComponent'/Game/Shots/EP001/sc004/Ep001_sc004_076/NewWorld.NewWorld:PersistentLevel.Actor_2.DefaultSceneRoot'"
#          End Object
#          Begin Object Name="DefaultSceneRoot" ExportPath="/Script/Engine.SceneComponent'/Game/Shots/EP001/sc004/Ep001_sc004_076/NewWorld.NewWorld:PersistentLevel.Actor_2.DefaultSceneRoot'"
#             RelativeLocation=(X=2112.000000,Y=-344.000000,Z=190.000000)
#             RelativeRotation=(Pitch=107.000000,Yaw=69.000000,Roll=130.000000)
#             RelativeScale3D=(X=1.000000,Y=0.585000,Z=1.000000)
#             bVisualizeComponent=True
#             CreationMethod=Instance
#          End Object
#          RootComponent="/Script/Engine.SceneComponent'DefaultSceneRoot'"
#          ActorLabel="Actor2"
#          InstanceComponents(0)="/Script/Engine.SceneComponent'DefaultSceneRoot'"
#          InstanceComponents(1)="/Script/Engine.SceneComponent'DefaultSceneRoot'"
#       End Actor
#    End Level
# Begin Surface
# End Surface
# End Map

#         '''

#         unreal.BrowserBridge.paste_actor_from_text(
#             actor_text
#         )

        # selected_assets = [
        #     asset
        #     for asset in unreal.EditorUtilityLibrary.get_selected_assets()
        #     if asset is not None
        # ]
        # for i, item in enumerate(selected_assets):
        #     asset_path_name = item.get_path_name()
        #     asset_name = asset_path_name[asset_path_name.rfind(".") + 1 :]

        #     asset_new_pathstr = f"/Game/Scenes/Maps/S01/{asset_name}/"
        #     unreal.BrowserBridge.copy_large_scene_asset_and_dependency_to_folder(
        #         item, asset_new_pathstr
        #     )
        #     print("[__move_Sence]整理完成")
        #     QMessageBox.information(None,"提示","场景整理完成")

    def __move_asset(self):

        #    export interface EffectSavePayload {
        # 	effectName: string; //特效名称
        # 	software: string; //软件列表
        # 	tags: string[]; //标签列表
        # 	aiDescription: string; //AI生成描述
        # 	updateLog: string;
        # 	projectFiles: ProjectFilesByCategory;
        # 	previewVideo: File | null;
        # 	thumbnail: File | null; 
        # 	category?: EffectSaveCategory;
        #   }

        #    asset = unreal.EditorUtilityLibrary.get_selected_assets()[0]
        movie_capture_dir = os.path.join(
            unreal.Paths.project_saved_dir(), "MovieRenders"
        )
        self.clear_all_in_dir(movie_capture_dir)

        # 需要整理的类型
        need_arrangement_types = ["NiagaraSystem", "ParticleSystem"]
        asset_list = []
        selected_assets = [
            asset
            for asset in unreal.EditorUtilityLibrary.get_selected_assets()
            if asset is not None
        ]
        print(f"复制中: {len(selected_assets)} 个资产")
        total = len(selected_assets)

        if total == 0:
            return

        with unreal.ScopedSlowTask(total, unreal.Text("复制资产中...")) as slow_task:
            slow_task.make_dialog(True)

            for i, item in enumerate(selected_assets):
                if slow_task.should_cancel():
                    return
                slow_task.enter_progress_frame(
                    1, unreal.Text(f"复制中: {item.get_name()}")
                )
                asset_path_name = item.get_path_name()
                asset_name = asset_path_name[asset_path_name.rfind(".") + 1 :]
                asset_class = item.get_class().get_name()
                package_name = item.get_outermost().get_name()
                package_path = (
                    package_name[: package_name.rfind("/")]
                    if "/" in package_name
                    else package_name
                )
                object_path = asset_path_name
                neweffectNamestr = f"{asset_name}_{self._get_timestamp()}"
                asset_new_pathstr = f"/Game/VFX/effectsLibrary/{neweffectNamestr}/"

                content_dir = unreal.Paths.project_content_dir()
                copied_files = []
                preview_video_path = ""
                software = ""
                renderer_tags = []
                if asset_class in need_arrangement_types:
                    renderer_tags = self._collect_renderer_tags(package_name)
                    print(f"renderer_tags: {renderer_tags}")
                    software = "UE" + self._get_engine_version()
                    print(f"asset_new_pathstr: {asset_new_pathstr}")
                    
                    unreal.BrowserBridge.copy_asset_and_dependency_to_folder(
                        item, asset_new_pathstr
                    )
                    local_dir = content_dir + asset_new_pathstr.replace("/Game/", "")
                    if os.path.isdir(local_dir):
                        for root, dirs, filenames in os.walk(local_dir):
                            for filename in filenames:
                                full_path = self._to_abs_file_path(
                                    os.path.join(root, filename)
                                )
                                copied_files.append(full_path)

                else:
                    software = "素材"
                    unreal.BrowserBridge.copy_asset_and_dependency_to_folder(
                        item, asset_new_pathstr
                    )
                    local_dir = content_dir + asset_new_pathstr.replace("/Game/", "")
                    if os.path.isdir(local_dir):
                        for root, dirs, filenames in os.walk(local_dir):
                            for filename in filenames:
                                full_path = self._to_abs_file_path(
                                    os.path.join(root, filename)
                                )
                                copied_files.append(full_path)

                asset_list.append(
                    {
                        "neweffectName": neweffectNamestr,
                        "effectName": asset_name,
                        "software": software,
                        "tags": [
                            "UE" + self._get_engine_version(),
                            asset_class,
                            *renderer_tags,
                        ],
                        "asset_class": asset_class,
                        "package_name": package_name,
                        "package_path": package_path,
                        "object_path": object_path,
                        "asset_new_path": asset_new_pathstr,
                        "thumbnail": "",
                        "files": copied_files,
                        "previewVideo": preview_video_path,
                    }
                )
        print(f"整理完成: {len(asset_list)} 个资产")
   
        # 特效类型走录制流程，其他类型直接上传
        first_asset = selected_assets[0]
        first_asset_class = first_asset.get_class().get_name()
        if first_asset_class in need_arrangement_types:
            # NiagaraSystem / ParticleSystem：录制预览视频后上传
            effect_capture.record_effect(
                effect_asset=first_asset, asset_list=asset_list
            )
        else:
            # 素材等非特效类型：跳过录制，直接调用 web 上传
            effect_capture.upload_effect(asset_list)


def show():
    effect_capture.stop_all_callbacks()
    importlib.reload(effect_capture)
    w = AssetArrangement()
    w._AssetArrangement__move_asset()


def move_scene():
    w = AssetArrangement()
    w._AssetArrangement__move_Sence()
def move_effect():
    w = AssetArrangement()
    w._AssetArrangement__move_Effect()
