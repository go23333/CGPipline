# -*- coding: utf-8 -*-
import unreal
import openpyxl as op
import hashlib
import shutil
import os
import json
import requests
import getpass
import importlib

from UnrealPipeline.core.Config import globalConfig
import UnrealPipeline.core.Config as UC
importlib.reload(UC)


from Qt import QtCore
from Qt import QtWidgets

from Qt.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                             QPushButton, QPlainTextEdit, QDialog, 
                             QDialogButtonBox,QLabel)


editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_sequence_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
layers_subsystem = unreal.get_editor_subsystem(unreal.LayersSubsystem)
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


class GroomAbcImport():
    # @classmethod
    # def groomImport(cls,file_path,des_path,start_frame,end_frame):
    #     groom_task=cls.buildImportTask(file_path,des_path,cls.buildGroomImportOptions(start_frame,end_frame))
    #     unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([groom_task])
        
    @classmethod
    def buildImportTask(cls,file_path,destination_path,options=None,automated=True):
        task=unreal.AssetImportTask()
        task.set_editor_property('automated',automated)
        task.set_editor_property('destination_name','')
        task.set_editor_property('destination_path',destination_path)
        task.set_editor_property('filename',file_path)
        task.set_editor_property('replace_existing',True)
        task.set_editor_property('save',True)
        task.set_editor_property('options',options)
        return task

    @classmethod
    def buildGroomImportOptions(cls):

        options=unreal.GroomImportOptions()

        options.conversion_settings = unreal.GroomConversionSettings(rotation=[90.0, 0.0, 0.0],scale=[1.0, -1.0, 1.0])


        return options
    
    @classmethod
    def buildGroomCacheImportOptions(cls,groom_asset_soft,start_frame,end_frame,groom_type=unreal.GroomCacheImportType.STRANDS):
        options=unreal.GroomCacheImportOptions()
        

        options.import_settings.import_groom_asset=False
        options.import_settings.groom_asset=groom_asset_soft

        #是否导入cache
        options.import_settings.import_groom_cache=True

        #只导入STRANDS
        options.import_settings.import_type=groom_type

        #设置导入的起始结束帧
        options.import_settings.frame_start=start_frame
        options.import_settings.frame_end=end_frame
        
        conversion_settings = unreal.GroomConversionSettings()
        conversion_settings.rotation = unreal.Vector(90.0, 0.0, 0.0)
        conversion_settings.scale = unreal.Vector(1.0, -1.0, 1.0)

        options.import_settings.conversion_settings = conversion_settings


        return options
    
class ClothAbcImport():
    # @classmethod
    # def groomImport(cls,file_path,des_path,start_frame,end_frame):
    #     groom_task=cls.buildImportTask(file_path,des_path,cls.buildGroomImportOptions(start_frame,end_frame))
    #     unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([groom_task])
        
    @classmethod
    def buildImportTask(cls,file_path,destination_path,options=None,automated=True):
        task=unreal.AssetImportTask()
        task.set_editor_property('automated',automated)
        task.set_editor_property('destination_name','')
        task.set_editor_property('destination_path',destination_path)
        task.set_editor_property('filename',file_path)
        task.set_editor_property('replace_existing',True)
        task.set_editor_property('save',True)
        task.set_editor_property('options',options)
        return task

    @classmethod
    def buildClothImportOptions(cls,frame_start=None,frame_end=None):

        options = unreal.AbcImportSettings()

        options.import_type = unreal.AlembicImportType.GEOMETRY_CACHE

        sampling_settings=unreal.AbcSamplingSettings()
        if frame_start is not None:
            sampling_settings.frame_start = frame_start
        if frame_end is not None:
            sampling_settings.frame_end = frame_end
        sampling_settings.sampling_type = unreal.AlembicSamplingType.PER_FRAME

        options.sampling_settings = sampling_settings

        conversion_settings = unreal.AbcConversionSettings()
        conversion_settings.rotation = unreal.Vector(90.0, 0.0, 0.0)
        conversion_settings.scale = unreal.Vector(1.0, -1.0, 1.0)

        options.conversion_settings = conversion_settings

        material_settings = unreal.AbcMaterialSettings()
        material_settings.create_materials = False

        options.material_settings = material_settings

        options.geometry_cache_settings.apply_constant_topology_optimizations = True




        return options
    



class fbxImport():
    
    @classmethod
    def staticMeshImport(cls,fbx,fbx_create_path):
        sataic_mesh_task=cls.buildImportTask(cls,fbx,fbx_create_path,cls.buildStaticMeshImportOptions(cls))
        cls.executeImportTasks(cls,[sataic_mesh_task])
    
    @classmethod
    def skeletonMeshImport(cls,fbx,fbx_create_path,parent_skmesh=None):
        sataic_mesh_task=cls.buildImportTask(cls,fbx,fbx_create_path,cls.buildSkeletonMeshImportOptions(cls,parent_skmesh=parent_skmesh))
        cls.executeImportTasks(cls,[sataic_mesh_task])

    @classmethod
    def skeletonMeshImport574(cls,fbx,fbx_create_path,parent_skmesh=None):
        interchange_manager = unreal.InterchangeManager.get_interchange_manager_scripted()
        source_data = interchange_manager.create_source_data(fbx)

        import_asset_parameters = cls.buildSkeletonMeshAssetsPipeline(cls,parent_skmesh=parent_skmesh)
        interchange_manager.import_asset(fbx_create_path, source_data, import_asset_parameters)


    @classmethod
    def animSequenceImport(cls,fbx,fbx_create_path,skeleton_mesh):
        anim_sequence_task=cls.buildImportTask(cls,fbx,fbx_create_path,cls.buildAnimSequenceImportOptions(cls,skeleton_mesh))
        cls.executeImportTasks(cls,[anim_sequence_task])

    @classmethod
    def matICreate(cls,Common_path,fbx_path,matI_tar_path,mat_switch):

        mats=unreal.EditorAssetLibrary.list_assets(Common_path)
        fbx_objs=unreal.EditorAssetLibrary.list_assets(fbx_path)

        fbx_mat_list=[]
        fbx_assets=[]

        
        for fbx_mat in fbx_objs:
            asset=unreal.EditorAssetLibrary.find_asset_data(fbx_mat).get_asset()
            asset_info=unreal.EditorAssetLibrary.find_asset_data(fbx_mat)
            fbx_obj_class=asset_info.asset_class_path.asset_name

            #获取mesh  
            if fbx_obj_class=='StaticMesh':
                fbx_assets.append(asset)
        #创建材质实例并赋予模型
        # for fbx_asset in fbx_assets:
            #获取所有材质插槽名称
        mesh_mats = fbx_assets[0].get_editor_property('static_materials')
        for mesh_mat in mesh_mats:
            fbx_mat_list.append(str(mesh_mat.get_editor_property('material_slot_name')))

        
        for mat in mats:
            mat_asset=unreal.EditorAssetLibrary.find_asset_data(mat).get_asset()
            mat_name=mat_asset.get_name()
            if mat_name=='MaterialBlender':
                mat_blend_asset = mat_asset
                break
            
        #遍历common文件夹内的材质母球
        for mat in mats:
            mat_asset=unreal.EditorAssetLibrary.find_asset_data(mat).get_asset()
            mat_info=unreal.EditorAssetLibrary.find_asset_data(mat)
            mat_class=mat_info.asset_class_path.asset_name
            mat_name=mat_asset.get_name()
            if mat_name=='MaterialBlender':
                mat_blend_asset = mat_asset
            
            #判断asset类型是否为材质或材质实例
            if mat_class=='Material' or mat_class=='MaterialInstanceConstant':
                # print(mat_name)
                #遍历模型材质
                for fbx_mat in fbx_mat_list:
                    if mat_switch or not editor_asset_subsystem.does_asset_exist(matI_tar_path+'/'+fbx_mat):
                        # #删除旧材质
                        # try:
                        #     if unreal.EditorAssetSubsystem().does_asset_exist(matI_tar_path+'/'+fbx_mat):
                        #         unreal.EditorAssetLibrary.delete_asset(matI_tar_path+'/'+fbx_mat)
                        # except:
                        #     pass
                        #材质球生成开关，生成材质球后值为1
                        switch=0
                        #判断材质后缀名称是否对应，对应后创建对应材质球
                        if 'BoLiTi' in fbx_mat:
                            if mat_name=='M_CH_EyeOcclusion':
                                matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                matI_create.set_editor_property('parent',mat_asset)
                                switch=1
                            else:
                                continue
                        
                        elif 'YanJian' == fbx_mat.rsplit('_')[-1] :
                            if mat_name=='M_lacrimal_fluid':
                                matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                matI_create.set_editor_property('parent',mat_asset)
                                switch=1
                            else:
                                continue
                        

                        elif 'YanQiu' in fbx_mat :
                            if mat_name=='M_CH_YanQiu':
                                matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                matI_create.set_editor_property('parent',mat_asset)
                                switch=1
                            else:
                                continue
                        
                        elif 'KouQiang' in fbx_mat :
                            if mat_name=='M_CH_KouQiang':
                                matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                matI_create.set_editor_property('parent',mat_asset)
                                switch=1
                            else:
                                continue
                        
                        elif 'JieMao' in fbx_mat :
                            if mat_name=='M_CH_JieMao':
                                matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                matI_create.set_editor_property('parent',mat_asset)
                                switch=1
                            else:
                                continue

                        elif 'YanJian_TouMing' in fbx_mat :
                            if mat_name=='Hide_Mask':
                                matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                matI_create.set_editor_property('parent',mat_asset)
                                switch=1
                            else:
                                continue

                        elif 'MeiMao' in fbx_mat :
                            if mat_name=='M_CH_JieMao':
                                matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                matI_create.set_editor_property('parent',mat_asset)
                                switch=1
                            else:
                                continue

                        #判断材质球类型为皮肤时,使用MI_MaterialBlender_Skin材质球
                        elif 'skin' in fbx_mat.lower() :
                            if mat_name=='MaterialBlender':
                                matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                matI_create.set_editor_property('parent',mat_asset)
                                # matI_create = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(asset_name=fbx_obj,package_path=matI_tar_path,original_object=mat_asset)
                                switch=1
                            else:
                                continue
                        

                        elif '_hair' in fbx_mat.lower() :
                            #防止重复生成毛发材质球
                            if not editor_asset_subsystem.does_asset_exist(matI_tar_path+'/'+fbx_mat):
                                if mat_name=='M_Hair_Slice':
                                    matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                                    matI_create.set_editor_property('parent',mat_asset)
                                    switch=1
                                else:
                                    matI_create = editor_asset_subsystem.find_asset_data(matI_tar_path+'/'+fbx_mat).get_asset()
                                    switch=1
                            else:
                                continue

                        #其他材质球统一使用MI_MaterialBlender_Cloth材质球
                        elif not editor_asset_subsystem.does_asset_exist(matI_tar_path+'/'+fbx_mat) and mat_name=='MaterialBlender':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)

                            # matI_create = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(asset_name=fbx_obj,package_path=matI_tar_path,original_object=mat_asset)
                            switch=1

                        # mesh_mats = fbx_assets[0].get_editor_property('static_materials')
                        # for mesh_mat in mesh_mats:
                        #     fbx_mat_list.append(str(mesh_mat.get_editor_property('material_slot_name')))
                        
                        # print(mat_name)
                        #替换模型材质球
                        if switch==1:
                            fbx_asset = fbx_assets[0]
                            i=0
                            
                            while i<1024:
                                try:
                                    # mesh_index_mat=unreal.StaticMesh.get_material(fbx_asset,i)
                                    #对比材质球和材质插槽名称
                                    mesh_index_mat = fbx_mat_list[i]
                                    if mesh_index_mat==matI_create.get_name():
                                        unreal.StaticMesh.set_material(fbx_asset,i,matI_create)
                                        print(mesh_index_mat,matI_create.get_name())
                                except:
                                    break
                                if mesh_index_mat==None:
                                    break
                                i+=1
                        
        #删除旧材质
        cls.deletOldMat(cls,fbx_path)

        # unreal.EditorAssetLibrary.save_directory('/Game')

        cls.giveTexture(fbx_assets,mat_switch)

    @classmethod
    def importTexture(cls,texture_dict:dict,destination_path,tex_switch):
        
        texture_objs=[]
        base_color_path=''
        for shade_name,type_dict in texture_dict.items():
            for texture_type,textures in type_dict.items():
                if textures:      
                    texture =textures[0]
                    #获取无UDIM后缀的贴图路径
                    base_color_path=destination_path+'/'+texture.rsplit('/',1)[-1].split('.')[0]
                    #构建贴图导入任务
                    if tex_switch or not editor_asset_subsystem.does_asset_exist(base_color_path):
                        task=cls.buildImportTask(cls,texture,destination_path)
                        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
                        
                        
                        if editor_asset_subsystem.does_asset_exist(base_color_path):
                            texture_obj:unreal.Texture2D
                            texture_obj=unreal.EditorAssetLibrary.load_asset(base_color_path)
                            texture_obj.set_editor_property("virtual_texture_streaming",1)

                            if texture_type=='c':
                                texture_obj.compression_settings = unreal.TextureCompressionSettings.TC_DEFAULT
                                texture_obj.srgb = True

                            elif texture_type=='e':
                                texture_obj.compression_settings = unreal.TextureCompressionSettings.TC_DEFAULT
                                texture_obj.srgb = True

                            elif texture_type=='n':
                                texture_obj.compression_settings = unreal.TextureCompressionSettings.TC_NORMALMAP
                                texture_obj.srgb = False

                            elif texture_type=='arms':
                                texture_obj.compression_settings = unreal.TextureCompressionSettings.TC_MASKS
                                texture_obj.srgb = False

                            elif texture_type=='sp':
                                texture_obj.compression_settings = unreal.TextureCompressionSettings.TC_DEFAULT
                                texture_obj.srgb = True
                            
                            texture_objs.append(texture_obj)

        # unreal.EditorAssetLibrary.save_directory('/Game/Assets/Character')

        #打开所有贴图资产以确保贴图正常更新
        unreal.AssetToolsHelpers.get_asset_tools().open_editor_for_assets(texture_objs)



    @classmethod
    def giveTexture(cls,meshs,mat_switch):
        #创建存有材质球和贴图类型信息的字典
        cloth_link_dict={'ARMS':'ARMS_Map','BaseColor':'BaseColor_Map','Normal':'Normal_Map','BaseNormal':'BaseNormalMap','Anisotropy':'Anisotropy_Map','Emmissive':'Emmissive_Map'}
        skin_link_dict={'ARMS':'ARMS','BaseColor':'BaseColor','Normal':'NormalMap','DetailNormal':'DetailMap','Specular':'SpecularMap','Roughness':'ARMS','CV':'Cavity_MAIN','SSSMask':'SSSMask'}
        all_link_dict={'skin':skin_link_dict,'cloth':cloth_link_dict}
        for mesh in meshs:
            #判断mesh类型是否为静态网格
            if mesh.get_class().get_name()=='StaticMesh':
                mesh:unreal.StaticMesh
                #遍历所有贴图文件
                texture_assets=[]
                Texture_path=mesh.get_path_name().rsplit('/',2)[0]+'/Texture'
                Texture_assets_data=unreal.EditorAssetLibrary.list_assets(Texture_path)
                for Texture_asset_data in Texture_assets_data:
                    #写入列表
                    texture_assets.append(unreal.EditorAssetLibrary.find_asset_data(Texture_asset_data).get_asset())
                #遍历mesh材质球
                i=0
                while i<127:
                    mesh_index_mat=unreal.StaticMesh.get_material(mesh,i)
                    if mesh_index_mat and mesh_index_mat.get_class().get_name()=='MaterialInstanceConstant':
                        #获取父级材质球
                        parent_mat=mesh_index_mat.get_editor_property('parent')
                        mesh_index_mat_name = mesh_index_mat.get_name().lower()
                        if '_skin' in mesh_index_mat_name:
                            mat_type = 'skin'
                        else:
                            mat_type = 'cloth'

                        #遍历贴图
                        for texture_asset in texture_assets:
                            #判断贴图关键字是否与模型的材质关键字对应
                            if texture_asset.get_name().split('_')[-2]==mesh_index_mat.get_name().split('_')[-1]:
                                # print(texture_asset.get_name())
                                #遍历材质参数字典内容
                                for mat,parameter_dict in all_link_dict.items():
                                    # if parent_mat.get_name()==mat:
                                    if mat == mat_type:
                                        for tex_class,parameter_name in parameter_dict.items():
                                            #不区分大小写判断贴图后缀名是否与贴图类型对应
                                            if texture_asset.get_name().split('_')[-1].lower()==tex_class.lower():
                                                #判断材质的贴图内容是否已存在,不存在或开启替换材质时则添加贴图到材质中
                                                if not unreal.MaterialEditingLibrary.get_texture_parameter_source(mesh_index_mat,'BaseColor_Map') or mat_switch:
                                                    #为材质球赋予贴图，类型选择为LAYER_PARAMETER
                                                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mesh_index_mat,parameter_name,texture_asset,association=unreal.MaterialParameterAssociation.LAYER_PARAMETER)
                                            

                    if not mesh_index_mat:
                        break
                    i+=1


    def deletOldMat(self,asset_path):                            
        del_mats=unreal.EditorAssetLibrary.list_assets(asset_path)
        for del_mat in del_mats:
            mat_class=unreal.EditorAssetLibrary.find_asset_data(del_mat).asset_class_path.asset_name
            if mat_class=='Material':
                unreal.EditorAssetLibrary.delete_asset(del_mat)

    #fbx导入设置
    def buildStaticMeshImportOptions(self):
        options=unreal.FbxImportUI()
        options.set_editor_property('import_mesh',True)
        options.set_editor_property('import_textures',False)
        options.set_editor_property('import_materials',True)
        options.set_editor_property('import_as_skeletal',False)

        options.static_mesh_import_data.set_editor_property('import_translation',unreal.Vector(0,0,0))
        options.static_mesh_import_data.set_editor_property('import_rotation',unreal.Rotator(0,0,0))
        options.static_mesh_import_data.set_editor_property('import_uniform_scale',1)

        options.static_mesh_import_data.set_editor_property('combine_meshes',True)
        options.static_mesh_import_data.set_editor_property('generate_lightmap_u_vs',True)
        options.static_mesh_import_data.set_editor_property('auto_generate_collision',True)

        return options
    
    #fbx导入设置
    def buildSkeletonMeshImportOptions(self,parent_skmesh=None):
        

        options=unreal.FbxImportUI()

        if parent_skmesh:
            options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
            skeleton = parent_skmesh.get_editor_property("skeleton")
            options.skeleton = skeleton
            options.import_mesh = True
            options.import_textures = False
            options.import_materials = False
            options.import_as_skeletal = True

        else:
            options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
            options.import_mesh = True
            options.import_textures = False
            options.import_materials = False
            options.import_as_skeletal = False
            options.create_physics_asset = True
        

        skeletal_mesh_import_data = unreal.FbxSkeletalMeshImportData()
        skeletal_mesh_import_data.set_editor_property('import_translation',unreal.Vector(0,0,0))
        skeletal_mesh_import_data.set_editor_property('import_rotation',unreal.Rotator(0,0,0))
        skeletal_mesh_import_data.set_editor_property('import_uniform_scale',1.0)

        skeletal_mesh_import_data.set_editor_property('use_t0_as_ref_pose',True)
        skeletal_mesh_import_data.set_editor_property('import_morph_targets',True)        
        skeletal_mesh_import_data.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS       

        options.skeletal_mesh_import_data = skeletal_mesh_import_data


        return options

    def buildSkeletonMeshAssetsPipeline(self,parent_skmesh=None):

        import_asset_parameters = unreal.ImportAssetParameters()
        # import_asset_parameters.is_automated = False          # 不弹出导入对话框
        # import_asset_parameters.replace_existing = True      # 替换已存在的资源


        # assets_pipeline = unreal.InterchangeGenericAssetsPipeline()

        # # assets_pipeline.import_offset_translation = unreal.Vector(0,0,0)
        # # assets_pipeline.import_offset_rotation = unreal.Rotator(0,0,0)


        # assets_pipeline.mesh_pipeline.import_skeletal_meshes = True
        # assets_pipeline.mesh_pipeline.create_physics_asset = True
        # assets_pipeline.mesh_pipeline.import_morph_targets = True

        # assets_pipeline.material_pipeline.import_materials = False
        # assets_pipeline.material_pipeline.texture_pipeline.import_textures = False

        # assets_pipeline.common_meshes_properties.force_all_mesh_as_type = unreal.InterchangeForceMeshType.IFMT_SKELETAL_MESH
        # assets_pipeline.common_meshes_properties.use_full_precision_u_vs = True

        # sk_mesh_props = assets_pipeline.common_skeletal_meshes_and_animations_properties
        # sk_mesh_props.use_t0_as_ref_pose = True

        # # 如果存在 parent_skmesh，复用其骨骼
        # if parent_skmesh:
        #     skeleton = parent_skmesh.get_editor_property("skeleton")
        #     sk_mesh_props.skeleton = skeleton


        # import_asset_parameters.override_pipelines.append(unreal.SoftObjectPath(assets_pipeline.get_path_name()))

        return import_asset_parameters

    
    def buildAnimSequenceImportOptions(self,skeleton_mesh):
        options=unreal.FbxImportUI()

        #动画序列导入设置
        options.automated_import_should_detect_type=False
        options.mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION
        options.import_mesh=False
        options.import_animations=True
        options.skeleton=skeleton_mesh
        options.create_physics_asset=False
        

        options.import_materials=False
        options.import_textures=False
        options.import_as_skeletal=False

        options.anim_sequence_import_data.set_editor_property('animation_length',unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        options.anim_sequence_import_data.set_editor_property('import_translation',unreal.Vector(0,0,0))
        options.anim_sequence_import_data.set_editor_property('import_rotation',unreal.Rotator(0,0,0))
        options.anim_sequence_import_data.set_editor_property('import_uniform_scale',1)

        options.anim_sequence_import_data.set_editor_property('import_meshes_in_bone_hierarchy',True)
        options.anim_sequence_import_data.set_editor_property('import_bone_tracks',True)
        options.anim_sequence_import_data.set_editor_property('remove_redundant_keys',True)
        options.anim_sequence_import_data.set_editor_property('do_not_import_curve_with_zero',True)
        options.anim_sequence_import_data.set_editor_property('convert_scene',True)
        options.anim_sequence_import_data.set_editor_property('convert_scene',True)

     

        return options
    
    #导入任务创建
    def buildImportTask(self,file_path,destination_path,options=None):
        task=unreal.AssetImportTask()
        task.set_editor_property('automated',True)
        task.set_editor_property('destination_name','')
        task.set_editor_property('destination_path',destination_path)
        task.set_editor_property('filename',file_path)
        task.set_editor_property('replace_existing',True)
        task.set_editor_property('save',True)
        task.set_editor_property('options',options)
        return task
    
    def executeImportTasks(self,task):
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(task)




class CacheImportTool():
    
    def listClassAsset(cls,path,class_name):

        assets=[]
        if unreal.EditorAssetLibrary.does_directory_exist(path):
            asset_list=unreal.EditorAssetLibrary.list_assets(path)
            for asset_info in asset_list:
                asset_class=unreal.EditorAssetLibrary.find_asset_data(asset_info).get_class().get_name()
                asset=unreal.EditorAssetLibrary.find_asset_data(asset_info).get_asset()

                if '_BD' in asset.get_name() and asset_class==class_name:
                    assets.append(asset)

        return assets
    
    def groomCacheToChDirectory(cls,abc_path,main_path):
        asset_basename=abc_path.split('/')[-1].split('_',3)[3].rsplit('_',3)[0]
        if unreal.EditorAssetLibrary.does_directory_exist(main_path+asset_basename):
            ch_base_path=main_path+asset_basename
            return ch_base_path
        else:
            return False

    def __groomLocateToCh(cls,groom_actor:unreal.Actor, ch_actor:unreal.Actor, bone_name:str):
        
        # all_actors = actor_subsystem.get_all_level_actors()
        # groom_actor = next((a for a in all_actors if a.get_actor_label() == groom_actor_name), None)
        # mesh_actor = next((a for a in all_actors if a.get_actor_label() == mesh_actor_name), None)

        # if not groom_actor or not mesh_actor:
        #     unreal.log_warning("未找到 Actor，请检查 Label 名称。")
        #     return
                
        # groom_actor = unreal.EditorActorSubsystem().get_selected_level_actors()[0]
        # ch_actor = unreal.EditorActorSubsystem().get_selected_level_actors()[1]
        # bone_name = 'Root_M'

        mesh_comp = ch_actor.get_component_by_class(unreal.SkeletalMeshComponent)
        
        if mesh_comp:
            bone_transform = mesh_comp.get_socket_transform(unreal.Name(bone_name), unreal.RelativeTransformSpace.RTS_WORLD)
            
            # 在 Rotator 中，修正坐标
            current_bone_rot = bone_transform.rotation.rotator()
            groom_actor_rot = groom_actor.get_actor_rotation()
            if bone_name == 'Head_M' :
                local_correction = unreal.Rotator(pitch=90.0, yaw=180.0, roll=0.0)
            elif bone_name == 'head':
                local_correction = unreal.Rotator(pitch=-90.0, yaw=0.0, roll=0.0)

            final_rot = unreal.MathLibrary.compose_rotators(local_correction, current_bone_rot)
            final_rot = unreal.MathLibrary.compose_rotators(final_rot, groom_actor_rot)
            
            groom_actor.set_actor_location(bone_transform.translation, False, False)
            groom_actor.set_actor_rotation(final_rot, False)

            socket = unreal.Name(bone_name)
            groom_actor.attach_to_actor(parent_actor=ch_actor,socket_name=socket,location_rule=unreal.AttachmentRule.KEEP_WORLD,rotation_rule=unreal.AttachmentRule.KEEP_WORLD,scale_rule=unreal.AttachmentRule.KEEP_WORLD)
    
    def __bpRemoveGroom(cls,parent_actor):
        #清除角色bp中的groom资产
        # for i in range(3):
        #     groom_index = str(i+1)
        #     try:
        #         parent_actor.set_editor_property(f'Groom{groom_index}Asset',None)
        #         parent_actor.set_editor_property(f'Groom{groom_index}Binding',None)
        #     except:
        #         pass
        try:
            parent_actor.set_editor_property(f'Groom1Asset',None)
            parent_actor.set_editor_property(f'Groom1Binding',None)
            parent_actor.set_editor_property(f'Groom1Cache',None)
        except:
            pass


    @classmethod
    def groomToChActor(cls,cam_name,version = 1):   #1:踏星流程,0:财神流程
        ch_asset_path = UC.globalConfig.get().AssetPath + 'Character/'              #基础角色路径
        groom_actors = []
        parent_actors = []
        cam_split = cam_name.split('_')
        ep = cam_split[0]
        sc = cam_split[1]
        an_level_path = f'/Game/Shots/{ep}/{sc}/{cam_name}/Animation/{cam_name}_an_Map'
        an_level_asset_data = unreal.EditorAssetLibrary().find_asset_data(an_level_path)
        if unreal.EditorAssetLibrary().does_asset_exist(an_level_path):
            level_editor_subsystem.load_level(an_level_path)
            actors=editor_actor_subsystem.get_all_level_actors()
            #收集当前关卡内的角色和groom actor
            for act in actors:
                act:unreal.Actor
                if '_BD' in act.get_actor_label():
                    groom_actors.append(act)
                
                if '_AAI' in act.get_actor_label() or 'BP_CH_' in act.get_actor_label():
                    parent_actors.append(act)

            for parent_actor in parent_actors:
                if '_AAI' in parent_actor.get_actor_label():
                    parent_base_name = parent_actor.get_actor_label().split('_AAI')[0]
                elif 'BP_CH_' in parent_actor.get_actor_label():
                    parent_base_name = parent_actor.get_actor_label().split('BP_CH_')[-1]
                yd_folder_path = ch_asset_path+parent_base_name+'/Groom/YD_Hair'  #判断是否存在原点groom文件夹,不存在则使用角色文件夹
                if unreal.EditorAssetLibrary.does_directory_exist(yd_folder_path):
                    groom_asset_datas = assetFilter('GroomAsset',yd_folder_path)
                else:
                    if version == 0:
                        groom_asset_datas = None
                    elif version == 1:
                        groom_asset_datas = assetFilter('GroomAsset',ch_asset_path+parent_base_name)
                for groom_asset_data in groom_asset_datas:
                    if 'mesh' in assetDataToAssetPath(groom_asset_data).lower():    #当路径存在mesh时,跳过当前groom资产
                        continue
                    groom_asset = groom_asset_data.get_asset()
                    groom_asset_name = groom_asset.get_name()
                    groom_actor = None
                    if groom_actors:
                        for groom_act in groom_actors:
                            if groom_asset_name in groom_act.get_actor_label():
                                #当存在旧同名actor时删除旧actor并生成新actor
                                editor_actor_subsystem.destroy_actor(groom_act)
                    
                    if not groom_actor:
                        groom_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(groom_asset,unreal.Vector(0.0, 0.0, 0.0))
        
                    if parent_actor and groom_actor:
                        #适配骨骼
                        base_bones = ['Head_M','head']
                        socket_name = ''
                        skeletal_mesh_comp = parent_actor.get_component_by_class(unreal.SkeletalMeshComponent)
                        bone_num = skeletal_mesh_comp.get_num_bones()
                        #判断基础骨骼名称
                        for index in range(bone_num):
                            bone_name = skeletal_mesh_comp.get_bone_name(index)
                            if bone_name in base_bones:
                                socket_name = bone_name
                                break
                        cls.__groomLocateToCh(cls,groom_actor,parent_actor,socket_name)
                        
                        if version == 0:    #财神流程,删除角色bp中的groom资产
                            #删除角色bp中的groom资产
                            cls.__bpRemoveGroom(cls,parent_actor)


    @classmethod
    def groomToSequence574(cls,groom_cache_path,cache_seq,groom_type_index:int,groom_asset):   #groom_type_index     0:guid  1:strand
        asset_basename = groom_cache_path.split('/')[-1].split('.')[-1].split('_',3)[3].rsplit('_',5)[0]
        groom_asset_basename = groom_asset.get_name().split('_BD')[0]
        abc_asset=groom_cache_path.split('/')[-1]
        abc_split = abc_asset.split('_')
        base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'
        
        seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_hcache'   #动画序列路径,若不存在hcache则用cache路径
        if not unreal.EditorAssetLibrary.does_asset_exist(seq_path):
            seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_cache'
        cache_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取cache关卡序列
        #打开对应level
        level_path = base_path+f'{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_Map'
        an_level_path = base_path+f'Animation/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_an_Map'
        if unreal.EditorAssetSubsystem().does_asset_exist(an_level_path):
            unreal.LevelEditorSubsystem().load_level(an_level_path)
        else:
            unreal.LevelEditorSubsystem().load_level(level_path)
        #获取用于添加关卡序列的cache
        groom_cache=unreal.EditorAssetLibrary.find_asset_data(groom_cache_path).get_asset()
        
        #打开cache关卡序列
        unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(cache_seq)
        #sequence解锁
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(False)

        abc_asset_frame=groom_cache_path.split('_')[-4].rsplit('-',1)
        #获取cache的起始结束帧
        start_frame=int(abc_asset_frame[0])+UC.globalConfig.get().start_offset
        end_frame=int(abc_asset_frame[1])+UC.globalConfig.get().start_offset

        #获取当前打开的关卡序列
        current_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        possessables = current_sequence.get_possessables()
        frame_range = current_sequence.get_playback_range()
        frame_start = frame_range.get_start_frame()
        parent_actor = None
        groom_actor = None
        actors=editor_actor_subsystem.get_all_level_actors()
        print(asset_basename)
        for act in actors:
            act:unreal.Actor
            if act.get_actor_label().split('_AAI')[0] == asset_basename:
                parent_actor = act
                # break
            elif act.get_actor_label().split('BP_CH_')[-1] == asset_basename:
                parent_actor = act
                # break
            elif act.get_actor_label().split('_BD')[0] == groom_asset_basename:
                groom_actor = act
            
        bp_exist = False
        groom_bp_exist = False
        #当不存在角色bp时将level的bp actor添加到cache sequence中
        for possessable in possessables:
            #获取bp名称
            try:    #跳过识别失败的资产
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue

            if '_AAI' in track_bpname and asset_basename==track_bpname.split('_AAI')[0]:
                bp_exist = True
                parent_bind = possessable
            
            if 'BP_CH_' in track_bpname and asset_basename==track_bpname.split('BP_CH_')[-1]:
                bp_exist = True 
                parent_bind = possessable
            
            if '_BD' in track_bpname and groom_asset_basename==track_bpname.split('_BD')[0]:
                groom_bp_exist = True
                groom_bind = possessable

        if not bp_exist:
            #添加bp_actor到sequence
            if parent_actor:
                parent_bind = level_sequence_editor_subsystem.add_actors([parent_actor])[0]
                for parent_track in parent_bind.get_tracks():
                    parent_bind.remove_track(parent_track)
        if parent_actor:
            #将基础groom资产添加到level中
            if not groom_actor:
                groom_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(groom_asset,unreal.Vector(0.0, 0.0, 0.0))
                setLightChannel(groom_actor,[False,True,False,False])  #设置灯光通道
            # groom_actor.set_actor_relative_scale3d(unreal.Vector(1.0, 1.0, -1.0))

            base_bones = ['Head_M','head']
            socket_name = ''
            skeletal_mesh_comp = parent_actor.get_component_by_class(unreal.SkeletalMeshComponent)
            bone_num = skeletal_mesh_comp.get_num_bones()
            #判断基础骨骼名称
            for index in range(bone_num):
                bone_name = skeletal_mesh_comp.get_bone_name(index)
                if bone_name in base_bones:
                    socket_name = bone_name
                    break
            cls.__groomLocateToCh(cls,groom_actor,parent_actor,socket_name)
            cls.__bpRemoveGroom(cls,parent_actor)

            #判断groom possessable是否已存在
            if not groom_bp_exist:
                groom_possessable = current_sequence.add_possessable(groom_actor)
            else:
                groom_possessable = groom_bind
            old_tracks = groom_possessable.get_tracks()
            #删除旧track
            for old_track in old_tracks:
                groom_possessable.remove_track(old_track)
            groom_cache_track = groom_possessable.add_track(unreal.MovieSceneGroomCacheTrack)
            #track设置为计算最近分段
            eval_options = groom_cache_track.get_editor_property('eval_options')
            eval_options.set_editor_property('eval_nearest_section', True)
            eval_options.set_editor_property('evaluate_in_postroll', False)
            eval_options.set_editor_property('evaluate_in_preroll', False)
            groom_cache_track.set_editor_property('eval_options',eval_options)

            groom_cache_section = groom_cache_track.add_section()

            #groom缓存添加设置
            groom_cache_params=unreal.MovieSceneGroomCacheParams()
            groom_cache_params.set_editor_property('groom_cache',groom_cache)
            groom_cache_section.set_editor_property('params',groom_cache_params)
            groom_cache_section.set_range(start_frame,end_frame)


        return True


    @classmethod
    def groomToSequence(cls,groom_cache_path,cache_seq,groom_type_index:int,is_offset=True):        #groom_type_index     0:guid  1:strand
        asset_basename = groom_cache_path.split('/')[-1].split('.')[-1].split('_',3)[3].rsplit('_',5)[0]
        if is_offset:
            start_offset = UC.globalConfig.get().start_offset
            end_offset = UC.globalConfig.get().end_offset
        else:
            start_offset = 0
            end_offset = 0
        abc_asset=groom_cache_path.split('/')[-1]
        abc_split = abc_asset.split('_')
        base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'

        seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_hcache'   #动画序列路径,若不存在hcache则用cache路径
        if not unreal.EditorAssetLibrary.does_asset_exist(seq_path):
            seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_cache'

        cache_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取cache关卡序列

        #打开对应level
        level_path = base_path+f'{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_Map'
        an_level_path = base_path+f'Animation/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_an_Map'
        if unreal.EditorAssetSubsystem().does_asset_exist(an_level_path):
            unreal.LevelEditorSubsystem().load_level(an_level_path)
        else:
            unreal.LevelEditorSubsystem().load_level(level_path)
        
        #获取用于添加关卡序列的cache
        groom_cache=unreal.EditorAssetLibrary.find_asset_data(groom_cache_path).get_asset()
        
        #打开动画序列
        unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(cache_seq)
        #sequence解锁
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(False)

        abc_asset_frame=groom_cache_path.split('_')[-4].rsplit('-',1)
        #获取cache的起始结束帧
        start_frame=int(abc_asset_frame[0])+start_offset
        end_frame=int(abc_asset_frame[1])+start_offset

        #获取当前打开的关卡序列
        current_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        possessables = current_sequence.get_possessables()
        frame_range = current_sequence.get_playback_range()
        frame_start = frame_range.get_start_frame()

        parent_actor = None
        actors=editor_actor_subsystem.get_all_level_actors()
        for act in actors:
            act:unreal.Actor
            if act.get_actor_label().split('_AAI')[0] == asset_basename:
                
                parent_actor = act
                break
            elif act.get_actor_label().split('BP_CH_')[-1] == asset_basename:
                parent_actor = act
                break
            
        
        
        bp_exist = False
        #当不存在角色bp时将level的bp actor添加到cache sequence中
        for possessable in possessables:
            #获取bp名称
            try:    #跳过识别失败的资产
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue

            if '_AAI' in track_bpname and asset_basename==track_bpname.split('_AAI')[0]:
                bp_exist = True
                parent_bind = possessable
            
            if 'BP_CH_' in track_bpname and asset_basename==track_bpname.split('BP_CH_')[-1]:
                bp_exist = True
                parent_bind = possessable

        if not bp_exist:
            #添加bp_actor到sequence
            if parent_actor:

                parent_bind = level_sequence_editor_subsystem.add_actors([parent_actor])[0]
                for parent_track in parent_bind.get_tracks():
                    parent_bind.remove_track(parent_track)

                # #设置中继器事件
                # event_track=parent_bind.add_track(unreal.MovieSceneEventTrack)
                # trigger_section=event_track.add_event_trigger_section()
                # #添加事件端口
                # quick_bingding=unreal.SequencerTools.create_quick_binding(current_sequence,parent_actor,"construction",True)
                # new_event=unreal.SequencerTools.create_event(current_sequence,trigger_section,quick_bingding,[])
                # trigger_channel = trigger_section.get_all_channels()[0]
                # trigger_channel.add_key(time=unreal.FrameNumber(frame_start+1),new_value=new_event)

            
        #按照顺序挂载groom组件
        for i in range(3):
            groom_index = str(i+1)
            print(parent_actor)
            groom_component = unreal.find_object(parent_actor, "Groom"+groom_index)
            
            groom_component_asset = groom_component.groom_asset
            
            #判断groom组件是否挂载了groom
            if groom_component_asset:
                cache_asset_basename = groom_cache.get_name().rsplit('_',4)[0].split('_',3)[-1]
                groom_component_asset_basename = groom_component_asset.get_name().rsplit('_BD',1)[0]
                #判断groom组件的资产名称是否与cache的名称对应
                if cache_asset_basename == groom_component_asset_basename:
                    #删除旧track
                    tracks=parent_bind.get_tracks()
                    for track in tracks:
                        #删除自定义track
                        if track.get_display_name()==f'Groom{groom_index}Cache':
                            possessable.remove_track(track)
                    #为actor添加groom cache并k帧
                    groom_cache_track = parent_bind.add_track(unreal.MovieSceneObjectPropertyTrack)
                    groom_cache_track.set_property_name_and_path(f'Groom{groom_index}Cache', f'Groom{groom_index}Cache')
                    #track设置为计算最近分段
                    eval_options = groom_cache_track.get_editor_property('eval_options')
                    eval_options.set_editor_property('eval_nearest_section', True)
                    eval_options.set_editor_property('evaluate_in_postroll', False)
                    eval_options.set_editor_property('evaluate_in_preroll', False)
                    groom_cache_track.set_editor_property('eval_options',eval_options)
                    
                    object_section = groom_cache_track.add_section()
                    object_channel = object_section.get_all_channels()[0]
                    object_channel.add_key(time=unreal.FrameNumber(start_frame),new_value=groom_cache)

                    if groom_type_index == 1: 
                        try:
                            bd_name = parent_actor.get_editor_property(f"Groom{groom_index}Binding").get_name().rsplit('_BD',1)[0]
                            if cache_asset_basename == bd_name:
                                #为actor删除bind并k帧
                                groom_cache_track = parent_bind.add_track(unreal.MovieSceneObjectPropertyTrack)
                                groom_cache_track.set_property_name_and_path(f'Groom{groom_index}Binding', f'Groom{groom_index}Binding')
                                object_section = groom_cache_track.add_section()
                                object_channel = object_section.get_all_channels()[0]
                                object_channel.add_key(time=unreal.FrameNumber(start_frame),new_value=None)
                        except:
                            print(cache_asset_basename)


                    #添加GeometryCache到关卡序列中的对应BP中
                    groom_possessable=current_sequence.add_possessable(groom_component)
                    old_tracks = groom_possessable.get_tracks()
                    #删除旧track
                    for old_track in old_tracks:
                        groom_possessable.remove_track(old_track)
                    groom_cache_track = groom_possessable.add_track(unreal.MovieSceneGroomCacheTrack)
                    #track设置为计算最近分段
                    eval_options = groom_cache_track.get_editor_property('eval_options')
                    eval_options.set_editor_property('eval_nearest_section', True)
                    eval_options.set_editor_property('evaluate_in_postroll', False)
                    eval_options.set_editor_property('evaluate_in_preroll', False)
                    groom_cache_track.set_editor_property('eval_options',eval_options)
                    groom_cache_section = groom_cache_track.add_section()

                    #groom缓存添加设置
                    groom_cache_params=unreal.MovieSceneGroomCacheParams()
                    groom_cache_params.set_editor_property('groom_cache',groom_cache)
                    groom_cache_section.set_editor_property('params',groom_cache_params)
                    groom_cache_section.set_range(start_frame,end_frame)
    
        return True


    @classmethod
    #groom_type_index  0:guid  1:strand
    def groomMount(cls,groom_folder_path,groom_type_index,assets_path=[],mount_switch=True,version=0,is_offset=True,old_vision=False):  
        
        asset_ch_path=globalConfig.get().AssetPath+'Character/'
        import_error_datas=[]
        md5_same_list = []
        groom_paths=[]
        #当存在文件夹路径groom_folder_path时,读取文件夹内资产;不存在时,读取资产路径列表assets_path
        if groom_folder_path:
            for dirpath, dirnames, filenames in os.walk(groom_folder_path):
                for filename in filenames:
                    if '.abc' in filename and '_hCache' in filename:
                        groom_path=str(os.path.join(dirpath, filename)).replace('\\','/')
                        groom_paths.append(groom_path)
        else:
            groom_paths = assets_path
        
        #创建groom文件夹
        if not groom_paths:
            #未找到资产返回False
            return import_error_datas,md5_same_list
        

        old_groom_asset_basepath=None
        groom_assets=None

        for groom_import_path in groom_paths:
            # groom_split=groom_import_path[0].split('/')[-1].split('_')
            # unreal.EditorAssetLibrary.make_directory(f'/Game/Shots/{groom_split[0]}/{groom_split[1]}/{groom_split[0]}_{groom_split[1]}_{groom_split[2]}/Cache/Groom')
            #通过文件名获取对应ue路径
            abc_asset_frame = groom_import_path.split('_')[-2].split('.')[0].rsplit('-',1)
            abc_asset_name = groom_import_path.split('/')[-1].split('.')[0]
            abc_split = abc_asset_name.split('_')

            base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'
            des_path = base_path+'Cache/Groom'    #缓存目标文件夹
            seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_hcache'   #动画序列路径,若不存在hcache则用cache路径
            if not unreal.EditorAssetLibrary.does_asset_exist(seq_path):
                seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_cache'
            cache_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取cache关卡序列
            
            #哈希值判断文件重复时执行仅挂载
            if groom_type_index == 0:
                cache_asset_path = f'{des_path}/{abc_asset_name}_guides_cache'
            if groom_type_index == 1:
                cache_asset_path = f'{des_path}/{abc_asset_name}_strands_cache'
            

            #获取cache的起始结束帧
            start_frame=int(abc_asset_frame[0])
            end_frame=int(abc_asset_frame[1])
            
            
            #获取角色文件夹
            ch_path=cls.groomCacheToChDirectory(cls,abc_asset_name,asset_ch_path)
            #未找到对应基础groom
            if not ch_path:
                import_error_datas.append(groom_import_path)
                continue
            #获取groom部件名称
            asset_partname = groom_import_path.split('/')[-1].split('_',3)[3].rsplit('_',2)[0]
            
            # groom_import_basename = groom_import_path.split('/')[-1].split('.')[0]
            #角色目录下的groom文件夹
            groom_asset_basepath=ch_path+'/Groom'
            
            #判断新旧路径名称,防止重复运行
            if not groom_asset_basepath==old_groom_asset_basepath:
                groom_assets=cls.listClassAsset(cls,groom_asset_basepath,'GroomAsset')

            old_groom_asset_basepath=groom_asset_basepath   #记录文件夹名称

            
            #遍历绑定的groom资产
            for groom_asset in groom_assets:
                #判断绑定的groom和导入的cache命名是否一致
                if groom_asset.get_name().split('_BD')[0]==asset_partname:
                    groom_asset_path = groom_asset.get_path_name()
                    groom_yd_model = False
                    if 'yd_hair' in groom_asset_path.lower():           #判断文件路径是否存在yd_hair文件夹,存在则使用新版导入方式
                        if old_vision:  #旧流程跳过yd_hair
                            continue
                        groom_yd_model = True
                    if groom_type_index == 1:
                        groom_cache_path=des_path+'/'+abc_asset_name+'_strands_cache'
                    elif groom_type_index == 0:
                        groom_cache_path=des_path+'/'+abc_asset_name+'_guides_cache'

                    #当MD5值相同,则跳过导入直接挂载
                    if unreal.EditorAssetLibrary.does_asset_exist(cache_asset_path):
                        print(cache_asset_path)
                        cache_asset = unreal.EditorAssetLibrary.load_asset(cache_asset_path)
                        #判断哈希值,防止重复导入
                        if importAssetMd5Compare(groom_import_path,cache_asset):
                            print(groom_import_path+' 已是最新版本')
                            md5_same_list.append(groom_import_path)
                            #挂载到an Sequence
                            if mount_switch:
                                try:
                                    if version == 0 and not groom_yd_model:
                                        cls.groomToSequence(groom_cache_path,cache_seq,groom_type_index,is_offset=is_offset)
                                    elif version == 574 or groom_yd_model:
                                        cls.groomToSequence574(groom_cache_path,cache_seq,groom_type_index,groom_asset)
                                except:
                                    import_error_datas.append(groom_import_path)
                            continue

                    print(groom_asset.get_name())

                    #获取用于添加cache的groom soft信息
                    groom_asset_soft=unreal.EditorAssetLibrary.find_asset_data(groom_asset.get_path_name()).to_soft_object_path()
                    #创建cache
                    if groom_type_index == 0:
                        groom_type = unreal.GroomCacheImportType.GUIDES
                    if groom_type_index == 1:
                        groom_type = unreal.GroomCacheImportType.STRANDS
                    print(groom_import_path,des_path,groom_asset_soft,start_frame,end_frame,groom_type)
                    groom_cache_task=GroomAbcImport.buildImportTask(groom_import_path,des_path,GroomAbcImport.buildGroomCacheImportOptions(groom_asset_soft,start_frame,end_frame,groom_type))
                    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([groom_cache_task])
                    

                    #判断groom Cache是否正确导入(未正确导入不会存在)
                    if not unreal.EditorAssetLibrary.does_asset_exist(groom_cache_path):
                        import_error_datas.append(groom_import_path)
                        continue
                    
                    if mount_switch:    #判断是否挂载
                        #打开对应level
                        level_path = base_path+f'{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_Map'
                        an_level_path = base_path+f'Animation/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_an_Map'
                        if unreal.EditorAssetSubsystem().does_asset_exist(an_level_path):
                            unreal.LevelEditorSubsystem().load_level(an_level_path)
                        else:
                            unreal.LevelEditorSubsystem().load_level(level_path)
                        try:
                            if version == 0 and not groom_yd_model:
                                cls.groomToSequence(groom_cache_path,cache_seq,groom_type_index,is_offset=is_offset)
                            elif version == 574 or groom_yd_model:
                                cls.groomToSequence574(groom_cache_path,cache_seq,groom_type_index,groom_asset)
                        except:
                            import_error_datas.append(groom_import_path)

            unreal.EditorAssetLibrary.save_directory('/Game')
        return import_error_datas,md5_same_list



def assetFilter(class_name,folder):
    filter=unreal.ARFilter(class_names=[class_name], package_paths=[folder],recursive_paths=True)
    asset_reg=unreal.AssetRegistryHelpers.get_asset_registry()
    return asset_reg.get_assets(filter)

def assetDataToAssetName(asset_data):
    asset_name=str(asset_data).split('asset_name: "',1)[-1].split('"')[0]
    return asset_name

def assetDataToAssetPath(asset_data):
    asset_path=str(asset_data).split('package_path: "',1)[-1].split('"')[0]
    return asset_path

def importAssetMd5Compare(file_path,cache_asset):
    cache_asset_path = cache_asset.get_path_name()
    asset_tag = unreal.EditorAssetLibrary.get_tag_values(cache_asset_path)
    asset_import_data = asset_tag.get('AssetImportData')
    #读取UE缓存资产md5信息
    md5_data = asset_import_data.split('"FileMD5" : "')[-1].split('"')[0]

    #计算文件的MD5哈希值
    md5_hash = hashlib.md5()

    try:
        with open(file_path, 'rb') as f:
            # 分块读取文件，避免大文件占用过多内存
            for chunk in iter(lambda: f.read(4096), b''):
                md5_hash.update(chunk)
    except FileNotFoundError:
        print(f'未找到文件 {file_path}')
        return False
    except Exception as e:
        print(f"计算MD5时出错: {e}")
        return False

    if md5_hash.hexdigest() == md5_data:
        return True
    else:
        return False


#清除Cloth Possessable多余track
def clearClothPossessable(possessable:unreal.MovieSceneBindingProxy):
    current_event=None
    tracks=possessable.get_tracks()
    for track in tracks:
        #删除事件track
        if track.get_class().get_name()=='MovieSceneEventTrack':
            event_section = track.get_sections()[0]
            event_channel = event_section.get_all_channels()[0]
            # current_event = event_section.get_editor_property('event')
            current_event = event_channel.get_keys()[0].get_value()
            possessable.remove_track(track)
        #删除自定义track
        # elif track.get_class().get_name()=='MovieSceneObjectPropertyTrack' or track.get_display_name()=='显示头发':
        elif track.get_display_name()=='解算缓存' or track.get_display_name()=='显示头发':
            possessable.remove_track(track)
    #删除子GeometryCacheComponent
    for sub_possessable in possessable.get_child_possessables():
        if sub_possessable.get_possessed_object_class():
            if sub_possessable.get_possessed_object_class().get_name() == 'GeometryCacheComponent':
                sub_possessable.remove()
    # sub_possessables=possessable.get_child_possessables()
    # if sub_possessables:
    #     sub_possessables[0].remove()

    return current_event


def pathToMaterial(assets_path):

    asset_list=unreal.EditorAssetLibrary.list_assets(assets_path)

    return_list=[]
    

    for asset in asset_list:
        asset_class=unreal.EditorAssetLibrary.find_asset_data(asset).get_class().get_name()
        if asset_class=='MaterialInstanceConstant' or asset_class=='Material':
            return_list.append(unreal.EditorAssetLibrary.find_asset_data(asset).get_asset())
        
    
    return return_list




def clothImportMount(abc_import_path,assets_path=[],only_import_switch=False,offset_switch=True,version=0):   #only_import_switch 仅导入不挂载,offset_switch 是否使用偏移帧
    asset_ch_path=globalConfig.get().AssetPath+'Character/'
    
    import_error_paths = []
    mat_error_asset_paths = []
    md5_same_list = []
    abc_paths=[]
    #当存在文件夹路径abc_import_path时,读取文件夹内资产;不存在时,读取资产路径列表assets_path
    if abc_import_path:
        for dirpath, dirnames, filenames in os.walk(abc_import_path):
            for filename in filenames :
                if '.abc' in filename and '_Cache' in filename:
                    groom_path=str(os.path.join(dirpath, filename)).replace('\\','/')
                    abc_paths.append(groom_path)
    else:
        abc_paths = assets_path
    
    abc_assets = []
    used_actors = []
    error_nosk_assets = []
    for abc_path in abc_paths:
        md5_same = False
        abc_asset_index = None
        abc_asset_frame = abc_path.split('_')[-2].rsplit('-',1)
        abc_asset_name = abc_path.split('/')[-1].split('.')[0]
        abc_base_name = abc_asset_name.rsplit('_',2)[0].split('_',3)[-1]
        abc_split = abc_asset_name.split('_')
        abc_json_path = abc_path.split('.')[0]+'.json'
        new_abc_mats=[]
        if '-' in abc_base_name:
            abc_base_name = abc_base_name.split('-')[0]
            abc_asset_index = abc_base_name.split('-')[-1]

        abc_base_name = abc_base_name.rstrip('0123456789')      #清除cache后缀数字
        mat_path=asset_ch_path+abc_base_name+'/Material'

        cache_asset_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/Cache/{abc_asset_name}'
        if unreal.EditorAssetLibrary.does_asset_exist(cache_asset_path):
            cache_asset = unreal.EditorAssetLibrary.load_asset(cache_asset_path)
            #判断哈希值,防止重复导入
            if importAssetMd5Compare(abc_path,cache_asset):
                print(abc_path+' 已是最新版本')
                md5_same_list.append(abc_path)
                md5_same = True
                

        ch_mats=pathToMaterial(mat_path)

        #获取cache的起始结束帧
        start_frame=int(abc_asset_frame[0])
        end_frame=int(abc_asset_frame[1])

        #获取对应镜头文件夹
        base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'
        des_path = base_path+'Cache'    #缓存目标文件夹
        seq_path = base_path+f'Animation/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_an'   #动画序列对象路径

        # 导入abc文件
        if not md5_same:
            full_asset_path = des_path+'/'+abc_asset_name       #删除旧文件
            if unreal.EditorAssetLibrary().does_asset_exist(full_asset_path):
                print(f"资产已存在，正在删除: {full_asset_path}")
                unreal.EditorAssetLibrary().delete_asset(full_asset_path)
            abc_task=ClothAbcImport.buildImportTask(abc_path,des_path,ClothAbcImport.buildClothImportOptions(start_frame,end_frame))
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([abc_task])

        abc_asset=unreal.EditorAssetLibrary.find_asset_data(des_path+'/'+abc_asset_name).get_asset()
        abc_asset:unreal.GeometryCache

        #判断json文件是否存在
        if os.path.isfile(abc_json_path):
            #通过json文件获取材质球信息
            with open(abc_json_path, 'r') as json_file:
                abc_mats = json.load(json_file)

        #json文件不存在时使用abc材质插槽名称查询材质
        else:
            if abc_asset:
                abc_mats = abc_asset.material_slot_names
            else:
                import_error_paths.append(abc_path)
                continue
        
        #遍历abc对应材质球对象
        for abc_mat in abc_mats:
            for ch_mat in ch_mats:
                # print(ch_mat.get_name(),abc_mat)
                #清除:号
                if ':' in str(abc_mat):
                    if ch_mat.get_name() == str(abc_mat).split(':')[-1]:
                        new_abc_mats.append(ch_mat)
                else:
                    if ch_mat.get_name() == abc_mat:
                        new_abc_mats.append(ch_mat)

        #赋予abc文件材质球
        if abc_asset:
            # print(new_abc_mats,abc_mats)
            
            if len(new_abc_mats)==len(abc_mats):
                abc_asset.materials = new_abc_mats
            else:
                mat_error_asset_paths.append(abc_path)
                continue
            
            #判断abc仅导入判定
            if only_import_switch==False:
                try:
                    if version == 0:
                        mountClothAbc([abc_asset],offset_switch)
                    elif version == 574:
                        used_parent_actors,error_nosk = mountClothAbc574([abc_asset],offset_switch,used_actors)
                        used_actors.extend(used_parent_actors)
                        error_nosk_assets.extend(error_nosk)
                except:
                    import_error_paths.append(abc_path)
            #收集abc资产
            abc_assets.append(abc_asset)
        else:
            import_error_paths.append(abc_path)


        #保存文件
        unreal.EditorAssetLibrary.save_directory(des_path, only_if_is_dirty=False)


    # #判断abc仅导入判定
    # if only_import_switch==False:
    #     mountClothAbc(abc_assets)

    
    #保存文件
    unreal.EditorAssetLibrary.save_directory('/Game')

    if version == 574:
        return import_error_paths,mat_error_asset_paths,md5_same_list,error_nosk_assets
    else:
        return import_error_paths,mat_error_asset_paths,md5_same_list



def mountClothAbc574(cloth_abc_list=None, offset_switch=True,used_actors=[]):

    used_parent_actors = used_actors
    error_nosk_assets = []
    
    #如果没有导入列表则按照选择的abc缓存进行执行
    if not cloth_abc_list:
        select_assets=unreal.EditorUtilityLibrary.get_selected_assets()
        abc_assets=[]
        for select_asset in select_assets:
            if select_asset.get_class().get_name()=='GeometryCache':
                abc_assets.append(select_asset)
                print(select_asset.get_name())
    
    else:
        abc_assets = cloth_abc_list
    
    for abc_asset in abc_assets:
        abc_asset_name = abc_asset.get_name()
        #判断命名规则
        if '_Cache' not in abc_asset_name:
            continue
        
        abc_split = abc_asset_name.split('_')
        abc_basename = abc_asset_name.rsplit('_',2)[0].split('_',3)[-1]
        base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'
        des_path = base_path+'Cache'    #缓存目标文件夹
        seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_hcache'   #动画序列对象路径
        if not unreal.EditorAssetSubsystem().does_asset_exist(seq_path):
            seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_cache'

        #获取cache的起始结束帧
        abc_asset_frame = abc_asset_name.split('_')[-2].rsplit('-',1)
        if offset_switch:
            start_frame = int(abc_asset_frame[0])+UC.globalConfig.get().start_offset
            end_frame = int(abc_asset_frame[1])+UC.globalConfig.get().start_offset
        else:
            start_frame = int(abc_asset_frame[0])
            end_frame = int(abc_asset_frame[1])
        
        #打开对应level
        level_path = base_path+f'{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_Map'
        an_level_path = base_path+f'Animation/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_an_Map'
        if unreal.EditorAssetSubsystem().does_asset_exist(an_level_path):
            unreal.LevelEditorSubsystem().load_level(an_level_path)
        else:
            unreal.LevelEditorSubsystem().load_level(level_path)

        #获取当前关卡
        current_level = level_editor_subsystem.get_current_level()
        #解锁当前关卡
        unreal.PythonExtensionBPLibrary.unlock_level(current_level)
        
        #打开动画序列
        cache_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取动画序列
        unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(cache_seq)
        #获取当前打开的关卡序列
        current_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        #关闭锁定
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(False)

        #获取所有actor
        actors=unreal.EditorActorSubsystem().get_all_level_actors()

        parent_actor = None
        for act in actors:
            #删除同名actor,防止重复挂载
            if abc_asset_name in act.get_actor_label():
                editor_actor_subsystem.destroy_actor(act)
            #获取角色actor
            if act.get_actor_label().split('_AAI')[0].rstrip('0123456789') == abc_basename:
                if parent_actor not in used_parent_actors:  #已被使用的actor跳过
                    parent_actor = act
                continue
            elif act.get_actor_label().split('BP_CH_')[-1].rstrip('0123456789') == abc_basename:
                if parent_actor not in used_parent_actors:
                    parent_actor = act
                continue
            elif act.get_actor_label().split('BP_Pro_')[-1].rstrip('0123456789') == abc_basename:
                if parent_actor not in used_parent_actors:
                    parent_actor = act
                continue

        #当存在角色actor时,将其skeletal mesh替换为无sk版本,防止与解算缓存冲突
        if parent_actor:
            sk_component = parent_actor.skeletal_mesh_component
            sk_asset = sk_component.get_editor_property('skeletal_mesh_asset')
            sk_path = sk_asset.get_path_name().rsplit('/',1)[0]
            sk_name = sk_asset.get_name()
            if '/Pro/' in sk_path:
                sk_type = 'Pro'
            elif '/Character/' in sk_path:
                sk_type = 'CH'
            if '_NoSK' not in sk_name:      #当前骨骼网格体为'_NoSK'时跳过,防止重复替换
                
                sk_nosk_name = sk_name+'_NoSK'
                sk_nosk_path = sk_path+'/'+sk_nosk_name
                sk_nosk_asset = unreal.load_asset(sk_nosk_path)

                used_parent_actors.append(parent_actor)     #将改变过骨骼网格体的actor记录

                if sk_nosk_asset:
                    sk_component.set_editor_property('skeletal_mesh_asset',sk_nosk_asset)
                else:
                    print(f'未找到{sk_nosk_path}骨骼网格体')
                    error_nosk_assets.append(sk_nosk_path)
                

        add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(abc_asset,unreal.Vector(0.0, 0.0, 0.0))
        print(add_actor)
        if sk_type == 'CH':
            setLightChannel(add_actor,[False,True,False,False])  #设置灯光通道
        elif sk_type == 'Pro':
            setLightChannel(add_actor,[False,False,True,False])  #设置灯光通道

        possessables = current_sequence.get_possessables()
        for possessable in possessables:
            #获取bp名称
            try:    #跳过识别失败的资产
                track_name = possessable.get_display_name()
            except:
                continue
            #存在重命名的possessable时,将其删除,防止重复挂载
            if abc_asset_name==track_name:
                possessable.remove()

        #添加bp_actor到sequence
        geo_cache_possessable = level_sequence_editor_subsystem.add_actors([add_actor])[0]
        geo_cache_possessable = level_sequence_editor_subsystem.convert_to_spawnable(geo_cache_possessable)[0]
        for parent_track in geo_cache_possessable.get_tracks():
            geo_cache_possessable.remove_track(parent_track)


        #添加解算缓存组件
        #获取actor中的GeometryCache组件
        GeometryCache = unreal.find_object(add_actor, "GeometryCacheComponent")
        print(add_actor)
        #添加GeometryCache到关卡序列中的对应BP中
        geo_cache_comp_possessable=cache_seq.add_possessable(GeometryCache)

        #添加解算缓存
        geo_cache_track = geo_cache_possessable.add_track(unreal.MovieSceneGeometryCacheTrack)
        #track设置为计算最近分段
        eval_options = geo_cache_track.get_editor_property('eval_options')
        eval_options.set_editor_property('eval_nearest_section', True)
        eval_options.set_editor_property('evaluate_in_postroll', False)
        eval_options.set_editor_property('evaluate_in_preroll', False)
        geo_cache_track.set_editor_property('eval_options',eval_options)

        geo_cache_section = geo_cache_track.add_section()

        #解算缓存设置
        geo_cache_params = unreal.MovieSceneGeometryCacheParams()
        geo_cache_params.set_editor_property('geometry_cache_asset',abc_asset)
        geo_cache_section.set_editor_property('params',geo_cache_params)
        #设置起始结束帧
        geo_cache_section.set_range(start_frame,end_frame)

        #添加'正在运行track'
        object_track = geo_cache_comp_possessable.add_track(unreal.MovieSceneBoolTrack)
        object_track.set_property_name_and_path("正在运行", "bRunning")
        object_section = object_track.add_section()
        object_channel = object_section.get_all_channels()[0]
        
        object_channel.add_key(time=unreal.FrameNumber(start_frame),new_value=True)
        object_channel.add_key(time=unreal.FrameNumber(start_frame-1),new_value=False)
        
        unreal.EditorAssetLibrary.save_directory('/Game')




    return used_parent_actors,error_nosk_assets
        




def mountClothAbc(cloth_abc_list=None, offset_switch=True):
    
    #如果没有导入列表则按照选择的abc缓存进行执行
    if not cloth_abc_list:
        select_assets=unreal.EditorUtilityLibrary.get_selected_assets()
        abc_assets=[]
        for select_asset in select_assets:
            if select_asset.get_class().get_name()=='GeometryCache':
                abc_assets.append(select_asset)
                print(select_asset.get_name())
    
    else:
        abc_assets = cloth_abc_list

    used_possessable_dict = {}
    used_actor_dict = {}
    
    for abc_asset in abc_assets:

        abc_asset_name = abc_asset.get_name()

        #判断命名规则
        if '_Cache' not in abc_asset_name:
            continue
        
        abc_split = abc_asset_name.split('_')
        abc_basename = abc_asset_name.rsplit('_',2)[0].split('_',3)[-1]
        base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'
        des_path = base_path+'Cache'    #缓存目标文件夹
        seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_hcache'   #动画序列对象路径
        if not unreal.EditorAssetSubsystem().does_asset_exist(seq_path):
            seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_cache'


        if '-' in abc_basename:
            abc_basename = abc_basename.split('-')[0]

        #删除后缀数字
        abc_basename = abc_basename.rstrip('0123456789')

        #获取cache的起始结束帧
        abc_asset_frame = abc_asset_name.split('_')[-2].rsplit('-',1)
        if offset_switch:
            start_frame = int(abc_asset_frame[0])+UC.globalConfig.get().start_offset
            end_frame = int(abc_asset_frame[1])+UC.globalConfig.get().start_offset
        else:
            start_frame = int(abc_asset_frame[0])
            end_frame = int(abc_asset_frame[1])
        


        #打开对应level
        level_path = base_path+f'{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_Map'
        an_level_path = base_path+f'Animation/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_an_Map'
        if unreal.EditorAssetSubsystem().does_asset_exist(an_level_path):
            unreal.LevelEditorSubsystem().load_level(an_level_path)
        else:
            unreal.LevelEditorSubsystem().load_level(level_path)

        #获取当前关卡
        current_level = level_editor_subsystem.get_current_level()
        #解锁当前关卡
        unreal.PythonExtensionBPLibrary.unlock_level(current_level)
        #获取所有actor
        actors=unreal.EditorActorSubsystem().get_all_level_actors()


        #打开动画序列
        cache_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取动画序列
        unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(cache_seq)
        #获取当前打开的关卡序列
        current_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        #关闭锁定
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(False)

        possessables = current_sequence.get_possessables()
        frame_range = current_sequence.get_playback_range()
        frame_end = frame_range.get_end_frame()
        frame_start = frame_range.get_start_frame()

        


        bp_exist = False
        #当不存在角色bp时将level的bp actor添加到cache sequence中
        for possessable in possessables:
            #获取bp名称
            try:    #跳过识别失败的资产
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue

            if '_AAI' in track_bpname and abc_basename==track_bpname.split('_AAI')[0]:
                bp_exist = True
            if 'BP_CH_' in track_bpname and abc_basename==track_bpname.split('BP_CH_')[-1]:
                bp_exist = True

        if not bp_exist:
            #添加bp_actor到sequence
            actors=editor_actor_subsystem.get_all_level_actors()
            parent_actor = None
            for act in actors:
                act:unreal.Actor
                if act.get_actor_label().split('_AAI')[0] == abc_basename:
                    parent_actor = act
                    break
                elif act.get_actor_label().split('BP_CH_')[-1] == abc_basename:
                    parent_actor = act
                    break
            if parent_actor:
                try:    #失败则代表Sequence中已存在对应actor
                    parent_bind = level_sequence_editor_subsystem.add_actors([parent_actor])[0]
                    for parent_track in parent_bind.get_tracks():
                        parent_bind.remove_track(parent_track)
                except:
                    pass

        #更新possessables
        possessables = current_sequence.get_possessables()
        track_base_name=None    

        for possessable in possessables:
            #判断名称是否符合规则或者possessable是否已被使用
            used_sequence = False
            try:
                if used_possessable_dict[current_sequence.get_name()]:
                    used_sequence = True
            except:
                pass
            
            if 'BP' not in str(possessable.get_display_name()):
                continue
            if used_sequence:
                if possessable.get_display_name() in used_possessable_dict[current_sequence.get_name()]:
                    continue
            
            possessable:unreal.MovieSceneBindingProxy
            #获取bp名称
            try:    #跳过识别失败的资产
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue

            if '_AAI' in track_bpname and abc_basename.lower()==track_bpname.split('_AAI')[0].lower():
                mount_switch = True
            elif 'BP_CH_' in track_bpname and abc_basename.lower()==track_bpname.split('BP_CH_')[-1].lower():
                mount_switch = True
            else:
                mount_switch = False

            if mount_switch:
                #通过当前possessable选择对应actor
                unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(cache_seq)
                unreal.LevelSequenceEditorBlueprintLibrary.select_bindings([possessable])
                actor=editor_actor_subsystem.get_selected_level_actors()[0]
                #删除旧挂载对象,获取旧event
                old_event = clearClothPossessable(possessable)
                #添加结算缓存到actor
                actor.set_editor_property("解算缓存", abc_asset)
                #获取actor中的GeometryCache组件
                GeometryCache = unreal.find_object(actor, "GeometryCache")
                #添加GeometryCache到关卡序列中的对应BP中
                geo_cache_possessable=cache_seq.add_possessable(GeometryCache)
                #添加解算缓存
                geo_cache_track = geo_cache_possessable.add_track(unreal.MovieSceneGeometryCacheTrack)
                #track设置为计算最近分段
                eval_options = geo_cache_track.get_editor_property('eval_options')
                eval_options.set_editor_property('eval_nearest_section', True)
                eval_options.set_editor_property('evaluate_in_postroll', False)
                eval_options.set_editor_property('evaluate_in_preroll', False)
                geo_cache_track.set_editor_property('eval_options',eval_options)
                geo_cache_section = geo_cache_track.add_section()

                #解算缓存设置
                geo_cache_params = unreal.MovieSceneGeometryCacheParams()
                geo_cache_params.set_editor_property('geometry_cache_asset',abc_asset)
                geo_cache_section.set_editor_property('params',geo_cache_params)
                #设置起始结束帧
                geo_cache_section.set_range(start_frame,end_frame)

                # #设置中继器事件
                # event_track=possessable.add_track(unreal.MovieSceneEventTrack)
                # trigger_section=event_track.add_event_trigger_section()
                # # trigger_section.set_range(0,an_seq.get_playback_end())

                # #添加事件端口
                # if old_event:               #判断是否存在旧事件,存在则使用旧事件
                #     new_event=old_event
                # else:
                #     quick_bingding=unreal.SequencerTools.create_quick_binding(current_sequence,actor,"construction",True)
                #     new_event=unreal.SequencerTools.create_event(current_sequence,trigger_section,quick_bingding,[])
                # # trigger_section.set_editor_property('event',new_event)

                # trigger_channel = trigger_section.get_all_channels()[0]
                # trigger_channel.add_key(time=unreal.FrameNumber(frame_start+1),new_value=new_event)



                #添加缓存到sequence中并k帧
                object_track = possessable.add_track(unreal.MovieSceneObjectPropertyTrack)
                object_track.set_property_name_and_path("解算缓存", "解算缓存")
                object_section = object_track.add_section()
                object_channel = object_section.get_all_channels()[0]

                object_channel.add_key(time=unreal.FrameNumber(frame_start),new_value=abc_asset)

                #添加'正在运行track'
                object_track = geo_cache_possessable.add_track(unreal.MovieSceneBoolTrack)
                object_track.set_property_name_and_path("正在运行", "bRunning")
                object_section = object_track.add_section()
                object_channel = object_section.get_all_channels()[0]
                
                object_channel.add_key(time=unreal.FrameNumber(start_frame),new_value=True)
                object_channel.add_key(time=unreal.FrameNumber(start_frame-1),new_value=False)

                # #添加显示毛发框到sequence并k帧
                # groom_track = possessable.add_track(unreal.MovieSceneBoolTrack)
                # groom_track.set_property_name_and_path("显示头发", "显示头发")
                # groom_section = groom_track.add_section()
                # groom_channel = groom_section.get_all_channels()[0]
                # groom_channel.add_key(time=unreal.FrameNumber(frame_start+1),new_value=False)

                unreal.EditorAssetLibrary.save_directory('/Game')
                
                #记录当前possessable和actor以防重复使用
                try:
                    used_possessable_dict[current_sequence.get_name()].append(possessable.get_display_name())
                except:
                    used_possessable_dict[current_sequence.get_name()]=[]
                    used_possessable_dict[current_sequence.get_name()].append(possessable.get_display_name())

                break


            else:
                #名称不符合,跳过
                continue
        





class ErrorDialog(QDialog):

    def __init__(self, parent=None, initialText=""):
        super().__init__(parent)
        self.setWindowTitle("错误信息")
        self.resize(700, 400)  # 设置一个较大的初始尺寸

        layout = QVBoxLayout(self)

        # 创建纯文本编辑区域
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlainText(initialText)  # 设置初始文本
        # 可以设置字体等属性
        # self.text_edit.setFont(QFont("Consolas", 10)) 
        layout.addWidget(self.text_edit)

        #添加标准对话框按钮 (确定和取消)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        button_box.accepted.connect(self.accept)  # 点击“确定”触发accept
        button_box.rejected.connect(self.reject)  # 点击“取消”触发reject
        layout.addWidget(button_box)

class ContinueErrorDialog(QDialog):

    def __init__(self, parent=None, initialText=""):
        super().__init__(parent)
        self.setWindowTitle("错误信息")
        self.resize(700, 400)  # 设置一个较大的初始尺寸

        layout = QVBoxLayout(self)
        error_label = QLabel('发现了以下错误，是否继续执行？(选择"确定"将跳过错误数据执行后续操作，选择"取消"将停止执行)')
        error_label.setStyleSheet("color: red") 

        # 创建纯文本编辑区域
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlainText(initialText)  # 设置初始文本
        # 可以设置字体等属性
        # self.text_edit.setFont(QFont("Consolas", 10)) 
        layout.addWidget(self.text_edit)
        layout.addWidget(error_label)


        #添加标准对话框按钮 (确定和取消)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
        button_box.accepted.connect(self.accept)  # 点击“确定”触发accept
        button_box.rejected.connect(self.reject)  # 点击“取消”触发reject
        layout.addWidget(button_box)




def interChangeExamine(main_window,error_plugin_name='interchange'):
    plugins = unreal.PluginBlueprintLibrary.get_enabled_plugin_names()
    plugins.sort()
    error_plugins = []
    for plugin in plugins:
        if error_plugin_name in plugin.lower():
            error_plugins.append(plugin)
    
    if error_plugins:
        import_error_text = ''
        import_error_text += '请关闭以下插件:\n'
        for error_data in error_plugins:
            import_error_text += f'{error_data}\n'
        error_dialog = ErrorDialog(main_window,initialText = import_error_text)
        error_dialog.exec_()
        return False
    
    return True



def getProjectId():
    #获取UE当前工程的项目名称
    project_dir = unreal.Paths.project_dir()
    project_name = project_dir.split('/')[-3]

    project_url = "http://papi.cgyear.com.cn/taskapi/project/fetchListByEnName"
    project_payload = {'enNames':[project_name]}
    
    #获取用户名
    user_name = getpass.getuser()
    user_path = rf'C:\Users\{user_name}\AppData\Local\zynn\info.json'
    with open(user_path,'r',encoding='UTF-16') as file:
        json_data = json.load(file)

    user_key = json_data['key']

    headers = {
        "task-token": user_key,   # 替换为真实的 token
        "Content-Type": "application/json"      # 指明发送 JSON 数据
    }

    project_id = None
    try:
        response = requests.post(project_url, json=project_payload, headers=headers, timeout=10)
        # 检查 HTTP 状态码
        if response.status_code == 200:
            # 服务器返回的信息（假设为 JSON 格式）
            server_info = response.json()
            # print(server_info)
            project_id = server_info['data'][0]['id']
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)

    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求发生异常：{e}")
    
    return project_id,headers,project_name



def getFileInfo(project_name,project_id,headers,pfile_path):

    file_url = "http://papi.cgyear.com.cn/taskapi/projectFile/listByPackageName"
    file_payload = {
                        'projectId':project_id,
                        'packageNames':[pfile_path]
                        }

    try:
        response = requests.post(file_url, json=file_payload, headers=headers, timeout=10)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            # 服务器返回的信息（假设为 JSON 格式）
            server_info = response.json()
            # print("服务器返回信息：")
            # print(server_info)
        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)

    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求发生异常：{e}")


    urlPath = server_info['data'][0]['file']['urlPath']
    serverPath = server_info['data'][0]['file']['serverPath']

    packageName = server_info['data'][0]['packageName']
    file_name = server_info['data'][0]['name']
    pfile_mtime = server_info['data'][0]['file']['mtime']

    des_path = f'Y:/{project_name}/{packageName.rsplit("/", 1)[0]}'
    down_url = f'http://{urlPath}.cgyear.com.cn/{serverPath}'

    file_path = rf"{des_path}/{file_name}"
    

    file_path = file_path.replace("\\","/")
    # print(f" {file_mtime}   {pfile_mtime}")
    if not os.path.exists(file_path):
        # print(f"{file_path}  本地文件不存在，需要下载")
        return down_url,file_path,pfile_mtime
    
    else:
        stat_info = os.stat(file_path)
        file_mtime = int(stat_info.st_mtime)
        if file_mtime == pfile_mtime:
            print(f"{file_path}  本地文件与服务器文件一致，无需下载")
            return None, None, None
        else:
            return down_url,file_path,pfile_mtime
    # print(f"本地文件的修改时间戳: {file_mtime}   {pfile_mtime}")



def getFilesInfo(project_id, headers, folder_path):
    list_file_path = "http://papi.cgyear.com.cn/taskapi/projectFile/listByDirPaths"
    folder_path_payload = {
                            "projectId": project_id,
                            "dirPaths": [folder_path]
                            }

    files_data = None
    try:
        response = requests.post(list_file_path, json=folder_path_payload, headers=headers, timeout=10)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            # 服务器返回的信息（假设为 JSON 格式）
            server_info = response.json()
            # print("服务器返回信息：")
            # print(server_info)
            files_data = server_info['data']

        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)

    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求发生异常：{e}")

    new_files_data = []
    # print(files_data)
    if files_data:
        for file in files_data:
            mark = file['mark']
            if mark == 1:                   #当标注为1时，表示该文件被删除了，跳过不处理
                continue
            file_name = file['name']
            package_name = file['packageName']
            mtime = file['file']['mtime']
            asset_type = file['assetType']
            server_path = file['file']['serverPath']
            url_path = file['file']['urlPath']
            # print(f"文件名: {file_name}, 包路径: {package_name}, 修改时间戳: {mtime}, 资产类型: {asset_type}, 服务器路径: {server_path}, URL路径: {url_path}")
            new_files_data.append({
                "fileName": file_name,
                "packageName": package_name,
                "mtime": mtime,
                "serverPath": server_path,
                "urlPath": url_path
            })
    return new_files_data



def pipGetDir(project_id, headers, dir_id):

    get_dirs = f"http://papi.cgyear.com.cn/taskapi/projectFileDir/prlist?projectId={project_id}&id={dir_id}"

    dir_data = None
    dirs_info = []
    try:
        #get_dirs = 'http://papi.cgyear.com.cn/taskapi/projectFileDir/prlist?projectId=8&id=2690'
        # project_id, headers, project_name = uSTools.getProjectId()
        response = requests.post(get_dirs, headers=headers)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            # 服务器返回的信息（假设为 JSON 格式）
            server_info = response.json()
            dir_data = server_info['data']

        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)

    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求发生异常：{e}")

    if dir_data:
        for dir in dir_data:
            # dir_name = dir['name']
            dir_id = dir['id']
            path = dir['path']
            name = dir['name']
            dir_info = {
                "id": dir_id,
                "path": path,
                "name": name
            }
            dirs_info.append(dir_info)
            # print(f"目录名: {path}, 目录ID: {dir_id}")

    return dirs_info


def pipGetTaskDir(project_id, headers):

    get_task_dirs = f"http://papi.cgyear.com.cn/taskapi/taskDir/list"
    folder_path_payload = {
                        "projectId": project_id,
                        }

    dir_data = None
    dirs_info = []
    try:
        response = requests.post(get_task_dirs, json=folder_path_payload, headers=headers, timeout=10)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            # 服务器返回的信息（假设为 JSON 格式）
            server_info = response.json()
            dir_data = server_info['data']

        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)

    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求发生异常：{e}")

    if dir_data:
        for dir in dir_data:
            # dir_name = dir['name']
            dir_id = dir['id']
            path = dir['path']
            name = dir['name']
            if 'sc0' in path.lower():
                dir_info = {
                    "id": dir_id,
                    "path": path,
                    "name": name
                }
                dirs_info.append(dir_info)
            # print(f"目录名: {path}, 目录ID: {dir_id}")

    return dirs_info


def pipListPage(headers, dir_id):

    get_task_dirs = "http://papi.cgyear.com.cn/taskapi/task/listPage"
    folder_path_payload = {
                        "dirIds": [dir_id],
                            "page": 1,
                            "pageSize": 999
                        }
    dir_data = None
    tasks_info = []
    response = requests.post(get_task_dirs, json=folder_path_payload, headers=headers, timeout=10)

    # 检查 HTTP 状态码
    if response.status_code == 200:
        # 服务器返回的信息（假设为 JSON 格式）
        server_info = response.json()
        dir_data = server_info['data']['records']
        # print(dir_data)
    else:
        print(f"请求失败，状态码：{response.status_code}")
        print("响应内容：", response.text)

    if dir_data:
        for cam_data in dir_data:
            begin_frame = cam_data['beginFrame']
            end_frame = cam_data['endFrame']
            task_id = cam_data['id']
            cam_name = cam_data['taskCode']
            task_info = {
                'beginFrame':begin_frame,
                'endFrame':end_frame,
                'id':task_id,
                'taskCode':cam_name
            }
            tasks_info.append(task_info)

    return tasks_info


def pipGetCamRef(project_id, headers,task_id):

    get_task_dirs = f"http://papi.cgyear.com.cn/taskapi/taskRef/list"
    folder_path_payload = {
                        "projectId": project_id,
                        "taskId": 20569
                        }

    dir_data = None
    dirs_info = []
    try:
        response = requests.post(get_task_dirs, json=folder_path_payload, headers=headers, timeout=10)

        # 检查 HTTP 状态码
        if response.status_code == 200:
            # 服务器返回的信息（假设为 JSON 格式）
            server_info = response.json()
            dir_data = server_info['data']

        else:
            print(f"请求失败，状态码：{response.status_code}")
            print("响应内容：", response.text)

    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求发生异常：{e}")

    if dir_data:
        for dir in dir_data:
            # dir_name = dir['name']
            asset_type = dir['zcType']
            task_code = dir['taskCode']
            dir_info = {
                "zcType": asset_type,
                "taskCode": task_code,
            }
            dirs_info.append(dir_info)
            # print(f"目录名: {path}, 目录ID: {dir_id}")

    return dirs_info


def getPipTaskDir(project_id, headers):
    all_task_info = {}
    dirs_info = pipGetTaskDir(project_id, headers)
    for dir_info in dirs_info:
        # print(dir_info)
        tasks_info = pipListPage(headers,dir_info['id'])
        all_task_info[dir_info['path']] = tasks_info


def downLoadFile(url, local_filename):
    """流式下载文件，适合任意大小的文件"""
    folder_path = local_filename.rsplit('/',1)[0]
    if not os.path.exists(folder_path):         #未找到文件夹时,创建文件夹
        os.makedirs(folder_path, exist_ok=True)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()  # 检查请求是否成功
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    print(f"文件已保存为: {local_filename}")


def downloadFiles(files_info, project_name):
    for file_info in files_info:
        try:
            #当存在子骨骼网格体时,递归下载(用于下载骨骼网格体时使用)
            if file_info['subSkeletonMesh']:
                for sub_file_info in file_info['subSkeletonMesh']:
                    downloadFiles([sub_file_info], sub_file_info['projectName'])
        except:
            pass
        file_name = file_info['fileName']
        package_name = file_info['packageName']
        pfile_mtime = file_info['mtime']
        server_path = file_info['serverPath']
        url_path = file_info['urlPath']
        passet_type = file_name.split('.')[-1]

        local_file_path = f'Y:/{project_name}/{package_name}'
        file_path = local_file_path.replace("\\","/")

        down_url = f'http://{url_path}.cgyear.com.cn/{server_path}'

        down_file = False
        if not os.path.exists(file_path):
            down_file = True
            # print(f"{file_path}  本地文件不存在，需要下载")
        else:
            stat_info = os.stat(file_path)
            file_mtime = int(stat_info.st_mtime)
            if file_mtime == pfile_mtime:
                down_file = False
                # print(f"{file_path}  本地文件与服务器文件一致，无需下载")
            else:
                down_file = True
                # print(f"{file_path}  本地文件与服务器文件不一致，需要下载")

        if down_file:
            print(f"需要下载文件，下载链接为: {down_url}")
            file_name = os.path.basename(file_path)
            folder_path = os.path.dirname(file_path)
            downLoadFile(down_url, file_path)
            
            current_atime = os.path.getatime(file_path)
            os.utime(file_path, (current_atime, pfile_mtime))   #重设mtime值为pipeline上的mtime值



def baseAssetCreate(sc_list, shot_ep_path, cam_dict, ep,start_offset,end_offset):
    flie_class=['Light','Animation','Cache','VFX','Modify']
    
    render_ls_list=[]
    lt_ls_list=[]
    an_ls_list=[]
    ly_ls_list=[]
    groom_seq_list=[]
    vfx_seq_list=[]
    # 创建文件夹和所需的文件
    unreal.EditorAssetLibrary.make_directory('%s/Preview'%(shot_ep_path))
    for sc_name in sc_list:
            
        unreal.EditorAssetLibrary.save_directory('%s/Preview'%(shot_ep_path))
        level_editor_subsystem.load_level('%s/Preview/%s_%s_Pv_Map'%(shot_ep_path,ep,sc_name))

        for cam_name in cam_dict[sc_name]:
            flie_name = cam_name[0]
            for file_class_name in flie_class:
                if file_class_name=='Light':
                    render_seq_create = False   #当render未存在时将render添加到记录列表,用于添加其余基础序列,否则只修改帧数
                    render_path='%s/%s/%s/%s_Render'%(shot_ep_path,sc_name,flie_name,flie_name)
                    lt_map_path='%s/%s/%s/%s/%s_lt_Map'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(lt_map_path):
                        unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_lt_Map'%(cam_name[0]),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.World,factory=unreal.WorldFactory())
                    if not editor_asset_subsystem.does_asset_exist(render_path):
                        render_seq_create = True
                        render_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_Render'%(flie_name),package_path='%s/%s/%s'%(shot_ep_path,sc_name,flie_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                    else:
                        render_ls=unreal.EditorAssetLibrary.find_asset_data(render_path).get_asset()
                        render_ls:unreal.LevelSequence
                    render_ls.set_display_rate((25,1))
                    if cam_name[1]:
                        render_ls.set_playback_start(int(cam_name[1]))                                  #设置起始帧
                    if cam_name[2]:
                        render_ls.set_playback_end(int(cam_name[2])+end_offset+start_offset)  #设置结束帧
                    # if render_seq_create:
                    render_ls_list.append(render_ls)
                    unreal.EditorAssetLibrary.save_directory('%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name))
                    #打开其他关卡清理内存
                    level_editor_subsystem.load_level(lt_map_path)

                    lt_map_data = unreal.EditorAssetLibrary.find_asset_data(lt_map_path)



                    #创建灯光序列
                    lt_path='%s/%s/%s/%s/%s_lt'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(lt_path):
                        lt_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_lt'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                    else:
                        lt_ls=unreal.EditorAssetLibrary.find_asset_data(lt_path).get_asset()
                    lt_ls.set_display_rate((25,1))
                    if cam_name[1]:
                        lt_ls.set_playback_start(int(cam_name[1]))
                    if cam_name[2]:
                        lt_ls.set_playback_end(int(cam_name[2])+end_offset+start_offset)
                    lt_ls_list.append(lt_ls)

                
                if file_class_name=='Animation':
                    an_path='%s/%s/%s/%s/%s_an'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(an_path):
                        an_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_an'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                    else:
                        an_ls=unreal.EditorAssetLibrary.find_asset_data(an_path).get_asset()
                    an_ls.set_display_rate((25,1))
                    if cam_name[1]:
                        an_ls.set_playback_start(int(cam_name[1]))
                    if cam_name[2]:
                        an_ls.set_playback_end(int(cam_name[2])+end_offset+start_offset)
                    an_ls_list.append(an_ls)

                    #创建an关卡
                    an_map_path='%s/%s/%s/%s/%s_an_Map'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(an_map_path):
                        an_map = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_an_Map'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.World,factory=unreal.WorldFactory())

                    an_map_data = unreal.EditorAssetLibrary.find_asset_data(an_map_path)

                    #layout序列
                    ly_path='%s/%s/%s/%s/Layout/%s_Ly'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(ly_path):
                        ly_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_Ly'%(flie_name),package_path='%s/%s/%s/%s/Layout'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                    else:
                        ly_ls=unreal.EditorAssetLibrary.find_asset_data(ly_path).get_asset()
                    ly_ls.set_display_rate((25,1))
                    if cam_name[1]:
                        ly_ls.set_playback_start(int(cam_name[1]))
                    if cam_name[2]:
                        ly_ls.set_playback_end(int(cam_name[2])+end_offset+start_offset)
                    ly_ls_list.append(ly_ls)

                    

                if file_class_name=='Cache':
                    # 创建groom关卡序列
                    cache_path='%s/%s/%s/%s/%s_cache'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(cache_path):
                        groom_seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_cache'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                    else:
                        groom_seq=unreal.EditorAssetLibrary.find_asset_data(cache_path).get_asset()
                    groom_seq.set_display_rate((25,1))
                    if cam_name[1]:
                        groom_seq.set_playback_start(int(cam_name[1]))
                    if cam_name[2]:
                        groom_seq.set_playback_end(int(cam_name[2])+end_offset+start_offset)
                    groom_seq_list.append(groom_seq)
                    unreal.EditorAssetLibrary.make_directory('%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name))
                if file_class_name=='VFX':
                    unreal.EditorAssetLibrary.make_directory('%s/%s/%s/%s/VFX_DT'%(shot_ep_path,sc_name,flie_name,file_class_name))
                    # 创建VFX关卡序列
                    vfx_path='%s/%s/%s/%s/%s_VFX'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(vfx_path):
                        vfx_seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_VFX'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                    else:
                        vfx_seq=unreal.EditorAssetLibrary.find_asset_data(vfx_path).get_asset()
                    vfx_seq.set_display_rate((25,1))
                    if cam_name[1]:
                        vfx_seq.set_playback_start(int(cam_name[1]))
                    if cam_name[2]:
                        vfx_seq.set_playback_end(int(cam_name[2])+end_offset+start_offset)
                    vfx_seq_list.append(vfx_seq)
                    #创建VFX关卡
                    vfx_map_path='%s/%s/%s/%s/%s_VFX_Map'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(vfx_map_path):
                        vfx_map = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_VFX_Map'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.World,factory=unreal.WorldFactory())

                    vfx_map_data = unreal.EditorAssetLibrary.find_asset_data(vfx_map_path)

                if file_class_name=='Modify':
                    unreal.EditorAssetLibrary.make_directory('%s/%s/%s/%s/Scenes'%(shot_ep_path,sc_name,flie_name,file_class_name))
                    unreal.EditorAssetLibrary.make_directory('%s/%s/%s/%s/Character'%(shot_ep_path,sc_name,flie_name,file_class_name))
                    modify_path='%s/%s/%s/%s/%s_Modify'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                    if not editor_asset_subsystem.does_asset_exist(modify_path):
                        modify_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_Modify'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                    else:
                        modify_ls=unreal.EditorAssetLibrary.find_asset_data(modify_path).get_asset()
                    modify_ls.set_display_rate((25,1))
                    if cam_name[1]:
                        modify_ls.set_playback_start(int(cam_name[1]))
                    if cam_name[2]:
                        modify_ls.set_playback_end(int(cam_name[2])+end_offset+start_offset)

                
            #创建总关卡
            overall_level_path = '%s/%s/%s/%s_Map'%(shot_ep_path,sc_name,flie_name,flie_name)
            if not editor_asset_subsystem.does_asset_exist(overall_level_path):
                unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_Map'%(flie_name),package_path='%s/%s/%s'%(shot_ep_path,sc_name,flie_name),asset_class=unreal.World,factory=unreal.WorldFactory())
            unreal.EditorAssetLibrary.save_directory('/Game')
            #打开其他关卡清理内存
            level_editor_subsystem.load_level(lt_map_path)
            
            overall_level_data = unreal.EditorAssetLibrary().find_asset_data(overall_level_path)

            level_editor_subsystem.load_level(overall_level_path)
            current_world = unreal_editor_subsystem.get_editor_world()
            levels = unreal.EditorLevelUtils().get_levels(overall_level_data.get_asset())
            # print(levels)

            #判断对应子关卡是否存在
            an_map_exist = False
            vfx_map_exist = False
            lt_map_exist = False
            if len(levels)>1:
                for level in levels[1:]:
                    # print(level)
                    if '_an_Map' in str(level):
                        an_map_exist = True
                    if '_VFX_Map' in str(level):
                        vfx_map_exist = True
                    if '_lt_Map' in str(level):
                        lt_map_exist = True
            if an_map_data and not an_map_exist:
                unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=an_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
            if vfx_map_data and not vfx_map_exist:
                unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=vfx_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
            if lt_map_data and not lt_map_exist:
                unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=lt_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
            unreal.EditorAssetLibrary.save_directory('/Game')


    #将Light anim cache的sequence组装到总sequence
    for render_seq in render_ls_list:
        
        for lt_seq in lt_ls_list:
            if render_seq.get_name().rsplit('_',1)[0]==lt_seq.get_name().rsplit('_',1)[0]:
                render_tracks=render_seq.get_tracks()
                #删除原有track
                for render_track in render_tracks:
                    try:
                        if render_track.get_sections()[0].get_sequence()==lt_seq:
                            render_seq.remove_track(render_track)
                    except:
                        pass
                # lt.add_spawnable_from_instance(an) 
                render_track=render_seq.add_track(unreal.MovieSceneSubTrack)
                render_section=render_track.add_section()
                render_section.set_sequence(lt_seq)
                render_section.set_range(lt_seq.get_playback_start(),lt_seq.get_playback_end())
                break

        for groom_cache in groom_seq_list:
            if render_seq.get_name().rsplit('_',1)[0]==groom_cache.get_name().rsplit('_',1)[0]:
                render_tracks=render_seq.get_tracks()
                #删除原有track
                for render_track in render_tracks:
                    try:
                        if render_track.get_sections()[0].get_sequence()==groom_cache:
                            render_seq.remove_track(render_track)
                    except:
                        pass
                render_track=render_seq.add_track(unreal.MovieSceneSubTrack)
                render_section=render_track.add_section()
                render_section.set_sequence(groom_cache)
                render_section.set_range(groom_cache.get_playback_start(),groom_cache.get_playback_end())
                break
        for vfx_cache in vfx_seq_list:
            if render_seq.get_name().rsplit('_',1)[0]==vfx_cache.get_name().rsplit('_',1)[0]:
                render_tracks=render_seq.get_tracks()
                #删除原有track
                for render_track in render_tracks:
                    try:
                        if render_track.get_sections()[0].get_sequence()==vfx_cache:
                            render_seq.remove_track(render_track)
                    except:
                        pass
                render_track=render_seq.add_track(unreal.MovieSceneSubTrack)
                render_section=render_track.add_section()
                render_section.set_sequence(vfx_cache)
                render_section.set_range(vfx_cache.get_playback_start(),vfx_cache.get_playback_end())
                break
    #保存全部创建的文件
    unreal.EditorAssetLibrary.save_directory('/Game')






#aai auto
def excelRead(excel_path):

    df=op.load_workbook(excel_path,data_only=True)
    sheet=df['Sheet1']

    asset_dict={}
    i=0
    #确定行和列
    rowcount=sheet.max_row
    colcount=3
    #读取所需的Excel内容
    for i in range(1,rowcount+1):
        row_data_list=[]
        for j in range(1,colcount+1):
            row_data_list.append(sheet.cell(row=i,column=j).value)
        if row_data_list[0]:
            try:
                asset_dict[row_data_list[0]].append([row_data_list[1].split('.')[0],row_data_list[2]])
            except:
                asset_dict[row_data_list[0]] = []
                asset_dict[row_data_list[0]].append([row_data_list[1].split('.')[0],row_data_list[2]])


    return asset_dict



def oldBaseDirectory():
    #AAI文件夹
    unreal.EditorAssetLibrary.make_directory('/Game/AAI/Reference/Character')
    unreal.EditorAssetLibrary.make_directory('/Game/AAI/Reference/Pro')
    unreal.EditorAssetLibrary.make_directory('/Game/AAI/Reference/Scenes')
    unreal.EditorAssetLibrary.make_directory('/Game/AAI/Reference/Common')

    #Assets文件夹
    unreal.EditorAssetLibrary.make_directory('/Game/Assets/Common')
    unreal.EditorAssetLibrary.make_directory('/Game/Assets/Character')
    unreal.EditorAssetLibrary.make_directory('/Game/Assets/Pro')
    unreal.EditorAssetLibrary.make_directory('/Game/Assets/Scenes')

    #Shots文件夹
    unreal.EditorAssetLibrary.make_directory('/Game/Shots/Lighting')


    #保存全部创建的文件
    unreal.EditorAssetLibrary.save_directory('/Game')



def baseDirectory():

    #Assets文件夹
    unreal.EditorAssetLibrary.make_directory('/Game/Assets/Common')
    unreal.EditorAssetLibrary.make_directory('/Game/Assets/Character')
    unreal.EditorAssetLibrary.make_directory('/Game/Assets/Pro')
    unreal.EditorAssetLibrary.make_directory('/Game/Assets/Scenes')

    #scenes文件夹
    unreal.EditorAssetLibrary.make_directory('/Game/Scenes/Environment/Common')
    unreal.EditorAssetLibrary.make_directory('/Game/Scenes/Environment/Customized')
    unreal.EditorAssetLibrary.make_directory('/Game/Scenes/Environment/Reuse')
    unreal.EditorAssetLibrary.make_directory('/Game/Scenes/Environment/Tool')
    unreal.EditorAssetLibrary.make_directory('/Game/Scenes/Maps')

    #VFX文件夹
    unreal.EditorAssetLibrary.make_directory('/Game/VFX/Effects/Scene')
    unreal.EditorAssetLibrary.make_directory('/Game/VFX/Effects/Character')
    unreal.EditorAssetLibrary.make_directory('/Game/VFX/Common/BP')
    unreal.EditorAssetLibrary.make_directory('/Game/VFX/Common/NS')
    unreal.EditorAssetLibrary.make_directory('/Game/VFX/Common/Mesh')
    unreal.EditorAssetLibrary.make_directory('/Game/VFX/Common/Material/Function')
    unreal.EditorAssetLibrary.make_directory('/Game/VFX/Common/Texture')

    #Shots文件夹
    unreal.EditorAssetLibrary.make_directory('/Game/Shots/Lighting/Keylight')
    unreal.EditorAssetLibrary.make_directory('/Game/Shots/Lighting/EYE')
    unreal.EditorAssetLibrary.make_directory('/Game/Shots/Lighting/Sky')
    unreal.EditorAssetLibrary.make_directory('/Game/Shots/AAI')


    #保存全部创建的文件
    unreal.EditorAssetLibrary.save_directory('/Game')




def assetExamine(asset_dict):
    bp_root_path = UC.globalConfig.get().ReferencePath
    asset_root_path = UC.globalConfig.get().AssetPath
    ch_bp_path = bp_root_path+'Character'
    pro_bp_path = bp_root_path+'Pro'
    scenes_path = asset_root_path+'Scenes'

    ch_bp_datas=assetFilter('BluePrint',ch_bp_path)
    pro_bp_datas=assetFilter('BluePrint',pro_bp_path)
    scenes_bp_datas=assetFilter('World',scenes_path)


    #获取所有资产名称
    ch_bp_basenames = {}
    for ch_bp_data in ch_bp_datas:
        asset_basename = assetDataToAssetName(ch_bp_data).split('_AAI')[0]
        ch_bp_basenames[asset_basename] = ch_bp_data

    pro_bp_basenames = {}
    for pro_bp_data in pro_bp_datas:
        asset_basename = assetDataToAssetName(pro_bp_data).split('_AAI')[0]
        pro_bp_basenames[asset_basename] = pro_bp_data

    scenes_basenames = {}
    for scenes_bp_data in scenes_bp_datas:
        asset_name = assetDataToAssetName(scenes_bp_data)
        if 'Shade' == asset_name.split('_')[-1]:
            asset_basename = asset_name.split('_Shade')[0]
            scenes_basenames[asset_basename] = scenes_bp_data
        # elif 'VFX' == asset_name.split('_')[-1]:
        #     asset_basename = asset_name.split('_VFX')[0]
        #     scenes_basenames[asset_basename] = scenes_bp_data


    #查找缺失资产
    error_dict = {}
    new_asset_dict = asset_dict
    for cam_index,asset_excel_datas in asset_dict.items():
        for asset_excel_data in asset_excel_datas:
            if '_CH' in asset_excel_data[0]:
                for ch_name,ch_bp_data in ch_bp_basenames.items():
                    if ch_name == asset_excel_data[0].split('_CH')[0]:
                        asset_excel_data.append(ch_bp_data)

                if asset_excel_data[0].split('_CH')[0] not in ch_bp_basenames and asset_excel_data[0] not in error_dict:
                    # print(asset_excel_data)
                    try:
                        error_dict[cam_index].append(asset_excel_data[0])
                    except:
                        error_dict[cam_index] = []
                        error_dict[cam_index].append(asset_excel_data[0])

            if '_Pro' in asset_excel_data[0] :
                for pro_name,pro_bp_data in pro_bp_basenames.items():
                    if pro_name == asset_excel_data[0].split('_Pro')[0]:
                        asset_excel_data.append(pro_bp_data)
                if asset_excel_data[0].split('_Pro')[0] not in pro_bp_basenames and asset_excel_data[0] not in error_dict:
                    # print(asset_excel_data)
                    try:
                        error_dict[cam_index].append(asset_excel_data[0])
                    except:
                        error_dict[cam_index] = []
                        error_dict[cam_index].append(asset_excel_data[0])

            if '_BG' in asset_excel_data[0] :
                for scenes_name,scenes_bp_data in scenes_basenames.items():
                    if scenes_name == asset_excel_data[0].split('_BG')[0]:
                        asset_excel_data.append(scenes_bp_data)
                if asset_excel_data[0].split('_BG')[0] not in scenes_basenames and asset_excel_data[0] not in error_dict:
                    # print(asset_excel_data)
                    try:
                        error_dict[cam_index].append(asset_excel_data[0])
                    except:
                        error_dict[cam_index] = []
                        error_dict[cam_index].append(asset_excel_data[0])


    return error_dict,asset_dict


def assetExamine57(asset_dict):
    # {'Ep000_sc001_001': [['GuanTou_Pro', 1], ['ShiZi_Pro', 5], ['XiaoNvHai_CH', 1], ['ShangChangFeiXu_Nei_BG', 1]}
    bp_root_path = UC.globalConfig.get().AssetPath
    scenes_path = '/Game/Scenes/Maps'
    ch_bp_path = bp_root_path+'Character'
    pro_bp_path = bp_root_path+'Pro'

    ch_bp_datas=assetFilter('BluePrint',ch_bp_path)
    pro_bp_datas=assetFilter('BluePrint',pro_bp_path)
    scenes_map_datas=assetFilter('World',scenes_path)


    #获取所有资产名称
    ch_bp_basenames = {}
    for ch_bp_data in ch_bp_datas:
        asset_basename = assetDataToAssetName(ch_bp_data).split('BP_CH_')[-1]
        ch_bp_basenames[asset_basename] = ch_bp_data

    pro_bp_basenames = {}
    for pro_bp_data in pro_bp_datas:
        asset_basename = assetDataToAssetName(pro_bp_data).split('BP_Pro_')[-1]
        pro_bp_basenames[asset_basename] = pro_bp_data

    scenes_basenames = {}
    for scenes_map_data in scenes_map_datas:
        asset_name = assetDataToAssetName(scenes_map_data)
        if 'Shade' == asset_name.split('_')[-1]:
            asset_basename = asset_name.split('_Shade')[0]
            scenes_basenames[asset_basename] = scenes_map_data
        # elif 'VFX' == asset_name.split('_')[-1]:
        #     asset_basename = asset_name.split('_VFX')[0]
        #     scenes_basenames[asset_basename] = scenes_bp_data


    #查找缺失资产
    error_dict = {}
    for cam_index,asset_excel_datas in asset_dict.items():
        for asset_excel_data in asset_excel_datas:
            if '_CH' in asset_excel_data[0]:
                for ch_name,ch_bp_data in ch_bp_basenames.items():
                    if ch_name == asset_excel_data[0].split('_CH')[0]:
                        asset_excel_data.append(ch_bp_data)

                if asset_excel_data[0].split('_CH')[0] not in ch_bp_basenames and asset_excel_data[0] not in error_dict:
                    # print(asset_excel_data)
                    try:
                        error_dict[cam_index].append(asset_excel_data[0])
                    except:
                        error_dict[cam_index] = []
                        error_dict[cam_index].append(asset_excel_data[0])

            if '_Pro' in asset_excel_data[0] :
                for pro_name,pro_bp_data in pro_bp_basenames.items():
                    if pro_name == asset_excel_data[0].split('_Pro')[0]:
                        asset_excel_data.append(pro_bp_data)
                if asset_excel_data[0].split('_Pro')[0] not in pro_bp_basenames and asset_excel_data[0] not in error_dict:
                    # print(asset_excel_data)
                    try:
                        error_dict[cam_index].append(asset_excel_data[0])
                    except:
                        error_dict[cam_index] = []
                        error_dict[cam_index].append(asset_excel_data[0])

            if '_BG' in asset_excel_data[0] :
                for scenes_name,scenes_map_data in scenes_basenames.items():
                    if scenes_name.split('_BG')[0] == asset_excel_data[0].split('_BG')[0]:
                        asset_excel_data.append(scenes_map_data)
                if asset_excel_data[0].split('_BG')[0] not in scenes_basenames and asset_excel_data[0] not in scenes_basenames:
                    # print(asset_excel_data)
                    try:
                        error_dict[cam_index].append(asset_excel_data[0])
                    except:
                        error_dict[cam_index] = []
                        error_dict[cam_index].append(asset_excel_data[0])
                #在pro文件夹下查找场景道具并收集
                for pro_name,pro_bp_data in pro_bp_basenames.items():       #第四个元素存储场景道具
                    if pro_name == asset_excel_data[0].split('_BG')[0]:
                        asset_excel_data.append(pro_bp_data)


    print('error_dict:',error_dict)
    return error_dict,asset_dict



def assetAssembly(selected_cams,asset_excel_dict,error_list,sequence_type='an',groom_switch=False):
    ch_layer_name = 'CH'
    pro_layer_name = 'Pro'
    bg_layer_name = 'BG'

    ch_tag = 'ch'
    pro_tag = 'pro'

    for cam_all_name,excel_asset_datas in asset_excel_dict.items():
        #当selected_cams存在内容时则只执行列表内的镜头,当不存在时则执行全部镜头
        if cam_all_name in selected_cams or not selected_cams:
            level_asset_data_list = []
            sequnence_asset_find_list = []
            scene_bp_list = []
            asset_count_ch_dict = {}
            asset_count_pro_dict = {}

            cam_split = cam_all_name.split('_')
            ep = cam_split[0]
            sc = cam_split[1]
            cam = cam_split[2]

            an_sequence_path = f'/Game/Shots/{ep}/{sc}/{cam_all_name}/Animation/{cam_all_name}_an'
            ly_sequence_path = f'/Game/Shots/{ep}/{sc}/{cam_all_name}/Animation/Layout/{cam_all_name}_Ly'
            scene_bp_base_path = UC.globalConfig.get().ReferencePath+'Scenes/'

            an_level_path = f'/Game/Shots/{ep}/{sc}/{cam_all_name}/Animation/{cam_all_name}_an_Map'
            final_level_path = f'/Game/Shots/{ep}/{sc}/{cam_all_name}/{cam_all_name}_Map'
            an_level_asset_data = unreal.EditorAssetLibrary().find_asset_data(an_level_path)
            final_level_asset_data = unreal.EditorAssetLibrary().find_asset_data(final_level_path)


            if unreal.EditorAssetLibrary().does_asset_exist(an_sequence_path):
                an_sequence_asset = unreal.EditorAssetLibrary().load_asset(an_sequence_path)
                an_sequence_asset:unreal.MovieSceneSequence
            #当缺少对应资产时跳过循环
            else:
                continue
            if unreal.EditorAssetLibrary().does_asset_exist(ly_sequence_path):
                ly_sequence_asset = unreal.EditorAssetLibrary().load_asset(ly_sequence_path)
                ly_sequence_asset:unreal.MovieSceneSequence
                ly_exist = True
            else:
                ly_exist = False
                pass

            if unreal.EditorAssetLibrary().does_asset_exist(final_level_path):
                unreal.EditorAssetLibrary.save_directory('/Game')
            #当缺少对应资产时跳过循环
            else:
                continue


            level_editor_subsystem.load_level(final_level_asset_data.get_asset().get_path_name())

            #清理场景
            #删除所有通道
            bindings = an_sequence_asset.get_bindings()
            for binding in bindings:
                binding.remove()
            unreal.EditorAssetLibrary.save_directory(an_sequence_path.rsplit('/',1)[0],only_if_is_dirty=False)

            #删除所有场景
            final_world = unreal_editor_subsystem.get_editor_world()
            levels = unreal.EditorLevelUtils().get_levels(final_world)
            new_levels = levels[1:]
            for level in range(len(new_levels)-1,-1,-1):
                level = new_levels[level]
                level_path = level.get_path_name()
                if '_an_Map' not in level_path and '_VFX_Map' not in level_path and '_lt_Map' not in level_path:
                    # print(level_path)
                    unreal.PythonExtensionBPLibrary.remove_level_from_world(level,True,False)

            unreal.EditorAssetLibrary.save_directory('/Game')


            #获取当前level
            current_level = level_editor_subsystem.get_current_level()
            #获取当前world
            current_world = unreal_editor_subsystem.get_editor_world()
            #解锁当前关卡
            unreal.PythonExtensionBPLibrary.unlock_level(current_level)
            #删除所有actor
            actors = editor_actor_subsystem.get_all_level_actors()
            editor_actor_subsystem.destroy_actors(actors)
            # actor_subsystem.set_selected_level_actors(actors)
            # actor_subsystem.delete_selected_actors(current_world)
            
            for excel_asset_data in excel_asset_datas:
                if excel_asset_data[0] in error_list:
                    continue
                if '_BG' in excel_asset_data[0]:
                    #获取场景资产根目录,将所有带有_Shade和_VFX名称的level资产放入world_asset_find_list中
                    level_asset_path = assetDataToAssetPath(excel_asset_data[2])
                    level_folder_assets = unreal.EditorAssetLibrary().list_assets(level_asset_path)
                    for asset_path in level_folder_assets:
                        if excel_asset_data[0].split('_BG')[0] not in asset_path:
                            continue
                        if 'Shade' == asset_path.split('_')[-1] or 'VFX' == asset_path.split('_')[-1] :
                            scene_asset_data = unreal.EditorAssetLibrary().find_asset_data(asset_path)
                            level_asset_data_list.append(scene_asset_data)
                    scene_bp_path = scene_bp_base_path+excel_asset_data[0].split('_BG')[0]
                    if unreal.EditorAssetLibrary().does_directory_exist(scene_bp_path):
                        secene_bp_datas = assetFilter('BluePrint',scene_bp_path)
                        if secene_bp_datas:
                            secene_bp_data = secene_bp_datas[0]
                            scene_bp_list.append(secene_bp_data.get_asset())

                    if len(excel_asset_data) == 4:      #当存在场景道具时,添加到道具字典
                        asset_count_pro_dict[excel_asset_data[3]] = excel_asset_data[1]
                
                elif '_CH' in excel_asset_data[0]:
                    #将asset_data和数量加入到字典
                    asset_count_ch_dict[excel_asset_data[2]] = excel_asset_data[1]

                elif '_Pro' in excel_asset_data[0]:
                    #将asset_data和数量加入到字典
                    asset_count_pro_dict[excel_asset_data[2]] = excel_asset_data[1]


            #添加场景
            if level_asset_data_list:
                for level_asset_data in level_asset_data_list:
                    # find_level_asset_name = assetDataToAssetName(level_asset_data)
                    # des_level_path = final_level_asset_data.get_asset().get_path_name().rsplit('/',1)[0]+'/Modify/Scenes'
                    # asset_level_name = level_asset_data.get_asset().get_name()
                    # asset_level_path = des_level_path+'/'+asset_level_name
                    # #将源关卡复制到Modify目录下
                    # if not unreal.EditorAssetLibrary().does_asset_exist(asset_level_path):
                    #     unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(asset_name=asset_level_name,package_path=des_level_path,original_object=level_asset_data.get_asset())
                    # else:
                    #     unreal.EditorAssetLibrary().delete_asset(asset_level_path)
                    #     unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(asset_name=asset_level_name,package_path=des_level_path,original_object=level_asset_data.get_asset())
                    try:        #场景读取失败时跳过
                        asset_level_path = level_asset_data.get_asset().get_path_name()
                    except:
                        print('读取场景错误,已跳过  '+asset_level_path)
                        continue
                    level_streaming= unreal.EditorLevelUtils().add_level_to_world(final_level_asset_data.get_asset(),level_package_name=asset_level_path,level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
                    # level_streaming.set_editor_property('lock',True)

            unreal.EditorAssetLibrary.save_directory('/Game')

            #打开需要执行操作的level
            if unreal.EditorAssetLibrary().does_asset_exist(an_level_path):
                level_editor_subsystem.load_level(an_level_asset_data.get_asset().get_path_name())
            #当缺少对应资产时打开总关卡
            else:
                level_editor_subsystem.load_level(final_level_asset_data.get_asset().get_path_name())

            #对动画关卡序列添加资产
            #添加道具``
            if asset_count_pro_dict:
                for asset_pro_data,value in asset_count_pro_dict.items():
                    if value > 1:
                        for i in range(value):
                            add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(asset_pro_data.get_asset(),unreal.Vector(0.0, 0.0, 0.0))
                            layers_subsystem.add_actor_to_layer(add_actor, pro_layer_name)      #添加actor到层
                            actorAddTag(add_actor,pro_tag)
                            setLightChannel(add_actor,[False,False,True,False])  #设置灯光通道
                            if sequence_type == 'an':
                                an_sequence_asset.add_possessable(add_actor)
                            elif ly_exist and sequence_type == 'ly':
                                ly_sequence_asset.add_possessable(add_actor)
                    else:
                        add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(asset_pro_data.get_asset(),unreal.Vector(0.0, 0.0, 0.0))
                        layers_subsystem.add_actor_to_layer(add_actor, pro_layer_name)
                        actorAddTag(add_actor,pro_tag)
                        setLightChannel(add_actor,[False,False,True,False])  #设置灯光通道
                        if sequence_type == 'an':
                            an_sequence_asset.add_possessable(add_actor)
                        elif ly_exist and sequence_type == 'ly':
                            ly_sequence_asset.add_possessable(add_actor)

            #添加角色
            if asset_count_ch_dict:
                for asset_ch_data,value in asset_count_ch_dict.items():
                    if value > 1:
                        for i in range(value):
                            #创建actor并添加到关卡序列
                            add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(asset_ch_data.get_asset(),unreal.Vector(0.0, 0.0, 0.0))
                            layers_subsystem.add_actor_to_layer(add_actor, ch_layer_name)
                            actorAddTag(add_actor,ch_tag)
                            setLightChannel(add_actor,[False,True,False,False])  #设v置灯光通道
                            if sequence_type == 'an':
                                an_sequence_asset.add_possessable(add_actor)
                            elif ly_exist and sequence_type == 'ly':
                                ly_sequence_asset.add_possessable(add_actor)
                    else:
                        add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(asset_ch_data.get_asset(),unreal.Vector(0.0, 0.0, 0.0))
                        layers_subsystem.add_actor_to_layer(add_actor, ch_layer_name)
                        actorAddTag(add_actor,ch_tag)
                        setLightChannel(add_actor,[False,True,False,False])  #设置灯光通道
                        if sequence_type == 'an':
                                an_sequence_asset.add_possessable(add_actor)
                        elif ly_exist and sequence_type == 'ly':
                            ly_sequence_asset.add_possessable(add_actor)

            #添加场景BP资产
            if scene_bp_list:  #当打开导入开关时导入BP
                for scene_bp in scene_bp_list:
                    #创建actor并添加到关卡序列
                    add_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(scene_bp,unreal.Vector(0.0, 0.0, 0.0))
                    if sequence_type == 'an':
                        actor_bind = an_sequence_asset.add_possessable(add_actor)
                        #创建可视性track
                        hidden_track = actor_bind.add_track(unreal.MovieSceneVisibilityTrack)
                        hidden_track.set_property_name_and_path('ActorHidden', 'ActorHidden')
                        #创建bool选项框
                        hidden_section = hidden_track.add_section()
                        hidden_section.set_start_frame_bounded(False)
                        hidden_section.set_end_frame_bounded(False)
                        #设置可视性选项框去√
                        hidden_channel = hidden_section.get_all_channels()[0]
                        hidden_channel.set_default(False)
                    elif ly_exist and sequence_type == 'ly':
                        ly_actor_bind = ly_sequence_asset.add_possessable(add_actor)
                        #创建可视性track
                        ly_hidden_track = ly_actor_bind.add_track(unreal.MovieSceneVisibilityTrack)
                        ly_hidden_track.set_property_name_and_path('ActorHidden', 'ActorHidden')
                        #创建bool选项框
                        ly_hidden_section = ly_hidden_track.add_section()
                        ly_hidden_section.set_start_frame_bounded(False)
                        ly_hidden_section.set_end_frame_bounded(False)
                        #设置可视性选项框去√
                        ly_hidden_channel = ly_hidden_section.get_all_channels()[0]
                        ly_hidden_channel.set_default(False)
            
            
            unreal.EditorAssetLibrary.save_directory('/Game')
            #挂载groom到场景角色
            if groom_switch:
                CacheImportTool.groomToChActor(cam_all_name)
                unreal.EditorAssetLibrary.save_directory('/Game')



def actorAddTag(actor,tag):
    current_tags = actor.get_editor_property('tags')
    current_tags.append(tag)
    actor.set_editor_property('tags', current_tags)


#an fbx导入
#根据路径过滤骨骼网格体
def skeletonMeshGet(skeleton_path):

    skeleton_asset=[]
    #列举路径内所有资产
    skeleton_path_assets=assetFilter('Skeleton',skeleton_path)
    #skeleton_path_assets=unreal.EditorAssetLibrary.list_assets(self.skeleton_base_path)
    for skeleton_path_asset in skeleton_path_assets:
        
        asset=skeleton_path_asset.get_asset()
        skeleton_asset.append(asset)
        #if unreal.EditorAssetLibrary.find_asset_data(skeleton_path_asset).get_class():
            #asset_class=unreal.EditorAssetLibrary.find_asset_data(skeleton_path_asset).get_class().get_name()
            #判断资产类型
            #if asset_class == 'Skeleton':
                #skeleton_asset.append(asset)
        
    return skeleton_asset


def assetReplace(asset_path1,asset_path2):

    asset1=unreal.EditorAssetLibrary.find_asset_data(asset_path1).get_asset()
    asset2=unreal.EditorAssetLibrary.find_asset_data(asset_path2).get_asset()


    unreal.EditorAssetLibrary.consolidate_assets(asset1,[asset2])
    unreal.EditorAssetLibrary.delete_asset(asset_path2)


def anFbxImport(anim_path,version=1):   #1:踏星流程,0:财神流程
    fbx_base_path=UC.globalConfig().ShotPath
    type_name=''
    import_sk_error_list = []
    an_file_paths = []
    #当输入的对象为列表时,将列表作为资产,否则当做文件夹处理
    if isinstance(anim_path, list):
        an_file_paths = anim_path
    else:
        # 遍历文件夹内文件
        for dirpath, dirnames, filenames in os.walk(anim_path):
            for filename in filenames:
                #判断后缀名是否为fbx
                if '.fbx' in filename.lower():
                    an_file_path = dirpath+'/'+filename
                    an_file_paths.append(an_file_path)

    for an_file_path in an_file_paths:
        an_file_path = an_file_path.replace('\\','/')
        filename = an_file_path.rsplit('/',1)[-1]
        #判断动画类型
        if '_an_' in filename:
            type_name='_an_'
        elif '_ly_' in filename:
            type_name='_ly_'
        #初始化命名
        ep=''
        sc=''
        mesh_name=''
        sc_all_name=''
        
        anim_fbx_name=filename.split('.')[0]
        anim_fbx=an_file_path                       #合并文件路径和文件名称
        ep=filename.split('_')[0]                   #获取ep名称
        sc=filename.split('_')[1]                   #获取sc主名称
        sc_all_name=filename.rsplit(type_name)[0]      #获取sc全名称


        if not sc_all_name:
            break
        #判断后缀名
        if 'Pro' in filename:
            mesh_name=filename.rsplit(type_name)[-1].split('_Pro',1)[0]
        elif 'CH' in filename:
            mesh_name=filename.rsplit(type_name)[-1].split('_CH',1)[0]
        elif 'BG' in filename:
            mesh_name=filename.rsplit(type_name)[-1].split('_BG',1)[0]
        else:
            continue


        fbx_create_path=f'{fbx_base_path}{ep}/{sc}/'     #创建基础文件夹路径

        # sc_section_names=sc_all_name.split('_')

        # #添加分段文件夹路径
        # if len(sc_section_names)>2:
        #     sc_sub_name=ep+'_'+sc
        #     for sc_section_name in sc_section_names[2:]:
        #         sc_sub_name+='_'+sc_section_name
        #         fbx_create_sub_path='/'+sc_sub_name+'_an'

        if type_name=='_an_':
            fbx_create_path += sc_all_name+'/Animation'
        elif type_name=='_ly_':
            fbx_create_path += sc_all_name+'/Animation/Layout'

        #获取骨骼网格体路径
        if version:
            skeleton_base_path = UC.globalConfig().AssetPath
            split_prefix = 'SK_'
        else:
            skeleton_base_path = UC.globalConfig().ReferencePath
            split_prefix = 'UE_'
        mesh_type=None
        if '_Pro' in filename:
            mesh_type='Pro'
            skeleton_base_path+='Pro'
        elif '_CH' in filename:
            mesh_type='CH'
            skeleton_base_path+='Character'
        elif '_BG' in filename:
            mesh_type='BG'
            if version:
                skeleton_base_path = '/Game/Scenes/Maps'
            else:
                skeleton_base_path+='Scenes'

        #遍历路径寻找骨骼网格体
        skeleton_meshs=skeletonMeshGet(skeleton_base_path)
        # print(skeleton_meshs)
        import_done = False
        for skeleton_mesh in skeleton_meshs:
            skeleton_mesh:unreal.SkeletalMesh
            skeleton_base_name=None
            if mesh_type=='Pro':
                skeleton_base_name=skeleton_mesh.get_name().split(split_prefix)[-1].split('_Skeleton')[0]
            elif mesh_type=='CH':
                skeleton_base_name=skeleton_mesh.get_name().split(split_prefix)[-1].split('_Skeleton')[0]
            elif mesh_type=='BG':
                skeleton_base_name=skeleton_mesh.get_name().split(split_prefix)[-1].split('_Skeleton')[0]
            # print(mesh_name,skeleton_base_name)
            if mesh_name == skeleton_base_name:
                #如果动画序列已存在,则删除并清除缓存
                an_asset_path = fbx_create_path+'/'+anim_fbx_name
                if unreal.EditorAssetLibrary.does_asset_exist(an_asset_path):
                    unreal.EditorAssetLibrary.delete_asset(an_asset_path)
                    # print(f'{an_asset_path} 已存在,执行删除')
                    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
                    asset_registry.scan_modified_asset_files([])
                print(mesh_name,skeleton_mesh.get_name())

                #导入动画序列
                fbxImport.animSequenceImport(anim_fbx,fbx_create_path,skeleton_mesh)

                #如果存在ly文件,则使用an文件替换
                if type_name=='_an_':
                    ly_path=fbx_create_path+'/'+anim_fbx_name.replace('_an_','_ly_')
                    an_path=fbx_create_path+'/'+anim_fbx_name
                    # print(ly_path)
                    if unreal.EditorAssetLibrary.does_asset_exist(ly_path):
                        assetReplace(an_path,ly_path)
                        print(ly_path)

                if unreal.EditorAssetLibrary.does_asset_exist(an_asset_path):   #当资产未找到时报错
                    import_done = True

                #保存全部创建的文件
                unreal.EditorAssetLibrary.save_directory('/Game/Shots')
        if not import_done:
            import_sk_error_list.append(filename)
    

    return import_sk_error_list



#动画序列挂载到关卡序列
def pathToSequenceAnim(path, version=0):    #0 an,1 ly
    asset_list = unreal.EditorAssetLibrary.list_assets(path)
    start_offset = UC.globalConfig.get().start_offset

    anim_list=[]
    unuse_an_assets = []
    level_sequnce=None
    old_anims=[]
    
    for asset in asset_list:
        asset_class=unreal.EditorAssetLibrary.find_asset_data(asset).get_class().get_name()
        asset_name=str(unreal.EditorAssetLibrary.find_asset_data(asset).asset_name)

        if version==0:
            if asset_class=='AnimSequence' and '_an' in asset_name:
                anim_list.append(unreal.EditorAssetLibrary.find_asset_data(asset).get_asset())
            if asset_class=='LevelSequence' and '_an' in asset_name:
                level_sequnce=unreal.EditorAssetLibrary.find_asset_data(asset).get_asset()
        if version==1:
            if asset_class=='AnimSequence' and '_ly' in asset_name:
                anim_list.append(unreal.EditorAssetLibrary.find_asset_data(asset).get_asset())
            if asset_class=='LevelSequence' and '_Ly' in asset_name:
                level_sequnce=unreal.EditorAssetLibrary.find_asset_data(asset).get_asset()

    unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(level_sequnce)


    #获取当前打开的关卡序列
    export_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()

    #获取场景路径
    sequence_path = export_sequence.get_path_name()
    level_path = sequence_path.split('Animation')[0]+sequence_path.split('.')[-1].replace('_an','_Map')
    # level_asset = unreal.EditorAssetLibrary.find_asset_data(level_path).get_asset()

    #解锁sequence
    unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(False)

    possessables = export_sequence.get_possessables()
    possessables.sort(key=lambda x: str(x.get_display_name()))  #根据名称重新排序
    frame_range = export_sequence.get_playback_range()
    frame_end = frame_range.get_end_frame()
    frame_start = frame_range.get_start_frame()

    track_base_name = None

    for possessable in possessables:
        if 'BP' not in str(possessable.get_display_name()):         #判断名称是否符合规则
            continue
        #获取bp名称
        try:        #当获取名称报错时打开一遍对应场景
            track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
        except:
            unreal.LevelEditorSubsystem().load_level(level_path)
            #打开关卡序列
            unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(level_sequnce)
            try:
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue

        #判断命名规范
        if '_AAI' in track_bpname:
            track_base_name = track_bpname.split('_AAI',1)[0]
        elif 'BP_CH_' in track_bpname:
            track_base_name = track_bpname.split('BP_CH_',1)[-1]
        elif 'BP_Pro_' in track_bpname:
            track_base_name = track_bpname.split('BP_Pro_',1)[-1]
        else:
            #名称不符合,跳过
            continue
        type_name=''
        #遍历动画资产
        for anim_asset in anim_list:
            anim_name = anim_asset.get_name()
            #通过名称判断动画类型
            if '_ly_' in anim_name:
                type_name='_ly_'
            elif '_an_' in anim_name:
                type_name='_an_'
            if '_CH' in anim_name:
                anim_base_name=anim_name.split('_CH')[0].split(type_name)[-1]
            elif '_Pro' in anim_name:
                anim_base_name=anim_name.split('_Pro')[0].split(type_name)[-1]
            elif '_BG' in anim_name:
                anim_base_name=anim_name.split('_BG')[0].split(type_name)[-1]
            else:
                continue

            # print(track_base_name,anim_base_name)
            break_switch = False
            if anim_base_name.lower()==track_base_name.lower():
                if anim_asset in old_anims:     #重复动画跳过
                    continue
                #将possessable及其子possessable一起挂载上动画
                sub_possessables = possessable.get_child_possessables()
                sub_possessables.append(possessable)
                for possessable in sub_possessables:
                    spawnable_old_tracks=possessable.get_tracks()
                    for spawnable_old_track in spawnable_old_tracks:
                        if spawnable_old_track.get_class().get_name() == 'MovieSceneSkeletalAnimationTrack':
                            possessable.remove_track(spawnable_old_track)
                    animation_track=possessable.add_track(unreal.MovieSceneSkeletalAnimationTrack)
                    #track设置为计算最近分段
                    eval_options = animation_track.get_editor_property('eval_options')
                    eval_options.set_editor_property('eval_nearest_section', True)
                    eval_options.set_editor_property('evaluate_in_postroll', False)
                    eval_options.set_editor_property('evaluate_in_preroll', False)
                    animation_track.set_editor_property('eval_options',eval_options)

                    animation_section=animation_track.add_section()
                    animation_section:unreal.MovieSceneSkeletalAnimationSection
                    animation_section.params.animation=anim_asset
                    #设置section为保持状态
                    animation_section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE)
                    #设置帧范围
                    an_frame = anim_asset.get_editor_property("number_of_sampled_frames")
                    start_frame = frame_start + start_offset
                    end_frame = start_frame + an_frame
                    animation_section.set_range(start_frame,end_frame)
                    
                    old_anims.append(anim_asset)
                    break_switch = True
                    break
                if break_switch:
                    break

            #保存全部创建的文件
            unreal.EditorAssetLibrary.save_directory('/Game/Shots')  

        unuse_an_assets = [anim for anim in anim_list if anim not in old_anims]
          

    #锁定sequence
    # unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(True)

    #根据序列类型替换render Sequence的序列
    if version==0:      #删除ly序列,添加an序列
        render_seq_path = sequence_path.split('Animation')[0]+sequence_path.split('.')[-1].replace('_an','_Render')
        an_seq = unreal.EditorAssetLibrary.find_asset_data(sequence_path).get_asset()
        render_seq = unreal.EditorAssetLibrary.find_asset_data(render_seq_path).get_asset()
        unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(render_seq)
        #获取当前打开的关卡序列
        current_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        seq_tracks = current_sequence.get_tracks()
        for track in seq_tracks:
            try:
                seq_name = track.get_sections()[0].get_sequence().get_name()
                if '_Ly' in seq_name or '_an' in seq_name:
                    current_sequence.remove_track(track)
            except:
                pass
        render_track=current_sequence.add_track(unreal.MovieSceneSubTrack)
        render_section=render_track.add_section()
        render_section.set_sequence(an_seq)
        render_section.set_range(an_seq.get_playback_start(),an_seq.get_playback_end())
    
    elif version==1:      #删除an序列,添加ly序列
        render_seq_path = sequence_path.split('Animation')[0]+sequence_path.split('.')[-1].replace('_Ly','_Render')
        ly_seq = unreal.EditorAssetLibrary.find_asset_data(sequence_path).get_asset()
        render_seq = unreal.EditorAssetLibrary.find_asset_data(render_seq_path).get_asset()
        unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(render_seq)
        #获取当前打开的关卡序列
        current_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        seq_tracks = current_sequence.get_tracks()
        for track in seq_tracks:
            try:
                seq_name = str(track.get_sections()[0].get_sequence().get_name())
                if '_an' in seq_name or '_Ly' in seq_name:
                    current_sequence.remove_track(track)
            except:
                pass
        render_track=current_sequence.add_track(unreal.MovieSceneSubTrack)
        render_section=render_track.add_section()
        render_section.set_sequence(ly_seq)
        render_section.set_range(ly_seq.get_playback_start(),ly_seq.get_playback_end())

    #保存全部创建的文件
    unreal.EditorAssetLibrary.save_directory('/Game/Shots')

    #返回未被挂载的多余动画资产
    return unuse_an_assets




def excelCreate(error_list,save_path = r"d:\Desktop\an_import_error.xlsx"):

    data_dict = {}
    for line in error_list:
        if '_ly' in line:
            sc = line.split('_ly')[0]
        elif '_an' in line:
            sc = line.split('_an')[0]
        if '_CH' in line:
            basename = line.split('_',4)[-1].rsplit('_CH',1)[0]+'_CH'
            try:
                if basename not in [k for d in data_dict[sc] for k in d]:
                    data_dict[sc].append({basename: 1})
                else:
                    for d in data_dict[sc]:
                        if basename == list(d.keys())[0]:
                            d[basename] += 1
            except:
                data_dict[sc] = []
                data_dict[sc].append({basename: 1})
        if '_BG' in line:
            basename = line.split('_',4)[-1].rsplit('_BG',1)[0]+'_BG'
            try:
                if basename not in [k for d in data_dict[sc] for k in d]:
                    data_dict[sc].append({basename: 1})
                else:
                    for d in data_dict[sc]:
                        if basename == list(d.keys())[0]:
                            d[basename] += 1
            except:
                data_dict[sc] = []
                data_dict[sc].append({basename: 1})
        if '_Pro' in line:
            basename = line.split('_',4)[-1].rsplit('_Pro',1)[0]+'_Pro'
            try:
                if basename not in [k for d in data_dict[sc] for k in d]:
                    data_dict[sc].append({basename: 1})
                else:
                    for d in data_dict[sc]:
                        if basename == list(d.keys())[0]:
                            d[basename] += 1
            except:
                data_dict[sc] = []
                data_dict[sc].append({basename: 1})


    # 创建工作簿和工作表
    wb = op.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 15

    # 当前行号
    row_num = 1

    for seq, contents in data_dict.items():
        index = 0
        for content in contents:
            for basename, count in content.items():
                if index == 0:               # 第一个内容：写序号和内容
                    ws.cell(row=row_num, column=1, value=seq)
                    ws.cell(row=row_num, column=2, value=basename)
                    ws.cell(row=row_num, column=3, value=count)
                    index = 1
                else:                      # 后续内容：只写内容，A列留空
                    ws.cell(row=row_num, column=2, value=basename)
                    ws.cell(row=row_num, column=3, value=count)
                row_num += 1

    # 保存文件
    
    wb.save(save_path)


def bpMissExcelCreate(bp_miss_dict,save_path = r"d:\Desktop\bp_miss_error.xlsx"):



    # 创建工作簿和工作表
    wb = op.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 30
    ws.column_dimensions['C'].width = 15

    # 当前行号
    row_num = 1

    for seq, contents in bp_miss_dict.items():
        index = 0
        for content in contents:
            # for basename, count in content.items():
            if index == 0:               # 第一个内容：写序号和内容
                ws.cell(row=row_num, column=1, value=seq)
                ws.cell(row=row_num, column=2, value=content)
                # ws.cell(row=row_num, column=3, value=count)
                index = 1
            else:                      # 后续内容：只写内容，A列留空
                ws.cell(row=row_num, column=2, value=content)
                # ws.cell(row=row_num, column=3, value=count)
            row_num += 1

    # 保存文件
    
    wb.save(save_path)




def setLightChannel(actor,channels=[True,False,False,False]):
    actor_component = actor.get_component_by_class(component_class=unreal.SkeletalMeshComponent)
    if not actor_component:
        actor_component = actor.get_component_by_class(component_class=unreal.GeometryCacheComponent)
    if not actor_component:
        actor_component = actor.get_component_by_class(component_class=unreal.GroomComponent)
    new_channels = unreal.LightingChannels()
    new_channels.set_editor_property('channel0', channels[0])  
    new_channels.set_editor_property('channel1', channels[1])   
    new_channels.set_editor_property('channel2', channels[2])  
    new_channels.set_editor_property('channel3', channels[3])  
    actor_component.set_editor_property('lighting_channels', new_channels)



def camToPreview(path):

    

    # path = '/Game/Shots/EP001/sc001'

    path_split = path.split('/')
    ep_path = path.rsplit('/',1)[0]
    preview_name = f'{path_split[2]}_{path_split[3]}_Preview'
    preview_path = f'{ep_path}/Preview/{preview_name}'

    seq_datas = assetFilter('LevelSequence',path)
    render_seq_datas = [item for item in seq_datas if '_Render' in assetDataToAssetName(item)]
    render_seq_datas = sorted(render_seq_datas, key=lambda x: assetDataToAssetName(x))

    start_offset = UC.globalConfig.get().start_offset
    end_offset = UC.globalConfig.get().end_offset
    all_offset = start_offset+end_offset


    #删除旧preview track
    if editor_asset_subsystem.does_asset_exist(preview_path):
        preview_sequence=unreal.EditorAssetLibrary.find_asset_data(preview_path).get_asset()
        old_tracks=preview_sequence.get_tracks()
        for old_track in old_tracks:
            preview_sequence.remove_track(old_track)
    #创建preview_sequence
    else:
        preview_sequence=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=preview_name,package_path=f'{ep_path}/Preview',asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
        preview_sequence:unreal.LevelSequence
        preview_sequence.set_display_rate((25,1))
        preview_sequence=unreal.EditorAssetLibrary.find_asset_data(preview_path).get_asset()

    shot_track = preview_sequence.add_track(unreal.MovieSceneCinematicShotTrack)
    # shot_track2 = preview_sequence.add_track(unreal.MovieSceneCinematicShotTrack)

    i=1
    start_frame = 0
    end_frame = 0
    for render_seq_data in render_seq_datas:

        seq = render_seq_data.get_asset()
        end_key = seq.get_playback_end()-all_offset
        end_frame+=end_key
        # current_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()

        shot_section = shot_track.add_section()
        if i % 2 == 1:
            shot_section.set_row_index(0)
        else:
            shot_section.set_row_index(1)
        shot_section.set_sequence(seq)
        params = shot_section.get_editor_property("parameters")
        params.start_frame_offset = unreal.FrameNumber(960*start_offset)    #9600等于10帧
        shot_section.set_editor_property("parameters", params)
        # print(start_frame,end_key)
        shot_section.set_range(start_frame,end_frame)
        preview_sequence.set_playback_end(end_frame)

        start_frame+=end_key
        i+=1

    unreal.EditorAssetLibrary.save_directory('/Game')