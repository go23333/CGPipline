# -*- coding: utf-8 -*-

import unreal

import shutil
import os
import json




class fbxImport():
    
    @classmethod
    def staticMeshImport(cls,fbx,fbx_create_path):
        sataic_mesh_task=cls.buildImportTask(cls,fbx,fbx_create_path,cls.buildStaticMeshImportOptions(cls))
        cls.executeImportTasks(cls,[sataic_mesh_task])

    @classmethod
    def animSequenceImport(cls,fbx,fbx_create_path,skeleton_mesh):       
        anim_sequence_task=cls.buildImportTask(cls,fbx,fbx_create_path,cls.buildAnimSequenceImportOptions(cls,skeleton_mesh))
        cls.executeImportTasks(cls,[anim_sequence_task])

    @classmethod
    def matICreate(cls,Common_path,fbx_path,matI_tar_path):

        mats=unreal.EditorAssetLibrary.list_assets(Common_path)
        fbx_mats=unreal.EditorAssetLibrary.list_assets(fbx_path)
        fbx_meshs=unreal.EditorAssetLibrary.list_assets(fbx_path)


        fbx_mat_list=[]
        fbx_assets=[]

        #获取fbx材质名称
        for fbx_mat_name in fbx_mats:
            fbx_mat_asset=unreal.EditorAssetLibrary.find_asset_data(fbx_mat_name).get_asset()
            fbx_mat_info=unreal.EditorAssetLibrary.find_asset_data(fbx_mat_name)
            fbx_mat_class=fbx_mat_info.asset_class_path.asset_name
            if fbx_mat_class=='Material':
                fbx_mat_list.append(fbx_mat_asset.get_name())
        

        #获取mesh
        for fbx_mesh in fbx_meshs:
            mesh_asset=unreal.EditorAssetLibrary.find_asset_data(fbx_mesh).get_asset()
            mesh_info=unreal.EditorAssetLibrary.find_asset_data(fbx_mesh)
            mesh_class=mesh_info.asset_class_path.asset_name
            if mesh_class=='StaticMesh':
                fbx_assets.append(mesh_asset)

            
        #创建材质实例并赋予模型
        for mat in mats:
            mat_asset=unreal.EditorAssetLibrary.find_asset_data(mat).get_asset()
            mat_info=unreal.EditorAssetLibrary.find_asset_data(mat)
            mat_class=mat_info.asset_class_path.asset_name
            mat_name=mat_asset.get_name()
            
            #判断asset类型是否为材质或材质实例
            if mat_class=='Material' or mat_class=='MaterialInstanceConstant':
                print(mat_name)
                #遍历模型材质
                for fbx_mat_name in fbx_mat_list:
                    #材质球生成开关，生成材质球后值为1
                    switch=0
                    #判断材质后缀名称是否对应，对应后创建对应材质球
                    if 'BoLiTi' in fbx_mat_name:
                        if mat_name=='M_CH_EyeOcclusion':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue
                    
                    elif 'YanJian' == fbx_mat_name.rsplit('_')[-1] :
                        if mat_name=='M_lacrimal_fluid':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue
                    

                    elif 'YanQiu' in fbx_mat_name :
                        if mat_name=='M_CH_YanQiu':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue
                    
                    elif 'KouQiang' in fbx_mat_name :
                        if mat_name=='M_CH_KouQiang':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue
                    
                    elif 'JieMao' in fbx_mat_name :
                        if mat_name=='M_CH_JieMao':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    elif 'YanJian_TouMing' in fbx_mat_name :
                        if mat_name=='Hide_Mask':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    elif 'MeiMao' in fbx_mat_name :
                        if mat_name=='JieMao':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    #判断材质球类型为皮肤时,使用MI_MaterialBlender_Skin材质球
                    elif 'Skin' in fbx_mat_name :
                        if mat_name=='MI_MaterialBlender_Skin':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    elif '_Hair' in fbx_mat_name :
                        if mat_name=='M_Character_HairMaster1':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    #其他材质球统一使用MI_MaterialBlender_Cloth材质球
                    elif not unreal.EditorAssetSubsystem().does_asset_exist(matI_tar_path+'/'+fbx_mat_name) and mat_name=='MI_MaterialBlender_Cloth':
                        matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_tar_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                        matI_create.set_editor_property('parent',mat_asset)
                        switch=1

                    
                    
                        
                    #替换模型材质球   
                    if switch==1:   
                        for fbx_asset in fbx_assets:
                            i=0
                            while i<127:
                                try:
                                    mesh_index_mat=unreal.StaticMesh.get_material(fbx_asset,i)
                                    if mesh_index_mat.get_name()==matI_create.get_name():
                                        unreal.StaticMesh.set_material(fbx_asset,i,matI_create)
                                    # print(mesh_index_mat.get_name(),matI_create.get_name())
                                except:
                                    break
                                i+=1
        #删除旧材质
        cls.deletOldMat(cls,fbx_path)

        unreal.EditorAssetLibrary.save_directory('/Game')

        cls.giveTexture(fbx_assets)

    @classmethod
    def importTexture(cls,texture_dict:dict,destination_path):
        
        for shade_name,type_dict in texture_dict.items():
            for texture_type,textures in type_dict.items():
                
                texture =textures[0]
                #构建贴图导入任务
                task=cls.buildImportTask(cls,texture,destination_path)
                unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
                #获取无UDIM后缀的贴图路径
                base_color_path=destination_path+'/'+texture.rsplit('/',1)[-1].split('.')[0]
                
                if unreal.EditorAssetSubsystem().does_asset_exist(base_color_path):
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


    @classmethod
    def giveTexture(cls,meshs):
        #创建存有材质球和贴图类型信息的字典
        cloth_link_dict={'ARMS':'ARMS_Map','BaseColor':'BaseColor_Map','Normal':'Normal_Map','BaseNormal':'BaseNormalMap','Anisotropy':'Anisotropy_Map','Emmissive':'Emmissive_Map'}
        skin_link_dict={'ARMS':'ARMS','BaseColor':'BaseColor','Normal':'NormalMap','DetailNormal':'DetailMap','Specular':'SpecularMap','Roughness':'ARMS','CV':'Cavity_MAIN','SSSMask':'SSSMask'}
        all_link_dict={'MI_MaterialBlender_Skin':skin_link_dict,'MI_MaterialBlender_Cloth':cloth_link_dict}
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
                        #遍历贴图
                        for texture_asset in texture_assets:
                            #判断贴图关键字是否与模型的材质关键字对应
                            if texture_asset.get_name().split('_')[-2]==mesh_index_mat.get_name().split('_')[-1]:
                                # print(texture_asset.get_name())
                                #遍历材质参数字典内容
                                for mat,parameter_dict in all_link_dict.items():
                                    if parent_mat.get_name()==mat:
                                        for tex_class,parameter_name in parameter_dict.items():
                                            #不区分大小写判断贴图后缀名是否与贴图类型对应
                                            if texture_asset.get_name().split('_')[-1].lower()==tex_class.lower():
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
    
    def buildAnimSequenceImportOptions(self,skeleton_mesh):
        options=unreal.FbxImportUI()

        #动画序列导入设置
        options.import_animations=True
        options.skeleton=skeleton_mesh

        options.import_materials=False
        options.import_textures=False
        options.import_as_skeletal=False

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