# -*- coding: utf-8 -*-

import unreal

import os
import json
import sys

from importlib import reload
import UnrealPipeline.core.uSTools as uSTools
reload(uSTools)

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



print('AnimImport')



def assetReplace(asset_path1,asset_path2):

    asset1=unreal.EditorAssetLibrary.find_asset_data(asset_path1).get_asset()
    asset2=unreal.EditorAssetLibrary.find_asset_data(asset_path2).get_asset()


    unreal.EditorAssetLibrary.consolidate_assets(asset1,[asset2])
    unreal.EditorAssetLibrary.delete_asset(asset_path2)
    




class mw(QtWidgets.QWidget, MFieldMixin):


    def __init__(self, parent=None):
            super().__init__(parent)
            self.uii()

            self.skeleton_base_path=None        #骨骼路径缓存
            self.skeleton_asset=[]              #骨骼列表缓存
            
    def uii(self):   
        self.setWindowTitle('动画FBX导入')
        self.resize(320,120)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        self.flie_import=MLineEdit().folder().medium()
        self.flie_import.setPlaceholderText(self.tr("选择FBX路径"))
        create_folder=MPushButton(text="导入FBX动画文件")
        create_folder.clicked.connect(self.importAsset)
        
        self.error_lable=MLabel('')
        self.error_lable.setStyleSheet("color: red")

        folder_lay.addWidget(self.flie_import)
        folder_lay.addWidget(create_folder)
        folder_lay.addWidget(self.error_lable)

        
        lay.addLayout(folder_lay)
        self.setLayout(lay)


    def importAsset(self):
        
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')
        #获取FBX路径
        anim_path=self.flie_import.text()
        
        fbx_base_path='/Game/Shots/'

        type_name=''
        
        #遍历文件夹内文件
        for dirpath, dirnames, filenames in os.walk(anim_path):
            for filename in filenames:
                #判断后缀名是否为fbx
                if '.fbx' in filename.lower():
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
                    anim_fbx=dirpath+'/'+filename               #合并文件路径和文件名称
                    ep=filename.split('_')[0]                   #获取ep名称
                    sc=filename.split('_')[1]                   #获取sc主名称
                    sc_all_name=filename.rsplit(type_name)[0]      #获取sc全名称


                    if not sc_all_name:
                        break
                    #判断后缀名
                    if 'Pro' in filename:
                        mesh_name=filename.rsplit(type_name)[-1].split('_Pro',1)[0]
                    if 'CH' in filename:
                        mesh_name=filename.rsplit(type_name)[-1].split('_CH',1)[0]


                    fbx_create_path=f'{fbx_base_path}{ep}/{sc}/'     #创建基础文件夹路径

                    # sc_section_names=sc_all_name.split('_')

                    # #添加分段文件夹路径
                    # if len(sc_section_names)>2:
                    #     sc_sub_name=ep+'_'+sc
                    #     for sc_section_name in sc_section_names[2:]:
                    #         sc_sub_name+='_'+sc_section_name
                    #         fbx_create_sub_path='/'+sc_sub_name+'_an'

                    fbx_create_path+=sc_all_name+'/Animation'

                    #获取骨骼网格体路径
                    skeleton_base_path='/Game/AAI/Reference/'
                    mesh_type=None
                    if '_Pro' in filename:
                        mesh_type='Pro'
                        skeleton_base_path+='Pro'
                    if '_CH' in filename:
                        mesh_type='CH'
                        skeleton_base_path+='Character'
                    #遍历路径寻找骨骼网格体
                    skeleton_meshs=self.skeletonMeshGet(skeleton_base_path)
                    # print(skeleton_meshs)
                    for skeleton_mesh in skeleton_meshs:
                        
                        skeleton_mesh:unreal.SkeletalMesh
                        skeleton_base_name=None
                        if mesh_type=='Pro':
                            skeleton_base_name=skeleton_mesh.get_name().split('UE_')[-1].split('_Skeleton')[0]
                        if mesh_type=='CH':
                            skeleton_base_name=skeleton_mesh.get_name().split('UE_')[-1].split('_Skeleton')[0]
                        # print(mesh_name,skeleton_base_name)
                        if mesh_name == skeleton_base_name:
                            print(mesh_name,skeleton_mesh.get_name())

                            #导入动画序列
                            uSTools.fbxImport.animSequenceImport(anim_fbx,fbx_create_path,skeleton_mesh)

                            #如果存在ly文件,则使用an文件替换
                            if type_name=='_an_':
                                ly_path=fbx_create_path+'/'+anim_fbx_name.replace('_an_','_ly_')
                                an_path=fbx_create_path+'/'+anim_fbx_name
                                # print(ly_path)
                                if unreal.EditorAssetLibrary.does_asset_exist(an_path):
                                    assetReplace(an_path,ly_path)
                                    print(ly_path)
                            

                            #保存全部创建的文件
                            unreal.EditorAssetLibrary.save_directory('/Game/Shots')


        #保存全部创建的文件
        # unreal.EditorAssetLibrary.save_directory('/Game/Shots')
                            

        
        
     

    #根据路径过滤骨骼网格体
    def skeletonMeshGet(self,skeleton_path):
        #判断路径是否重复,重复的话返回旧值
        if self.skeleton_base_path==skeleton_path:
            return self.skeleton_asset
        else:
            self.skeleton_base_path=skeleton_path
            self.skeleton_asset=[]
            #列举路径内所有资产
            skeleton_path_assets=unreal.EditorAssetLibrary.list_assets(self.skeleton_base_path)
            for skeleton_path_asset in skeleton_path_assets:
                
                asset=unreal.EditorAssetLibrary.find_asset_data(skeleton_path_asset).get_asset()
                if unreal.EditorAssetLibrary.find_asset_data(skeleton_path_asset).get_class():
                    asset_class=unreal.EditorAssetLibrary.find_asset_data(skeleton_path_asset).get_class().get_name()
                    #判断资产类型
                    if asset_class == 'Skeleton':
                        self.skeleton_asset.append(asset)
            return self.skeleton_asset
            
    def executeImportTasks(self,task):
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(task)








def start():
    with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
   start()