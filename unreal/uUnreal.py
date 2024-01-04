#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################
import time
import unreal
from importlib import reload 


import CGUtils.uCommon as UC
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

class WarpBaseAsset():
    def __init__(self,asset) -> None:
        self.asset = asset
    def saveAsset(self,onlyIfIsDirty = True):
        unreal.EditorAssetLibrary.save_loaded_asset(self.asset,onlyIfIsDirty)


class WarpLevelSequence(WarpBaseAsset):
    def __init__(self,asset:unreal.LevelSequence) -> None:
        super().__init__(asset)
        self.asset:unreal.LevelSequence
    def setFrameRate(self,frameRate):
        frameRate = unreal.FrameRate(frameRate,1)
        self.asset.set_display_rate(frameRate)
    def getFBXImportSettings(self,CreateCamera:bool):
        importSettings = unreal.MovieSceneUserImportFBXSettings()
        importSettings.set_editor_property("convert_scene_unit",True)
        importSettings.set_editor_property("create_cameras",CreateCamera)
        importSettings.set_editor_property("force_front_x_axis",False)
        importSettings.set_editor_property("import_uniform_scale",UG.globalConfig.CameraimportUniformScale)
        importSettings.set_editor_property("match_by_name_only",False)
        importSettings.set_editor_property("reduce_keys",False)
        importSettings.set_editor_property("replace_transform_track",True)
        return importSettings
    def importSpawnableCamera(self,fbxPath:str,CameraName:str):
        LSBL = unreal.LevelSequenceEditorBlueprintLibrary()
        LSBL.open_level_sequence(self.asset)

        tools = unreal.SequencerTools() 
        importFbxSettings = self.getFBXImportSettings(False)
        bindingProxy,CinCameraActor=levelSequenceEditorSubsystem.create_camera(True)
        wrapCinCamera = WrapCineCameraActor(CinCameraActor)
        wrapCinCamera.setLabel(CameraName)

        world = unrealEditorSybsystem.get_editor_world()
        if world == None:
            unrealLogError("导入摄像机","获取当前世界失败")
        else:
            tools.import_level_sequence_fbx(world,self.asset,[bindingProxy],importFbxSettings,fbxPath)
        LSBL.close_level_sequence()

    def addCameraCutTrack(self,ID):
        cameraCutTrack = self.asset.add_master_track(unreal.MovieSceneCameraCutTrack)
        cameraCutScetion = cameraCutTrack.add_section()
        cameraCutScetion:unreal.MovieSceneCameraCutSection
        cameraCutScetion.set_camera_binding_id(ID)
        cameraCutScetion.set_start_frame(self.frameStart - 50)
        cameraCutScetion.set_end_frame(self.frameEnd + 50)
    def setLock(self,Lock:bool):
        LSBL = unreal.LevelSequenceEditorBlueprintLibrary()
        LSBL.open_level_sequence(self.asset)
        LSBL.set_lock_level_sequence(Lock)
        LSBL.close_level_sequence()
        unrealLog("锁定/解锁关卡序列",f"序列{self.asset.get_name()}的锁定状态设置为{Lock}")
    def deleteOldCameraBindings(self):
        '''
        删除已经存在在关卡序列上的相机
        '''
        #获取Trac并删除cameraCutTrack
        # for track in self.asset.get_tracks():
        #     if type(track) == unreal.MovieSceneCameraCutTrack:
        #         for section in track.get_sections():
        #             track.remove_section(section)
        #         self.asset.remove_track(track)
        
        cameraActor = self.getBindingCamera()

        bindings = unreal.MovieSceneSequenceExtensions.get_bindings(self.asset)
        for binding in bindings:

            for obj in binding.bound_objects:
                if type(obj) == unreal.CineCameraActor:
                    binding.binding_proxy.remove()
                elif type(obj) == unreal.CineCameraComponent:
                    binding.binding_proxy.remove()
                elif type(obj) == unreal.MovieSceneCameraCutTrack:
                    binding.binding_proxy.remove()

    def getBindingCamera(self):
        '''
        获取绑定在关卡序列上的首个相机包裹
        '''
        spawnables = self.asset.get_spawnables()
        for spawnable in spawnables:
            obj = spawnable.get_object_template()
            if type(obj) == unreal.CineCameraActor:
                unrealLog("获取序列上的相机Actor",f"从{self.asset.get_name()}上获取到相机{obj.get_name()}")
                return(WrapCineCameraActor(obj))
        unrealLogWarning("获取序列上的相机Actor",f"序列{self.asset.get_name()}上不存在相机")
        return False
    def setPlaybackRange(self):
        self.asset.set_playback_start(int(self.frameStart))
        self.asset.set_playback_end(int(self.frameEnd)+1)
    @classmethod
    def create(cls,assetPath:str,deleteExist:bool=True):
        if unreal.EditorAssetLibrary.does_asset_exist(assetPath) and deleteExist:
            unrealLogWarning("序列创建",f"序列{assetPath}已经存在需要删除")
            unreal.EditorAssetLibrary.delete_asset(assetPath)
            unrealLogWarning("序列创建",f"序列{assetPath}已经删除")
        if unreal.EditorAssetLibrary.does_asset_exist(assetPath) and not deleteExist:
            warpLevelSequence = WarpLevelSequence(unreal.EditorAssetLibrary.load_asset(assetPath)) #包裹现有的相机
            warpLevelSequence.setLock(False)             #解锁相机
            warpLevelSequence.deleteOldCameraBindings()  #删除序列上原有的相机
            return warpLevelSequence
        return(WarpLevelSequence(createGerericAsset(assetPath,False,unreal.LevelSequence,unreal.LevelSequenceFactoryNew())))
class WarpStaticMesh(WarpBaseAsset):
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
        self.component:unreal.CineCameraComponent
        self.actor:unreal.CineCameraActor
    def setFilmback(self,preset:str):
        self.component.set_filmback_preset_by_name(preset)
    def setFocusMethod(self,method:unreal.CameraFocusMethod):
        Currentfocussettings = self.component.focus_settings
        Currentfocussettings.focus_method = method
        self.component.focus_settings = Currentfocussettings
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
    def getStaticmesh(self)->WarpStaticMesh:
        return WarpStaticMesh(self.component.static_mesh)
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

def importCameras(datas:dict):
    saveAll()          # 保存所有资产,防止导入过程中崩溃
    for data in datas: # 遍历所有传入的资产数据
        name = data["name"]
        path = data["path"]
        parsedName = UC.parseCameraName(name)
        if parsedName:
            assetPath = UC.applyMacro(UG.globalConfig.CameraImportPathPatten,parsedName)
            wrapLevelSeq = WarpLevelSequence.create(assetPath,True)
            wrapLevelSeq.setFrameRate(25)
            wrapLevelSeq.importSpawnableCamera(path,parsedName["fullName"])
            # wrapLevelSeq.setPlaybackRange()
            # wrapCameraActor = WrapCineCameraActor(wrapLevelSeq.getBindingCameraActor())
            # wrapCameraActor.setFilmback(UC.FilmBackPreset.DSLR)
            # wrapCameraActor.setFocusMethod(unreal.CameraFocusMethod.DISABLE)
            # wrapLevelSeq.setLock(True)
            # wrapLevelSeq.saveAsset()
        else:
            unrealLogError("相机导入",f"无法解析相机名称{name}")
