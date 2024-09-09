# -*- coding: utf-8 -*-

import unreal

import os
import json
import sys

import UnrealPipeline.core.uSTools as uSTools

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



print('ShadeCreate1.1')



class mw(QtWidgets.QWidget, MFieldMixin):


    fbx_name=''
    mat_path='/Game/Assets/Common/Material'
    # cloth_link_dict={'ARMS':'ARMS_Map','BaseColor':'BaseColor_Map','Normal':'Normal_Map'}
    # skin_link_dict={'ARMS':'ARMS','BaseColor':'BaseColor','Normal':'NormalMap','DetailNormal':'DetailMap','Specular':'SpecularMap','Roughness':'Roughness_MAIN','AO':'OccMap','CV':'Cavity_MAIN','CV':'Cavity_MAIN'}
    
    # all_link_dict={'M_CH_SkinTest':skin_link_dict,'M_CH_ClothTest':cloth_link_dict}

    def __init__(self, parent=None):
            super().__init__(parent)
            self.uii()
            
    def uii(self):   
        self.setWindowTitle('角色材质FBX导入')
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


    def importAsset(self):
        
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')
        #获取FBX路径
        fbx=self.flie_import.text()
        #获取FBX名称
        self.fbx_name=fbx.rsplit('.',1)[0].split('/')[-1]
        self.mesh_folder_name=self.fbx_name.split('_CH_')[0]+'_CH'
        fbx_create_path='/Game/Assets/Character/'+self.mesh_folder_name+'/Mesh'
        if fbx.rsplit('.')[-1]=='fbx':
            #显示进度条
            self.progress.show()
            self.progress.setValue(10)

            
            unreal.EditorAssetLibrary.make_directory(fbx_create_path)
            unreal.EditorAssetLibrary.make_directory('/Game/Assets/Character/'+self.mesh_folder_name+'/Material')
            unreal.EditorAssetLibrary.make_directory('/Game/Assets/Character/'+self.mesh_folder_name+'/Texture')

            uSTools.fbxImport.staticMeshImport(fbx,fbx_create_path,'sataic_mesh')
            #设置进度
            self.error_lable.setText('')
            self.progress.setValue(35)

            json_path=fbx.rsplit('.')[0]+'.json'
            if os.path.exists(json_path):
                with open(json_path,'r') as js_file:
                    json_data=json.load(js_file)
                if json_data :
                    uSTools.fbxImport.importTexture(json_data,'/Game/Assets/Character/'+self.mesh_folder_name+'/Texture')
            self.progress.setValue(65)

            #生成并赋予材质实例
            self.materialInstance()

            self.progress.setValue(100)      

        else :
            self.progress.hide()
            self.error_lable.setText('导入失败，请确认导入文件是否正确')

            
    def executeImportTasks(self,task):
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(task)


    def materialInstance(self):

        matI_path='/Game/Assets/Character/'+self.mesh_folder_name+'/Material'
        fbx_path='/Game/Assets/Character/'+self.mesh_folder_name+'/Mesh'

        uSTools.fbxImport.matICreate(self.mat_path,fbx_path,matI_path)



    def giveTexture(self):
        #获取所选mesh
        select_meshs=unreal.EditorUtilityLibrary.get_selected_assets()
        uSTools.fbxImport.giveTexture(select_meshs)





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