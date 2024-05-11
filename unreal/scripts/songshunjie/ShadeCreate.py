# -*- coding: utf-8 -*-

import unreal

import shutil
import os
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

from dayu_widgets.label import MLabel
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.progress_bar import MProgressBar
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application


print('ShadeCreate')



class mw(QtWidgets.QWidget, MFieldMixin):


    fbx_name=''
    mat_path='/Game/Assets/Common/Material'
    cloth_link_dict={'ARMS':'ARMS_Map','BaseColor':'BaseColor_Map','Normal':'Normal_Map'}
    skin_link_dict={'ARMS':'ARMS_Map','BaseColor':'BaseColor','Normal':'NormalMap','DetailNormal':'DetailMap','Specular':'SpecularMap','Roughness':'Roughness_MAIN','AO':'OccMap','CV':'Cavity_MAIN','CV':'Cavity_MAIN'}
    
    all_link_dict={'M_CH_SkinTest':skin_link_dict,'M_CH_ClothTest':cloth_link_dict}

    def __init__(self, parent=None):
            super().__init__(parent)

            self.uii()
            
    def uii(self):   
        self.setWindowTitle('材质FBX导入')
        self.resize(320,120)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        self.flie_import=MLineEdit().file().medium()
        self.flie_import.setPlaceholderText(self.tr("选择FBX路径"))
        create_folder=MPushButton(text="导入FBX并自动赋予材质")
        create_folder.clicked.connect(self.importAsset)
        create_texture=MPushButton(text="自动为选中网格添加贴图")
        create_texture.clicked.connect(self.giveTexture)

        self.progress = MProgressBar().auto_color()
        self.progress.hide()
        
        self.error_lable=MLabel('')
        self.error_lable.setStyleSheet("color: red")

        folder_lay.addWidget(self.flie_import)
        folder_lay.addWidget(create_folder)
        folder_lay.addWidget(create_texture)
        folder_lay.addWidget(self.progress)
        folder_lay.addWidget(self.error_lable)

        
        lay.addLayout(folder_lay)
        self.setLayout(lay)


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

    #fbx导入任务创建
    def buildImportTask(self,filename,path,options=None):
        task=unreal.AssetImportTask()
        task.set_editor_property('automated',True)
        task.set_editor_property('destination_name','')
        task.set_editor_property('destination_path',path)
        task.set_editor_property('filename',filename)
        task.set_editor_property('replace_existing',True)
        task.set_editor_property('save',True)
        task.set_editor_property('options',options)
        return task


    def importAsset(self):
        
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')
        #获取FBX路径
        fbx=self.flie_import.text()
        #获取FBX名称
        self.fbx_name=fbx.rsplit('.',1)[0].split('/')[-1]
        fbx_create_path='/Game/Assets/Character/'+self.fbx_name+'/Mesh'
        if fbx.rsplit('.')[-1]=='fbx':
            #显示进度条
            self.progress.show()
            self.progress.setValue(10)
            unreal.EditorAssetLibrary.make_directory('/Game/Assets/Character/'+self.fbx_name+'/Mesh')
            unreal.EditorAssetLibrary.make_directory('/Game/Assets/Character/'+self.fbx_name+'/Material')
            unreal.EditorAssetLibrary.make_directory('/Game/Assets/Character/'+self.fbx_name+'/Texture')
            sataic_mesh_task=self.buildImportTask(fbx,fbx_create_path,self.buildStaticMeshImportOptions())
            self.executeImportTasks([sataic_mesh_task])

            self.error_lable.setText('')

            self.progress.setValue(40)

            #生成并赋予材质实例
            self.materialInstance()

            self.progress.setValue(100)
            

        else :
            self.progress.hide()
            self.error_lable.setText('导入失败，请确认导入文件是否正确')

            
    def executeImportTasks(self,task):
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(task)


    def materialInstance(self):

        matI_path='/Game/Assets/Character/'+self.fbx_name+'/Material'
        fbx_path='/Game/Assets/Character/'+self.fbx_name+'/Mesh'

        mats=unreal.EditorAssetLibrary.list_assets(self.mat_path)
        fbx_mats=unreal.EditorAssetLibrary.list_assets(fbx_path)
        fbx_meshs=unreal.EditorAssetLibrary.list_assets(fbx_path)

        fbx_mat_list=[]
        fbx_assets=[]
        matIs=[]

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

            if mat_class=='Material':
                #遍历模型材质
                for fbx_mat_name in fbx_mat_list:
                    #判断材质后缀名称是否对应
                    switch=0
                    if 'BoLiTi' in fbx_mat_name:
                        if mat_name=='M_CH_EyeOcclusion':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue
                    
                    elif 'YanJian' == fbx_mat_name.rsplit('_')[-1] :
                        if mat_name=='M_lacrimal_fluid':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue
                    
                    elif 'Skin' in fbx_mat_name :
                        if mat_name=='M_CH_SkinTest':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    elif 'YanQiu' in fbx_mat_name :
                        if mat_name=='M_CH_YanQiu':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue
                    
                    elif 'KouQiang' in fbx_mat_name :
                        if mat_name=='M_KouQiang':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue
                    
                    elif 'JieMao' in fbx_mat_name :
                        if mat_name=='JieMao':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    elif 'YanJian_TouMing' in fbx_mat_name :
                        if mat_name=='Hide_Mask':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    elif 'MeiMao' in fbx_mat_name :
                        if mat_name=='JieMao':
                            matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                            matI_create.set_editor_property('parent',mat_asset)
                            switch=1
                        else:
                            continue

                    elif not unreal.EditorAssetSubsystem().does_asset_exist(matI_path+'/'+fbx_mat_name) and mat_name=='M_CH_ClothTest':
                        matI_create=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=fbx_mat_name,package_path=matI_path,asset_class=unreal.MaterialInstanceConstant,factory=unreal.MaterialInstanceConstantFactoryNew())
                        matI_create.set_editor_property('parent',mat_asset)
                        switch=1
                    
                    
                        
                    #替换模型材质球   
                    if switch==1:   
                        for fbx_asset in fbx_assets:
                            i=0
                            while i<50:
                                try:
                                    mesh_index_mat=unreal.StaticMesh.get_material(fbx_asset,i)
                                    if mesh_index_mat.get_name()==matI_create.get_name():
                                        unreal.StaticMesh.set_material(fbx_asset,i,matI_create)
                                    print(mesh_index_mat.get_name(),matI_create.get_name())
                                except:
                                    break
                                i+=1
        #删除旧材质
        self.deletOldMat(fbx_path)


        unreal.EditorAssetLibrary.save_directory('/Game')
        
    def deletOldMat(self,asset_path):                            
        del_mats=unreal.EditorAssetLibrary.list_assets(asset_path)
        for del_mat in del_mats:
            mat_class=unreal.EditorAssetLibrary.find_asset_data(del_mat).asset_class_path.asset_name
            if mat_class=='Material':
                unreal.EditorAssetLibrary.delete_asset(del_mat)


    def giveTexture(self):
        #获取所选mesh
        select_meshs=unreal.EditorUtilityLibrary.get_selected_assets()
        for mesh in select_meshs:
            #获取mesh材质名称
            if mesh.get_class().get_name()=='StaticMesh':
                texture_assets=[]
                Texture_path=mesh.get_path_name().rsplit('/',2)[0]+'/Texture'
                Texture_assets_data=unreal.EditorAssetLibrary.list_assets(Texture_path)
                for Texture_asset_data in Texture_assets_data:
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
                            if texture_asset.get_name().split('_')[-2]==mesh_index_mat.get_name().split('_')[-1]:
                                print(texture_asset.get_name())
                                #遍历材质参数字典内容
                                for mat,par_dict in self.all_link_dict.items():
                                    if parent_mat.get_name()==mat:
                                        for tex_class,par_name in par_dict.items():
                                            if texture_asset.get_name().split('_')[-1]==tex_class:
                                                unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mesh_index_mat,par_name,texture_asset)

                    if not mesh_index_mat:
                        break
                    i+=1





def start():
    with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
   with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))