import unreal
import re
import os

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


from dayu_widgets.label import MLabel
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets.button_group import MCheckBoxGroup
from dayu_widgets.divider import MDivider
from dayu_widgets.browser import MClickBrowserFolderToolButton
from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.splitter import MSplitter
from dayu_widgets.item_view import MTreeView
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.spin_box import MSpinBox
from dayu_widgets.theme import MTheme

from dayu_widgets import dayu_theme
from dayu_widgets.qt import application






path='/Game/Shots/Ep002/sc002/Ep002_sc002_002/Animation'



def pathToSequenceAnim(path):
    asset_list=unreal.EditorAssetLibrary.list_assets(path)

    anim_list=[]
    level_sequnce=None
    

    for asset in asset_list:
        asset_class=unreal.EditorAssetLibrary.find_asset_data(asset).get_class().get_name()
        asset_name=unreal.EditorAssetLibrary.find_asset_data(asset).asset_name
        if asset_class=='AnimSequence':
            anim_list.append(unreal.EditorAssetLibrary.find_asset_data(asset).get_asset())
            
            #print(asset_class,asset_name)
        
        if asset_class=='LevelSequence':
            level_sequnce=unreal.EditorAssetLibrary.find_asset_data(asset).get_asset()
            #print(asset_class,asset_name)

    unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(level_sequnce)



    #获取当前打开的关卡序列
    export_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()

    spawnables = export_sequence.get_spawnables()
    frame_range = export_sequence.get_playback_range()
    frame_end = frame_range.get_end_frame()
    frame_start = frame_range.get_start_frame()


    track_base_name=None

    for spawnable in spawnables:
        #获取bp名称
        track_bpname = str(spawnable.get_object_template().get_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
        #判断命名规范
        if '_AAI' in track_bpname:
            track_base_name = track_bpname.split('_AAI',1)[0]
        else:
            #名称不符合,跳过
            continue
        for anim_asset in anim_list:
            anim_name = anim_asset.get_name()
            if '_CH' in anim_name:
                anim_base_name=anim_name.split('_CH')[0].split('an_')[-1]
            elif '_Pro' in anim_name:
                anim_base_name=anim_name.split('_Pro')[0].split('an_')[-1]
            else:
                continue

            #print(track_base_name,anim_base_name)
            if anim_base_name==track_base_name:
                spawnable_old_tracks=spawnable.get_tracks()
                for spawnable_old_track in spawnable_old_tracks:
                    if spawnable_old_track.get_class().get_name() == 'MovieSceneSkeletalAnimationTrack':
                        spawnable.remove_track(spawnable_old_track)
                animation_track=spawnable.add_track(unreal.MovieSceneSkeletalAnimationTrack)
                animation_section=animation_track.add_section()
                
                animation_section:unreal.MovieSceneSkeletalAnimationSection
                animation_section.params.animation=anim_asset
                
                animation_section.set_range(frame_start,frame_end)
                
                anim_list.remove(anim_asset)
                break
            



# pathToSequenceAnim(path)
        

class MyWindow(QtWidgets.QWidget, MFieldMixin):

    world_asset_names=[]
    select_world_names=[]



    def __init__(self, parent=None):
        super().__init__(parent)

        self.getEpList()
        
        self.ui()
        self.getLightMap()
        
    

    def ui(self):
        self.setWindowTitle('AAI文件导入')
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
            light_folder_asset_list=unreal.EditorAssetLibrary.list_assets('/Game/Shots/%s'%(self.ep_flie_list[ep_name]))
            
            light_sc_flie_lists=[]
            self.seq_assets_path=[]
            self.sequnence_find_assets=[]
            for light_folder_asset in light_folder_asset_list:
                light_asset_class=unreal.EditorAssetLibrary.find_asset_data(light_folder_asset).get_class().get_name()
                if light_asset_class=='LevelSequence':
                    #确定world资产
                    world_asset_find=unreal.EditorAssetLibrary.find_asset_data(light_folder_asset)
                    seq_asset_name=world_asset_find.get_asset().get_name()
                    seq_asset_path=world_asset_find.get_asset().get_path_name()
                    if '_an' in seq_asset_name :
                        #获取灯光路径名
                        light_flie_sc_name=seq_asset_path.rsplit('/')[-4]
                        #添加信息到列表
                        self.world_asset_names.append(seq_asset_name)
                        #获取符合要求的关卡序列路径
                        self.seq_assets_path.append(seq_asset_path)
                        light_sc_flie_lists.append(light_flie_sc_name)
                
                if light_asset_class=='LevelSequence':
                    #收集sequnence资产
                    sequnence_asset=unreal.EditorAssetLibrary.find_asset_data(light_folder_asset)
                    self.sequnence_find_assets.append(sequnence_asset)

        
                
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

        ep_name = self.field("ep_app")
        select_ep = self.ep_flie_list[ep_name]
        select_sc = self.select_world_names
        seq_assets_path = self.seq_assets_path
        # print(assets_path)

        for sc in select_sc:
            sc_folder = '/Game/Shots/%s/%s'%(select_ep,sc)
            if unreal.EditorAssetLibrary().does_directory_exist(sc_folder):
                for seq_asset_path in seq_assets_path:
                    if sc==seq_asset_path.split('/')[4]:
                        base_path = seq_asset_path.rsplit('/',1)[0]
                        pathToSequenceAnim(base_path)
                        #保存全部创建的文件
                        unreal.EditorAssetLibrary.save_directory('/Game/Shots')


        
        # pathToSequenceAnim(path)

        












def start():
    with application() as app:
        global test
        test = MyWindow()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
   start()