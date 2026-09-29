import unreal
import re
import os

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets.splitter import MSplitter
from dayu_widgets.item_view import MTreeView

from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

import UnrealPipeline.core.uSTools as uSTools

from importlib import reload
reload(uSTools)


level_sequence_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)






def bindToSpawnable(an_seq_path):
    an_map_path = an_seq_path+'_Map'
    an_seq = unreal.load_asset(an_seq_path)
    an_seq:unreal.LevelSequence
    unreal.LevelEditorSubsystem().load_level(an_map_path)
    unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(an_seq)
    current_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    bindings = current_sequence.get_bindings()
    for binding in bindings:
        print(binding.get_display_name())
        if 'BP' in str(binding.get_display_name()):
            print(level_sequence_editor_subsystem.convert_to_spawnable(binding))
            print(binding)

    unreal.EditorAssetLibrary.save_directory('/Game/Shots')





class MyWindow(QtWidgets.QWidget, MFieldMixin):

    world_asset_names=[]
    select_world_names=[]



    def __init__(self, parent=None):
        super().__init__(parent)

        self.getEpList()
        
        self.ui()
        self.getLightMap()
        
    

    def ui(self):
        self.setWindowTitle('关卡序列bind转为spawnable')
        self.resize(300,450)


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


        lay_main=QtWidgets.QVBoxLayout()
        lay_1=QtWidgets.QVBoxLayout()
        lay_2=QtWidgets.QVBoxLayout()

        lay_1.addWidget(scroll_ep)
        lay_1.addWidget(button_get)

        lay_2.addWidget(self.tree_map)
        lay_2.addWidget(button_create)

        box_1=QtWidgets.QGroupBox()
        box_1.setLayout(lay_1)
        box_1.setStyleSheet('QGroupBox{color:white;border:0px ;}')
        box_2=QtWidgets.QGroupBox()
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


    def getLightMap(self):
        
        ep_name=self.field("ep_app")


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

            
            #创建TreeView数据树
            self.model_map.clear()
            self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
            if self.light_sc_flie_list:
                for light_sc in self.light_sc_flie_list:
                    #创建一级菜单
                    tree_1=QtGui.QStandardItem(light_sc)

                    for world_sc_name,world_find_list in world_find_dict.items():
                        world_asset_names = []
                        #重新排序
                        for world_find in world_find_list:
                            world_asset_name=uSTools.assetDataToAssetName(world_find)
                            world_asset_names.append(world_asset_name)
                        world_asset_names.sort()

                        if light_sc==world_sc_name:
                            for world_asset_name in world_asset_names:
                                tree_2=QtGui.QStandardItem(world_asset_name)
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


    
    def execute(self):

        select_assets = self.select_world_names
        asset_to_path_dict = self.asset_to_path_dict
        # print(asset_to_path_dict)

        for asset_name,asset_path in asset_to_path_dict.items():
            for select_asset in select_assets:
                if select_asset == asset_name:
                    an_seq_path = asset_path+'/'+asset_name
                    bindToSpawnable(an_seq_path)
                    #保存全部创建的文件
                    unreal.EditorAssetLibrary.save_directory('/Game/Shots')
















def start():
    with application() as app:
        global test
        test = MyWindow()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
   start()