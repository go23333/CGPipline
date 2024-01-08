#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################
import time
from importlib import reload
from functools import wraps

import CGUtils.uCommon as UC

import unreal

reload(UC)
import uGlobalConfig as UG
reload(UG)



#获取一些subsystem
editorActorSubsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
staticMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assetEditorSubsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
levelEditorSybsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levelSequenceEditorSubsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
unrealEditorSybsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

# 定义一些包裹类

class WrapBaseAsset():
    def __init__(self,asset) -> None:
        self.asset = asset
    def saveAsset(self,onlyIfIsDirty = True):
        unreal.EditorAssetLibrary.save_loaded_asset(self.asset,onlyIfIsDirty)


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
            bindingProxy,TempCinCameraActor=levelSequenceEditorSubsystem.create_camera(True)

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
    def setAsNormal(self):
        self.asset.compression_settings = unreal.TextureCompressionSettings.TC_NORMALMAP
        self.asset.srgb = False
    @classmethod
    def importTexture(cls,sourcePath:str,destinationPath:str):
        task = buildImportTask(sourcePath,destinationPath)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        return(WrapTexture(task.get_objects()[0]))

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
        self.component.static_mesh =inStaticMesh
    def setMaterialByName(self,material:unreal.MaterialInterface,name:str):
        self.component.set_material_by_name(name,material)
    def setMaterialByIndex(self,material:unreal.MaterialInterface,index:int):
        self.component.set_material(index,material)
    def setStencilValue(self,value:int):
        self.component.set_editor_property('render_custom_depth',True)
        self.component.set_editor_property('custom_depth_stencil_value',value)

# 函数
def createGerericAsset(assetPath:str,uniqueName:bool,assetClass:unreal.StreamableRenderAsset,assetFactory:unreal.Factory):
    if uniqueName:
        assetPath,assetName = unreal.AssetToolsHelpers.get_asset_tools().create_unique_asset_name(base_package_name=assetPath,suffix="")
    if not unreal.EditorAssetLibrary.does_asset_exist(asset_path=assetPath):
        path = assetPath.rsplit("/",1)[0]
        name = assetPath.rsplit("/",1)[1]
        unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name=name,
            package_path=path,
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
            newStaticMeshActor = WrapStaticMeshActor(editorActorSubsystem.spawn_actor_from_class(unreal.StaticMeshActor,staticMeshComponent.get_actor_location()))
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
            newStaticMeshActor = WrapStaticMeshActor(editorActorSubsystem.spawn_actor_from_class(unreal.StaticMeshActor,staticMeshComponent.get_actor_location()))
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

def openImportCameraUI():
    pass

def nearClip(value:float):
    unreal.SystemLibrary.execute_console_command(unrealEditorSybsystem.get_editor_world(),f'r.SetNearClipPlane {value}')

def saveAll():
    unreal.EditorAssetLibrary.save_directory("/Game/")

def importCameras(datas:list):
    saveAll()          # 保存所有资产,防止导入过程中崩溃
    for data in datas: # 遍历所有传入的资产数据
        name = data["name"]
        path = data["path"]
        parsedName = UC.parseCameraName(name)
        if parsedName:
            assetPath = UC.applyMacro(UG.unrealConfig.CameraImportPathPatten,parsedName) # 应用宏替换
            wrapLevelSeq = WarpLevelSequence.create(assetPath,False)                     # 创建关卡序列
            wrapLevelSeq.setFrameRate(25)                                                # 设置帧率
            wrapLevelSeq.setPlayBackStart(int(parsedName["frameStart"]))
            wrapLevelSeq.setPlayBackEnd(int(parsedName["frameEnd"]))
            wrapLevelSeq.importCamera(path,UG.unrealConfig.CameraimportUniformScale)                                              # 导入相机
            templist = wrapLevelSeq.getBindingProxyAndObject(unreal.CineCameraActor)
            if not templist:
                unrealLogError("相机导入","从wrapLevelSeq上获取相机失败,相机属性设置失败")
                return False
            templist[0].set_name(name)                                                   # 重命名相机
            wrapCamera = WrapCineCameraActor(templist[1])
            wrapCamera.setFilmback(UC.FilmBackPreset.DSLR)
            wrapCamera.setFocusMethod(unreal.CameraFocusMethod.DISABLE)
            wrapCamera.setAspectRatio(UG.unrealConfig.CameraimportAspectRatio)

            wrapLevelSeq.setLock(True)                                                    # 锁定序列
            wrapLevelSeq.saveAsset()                                                      # 保存序列
        else:
            unrealLogError("相机导入",f"无法解析相机名称{name}")


def textureImport(texturePaths:list):
    wrapTex = WrapTexture.importTexture( texturePaths[0],UG.unrealConfig.TextureImportPathPatten)
    if not (wrapTex.setVTEnable(UG.unrealConfig.TextureEnableVT) and UG.unrealConfig.TextureEnableVT):
        UC.ConvertTexture.resizerTextures(texturePaths)
        wrapTex = WrapTexture.importTexture(texturePaths[0],UG.unrealConfig.TextureImportPathPatten)
    return wrapTex


def importStaticmeshs(datas:list,sceneName=None):
    saveAll()          # 保存所有资产,防止导入过程中崩溃
    duplicate_asset(UG.unrealConfig.SceneDefaultMaterial,UG.unrealConfig.LocalSceneDefaultMaterial)
    wrapMaterial = WrapMaterial(unreal.load_asset(UG.unrealConfig.LocalSceneDefaultMaterial))
    for data in datas: # 遍历所有传入的资产数据
        name = data["name"]
        path = data["path"]
        parseReslut = UC.parseStaticMeshName(name,sceneName)
        destinationPath = UC.applyMacro(UG.unrealConfig.StaticMeshImportPathPatten,parseReslut)
        wrapSM = WrapStaticMesh.importFromFbx(path,destinationPath,1) #导入静态网格体
        JsonPath = path.replace('.fbx','.json')
        Json_file = UC.ReadJsonFile(JsonPath)
        MaterialInfoList = UC.analyseJson(Json_file)
        for MaterialInfo in MaterialInfoList:
            # 判断是否创建材质
            if not MaterialInfo['CreateMaterial']:
                continue
            wrapMaterialIns = WrapMaterialInstance.create(UG.unrealConfig.MaterialInstancePath + MaterialInfo["Materialname"])
            wrapMaterialIns.setParent(wrapMaterial.asset)
            TexturePath = MaterialInfo['TexturePath']
            if TexturePath['diffuse_color'] != None:
                wrapBaseColor = textureImport(TexturePath['diffuse_color'])
                wrapBaseColor.setAsColor()
                wrapBaseColor.saveAsset()
                wrapMaterialIns.setTextureParameter("BaseColor_Map",wrapBaseColor.asset)

            if TexturePath['refl_roughness'] == None:
                ARMSPath = TexturePath['refl_metalness']
            else:
                ARMSPath = TexturePath['refl_roughness']
            WrapARMS = textureImport(ARMSPath)
            WrapARMS.setAsLinerColor()
            WrapARMS.saveAsset()
            wrapMaterialIns.setTextureParameter("ARMS_Map",WrapARMS.asset)
            
            
            if TexturePath['bump_input'] != None:
                wrapNormal = textureImport(TexturePath['bump_input'])
                wrapNormal.setAsNormal()
                wrapNormal.saveAsset()
                wrapMaterialIns.setTextureParameter("Normal_Map",wrapNormal.asset)

            if TexturePath['emission_color'] != None:
                WrapEmissive = textureImport(TexturePath['emission_color'])
                WrapEmissive.setAsColor()
                WrapEmissive.saveAsset()
                wrapMaterialIns.setTextureParameter("Emmissive_Map",wrapNormal.asset)
                wrapMaterialIns.setScalarParameter("自发光强度",1.0)
            wrapMaterialIns.saveAsset()
            wrapSM.setMaterialBySloatName(MaterialInfo["Materialname"],wrapMaterialIns.asset)
        wrapSM.saveAsset()