#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
import time
import unreal
import os
from enum import Enum,auto
import json
from functools import partial
import UnrealPipeline.core.glbHelper as g
import shutil
from UnrealPipeline.core.Config import globalConfig
import UnrealPipeline.core.utilis as UT

from PIL import Image

#获取一些subsystem
editorActorSubsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
staticMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assetEditorSubsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
levelEditorSybsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levelSequenceEditorSubsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
unrealEditorSybsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
unrealAssetsSubsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)




# 定义一些包裹类
class WrapBaseAsset():
    def __init__(self,asset) -> None:
        self.asset = asset
    def saveAsset(self,onlyIfIsDirty = True):
        unreal.EditorAssetLibrary.save_loaded_asset(self.asset,onlyIfIsDirty)
    def get_asset_name(self)-> str:
        return self.asset.get_name()


class WarpLevelSequence(WrapBaseAsset):
    def __init__(self,asset:unreal.LevelSequence) -> None:
        super().__init__(asset)
        self.asset:unreal.LevelSequence
    def setFrameRate(self,frameRate):
        frameRate = unreal.FrameRate(frameRate,1)
        self.asset.set_display_rate(frameRate)
    def setPlayBackStart(self,value:int):
        self.asset.set_playback_start(value)
    def setPlayBackEnd(self,value:int):
        self.asset.set_playback_end(value)
    def importCamera(self,fbxPath:str,UniforScale:int):
        LSBL = unreal.LevelSequenceEditorBlueprintLibrary()
        LSBL.open_level_sequence(self.asset)
        tools = unreal.SequencerTools() 
        originProxyAndCamera = self.getBindingProxyAndObject(unreal.CineCameraActor)
        if originProxyAndCamera:
            bindingProxy = originProxyAndCamera[0]
        else:
            bindingProxy,_=levelSequenceEditorSubsystem.create_camera(True)

        importSettings = unreal.MovieSceneUserImportFBXSettings()
        importSettings.set_editor_property("convert_scene_unit",True)
        importSettings.set_editor_property("create_cameras",False)
        importSettings.set_editor_property("force_front_x_axis",False)
        importSettings.set_editor_property("match_by_name_only",False)
        importSettings.set_editor_property("import_uniform_scale",UniforScale)
        importSettings.set_editor_property("reduce_keys",False)
        importSettings.set_editor_property("replace_transform_track",True)
        
        world = unrealEditorSybsystem.get_editor_world()
        if world == None:
            unrealLogError("导入摄像机","获取当前世界失败")
            return False
        tools.import_level_sequence_fbx(world,self.asset,[bindingProxy],importSettings,fbxPath)
        LSBL.close_level_sequence()
    def setLock(self,Lock:bool):
        LSBL = unreal.LevelSequenceEditorBlueprintLibrary()
        LSBL.open_level_sequence(self.asset)
        LSBL.set_lock_level_sequence(Lock)
        LSBL.close_level_sequence()
        unrealLog("锁定/解锁关卡序列",f"序列{self.asset.get_name()}的锁定状态设置为{Lock}")
    def getBindingProxyAndObject(self,objectType):
        '''
        获取绑定在关卡序列上的首个objectType类型的BindingProxys和对象
        '''
        bindingProxys  = self.asset.get_bindings()
        for bindingProxy in bindingProxys:
            obj = bindingProxy.get_object_template()
            if type(obj) == objectType:
                return(bindingProxy,obj)
        return False
    def SetCameraCutsStartEnd(self,startFrame:int,endFrame:int):
        cameraCut = self.asset.find_tracks_by_type(unreal.MovieSceneCameraCutTrack)[0]
        cameraCut:unreal.MovieSceneCameraCutTrack
        cameraCutSection = cameraCut.get_sections()[0]
        cameraCutSection:unreal.MovieSceneCameraCutSection
        cameraCutSection.set_start_frame(startFrame)
        cameraCutSection.set_end_frame(endFrame)
    @classmethod
    def create(cls,assetPath:str,override:bool=True):
        print(assetPath)
        if unreal.EditorAssetLibrary.does_asset_exist(assetPath) and override:
            unrealLogWarning("序列创建",f"序列{assetPath}已经存在需要删除")
            unreal.EditorAssetLibrary.delete_asset(assetPath)
            unrealLogWarning("序列创建",f"序列{assetPath}已经删除")
        elif unreal.EditorAssetLibrary.does_asset_exist(assetPath) and not override:
            return (WarpLevelSequence(unreal.EditorAssetLibrary.load_asset(assetPath)))
        return(WarpLevelSequence(createGerericAsset(assetPath,False,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())))

class WrapStaticMesh(WrapBaseAsset):
    def __init__(self,asset:unreal.StaticMesh) -> None:
        super().__init__(asset)
        self.asset:unreal.StaticMesh
    def getCurrentBuildSettings(self):
        return staticMeshEditorSubsystem.get_lod_build_settings(self.asset,0)
    def setCurrentBuildSettings(self,buildSettings):
        staticMeshEditorSubsystem.set_lod_build_settings(self.asset,0,buildSettings)
    def useFullPercisionUV(self):
        buildSettings = self.getCurrentBuildSettings()
        buildSettings.use_full_precision_u_vs = True
        self.setCurrentBuildSettings(buildSettings)
    def setMaterialBySloatName(self,sloatName:str,Material:unreal.MaterialInterface):
        index = self.asset.get_material_index(sloatName)
        self.asset.set_material(index,Material)
    def setMaterialByIndex(self,index:int,Material:unreal.MaterialInterface):
        self.asset.set_material(index,Material)
    def get_vertices_count(self):
        return(staticMeshEditorSubsystem.get_number_verts(self.asset,0))
    @classmethod
    def importFromFbx(cls,sourcePath:str,destinationPath,scale:int):
        # 构建导入选项
        options = unreal.FbxImportUI()
        options.import_mesh = True
        options.import_textures = False
        options.import_materials = False
        options.import_as_skeletal=False
        options.static_mesh_import_data.import_translation = unreal.Vector(0.0,0.0,0.0)
        options.static_mesh_import_data.import_rotation = unreal.Rotator(0.0,0.0,0.0)
        options.static_mesh_import_data.import_uniform_scale = scale
        options.static_mesh_import_data.combine_meshes = True
        options.static_mesh_import_data.generate_lightmap_u_vs = False
        options.static_mesh_import_data.auto_generate_collision  = True
        # 构建导入任务
        task = buildImportTask(sourcePath,destinationPath,options)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        return(WrapStaticMesh(task.get_objects()[0]))

class WrapTexture(WrapBaseAsset):
    def __init__(self,asset:unreal.Texture) -> None:
        super().__init__(asset)
        self.asset:unreal.Texture
    def setVTEnable(self,enable:bool):
        self.asset.set_editor_property("virtual_texture_streaming",enable)
        return (self.asset.virtual_texture_streaming)
    def setAsColor(self):
        self.asset.compression_settings = unreal.TextureCompressionSettings.TC_DEFAULT
        self.asset.srgb = True
    def setAsLinerColor(self):
        self.asset.compression_settings = unreal.TextureCompressionSettings.TC_MASKS
        self.asset.srgb = False
        pass
    def setAsNormal(self):
        self.asset.compression_settings = unreal.TextureCompressionSettings.TC_NORMALMAP
        self.asset.srgb = False
    def ExportTexture(self,dir:str)->list[str]:
        return(ExportTextureNew(self.asset,dir))
    @classmethod
    def importTexture(cls,sourcePath:str,destinationPath:str):
        importData = unreal.AutomatedAssetImportData()
        importData.destination_path = destinationPath
        importData.filenames = [sourcePath]
        importData.replace_existing = True
        importData.factory = unreal.TextureFactory()
        try:
            return(WrapTexture(unreal.AssetToolsHelpers.get_asset_tools().import_assets_automated(importData)[0]))
        except IndexError:
            return False
    

class WrapMaterial(WrapBaseAsset):
    def __init__(self,asset:unreal.Material) -> None:
        super().__init__(asset)
        self.asset:unreal.Material

class WrapMaterialInstance(WrapBaseAsset):
    def __init__(self,asset:unreal.MaterialInstance) -> None:
        super().__init__(asset)
        self.asset:unreal.MaterialInstance
    def setScalarParameter(self,name:str,value:float):
        unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(self.asset,name,value)
    def setTextureParameter(self,name:str,value:unreal.Texture):
        unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(self.asset,name,value)
    def setVectorParameter(self,name:str,value:unreal.LinearColor):
        unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(self.asset,name,value)
    def setParent(self,parent:unreal.Material):
        unreal.MaterialEditingLibrary.set_material_instance_parent(self.asset,parent)
    @classmethod
    def create(cls,desPath:str):
        return WrapMaterialInstance(createGerericAsset(desPath,False,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew()))


class WrapActor():
    def __init__(self,actor:unreal.Actor):
        self.actor = actor
        self.component = self.actor.root_component
        self.component:unreal.SceneComponent
    def appendToFolder(self,folderPath:str):
        self.actor.set_folder_path(folderPath)
    def setMobility(self,mobility:unreal.ComponentMobility):
        self.component.set_mobility(mobility)
    def setLocation(self,location:unreal.Vector,sweep:bool = False,teleport:bool = False):
        self.actor.set_actor_location(location,sweep,teleport)
    def setRotation(self,rotation:unreal.Rotator,teleport:bool = False):
        self.actor.set_actor_rotation(rotation,teleport)
    def setScale(self,scale:unreal.Vector):
        self.actor.set_actor_scale3d(scale)
    def getLevel(self)->unreal.Level:
        return(self.actor.get_level())
    def destroyActor(self):
        self.actor.destroy_actor()
        unrealLog("删除Actor",f"Actor:{self.actor.get_name()}已经被删除")
    def setLabel(self,label:str):
        self.actor.set_actor_label(label)



class WrapCineCameraActor(WrapActor):
    def __init__(self,actor:unreal.CineCameraActor):
        super().__init__(actor)
        self.actor:unreal.CineCameraActor 
        self.component = self.actor.camera_component
        self.component:unreal.CineCameraComponent
    def setFilmback(self,preset:str):
        self.component.set_filmback_preset_by_name(preset)
    def setFocusMethod(self,method:unreal.CameraFocusMethod):
        self.component.focus_settings.focus_method = method
    def setAspectRatio(self,value:float):
        self.component.crop_settings.aspect_ratio = value
    @classmethod
    def spawn(cls,location:unreal.Vector,rotation:unreal.Rotator):
        return(WrapCineCameraActor(editorActorSubsystem.spawn_actor_from_class(unreal.CineCameraActor,location,rotation)))


class WrapCustomActor(WrapActor):
    def __init__(self,actor:unreal.Actor):
        super().__init__(actor)
        self.component:unreal.SceneComponent
        self.actor:unreal.Actor

class WrapDirectionLight(WrapActor):
    def __init__(self,actor:unreal.DirectionalLight) -> None:
        super().__init__(actor)
        self.actor:unreal.DirectionalLight
        self.component:unreal.DirectionalLightComponent
    def setAtmosphereSunLight(self,isAtmosphereSunLight:bool):
        self.component.set_atmosphere_sun_light(isAtmosphereSunLight)

    
class WrapSkyLight(WrapActor):
    def __init__(self,actor:unreal.SkyLightComponent) -> None:
        super().__init__(actor)
        self.actor:unreal.SkyLight
        self.component:unreal.SkyLightComponent
    def setRealTimeCapture(self,isRealTimeCapture:bool):
        self.component.set_editor_property("real_time_capture",isRealTimeCapture)


class WrapSkyAtmophere(WrapActor):
    def __init__(self,actor:unreal.SkyAtmosphere) -> None:
        super().__init__(actor)
        self.actor:unreal.SkyAtmosphere
        self.component:unreal.SkyAtmosphereComponent

class WrapPostProcessVolume(WrapActor):
    def __init__(self,actor:unreal.PostProcessVolume) -> None:
        super().__init__(actor)
        self.actor:unreal.PostProcessVolume
    def setUnbound(self,isUnbound:bool):
        self.actor.unbound = isUnbound
    def getCurrentSettings(self)->unreal.PostProcessSettings:
        return self.actor.settings
    def setCurrentSettings(self,settings:unreal.PostProcessSettings):
        self.actor.settings = settings
    def setAutoExposureBias(self,value:float):
        processSettings = self.getCurrentSettings()
        processSettings.set_editor_property('auto_exposure_bias',0.0)
        processSettings.set_editor_property('override_auto_exposure_bias',True)
        self.setCurrentSettings(processSettings)
    def setAutoExposureMinBrightness(self,value:float):
        processSettings = self.getCurrentSettings()
        processSettings.set_editor_property('auto_exposure_min_brightness',value)
        processSettings.set_editor_property('override_auto_exposure_min_brightness',True)
        self.setCurrentSettings(processSettings)
    def setAutoExposureMaxBrightness(self,value:float):
        processSettings = self.getCurrentSettings()
        processSettings.set_editor_property('auto_exposure_max_brightness',value)
        processSettings.set_editor_property('override_auto_exposure_max_brightness',True)
        self.setCurrentSettings(processSettings)
    def setRayTracingGiType(self,type:unreal.RayTracingGlobalIlluminationType):
        processSettings = self.getCurrentSettings()
        processSettings.set_editor_property('ray_tracing_gi_type',type)
        processSettings.set_editor_property('override_ray_tracing_gi',True)
        self.setCurrentSettings(processSettings)
    def setRayTracingGiMaxBounces(self,value:int):
        processSettings = self.getCurrentSettings()
        processSettings.set_editor_property('ray_tracing_gi_max_bounces',value)
        processSettings.set_editor_property('override_ray_tracing_gi_max_bounces',True)
        self.setCurrentSettings(processSettings)
    def setRayTracingGiSamplesPerPixel(self,value:int):
        processSettings = self.getCurrentSettings()
        processSettings.set_editor_property('ray_tracing_gi_samples_per_pixel',value)
        processSettings.set_editor_property('override_ray_tracing_gi_samples_per_pixel',True)
        self.setCurrentSettings(processSettings)

class WrapStaticMeshActor(WrapActor):
    def __init__(self, actor:unreal.StaticMeshActor):
        super().__init__(actor)
        self.actor:unreal.StaticMeshActor
        self.component:unreal.StaticMeshComponent
    def getStaticmesh(self)->WrapStaticMesh:
        return WrapStaticMesh(self.component.static_mesh)
    def setStaticMesh(self,inStaticMesh:unreal.StaticMesh):
        self.component.set_static_mesh(inStaticMesh)
    def setMaterialByName(self,material:unreal.MaterialInterface,name:str):
        self.component.set_material_by_name(name,material)
    def setMaterialByIndex(self,material:unreal.MaterialInterface,index:int):
        self.component.set_material(index,material)
    def setStencilValue(self,value:int):
        self.component.set_editor_property('render_custom_depth',True)
        self.component.set_editor_property('custom_depth_stencil_value',value)


class FilmBackPreset():
    Film = "16:9 Film"
    DigitalFilm = "16:9 Digital Film"
    DSLR = "16:9 DSLR"
    Super8mm = "Super 8mm"
    Super16mm = "Super 16mm"
# 函数
def createGerericAsset(assetPath:str,uniqueName:bool,assetClass:unreal.StreamableRenderAsset,assetFactory:unreal.Factory):
    #保证路径分隔符为斜杠
    assetPath = assetPath.replace("\\","/")
    if uniqueName:
        assetPath,assetName = unreal.AssetToolsHelpers.get_asset_tools().create_unique_asset_name(base_package_name=assetPath,suffix="")
    if not unreal.EditorAssetLibrary.does_asset_exist(asset_path=assetPath):
        unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name = os.path.basename(assetPath),
            package_path = os.path.dirname(assetPath),
            asset_class=assetClass,
            factory=assetFactory
        )
    return unreal.load_asset(assetPath)

def duplicate_asset(Spath,Dpath):
    if unreal.EditorAssetLibrary.does_asset_exist(Dpath):
        return False
    unreal.EditorAssetLibrary.duplicate_asset(Spath,Dpath)
    unreal.EditorAssetLibrary.save_asset(Dpath,True)


def buildImportTask(filePath:str,destinationPath:str,options = None):
    task = unreal.AssetImportTask()
    task.automated = True
    task.destination_name = ""
    task.destination_path = destinationPath
    task.filename = filePath
    task.replace_existing = True
    task.save = True
    if options:
        task.options = options
    return task

def unrealLog(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log(logstring)

def unrealLogWarning(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log_warning(logstring)

def unrealLogError(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log_error(logstring)


def openSelectedFoliage():
    includeMode = unreal.RMAFoliageToolsIncludeMode.RMAIM_SELECTION
    buffer = unreal.RMAFoliageToolsFunctionLibrary.create_buffer(includeMode,False)
    assetEditorSubsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    assetEditorSubsystem.open_editor_for_assets([unreal.SystemLibrary.conv_soft_obj_path_to_soft_obj_ref(buffer.assets[0])])


def FoliageToSMActor():
    IncludeMode = unreal.RMAFoliageToolsIncludeMode.RMAIM_SELECTION
    unreal.RMAFoliageToolsFunctionLibrary.foliage_ins_to_sm_actor(IncludeMode,True)



def appendWindowToUnreal(winID:int):
    unrealLog("ZynnPipline",f"窗口{winID}已经注册到引擎中")
    unreal.parent_external_window_to_slate(winID)


def FilterObjects(Actors:list,Filters:list):
    Resoult = []
    for Filter in Filters:
        Resoult = Resoult + list(unreal.EditorFilterLibrary.by_class(Actors,Filter))
    return Resoult


def enableFullPercisionUV():
    actors = editorActorSubsystem.get_selected_level_actors()
    actors = unreal.EditorFilterLibrary.by_class(actors,unreal.StaticMeshActor)
    for actor in actors:
        warpactor = WrapStaticMeshActor(actor)
        warpactor.getStaticmesh().useFullPercisionUV()
        warpactor.getStaticmesh().saveAsset()

def simpleLight():
    wrapDirectionLight = WrapDirectionLight(editorActorSubsystem.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,0)))
    wrapDirectionLight.setMobility(unreal.ComponentMobility.MOVABLE)
    wrapDirectionLight.setRotation(unreal.Rotator(0,-27,-136))
    wrapDirectionLight.appendToFolder("SimpleLight")
    wrapSkyLight = WrapSkyLight(editorActorSubsystem.spawn_actor_from_class(unreal.SkyLight,unreal.Vector(0,0,0)))
    wrapSkyLight.setMobility(unreal.ComponentMobility.MOVABLE)
    wrapSkyLight.setRealTimeCapture(True)
    wrapSkyLight.appendToFolder("SimpleLight")
    wrapskyAtmophere = WrapSkyAtmophere(editorActorSubsystem.spawn_actor_from_class(unreal.SkyAtmosphere,unreal.Vector(0,0,0)))
    wrapskyAtmophere.appendToFolder("SimpleLight")
    wrapPPV = WrapPostProcessVolume(editorActorSubsystem.spawn_actor_from_class(unreal.PostProcessVolume,unreal.Vector(0,0,0)))
    wrapPPV.setAutoExposureBias(0.0)
    wrapPPV.setAutoExposureMinBrightness(0.0)
    wrapPPV.setAutoExposureMaxBrightness(0.0)
    wrapPPV.setUnbound(True)
    # 可以后续自定义
    wrapPPV.appendToFolder("SimpleLight")


def selectSimilarActor():
    slActor = editorActorSubsystem.get_selected_level_actors()[0]
    allActors = editorActorSubsystem.get_all_level_actors()
    simActors = []
    for Actor in allActors:
        if type(slActor) == unreal.StaticMeshActor and type(Actor) == unreal.StaticMeshActor:
            if slActor.static_mesh_component.static_mesh == Actor.static_mesh_component.static_mesh:
                    simActors.append(Actor)
        else:
            if slActor.get_class() == Actor.get_class():
                simActors.append(Actor)
    for actor in simActors:
        editorActorSubsystem.set_actor_selection_state(actor,True)

def breakBlueprint(deleteOrigin:bool):
    slActor = editorActorSubsystem.get_selected_level_actors()[0]
    breakFolderName = slActor.get_actor_label() + "_Break"
    meshComponents = slActor.get_components_by_class(unreal.MeshComponent)
    if len(meshComponents) > 0:
        staticMeshComponents = slActor.get_components_by_class(unreal.StaticMeshComponent)
        for staticMeshComponent in staticMeshComponents:
            staticMeshComponent:unreal.StaticMeshComponent
            newStaticMeshActor = WrapStaticMeshActor(editorActorSubsystem.spawn_actor_from_class(unreal.StaticMeshActor,staticMeshComponent.get_world_location(),staticMeshComponent.get_world_rotation()))
            newStaticMeshActor.setScale(staticMeshComponent.get_world_scale())
            newStaticMeshActor.appendToFolder(breakFolderName)
            newStaticMeshActor.setStaticMesh(staticMeshComponent.static_mesh)
            for materialStruct in staticMeshComponent.static_mesh.static_materials:
                materialStruct:unreal.StaticMaterial
                newStaticMeshActor.setMaterialByName(materialStruct.material_interface,materialStruct.material_slot_name)
    ChildActorComponents = slActor.get_components_by_class(unreal.ChildActorComponent)
    if len(ChildActorComponents) > 0:
        for ChildActorComponent in ChildActorComponents:
            ChildActorComponent:unreal.ChildActorComponent
            originStaticMeshActor = ChildActorComponent.child_actor
            originStaticMeshActor:unreal.StaticMeshActor
            newStaticMeshActor = WrapStaticMeshActor(editorActorSubsystem.spawn_actor_from_class(unreal.StaticMeshActor,ChildActorComponent.get_world_location(),ChildActorComponent.get_world_rotation()))
            newStaticMeshActor.setScale(ChildActorComponent.get_world_scale())
            newStaticMeshActor.appendToFolder(breakFolderName)
            newStaticMeshActor.setStaticMesh(originStaticMeshActor.static_mesh_component.static_mesh)   
            for materialStruct in originStaticMeshActor.static_mesh_component.static_mesh.static_materials:
                materialStruct:unreal.StaticMaterial
                newStaticMeshActor.setMaterialByName(materialStruct.material_interface,materialStruct.material_slot_name)
    if deleteOrigin:
        slActor.destroy_actor()
def autoID():
    allStaticmeshActors = editorActorSubsystem.get_all_level_actors()
    allStaticmeshActors = list(unreal.EditorFilterLibrary.by_class(allStaticmeshActors,unreal.StaticMeshActor))
    print(allStaticmeshActors)
    for i in range(len(allStaticmeshActors)):
        wrapStaticMeshActor = WrapStaticMeshActor(allStaticmeshActors[i])
        stencilValue = i % 200 + 1
        wrapStaticMeshActor.setStencilValue(stencilValue)
    components = editorActorSubsystem.get_all_level_actors_components()
    components = unreal.EditorFilterLibrary.by_class(components,unreal.FoliageInstancedStaticMeshComponent)
    for i in range(len(components)):
        component = components[i] 
        value = i % 50 + 201
        component:unreal.FoliageInstancedStaticMeshComponent
        component.set_editor_property('render_custom_depth',True)
        component.set_editor_property('custom_depth_stencil_value',value)
    levelEditorSybsystem.save_all_dirty_levels()
        

def poolSize(value=0):
    unreal.SystemLibrary.execute_console_command(unrealEditorSybsystem.get_editor_world(),f"r.Streaming.PoolSize {value}")

def popEmmissive():

    pass


def nearClip(value:float):
    unreal.SystemLibrary.execute_console_command(unrealEditorSybsystem.get_editor_world(),f'r.SetNearClipPlane {value}')

def saveAll():
    unreal.EditorAssetLibrary.save_directory("/Game/")
def importCameras(datas:list):
    saveAll()          # 保存所有资产,防止导入过程中崩溃
    dataCount = len(datas)
    for data in datas: # 遍历所有传入的资产数据
        name = data["name"]
        path = data["path"]
        parsedName = UT.parseCameraName(name)
        if parsedName:
            assetPath = UT.applyMacro(globalConfig.get().CameraImportPathPatten,parsedName) # 应用宏替换
            wrapLevelSeq = WarpLevelSequence.create(assetPath,False)                     # 创建关卡序列
            wrapLevelSeq.setFrameRate(25)                                                # 设置帧率
            wrapLevelSeq.setPlayBackStart(int(parsedName["frameStart"])-globalConfig.get().cameraPlaybackStartOffset)
            wrapLevelSeq.setPlayBackEnd(int(parsedName["frameEnd"])+globalConfig.get().cameraPlaybackStartOffset)
            wrapLevelSeq.importCamera(path,globalConfig.get().CameraimportUniformScale)                                              # 导入相机
            templist = wrapLevelSeq.getBindingProxyAndObject(unreal.CineCameraActor)
            if not templist:
                unrealLogError("相机导入","从wrapLevelSeq上获取相机失败,相机属性设置失败")
                return False
            templist[0].set_name(name)                                                   # 重命名相机
            wrapCamera = WrapCineCameraActor(templist[1])
            wrapCamera.setFilmback(FilmBackPreset.DSLR)
            wrapCamera.setFocusMethod(unreal.CameraFocusMethod.DISABLE)
            wrapCamera.setAspectRatio(globalConfig.get().CameraimportAspectRatio)
            wrapLevelSeq.SetCameraCutsStartEnd(int(parsedName["frameStart"])-globalConfig.get().cameraImportPreRollFrame,int(parsedName["frameEnd"])+globalConfig.get().cameraImportPostRollFrame)
            wrapLevelSeq.setLock(True)                                                    # 锁定序列
            wrapLevelSeq.saveAsset()
        else:
            unrealLogError("相机导入",f"无法解析相机名称{name}")


def textureImport(texturePaths:list,path):
    wrapTex = WrapTexture.importTexture(texturePaths[0],path)
    if len(texturePaths) == 1:
        return wrapTex
    if not (wrapTex.setVTEnable(globalConfig.get().TextureEnableVT) and globalConfig.get().TextureEnableVT):
        UT.ConvertTexture.resizerTextures(texturePaths)
        wrapTex = WrapTexture.importTexture(texturePaths[0],path)
    return wrapTex



def importStaticmeshs(datas:list,sceneName=None,createSwitch=False):


    sub_level_names=['_Shade','_Shade_Light','_Shade_VFX']
    basefloder_names=['Map/Level','Common','Material','Mesh','Other','BP','VFX','Texture']

    #判断输入名称是否为空
    if sceneName:
        scene_null = False
    else:
        scene_null = True

    saveAll()          # 保存所有资产,防止导入过程中崩溃
    #duplicate_asset(globalConfig.get().SceneDefaultMaterial,globalConfig.get().LocalSceneDefaultMaterial)
    # 载入对应母球
    wrapMaterial = WrapMaterial(unreal.load_asset(globalConfig.get().SceneDefaultVTMaterial))
    for data in datas: # 遍历所有传入的资产数据
        name = data["name"]
        path = data["path"]
        
        #未获取到场景名称时,使用导入的网格名称
        if scene_null:
            sceneName = name

        scene_root_name = globalConfig.get().StaticMeshImportPathPatten
        scene_root_name = scene_root_name.replace('$scenename',sceneName)

        if createSwitch == True:    #判断是否创建关卡
            #创建基础文件夹
            for basefloder_name in basefloder_names:
                unreal.EditorAssetLibrary.make_directory(scene_root_name+basefloder_name)
            #创建主关卡
            if not unreal.EditorAssetSubsystem().does_asset_exist(scene_root_name+'Map/'+sceneName+'_Main'):
                main_level=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=sceneName+'_Main',package_path=scene_root_name+'Map',asset_class=unreal.World,factory=unreal.WorldFactory())
            #创建子关卡
            for sub_level_name in sub_level_names:
                if not unreal.EditorAssetSubsystem().does_asset_exist(scene_root_name+'Map/Level/'+sceneName+sub_level_name):
                    sub_level=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=sceneName+sub_level_name,package_path=scene_root_name+'Map/Level',asset_class=unreal.World,factory=unreal.WorldFactory())
                    unreal.EditorLevelUtils().add_level_to_world(main_level,level_package_name=sub_level.get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)



        parseReslut = UT.parseStaticMeshName(name,sceneName)
        rootPath = UT.applyMacro(globalConfig.get().StaticMeshImportPathPatten,parseReslut)



        wrapSM = WrapStaticMesh.importFromFbx(path,os.path.join(rootPath,"Mesh"),1) #导入静态网格体
        
        JsonPath = path.replace('.fbx','.json')
        with open(JsonPath,"r",encoding="utf-8") as f:
            jsonData = json.loads(f.read())
        MaterialInfoList = UT.analyseJson(jsonData)
        for MaterialInfo in MaterialInfoList:
            # 判断是否创建材质
            if not MaterialInfo['CreateMaterial']:
                continue
            wrapMaterialIns = WrapMaterialInstance.create(os.path.join(rootPath,f"Material/{MaterialInfo['Materialname']}"))
            wrapMaterialIns.setParent(wrapMaterial.asset)
            TexturePath = MaterialInfo['TexturePath']
            if TexturePath['diffuse_color'] != None:
                wrapBaseColor = textureImport(TexturePath['diffuse_color'],os.path.join(rootPath,"Texture"))
                wrapBaseColor.saveAsset()
                wrapBaseColor.setAsColor()
                wrapBaseColor.setVTEnable(True)
                wrapBaseColor.saveAsset()
                wrapMaterialIns.setTextureParameter("BaseColor_Map",wrapBaseColor.asset)
            if TexturePath['refl_roughness'] == None:
                ARMSPath = TexturePath['refl_metalness']
            else:
                ARMSPath = TexturePath['refl_roughness']
            WrapARMS = textureImport(ARMSPath,os.path.join(rootPath,"Texture"))
            WrapARMS.saveAsset()
            WrapARMS.setAsLinerColor()
            WrapARMS.setVTEnable(True)
            WrapARMS.saveAsset()
            wrapMaterialIns.setTextureParameter("ARMS_Map",WrapARMS.asset)
            if TexturePath['bump_input'] != None:
                wrapNormal = textureImport(TexturePath['bump_input'],os.path.join(rootPath,"Texture"))
                wrapNormal.saveAsset()
                wrapNormal.setAsNormal()
                wrapNormal.setVTEnable(True)
                wrapNormal.saveAsset()
                wrapMaterialIns.setTextureParameter("Normal_Map",wrapNormal.asset)

            if TexturePath['emission_color'] != None:
                WrapEmissive = textureImport(TexturePath['emission_color'],os.path.join(rootPath,"Texture"))
                WrapEmissive.saveAsset()
                WrapEmissive.setAsColor()
                WrapEmissive.setVTEnable(True)
                WrapEmissive.saveAsset()
                wrapMaterialIns.setTextureParameter("Emmissive_Map",wrapNormal.asset)
                wrapMaterialIns.setScalarParameter("自发光强度",1.0)
            wrapMaterialIns.saveAsset()
            wrapSM.setMaterialBySloatName(MaterialInfo["Materialname"],wrapMaterialIns.asset)
        wrapSM.saveAsset()
    saveAll()





        

        
        
 
class MyTexture2D(object):
    def __init__(self):
        self.sloatname = None
        self.texture2D = None
        self.priority = 0
        pass


class TextureType(Enum):
    COLOR = auto()
    LINEARCOLOR = auto()
    NOMRAL = auto()




def convert_unreal_path_to_system_path(path:str)->str:
    dir = unreal.Paths.project_content_dir()
    result = dir + path.removeprefix("/Game/")
    return result





def getTextureSize(texture):
    return texture.blueprint_get_size_x()

def getKeyWordIndex(texture:MyTexture2D,keyWorlds:list[str]):
    textureName = texture.texture2D.get_name() 
    textureName = textureName+ "_" + str(texture.sloatname)
    for keyword in keyWorlds:
        if keyword in textureName.lower():
            return len(keyWorlds) - keyWorlds.index(keyword)
    return 0
def GetTextureByParam(texures:list[MyTexture2D],keywords:list[str],tType:TextureType) -> unreal.Texture2D:
    candidateTextures = []
    for texture in texures:
        if tType == TextureType.COLOR:
            if not texture.texture2D.srgb == True:
                continue
        elif tType == TextureType.LINEARCOLOR:
            if texture.texture2D.srgb == True or texture.texture2D.compression_settings == unreal.TextureCompressionSettings.TC_NORMALMAP:
                continue
        elif tType == TextureType.NOMRAL:
            if not texture.texture2D.compression_settings == unreal.TextureCompressionSettings.TC_NORMALMAP:
                continue
        candidateTextures.append(texture)
    
    #根据关键词过滤
    candidateTextures = list(filter(partial(getKeyWordIndex,keyWorlds=keywords),candidateTextures))

    # 根据关键词发现的顺序排序
    candidateTextures.sort(key=partial(getKeyWordIndex,keyWorlds=keywords),reverse=True)

    if candidateTextures == []:
        return False
    else:
        return candidateTextures[0].texture2D

def ExportTexture(Texture,dir):
    Path = os.path.join(dir,Texture.get_name() + '.png')
    task = unreal.AssetExportTask()
    task.replace_identical = False
    task.prompt = False
    task.automated = True
    task.options = unreal.TextureExporterPNG()
    task.object = Texture
    task.filename = Path
    if not unreal.Exporter.run_asset_export_task(task):
        return False
    return Path

def ExportMesh(Mesh,dir):
    Path = os.path.join(dir,Mesh.get_name() + '.fbx')
    task = unreal.AssetExportTask()
    task.replace_identical = False
    task.prompt = False
    task.automated = True
    task.options = unreal.FbxExportOption()
    task.options.level_of_detail = False
    task.options.collision = False

    task.object = Mesh
    task.filename = Path
    res = unreal.Exporter.run_asset_export_task(task)
    return Path

def NormalExportPipline(BaseColor:unreal.Texture2D,Normal:unreal.Texture2D,Metallic:unreal.Texture2D,Roughness:unreal.Texture2D):
    import tempfile
    import os
    temp_dir = tempfile.gettempdir()
    BaseColorpath = ExportTexture(BaseColor,temp_dir)
    Normalpath = ExportTexture(Normal,temp_dir)
    RoughnessPath = ExportTexture(Roughness,temp_dir)

    
    if not Metallic:
        MetallicPath = RoughnessPath.replace(".png","_Metallic.png")
        image = Image.new('L',(64,64),color = 0)
        image.save(MetallicPath,'png')
    else:
        MetallicPath = ExportTexture(Metallic,temp_dir)

    if not (BaseColorpath or Normalpath or RoughnessPath or MetallicPath):
        return False
    return [BaseColorpath,Normalpath,MetallicPath,RoughnessPath]


def CompositeExportPipline(BaseColor:unreal.Texture2D,Normal:unreal.Texture2D,Composite:unreal.Texture2D,RoughnessChannel:int,MetallicChannel:int):
    import tempfile
    temp_dir = tempfile.gettempdir()

    BaseColorpath = ExportTexture(BaseColor,temp_dir)
    Normalpath = ExportTexture(Normal,temp_dir)

    CompositePath = ExportTexture(Composite,temp_dir)
    if not CompositePath:
        return False
    
    CompositeImage = Image.open(CompositePath)
    channels = CompositeImage.split()
    if len(channels) == 1:
        # 当贴图通道较少时,贴图识别不合格
        return False
    RoughnessImage = channels[RoughnessChannel]
    MetallicImage = channels[MetallicChannel]

    RoughnessPath = CompositePath.replace(".png","_Roughness.png")
    RoughnessImage.save(RoughnessPath,"PNG")

    MetallicPath = CompositePath.replace(".png","_Metallic.png")
    MetallicImage.save(MetallicPath,"PNG")

    if not (BaseColorpath or Normalpath or RoughnessPath or MetallicPath):
        return False
    return [BaseColorpath,Normalpath,MetallicPath,RoughnessPath]


def ExportUsefulTextures(textures:list[MyTexture2D]):
    baseColorKeyWords = ['albedo','basecolor','diffuse','color',"_bc","_c","_d",'_b']
    roughnessKeyWords = ['roughness','_rough','_rou']
    metallicKeyWords = ["metal"]
    normalKeyWords = ["_n",'_norm','_normal']
    ramKeyWords = ["_ram"]
    armKeyWords = ['_orm','_arm','_mask']
    rmaKeyWords  =  ['_rma']
    mraKeyWords = ["_mra"]
    srmKeyWords = ['_srm']


    baseColorTexture = GetTextureByParam(textures,baseColorKeyWords,TextureType.COLOR)
    normalTexture = GetTextureByParam(textures,normalKeyWords,TextureType.NOMRAL)


    RoughnessTexture = GetTextureByParam(textures,roughnessKeyWords,TextureType.LINEARCOLOR)
    MetallicTexture = GetTextureByParam(textures,metallicKeyWords,TextureType.LINEARCOLOR)
    armTexture = GetTextureByParam(textures,armKeyWords,TextureType.LINEARCOLOR)
    ramTexture = GetTextureByParam(textures,ramKeyWords,TextureType.LINEARCOLOR)
    rmaTexture = GetTextureByParam(textures,rmaKeyWords,TextureType.LINEARCOLOR)
    mraTexture = GetTextureByParam(textures,mraKeyWords,TextureType.LINEARCOLOR)
    srmTexture = GetTextureByParam(textures,srmKeyWords,TextureType.LINEARCOLOR)
    

    #排除不需要的情况
    if not (baseColorTexture and normalTexture):
        return False
    
    
    if not (RoughnessTexture or armTexture or ramTexture or rmaTexture or mraTexture or srmTexture):
        return False
    
    if RoughnessTexture == MetallicTexture:
        return False
    
    if RoughnessTexture and not (armTexture or ramTexture or rmaTexture or mraTexture or srmTexture):
        print("当前贴图模式为默认模式")
        return NormalExportPipline(baseColorTexture,normalTexture,MetallicTexture,RoughnessTexture)
    elif armTexture:
        print("当前贴图模式为ARM")
        return CompositeExportPipline(baseColorTexture,normalTexture,armTexture,1,2)
    elif ramTexture:
        print("当前贴图模式为RAM")
        return CompositeExportPipline(baseColorTexture,normalTexture,ramTexture,0,2)
    elif rmaTexture:
        print("当前贴图模式为RMA")
        return CompositeExportPipline(baseColorTexture,normalTexture,rmaTexture,0,1)
    elif mraTexture:
        print("当前贴图模式为MRA")
        return CompositeExportPipline(baseColorTexture,normalTexture,mraTexture,1,0)
    elif srmTexture:
        print("当前贴图模式为SRM")
        return CompositeExportPipline(baseColorTexture,normalTexture,srmTexture,1,2)
    else:
        return False


def GetUsedTextures(mat) -> list[MyTexture2D]:
    textures = []
    if(type(mat) == unreal.Material):
        texs = unreal.MaterialEditingLibrary.get_used_textures(mat)
        for tex in texs:
            myTex = MyTexture2D()
            myTex.texture2D = tex
            textures.append(myTex)
        return textures
    else:
        for texParm in mat.texture_parameter_values:
            if texParm.parameter_value != None:
                sloatName = texParm.parameter_info.name
                texture2D = texParm.parameter_value
                myTex = MyTexture2D()
                myTex.sloatname = sloatName
                myTex.texture2D = texture2D
                textures.append(myTex)
        return textures

def MoveAndRenameFile(srcPath:str,desFolder:str,newFileName:str):
    if not os.path.exists(desFolder):
        os.makedirs(desFolder)
    import shutil
    desPath = os.path.join(desFolder,newFileName)
    shutil.move(srcPath,desPath)
    print(f"将文件{srcPath}移动到{desPath}")
    return desPath




def NormalizeExport_old(exportFolder:str):
    selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()
    #遍历所有模型
    for selectedAsset in selectedAssets:
        selectedAsset:unreal.StaticMesh
        meshName = selectedAsset.get_name()
        rootFolder = os.path.join(exportFolder,meshName)
        staticMaterials = selectedAsset.static_materials
        
        # 去重材质
        MaterialWaitForExport = []
        for m in staticMaterials:
            if m not in MaterialWaitForExport:
                MaterialWaitForExport.append(m)
                

        print(f"准备开始导出:{meshName},共有材质{len(MaterialWaitForExport)}个,导出的路径为:{rootFolder}")
        # 遍历所有材质
        materials = []
        for staticMaterial in MaterialWaitForExport:
            staticMaterial:unreal.StaticMaterial
            materialName = staticMaterial.material_interface.get_name()
            if staticMaterial.material_interface == None:
                print(f"模型{meshName}的材质:{materialName},不存在,跳过该材质")
                continue
            textures = GetUsedTextures(staticMaterial.material_interface)
            if len(textures) < 2:
                #踢除小于2材质
                print(f"模型{meshName}的材质:{materialName},上贴图数量少于2,判定为无效材质,跳过")
                continue
            textures = ExportUsefulTextures(textures)
            if not textures:
                print(f"模型{meshName}的材质:{materialName},贴图获取失败,或不符合标准,跳过")
                continue
            BaseColorpath,NormalPath,MetallicPath,RoughnessPath = textures
            textureRootPath = os.path.join(rootFolder,'Textures')

            newBaseColorPath = MoveAndRenameFile(BaseColorpath,textureRootPath,materialName + "_BaseColor.png")
            newNormalPath = MoveAndRenameFile(NormalPath,textureRootPath,materialName + "_Normal.png")
            newMetallicpath = MoveAndRenameFile(MetallicPath,textureRootPath,materialName + "_Metallic.png")
            newRoughnessPath = MoveAndRenameFile(RoughnessPath,textureRootPath,materialName + "_Roughness.png")

            materialInfo = dict(
                materialName = materialName,
                fUDIM = False,
                type = "PBR",
                baseColorPaths=[newBaseColorPath.replace(rootFolder,"")],
                roughnessPaths = [newRoughnessPath.replace(rootFolder,"")],
                metallicPaths = [newMetallicpath.replace(rootFolder,"")],
                normalPaths = [newNormalPath.replace(rootFolder,"")],
                TextureTiling = (1.0,1.0)
            )
            materials.append(materialInfo)
        if len(materials) == 0:
            print(f"模型{meshName}上有效材质过少,跳过")
            continue
        fbxFilePath = ExportMesh(selectedAsset,rootFolder)
        jsonFilepath = fbxFilePath.replace(".fbx",'.json')
        datas = json.dumps(materials)
        with open(jsonFilepath,'w+',encoding='utf-8') as f:
            f.write(datas)
        print(f"模型{meshName}导出成功")


def ExportMeshGLB(Mesh,dir):
    Path = os.path.join(dir,Mesh.get_name() + '.glb')

    ExportOptions = unreal.GLTFExportOptions()
    ExportOptions.export_uniform_scale = 0.01
    ExportOptions.export_preview_mesh = True
    ExportOptions.export_proxy_materials = False
    ExportOptions.export_unlit_materials = False
    ExportOptions.export_clear_coat_materials = False
    ExportOptions.export_emissive_strength = False
    ExportOptions.bake_material_inputs = unreal.GLTFMaterialBakeMode.USE_MESH_DATA
    ExportOptions.default_material_bake_size = unreal.GLTFMaterialBakeSizePOT.POT_2048

    unreal.GLTFExporter.export_to_gltf(Mesh,Path,ExportOptions,set())

    return Path

def HandleTextures(materials,rootPath):
    import shutil
    result = []
    TextureRootPath = os.path.join(rootPath,"Textures")
    if not os.path.exists(TextureRootPath):
        os.makedirs(TextureRootPath)
    for material in materials:
        name,basecolor,normal,mr = material
        baseColorPath = os.path.join(TextureRootPath,f"{name}_BaseColor.png")
        shutil.move(basecolor,baseColorPath)
        normalPath = os.path.join(TextureRootPath,f"{name}_Normal.png")
        shutil.move(normal,normalPath)

        RoughnessPath = os.path.join(TextureRootPath,f"{name}_Roughness.png")
        MetallicPath = os.path.join(TextureRootPath,f"{name}_Metallic.png")
        if mr != None:
            CompositeImage = Image.open(mr)
            channels = CompositeImage.split()
            MetallicImage = channels[1]
            RoughnessImage = channels[2]
            RoughnessImage.save(RoughnessPath,"PNG")
            MetallicImage.save(MetallicPath,"PNG")
            CompositeImage.close()
            os.remove(mr)
        else:
            image = Image.new('L',(64,64),color = 0)
            image.save(MetallicPath,'png')
            image = Image.new('L',(64,64),color = 1)
            image.save(RoughnessPath,'png')

        materialInfo = dict(
                materialName = name,
                fUDIM = False,
                type = "PBR",
                baseColorPaths=[baseColorPath.replace(rootPath,"")],
                roughnessPaths = [RoughnessPath.replace(rootPath,"")],
                metallicPaths = [MetallicPath.replace(rootPath,"")],
                normalPaths = [normalPath.replace(rootPath,"")],
                TextureTiling = (1.0,1.0)
            )
        result.append(materialInfo)
    return result


def NormalizeExport(exportFolder:str):
    selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()
    # 过滤掉非Mesh的类型
    staticMeshs = list(filter(lambda x : isinstance(x,unreal.StaticMesh),selectedAssets))
    for mesh in staticMeshs:
        meshName = mesh.get_name()
        print(f"开始导出模型{meshName}")
        rootFolder = os.path.join(exportFolder,meshName)
        GlbFilePath = ExportMeshGLB(mesh,rootFolder)
        if not GlbFilePath:
            print(f"模型{meshName}导出失败,跳过")
            shutil.rmtree(rootFolder)
            continue
        myglb = g.WrapGLB(GlbFilePath)
        result =  myglb.ExportAndGetMaterialData()
        if not result:
            print(f"模型{meshName}导出失败,跳过")
            shutil.rmtree(rootFolder)
            continue
        fbxFilePath = ExportMesh(mesh,rootFolder)
        jsonFilepath = fbxFilePath.replace(".fbx",'.json')
        datas = json.dumps(result)
        with open(jsonFilepath,'w+',encoding='utf-8') as f:
            f.write(datas)
        myglb.DeleteUseless()
        print(f"模型{meshName}导出成功")


def MakeEntry(name:str,label:str,command:str = "",toolTip:str = "") -> unreal.ToolMenuEntry:
    entry = unreal.ToolMenuEntry(
        name=name,
        type=unreal.MultiBlockType.MENU_ENTRY,
        insert_position=unreal.ToolMenuInsert("",unreal.ToolMenuInsertType.FIRST)
    )
    entry.set_label(label)
    entry.set_tool_tip(toolTip)
    entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON,"",command)
    return entry



def importAssetPipline(AssetData:dict):
    udim = False
    # 用来兼容旧版本的MyBridge
    try:
        if AssetData["udim"] == 'True':
            udim = True
    except:
        pass
    if AssetData["assetFormat"] == 'FBX':# 当类型为FBX资产
        rootPath = os.path.join(globalConfig.get().MyBridgeTargetPath,f"{AssetData['assetType'].replace(' ','_')}/{AssetData['name']}_{AssetData['AssetID']}")
        #导入贴图
        t_arm = WrapTexture.importTexture(AssetData["arm"],os.path.join(rootPath,f"Textures"))
        t_arm.saveAsset()
        t_arm.setAsLinerColor()
        t_arm.setVTEnable(udim)
        t_arm.saveAsset()

        t_baseColor = WrapTexture.importTexture(AssetData["baseColor"],os.path.join(rootPath,f"Textures"))
        t_baseColor.saveAsset()
        t_baseColor.setAsColor()
        t_baseColor.setVTEnable(udim)
        t_baseColor.saveAsset()


        t_normal = WrapTexture.importTexture(AssetData["normal"],os.path.join(rootPath,f"Textures"))
        t_normal.saveAsset()
        t_normal.setAsNormal()
        t_normal.setVTEnable(udim)
        t_normal.saveAsset()

        
        wrapMaterialIns = WrapMaterialInstance.create(os.path.normpath(os.path.join(rootPath,f"Materials/MI_{AssetData['name']}_{AssetData['AssetID']}")))
        if AssetData["assetType"] == '3D Assets':
            if udim:
                wrapMaterial = WrapMaterial(unreal.load_asset(globalConfig.get().SceneDefaultVTMaterial))
            else:
                wrapMaterial = WrapMaterial(unreal.load_asset(globalConfig.get().SceneDefaultMaterial))
            #导入静态网格体
            wrapSM = WrapStaticMesh.importFromFbx(AssetData["mesh"],rootPath,1) 
            wrapSM.setMaterialByIndex(0,wrapMaterialIns.asset)
            wrapSM.saveAsset()
        elif AssetData["assetType"] == 'Surface':
            wrapMaterial = WrapMaterial(unreal.load_asset(globalConfig.get().SceneDefaultMaterial))
            pass
        elif AssetData["assetType"] == 'Decal':
            wrapMaterial = WrapMaterial(unreal.load_asset(globalConfig.get().DefaultDecalMaterial))    
            pass
        elif AssetData["assetType"] == 'Plant':
            wrapMaterial = WrapMaterial(unreal.load_asset(globalConfig.get().DefaultFoliageMaterial))    
            wrapSM = WrapStaticMesh.importFromFbx(AssetData["mesh"],rootPath,1) 
            wrapSM.setMaterialByIndex(0,wrapMaterialIns.asset)
            wrapSM.saveAsset()
            pass
        wrapMaterialIns.setParent(wrapMaterial.asset)
        wrapMaterialIns.setTextureParameter("BaseColor_Map",t_baseColor.asset)
        wrapMaterialIns.setTextureParameter("Normal_Map",t_normal.asset)
        wrapMaterialIns.setTextureParameter("ARMS_Map",t_arm.asset)
        wrapMaterialIns.saveAsset()
    elif AssetData["assetFormat"] == "Unreal Engine":# 当类型为FBX资产
        tempPath = globalConfig.get().MyBridgeTargetPathBuildin + "3D_Assets/" + AssetData["AssetID"]
        system_path = convert_unreal_path_to_system_path(tempPath)
        if not os.path.exists(system_path):
            shutil.copytree(AssetData["mesh"],system_path)
        else:
            print(f"目录{system_path}已经存在跳过导出")
    else:
        pass
def getAllScenesName(rootFolder="/Game/Assets/Scenes"):
    dirs = unrealAssetsSubsystem.list_assets(rootFolder,False,True)
    return [dir.split("/")[-2] for dir in dirs]


def ExportTextureNew(Texture:unreal.Texture2D,dir:str)->list[str]:
    TextureCount = 1
    if Texture.virtual_texture_streaming:
        size_x = Texture.blueprint_get_size_x()
        size_y = Texture.blueprint_get_size_y()
        TextureCount = size_x//size_y
    textures = []
    if TextureCount == 1:
        textures.append(ExportTexture(Texture,dir))
    else:
        textureName = ExportTexture(Texture,dir)
        s,ext = os.path.splitext(textureName)
        for i in range(TextureCount):
            textures.append("{}.1{:03}{}".format(s,i+1,ext))
    return textures


def addWaterMarkToSelectedTextures():
    from UnrealPipeline.core.WTHelper import addWatermark
    selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()
    icpath = os.path.join(__file__.removesuffix(r"core\UnrealHelper.py"),r"Data\wm_ZYNN.png")
    for asset in selectedAssets:
        asset:unreal.Texture2D
        vt = asset.virtual_texture_streaming
        if asset.get_name().endswith("_1001"):
            asset.rename(asset.get_name().replace("_1001",""))
        exportTextures = ExportTextureNew(asset,globalConfig.get().tempFolder)
        for tex in exportTextures:
            if os.path.exists(tex):
                addWatermark('DCT',tex,tex,icpath)
        newTexture = WrapTexture.importTexture(exportTextures[0],os.path.dirname(asset.get_path_name()))
        if newTexture:
            newTexture.setVTEnable(vt)
            newTexture.saveAsset()
        for tex in exportTextures:
            if os.path.exists(tex):
                os.remove(tex)

def GetDependenceAssets(asset):
    options = unreal.AssetRegistryDependencyOptions()
    options.include_hard_management_references = True
    options.include_hard_package_references = True
    options.include_searchable_names = True
    options.include_soft_management_references = True
    options.include_soft_package_references = True
    assetRegistry = unreal.AssetRegistryHelpers.get_asset_registry()
    references = assetRegistry.get_dependencies(asset.get_package().get_name(),options)
    return [str(ref) for ref in references]




def MoveMaterialAndDependenceToFolder(material:unreal.Material,rootFolder:str):

    '''
        注意第二个参数需要传入一个文件夹路径,而且需要以/结尾
    '''
    dependencies = GetDependenceAssets(material)

    # 复制材质到指定目录
    new_material_path = rootFolder + os.path.basename(material.get_path_name())
    unreal.EditorAssetLibrary.duplicate_asset(material.get_path_name(),new_material_path)
    material = unreal.load_asset(new_material_path)

    # 遍历所有依赖项
    for dependency in dependencies:
        # 过滤引擎和插件中的资源
        if not dependency.startswith("/Game/"):
            continue
        # 复制资源到指定目录
        new_path = rootFolder + os.path.basename(dependency)
        unreal.EditorAssetLibrary.duplicate_asset(dependency,new_path)

        old_assets = unreal.load_asset(dependency)
        new_assets = unreal.load_asset(new_path)

        if type(new_assets)  == unreal.MaterialFunction:# 材质函数
            unreal.PythonExtensionBPLibrary.replace_material_function_reference_of_material(material,old_assets,new_assets)
        elif type(new_assets)  == unreal.Texture2D:# 贴图
            print(f"replace reference of texture {new_assets.get_name()}")
            unreal.PythonExtensionBPLibrary.replace_texture_reference_of_material(material,old_assets,new_assets)

        unreal.EditorAssetLibrary.save_asset(material.get_path_name())
        unreal.EditorAssetLibrary.save_asset(new_path)
    return new_material_path



def MoveStaticMeshAndDependenceToFolder(staticMesh:unreal.StaticMesh,rootFolder:str):
    '''
        注意第二个参数需要传入一个文件夹路径,而且需要以/结尾
    '''
    # 复制网格到指定目录
    new_asset_path = rootFolder + staticMesh.get_name()
    unreal.EditorAssetLibrary.duplicate_asset(staticMesh.get_path_name(),new_asset_path)
    staticMesh = unreal.load_asset(new_asset_path)
    static_materials = staticMesh.static_materials
    for static_material in static_materials:
        static_material:unreal.StaticMaterial
        material = static_material.material_interface
        material_name = static_material.material_slot_name #获取材质插槽名称
        if type(material) == unreal.MaterialInstanceConstant:
            # 复制母材质到指定目录
            new_master_material_path = MoveMaterialAndDependenceToFolder(material.parent,rootFolder + "Material/")
            new_master_material = unreal.load_asset(new_master_material_path)

            # 复制材质实例到指定目录
            new_material_instance_path = rootFolder+"MaterialInstance/"+material.get_name()
            unreal.EditorAssetLibrary.duplicate_asset(material.get_path_name(),new_material_instance_path)
            material = unreal.load_asset(new_material_instance_path)

            # 设置母球
            unreal.MaterialEditingLibrary.set_material_instance_parent(material,new_master_material)

            # 遍历贴图参数
            texture_parameter_values = material.texture_parameter_values
            for texture_parameter_value in texture_parameter_values:
                #复制贴图
                new_texture_path = rootFolder + "Textures/"+ texture_parameter_value.parameter_value.get_name()
                unreal.EditorAssetLibrary.duplicate_asset(texture_parameter_value.parameter_value.get_path_name(),new_texture_path)
                #设置贴图参数
                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material,texture_parameter_value.parameter_info.name,unreal.load_asset(new_texture_path))
                unreal.EditorAssetLibrary.save_asset(new_texture_path)
            
        elif type(material) == unreal.Material:
            new_material_path = MoveMaterialAndDependenceToFolder(material,rootFolder+"Material/")
            material = unreal.load_asset(new_material_path)
        # 替换材质
        staticMesh.set_material(staticMesh.get_material_index(material_name),material)
        unreal.EditorAssetLibrary.save_asset(material.get_path_name())
        unreal.EditorAssetLibrary.save_asset(staticMesh.get_path_name())
    return staticMesh



def ImportToLibrary():
    selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()
    for asset in selectedAssets:
        if type(asset) == unreal.StaticMesh:
            unreal.PythonExtensionBPLibrary.bake_mesh_pivot(asset,unreal.PivotPreset.BOUNDING_BOX_CENTER_BOTTOM)
            MoveStaticMeshAndDependenceToFolder(asset,"/Game/Test/3D_Assets/")

if __name__ == "__main__":
    selectedAssets = unreal.EditorUtilityLibrary.get_selected_assets()[0]
    MoveStaticMeshAndDependenceToFolder(selectedAssets,"/Game/Test/3D_Assets/")












