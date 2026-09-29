# -*- coding: utf-8 -*-

import unreal

import os
import json
import sys

import UnrealPipeline.core.Config as UC
from importlib import reload
from openpyxl import Workbook
import UnrealPipeline.core.uSTools as uSTools
reload(uSTools)

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

from dayu_widgets.label import MLabel
from dayu_widgets.switch import MSwitch
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.progress_bar import MProgressBar
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application



print('AnimImport 1.1')



def assetReplace(asset_path1,asset_path2):

    asset1=unreal.EditorAssetLibrary.find_asset_data(asset_path1).get_asset()
    asset2=unreal.EditorAssetLibrary.find_asset_data(asset_path2).get_asset()


    unreal.EditorAssetLibrary.consolidate_assets(asset1,[asset2])
    unreal.EditorAssetLibrary.delete_asset(asset_path2)
    

def excelCreate(error_list):

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
    wb = Workbook()
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
    try:
        save_path = r"d:\Desktop\an_import_error.xlsx"
        wb.save(save_path)
    except :
        save_path = os.path.join(os.path.expanduser('~'), 'Desktop/an_import_error.xlsx')
        wb.save(save_path)



class AnImportWin(QtWidgets.QWidget, MFieldMixin):


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

        fbx_check=MPushButton(text="FBX完整性检测工具")
        fbx_check.clicked.connect(self.fbxCheck)

        self.flie_import=MLineEdit().folder().medium()
        self.flie_import.setPlaceholderText(self.tr("选择FBX路径"))
        create_folder=MPushButton(text="导入FBX动画文件")
        create_folder.clicked.connect(self.importAsset)
        
        self.version_switch = MSwitch()
        self.version_switch.setChecked(False)
        version_switch_lay = QtWidgets.QFormLayout()
        version_switch_lay.addRow(MLabel("是否使用踏星流程"), self.version_switch)    #关卡创建开关

        self.error_lable=MLabel('')
        self.error_lable.setStyleSheet("color: red")

        folder_lay.addWidget(fbx_check)
        folder_lay.addWidget(self.flie_import)
        folder_lay.addWidget(create_folder)
        folder_lay.addLayout(version_switch_lay)
        folder_lay.addWidget(self.error_lable)
        
        lay.addLayout(folder_lay)
        self.setLayout(lay)

    
    def fbxCheck(self):
        import UnrealPipeline.pipeline.FbxDetection.FbxDetection as fbxDetection
        fbxDetection.start()


    def importAsset(self):
        #判断是否存在inter change插件,存在则停止执行
        plugin_examine = uSTools.interChangeExamine(self)
        if not plugin_examine:
            return False
        
        
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')
        #获取FBX路径
        anim_path=self.flie_import.text()

        import_sk_error_list = uSTools.anFbxImport(anim_path,self.version_switch.isChecked())
        
        #显示报错
        import_error_text = ''
        if import_sk_error_list:
            import_error_text += '以下动画未找到正确骨骼:\n'
            for error_data in import_sk_error_list:
                import_error_text += f'{error_data}\n'

        #创建导入失败excel表格
        excelCreate(import_sk_error_list)

        if import_error_text:
            error_dialog = uSTools.ErrorDialog(self,initialText = import_error_text)
            error_dialog.exec_()

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
            skeleton_path_assets=uSTools.assetFilter('Skeleton',self.skeleton_base_path)
            #skeleton_path_assets=unreal.EditorAssetLibrary.list_assets(self.skeleton_base_path)
            for skeleton_path_asset in skeleton_path_assets:
                
                asset=skeleton_path_asset.get_asset()
                self.skeleton_asset.append(asset)
                #if unreal.EditorAssetLibrary.find_asset_data(skeleton_path_asset).get_class():
                    #asset_class=unreal.EditorAssetLibrary.find_asset_data(skeleton_path_asset).get_class().get_name()
                    #判断资产类型
                    #if asset_class == 'Skeleton':
                        #self.skeleton_asset.append(asset)
                
            return self.skeleton_asset
            
    def executeImportTasks(self,task):
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(task)








def start():
    with application() as app:
        global test
        test = AnImportWin()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
   start()