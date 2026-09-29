import unreal
import os
import sys
import openpyxl as op

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.switch import MSwitch
from dayu_widgets.push_button import MPushButton
from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets.splitter import MSplitter
from dayu_widgets.item_view import MTreeView
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.label import MLabel

from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

import UnrealPipeline.core.uSTools as uSTools
import UnrealPipeline.core.Config as UC
from importlib import reload
reload(uSTools)




level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level_sequence_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)





class MyWindow(QtWidgets.QWidget, MFieldMixin):

    world_asset_names=[]
    select_world_names=[]



    def __init__(self, parent=None):
        super().__init__(parent)

        self.getEpList()
        
        self.ui()
        self.getLightMap()
        


    def ui(self):
        self.setWindowTitle('AAI自动挂载')
        self.resize(300,450)

        #导入文件
        self.flie_import=MLineEdit().file().medium()
        self.flie_import.setPlaceholderText(self.tr("选择需要导入信息的Excel文件"))


        #ep列表
        radio_group_ep = MRadioButtonGroup(orientation=QtCore.Qt.Vertical)
        radio_group_ep.set_button_list(self.ep_flie_list)
        radio_group_ep.set_spacing(1)
        radio_group_ep.get_button_group().buttonClicked.connect(self.getLightMap)
        


        self.register_field("ep_app")
        self.register_field(
            "ep_app_text",lambda: " 、 ".join(self.field("ep_app")) if self.field("ep_app") else None
        )   
        self.bind(
            "ep_app", radio_group_ep, "dayu_checked", signal="sig_checked_changed"
        )
        
        scroll_ep=QtWidgets.QScrollArea()
        scroll_ep.setMinimumWidth(100)
        scroll_ep.setWidget(radio_group_ep)
        
        button_get = MPushButton(text="获取信息")
        button_get.clicked.connect(self.getEpList)

        
        

        self.tree_map=MTreeView()
        self.tree_map.header().setStretchLastSection(True)
        self.tree_map.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree_map.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.model_map=QtGui.QStandardItemModel()
        self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
        
        
        self.tree_map.setModel(self.model_map)
        self.tree_map.selectionModel().selectionChanged.connect(self.treeSelect)
        self.tree_map.header().headerDataChanged
        
        
        button_create = MPushButton(text="执行")
        button_create.clicked.connect(self.execute)

        button_groom = MPushButton(text="挂载groom")
        button_groom.clicked.connect(self.groomToCh)

        # self.version_switch = MSwitch()
        # self.version_switch.setChecked(False)
        # version_switch_lay = QtWidgets.QFormLayout()
        # version_switch_lay.addRow(MLabel("是否使用踏星流程"), self.version_switch)    #关卡创建开关

        self.version_radio_group = MRadioButtonGroup()
        self.version_radio_group.set_button_list(['财神流程','踏星流程'])
        self.version_radio_group.set_dayu_checked(0)

        self.seq_type_radio_group = MRadioButtonGroup()
        self.seq_type_radio_group.set_button_list(['挂载到Ly','挂载到an'])
        self.seq_type_radio_group.set_dayu_checked(0)

        lay_main=QtWidgets.QVBoxLayout()
        lay_1=QtWidgets.QVBoxLayout()
        lay_2=QtWidgets.QVBoxLayout()

        lay_1.addWidget(self.flie_import)
        lay_1.addWidget(scroll_ep)
        lay_1.addWidget(button_get)

        lay_2.addWidget(self.tree_map)
        lay_2.addWidget(button_create)
        lay_2.addWidget(button_groom)
        lay_2.addWidget(self.version_radio_group)
        lay_2.addWidget(self.seq_type_radio_group)

        box_1=QtWidgets.QGroupBox()
        box_1.setLayout(lay_1)
        box_1.setStyleSheet('QGroupBox{color:white;border:0px ;}')
        box_2=QtWidgets.QGroupBox()
        # box_2.setFixedWidth(350)
        box_2.setLayout(lay_2)
        box_2.setStyleSheet('QGroupBox{color:white;border:0px ;}')

        #给布局添加调节滑块
        splitter= MSplitter()
        splitter.setOrientation(QtCore.Qt.Orientation.Vertical)
        splitter.setHandleWidth(3)
        splitter.addWidget(box_1)
        splitter.addWidget(box_2)

        lay_main.addWidget(splitter)
        
        
        

        self.setLayout(lay_main)


    def getEpList(self):
        self.ep_flie_list=[]
        ep_i=0
        self.tree_switch=0
        path=None
        while ep_i<300:
            path=None
            ep_i_str=str(ep_i).zfill(3)
            ep_path='/Game/Shots/Ep%s'%ep_i_str
            ep_path2='/Game/Shots/EP%s'%ep_i_str
            if unreal.EditorAssetLibrary().does_directory_exist(ep_path):
                path='Ep%s'%ep_i_str

            elif unreal.EditorAssetLibrary().does_directory_exist(ep_path2):
                path='EP%s'%ep_i_str

            if path:
                self.ep_flie_list.append(path)
                self.tree_switch=1

            ep_i+=1
        # print(self.ep_flie_list)


    def getLightMap(self):
        
        ep_name=self.field("ep_app")

        # print(self.ep_flie_list[ep_name])

        if self.tree_switch==1:
            asset_data_list=uSTools.assetFilter(class_name='LevelSequence',folder='/Game/Shots/%s'%(self.ep_flie_list[ep_name]))
            #tree字典
            world_find_dict={}
            #资产名称及路径字典
            self.asset_to_path_dict={}

            light_sc_flie_lists=[]
            self.seq_assets_path=[]
            self.sequnence_find_assets=[]
            for asset_data in asset_data_list:
                seq_asset_name = uSTools.assetDataToAssetName(asset_data)
                seq_asset_path = uSTools.assetDataToAssetPath(asset_data)
                if '_an' in seq_asset_name:
                    #确定world资产
                    self.asset_to_path_dict[seq_asset_name] = seq_asset_path

                    if '_an' in seq_asset_name :
                        #获取灯光路径名
                        light_flie_sc_name=seq_asset_path.rsplit('/')[-3]
                        #添加信息到列表
                        self.world_asset_names.append(seq_asset_name)
                        #获取符合要求的关卡序列路径
                        self.seq_assets_path.append(seq_asset_path)
                        light_sc_flie_lists.append(light_flie_sc_name)

                        try:
                            world_find_dict[light_flie_sc_name].append(asset_data)
                        except:
                            world_find_dict[light_flie_sc_name]=[]
                            world_find_dict[light_flie_sc_name].append(asset_data)
                
                    self.sequnence_find_assets.append(asset_data)

        
                
            #简化sc数据内容
            self.light_sc_flie_list=[]
            for sc_flie in light_sc_flie_lists:
                if sc_flie not in self.light_sc_flie_list:
                    self.light_sc_flie_list.append(sc_flie)
            self.light_sc_flie_list.sort()

            
            #创建TreeView数据树
            self.model_map.clear()
            self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
            if self.light_sc_flie_list:
                for light_sc in self.light_sc_flie_list:
                    #创建一级菜单
                    tree_1=QtGui.QStandardItem(light_sc)

                    for world_sc_name,world_find_list in world_find_dict.items():      

                        if light_sc==world_sc_name:
                            world_asset_names = []
                            for world_asset_find in world_find_list:
                                world_asset_name=uSTools.assetDataToAssetName(world_asset_find)
                                world_asset_names.append(world_asset_name)
                            world_asset_names.sort()
                            for world_asset_name in world_asset_names:
                                tree_2=QtGui.QStandardItem(world_asset_name.split('_an')[0])
                                tree_1.appendRow(tree_2)

                    self.model_map.appendRow(tree_1)



    def treeSelect(self):
        item_names=[]
        self.select_world_names=[]
        tree_map_indexs=self.tree_map.selectedIndexes()
        #获取tree选项名称
        for index in tree_map_indexs:
            item=self.model_map.itemFromIndex(index)
            item_names.append(item.text())

        self.select_world_names = item_names

        # #过滤名称
        # for item_name in item_names:
        #     if item_name in self.world_asset_names and item_name not in self.select_world_names:
        #         self.select_world_names.append(item_name)

    
    def execute(self):
        #获取选择的镜头
        selected_cams = self.select_world_names
        #获取excel文件路径
        excel_path = self.flie_import.text()
        asset_excel_dict = uSTools.excelRead(excel_path)
        #获取缺少对应镜头缺少资产,并为asset_excel_dict的asset列表的[2]添加assetData属性
        if self.version_radio_group.get_dayu_checked() == 1:    #财神0,踏星1
            groom_switch = True                 #踏星流程自动挂载毛发
            error_dict,asset_excel_dict = uSTools.assetExamine57(asset_excel_dict)
        else:
            groom_switch = False
            error_dict,asset_excel_dict = uSTools.assetExamine(asset_excel_dict)
        
        if self.seq_type_radio_group.get_dayu_checked() == 0:    #挂载到Ly 0,挂载到an 1
            sequence_type = 'ly'
        elif self.seq_type_radio_group.get_dayu_checked() == 1:
            sequence_type = 'an'

        error_hint = False
        error_list = []
        #收集缺少资产名称
        if error_dict:
            for error_cam,error_assets in error_dict.items():
                #判断是否存在选择镜头号,不存在则全部查询
                if selected_cams:
                    if error_cam in selected_cams:
                        error_hint = True
                        for error_asset in error_assets:
                            if error_asset not in error_list:
                                error_list.append(error_asset)
                else:
                    error_hint = True
                    for error_asset in error_assets:
                        if error_asset not in error_list:
                            error_list.append(error_asset)
        
        if error_list:
            error_log = '要执行的镜头缺少以下资产:'
            for error_asset in error_list:
                error_log += f'\n{error_asset}'
        
        if error_hint:
            
            #当存在缺少资产时弹窗提示
            dialog = uSTools.ContinueErrorDialog(self,initialText=error_log)
            result = dialog.exec_()
            if result == QtWidgets.QDialog.Accepted:    #当用户点击确定按钮时继续执行挂载
                uSTools.assetAssembly(selected_cams,asset_excel_dict,error_list,sequence_type,groom_switch)

        else:
            print(selected_cams)
            uSTools.assetAssembly(selected_cams,asset_excel_dict,error_list,sequence_type,groom_switch)


    def groomToCh(self):            
        selected_cams = self.select_world_names
        
        for cam_name in selected_cams:
            uSTools.CacheImportTool.groomToChActor(cam_name,self.version_radio_group.get_dayu_checked())
            unreal.EditorAssetLibrary.save_directory('/Game')
            


class CustomDialog(QtWidgets.QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ureal缺少资产")
        self.setFixedSize(300, 150)
        
        # 创建布局和控件
        layout = QtWidgets.QVBoxLayout()
        message_label = MLabel(message)
        message_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(message_label)
        
        # 添加按钮
        buttons = MPushButton('OK')
        buttons.clicked.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setLayout(layout)











def start():
    with application() as app:
        global test
        test = MyWindow()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":
   
   start()





