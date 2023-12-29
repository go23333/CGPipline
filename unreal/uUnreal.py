#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################
import time
import unreal


from CGUtils.uCommon import log_function_call


#获取一些subsystem
editorActorSubsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
staticMeshEditorSubsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
assetEditorSubsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
levelEditroSubsystenm = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

# 定义一些包裹类


class WarpBaseAsset():
    def __init__(self,asset) -> None:
        self.asset = asset
    def saveAsset(self,onlyIfIsDirty = True):
        unreal.EditorAssetLibrary.save_loaded_asset(self.asset,onlyIfIsDirty)


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
def unrealLog(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log(logstring)

def unrealLogWarning(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log_warning(logstring)

def unrealLogError(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log_error(logstring)

@log_function_call
def openSelectedFoliage():
    includeMode = unreal.RMAFoliageToolsIncludeMode.RMAIM_SELECTION
    buffer = unreal.RMAFoliageToolsFunctionLibrary.create_buffer(includeMode,False)
    assetEditorSubsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    assetEditorSubsystem.open_editor_for_assets([unreal.SystemLibrary.conv_soft_obj_path_to_soft_obj_ref(buffer.assets[0])])

@log_function_call
def FoliageToSMActor():
    IncludeMode = unreal.RMAFoliageToolsIncludeMode.RMAIM_SELECTION
    unreal.RMAFoliageToolsFunctionLibrary.foliage_ins_to_sm_actor(IncludeMode,True)


@log_function_call
def appendWindowToUnreal(winID:int):
    unrealLog("ZynnPipline",f"窗口{winID}已经注册到引擎中")
    unreal.parent_external_window_to_slate(winID)

@log_function_call
def FilterObjects(Actors:list,Filters:list):
    Resoult = []
    for Filter in Filters:
        Resoult = Resoult + list(unreal.EditorFilterLibrary.by_class(Actors,Filter))
    return Resoult

@log_function_call
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

@log_function_call
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
@log_function_call
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
    levelEditroSubsystenm.save_all_dirty_levels()
        


def poolSize(value=0):
    unreal.SystemLibrary.execute_console_command(editorActorSubsystem.get_world(),f"r.Streaming.PoolSize {value}")

def popEmmissive():
    
    pass

def openImportCameraUI():
    pass

def nearClip(value:float):
    unreal.SystemLibrary.execute_console_command(editorActorSubsystem.get_world(),f'r.SetNearClipPlane {value}')