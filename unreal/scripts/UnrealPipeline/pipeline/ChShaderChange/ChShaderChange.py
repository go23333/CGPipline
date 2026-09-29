import unreal

import os
import json

from importlib import reload
import UnrealPipeline.core.uSTools as uSTools
import UnrealPipeline.core.Config as UC
reload(uSTools)

from Qt import QtWidgets
from Qt import QtGui
from Qt import QtCore

from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets.splitter import MSplitter
from dayu_widgets.item_view import MTreeView
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.label import MLabel

from dayu_widgets import dayu_theme
from dayu_widgets.qt import application


print('ChShaderChange 1.0')

editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level_sequence_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)









class ChShaderChangeWin(QtWidgets.QWidget, MFieldMixin):


    def __init__(self, parent=None):
            super().__init__(parent)

            self.ChAssetPath = UC.globalConfig().ReferencePath+'Character/'

            self.getEpList()
            self.ui()
            self.getLightMap()

            self.assets_path=None
            self.select_world_names=[]


            
    def ui(self):   
        self.setWindowTitle('角色材质切换')
        self.resize(300,600)

        lay_main=QtWidgets.QVBoxLayout()
        lay_1=QtWidgets.QVBoxLayout()
        lay_2=QtWidgets.QVBoxLayout()

        #lay1
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
        
        button_get = MPushButton(text="刷新")
        button_get.clicked.connect(self.getEpList)

        #lay2
        self.tree_map=MTreeView()
        self.tree_map.header().setStretchLastSection(True)
        self.tree_map.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree_map.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.model_map=QtGui.QStandardItemModel()
        self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
        
        self.tree_map.setModel(self.model_map)
        self.tree_map.selectionModel().selectionChanged.connect(self.treeSelect)
        self.tree_map.header().headerDataChanged


        self.bp_name_le=MLineEdit()
        self.bp_name_le.setPlaceholderText(self.tr("设置BP名称,如DouZhanLong"))
        self.version_name_le=MLineEdit()
        self.version_name_le.setPlaceholderText(self.tr("设置角色版本名称"))
        create_shader_change=MPushButton(text="为选中的镜头进行版本切换")
        create_shader_change.clicked.connect(lambda: self.execute(mode=1))
        transmit_shader_change=MPushButton(text="将BP材质切换传递到所选镜头的布料缓存")
        transmit_shader_change.clicked.connect(lambda: self.execute(mode=2))

        self.error_lable = MLabel('')
        self.error_lable.setStyleSheet("color: red;")
        
        lay_1.addWidget(scroll_ep)
        lay_1.addWidget(button_get)
        
        lay_2.addWidget(self.tree_map)
        lay_2.addWidget(self.bp_name_le)
        lay_2.addWidget(self.version_name_le)
        lay_2.addWidget(create_shader_change)
        lay_2.addWidget(transmit_shader_change)
        lay_2.addWidget(self.error_lable)


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



    def execute(self,mode):
        if not self.select_world_names:
            dialog = uSTools.ErrorDialog(self,initialText='未选择镜头')
            dialog.exec_()
            return
        #获取选择的镜头
        for cam_name in self.select_world_names:

            cam_split = cam_name.split('_')
            ep = cam_split[0]
            sc = cam_split[1]
            cam = cam_split[2]

            an_sequence_path = f'/Game/Shots/{ep}/{sc}/{cam_name}/Animation/{cam_name}_an'

            an_level_path = f'/Game/Shots/{ep}/{sc}/{cam_name}/Animation/{cam_name}_an_Map'
            final_level_path = f'/Game/Shots/{ep}/{sc}/{cam_name}/{cam_name}_Map'
            an_level_asset_data = unreal.EditorAssetLibrary().find_asset_data(an_level_path)
            final_level_asset_data = unreal.EditorAssetLibrary().find_asset_data(final_level_path)

            
            if unreal.EditorAssetLibrary().does_asset_exist(an_level_path):
                level_editor_subsystem.load_level(an_level_asset_data.get_asset().get_path_name())
                unreal.EditorAssetLibrary.save_directory('/Game')
            elif unreal.EditorAssetLibrary().does_asset_exist(final_level_path):
                level_editor_subsystem.load_level(final_level_asset_data.get_asset().get_path_name())
                unreal.EditorAssetLibrary.save_directory('/Game')
            #当缺少对应资产时跳过循环
            else:
                continue

            if unreal.EditorAssetLibrary().does_asset_exist(an_sequence_path):
                an_sequence_asset = unreal.EditorAssetLibrary().load_asset(an_sequence_path)
                unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(an_sequence_asset)
            #当缺少对应资产时跳过循环
            else:
                continue
            
            if mode == 1:
                version_name = self.version_name_le.text()
                bp_name = self.bp_name_le.text()
                self.versionShaderChange(bp_name,version_name,an_sequence_asset)
            if mode == 2:
                self.clothCacheShaderTransmit(an_sequence_asset)
            
            unreal.EditorAssetLibrary.save_directory('/Game')


    def clothCacheShaderTransmit(self,sequence:unreal.MovieSceneSequence):
        
        # current_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()

        #获取cache Sequence路径
        sequence_path = sequence.get_path_name()
        cache_path = sequence_path.replace('/Animation/','/Cache/').replace('_an','_cache')
        if not unreal.EditorAssetLibrary().does_asset_exist(cache_path):
            cache_path = sequence_path.replace('/Animation/','/Cache/').replace('_an','_hcache')
            if not unreal.EditorAssetLibrary().does_asset_exist(cache_path):
                return False
        #加载cache Sequence资产
        cache_sequence = unreal.EditorAssetLibrary().load_asset(cache_path)

        #获取材质信息和切换版本信息
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        old_possessables = sequence.get_possessables()
        bp_ver_list = []
        for old_possessable in old_possessables:
            ch_base_name = None
            ver_name = None
            #获取bp名称
            try:    #跳过识别失败的资产
                track_bpname = str(old_possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue
            
            #获取角色bp名称和材质版本名称
            if '_AAI' in track_bpname:
                ch_base_name = track_bpname.split('_AAI')[0]
                child_possessables = old_possessable.get_child_possessables()
                skm_bind = None
                for child_possessable in child_possessables:
                    #查找SkeletalMeshComponent
                    if child_possessable.get_name() == 'SkeletalMeshComponent0':
                        skm_bind = child_possessable
                if not skm_bind:
                    continue
                skm_tracks = skm_bind.get_tracks()
                for skm_track in skm_tracks:
                    skm_section=skm_track.get_sections()[0]
                    skm_channel = skm_section.get_all_channels()[0]
                    mat_name = skm_channel.get_default().get_name()
                    if 'lambert' not in mat_name and ch_base_name in mat_name and '_CH_' in mat_name:
                        #将角色名与'_CH_'中间的版本名称记录
                        ver_name = mat_name.split(f'{ch_base_name}_')[-1].split('_CH_')[0]
                        break

            #当同时存在角色名与版本名时记录信息
            if ch_base_name and ver_name:
                bp_ver_list.append([ch_base_name,ver_name])
        
        print(bp_ver_list)
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(cache_sequence)
        #为cacheSequence赋予版本切换材质球
        # for bp_ver_data in bp_ver_list:
        #     bp_name = bp_ver_data[0]
        #     ver_name = bp_ver_data[1]
        #     self.versionShaderChange(bp_name,ver_name,cache_sequence)
        bp_name = self.bp_name_le.text()
        ver_name = self.version_name_le.text()
        self.versionShaderChange(bp_name,ver_name,cache_sequence)
        print(bp_name,ver_name)

        
        #为布料赋予材质球,并清除多余材质球

        possessables = cache_sequence.get_possessables()
        remove_mats = []
        for possessable in possessables:
            gcc_bind = None
            cache_mats = []
            #获取bp名称
            try:    #跳过识别失败的资产
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue

            if '_AAI' in track_bpname and bp_name in track_bpname:
                child_possessables = possessable.get_child_possessables()
                cache_mats = []
                tracks = possessable.get_tracks()
                for track in tracks:
                    #获取布料缓存资产
                    if track.get_display_name() == '解算缓存':
                        #当channel的参数为None时,获取key的参数
                        cache_asset = track.get_sections()[0].get_all_channels()[0].get_default()
                        if not cache_asset:
                            try:
                                cache_asset = track.get_sections()[0].get_all_channels()[0].get_keys()[-1].get_value()
                            except:
                                pass
                        if cache_asset:
                            cache_mats = cache_asset.materials

                smc_mats = {}
                for child_possessable in child_possessables:
                    if child_possessable.get_possessed_object_class().get_name() == 'GeometryCacheComponent':
                        gcc_bind = child_possessable

                    if child_possessable.get_possessed_object_class().get_name() == 'SkeletalMeshComponent':
                        smc_tracks = child_possessable.get_tracks()
                        for smc_track in smc_tracks:
                            #获取对应材质名
                            mat_asset = smc_track.get_sections()[0].get_all_channels()[0].get_default()
                            smc_mats[smc_track.get_material_index()] = [mat_asset,child_possessable,smc_track]

                if gcc_bind and cache_mats:
                    #清理bind
                    gcc_tracks = gcc_bind.get_tracks()
                    for gcc_track in gcc_tracks:
                        if gcc_track.get_class().get_name() == 'MovieScenePrimitiveMaterialTrack':
                            gcc_bind.remove_track(gcc_track)

                    mat_index = 0
                    for cache_mat in cache_mats:
                        for smc_mat_index,smc_mat_data in smc_mats.items():
                            smc_mat = smc_mat_data[0]
                            smc_possessable = smc_mat_data[1]
                            remove_track = smc_mat_data[2]
                            if smc_mat.get_name().split('_CH_')[-1] == cache_mat.get_name().split('_CH_')[-1]:
                                mat_slot_name = cache_mat.get_name()
                                #设置材质序号
                                mat_track = gcc_bind.add_track(unreal.MovieScenePrimitiveMaterialTrack)
                                mat_track.set_property_name_and_path(f"材质槽位:{mat_slot_name}", mat_slot_name)
                                mat_track.set_material_index(mat_index)
                                mat_section = mat_track.add_section()
                                mat_section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE) #改为保持状态
                                mat_channel = mat_section.get_all_channels()[0]
                                mat_channel.set_default(smc_mat)
                                
                                #记录需要删除的材质球,用于删除an Sequence中的旧材质球
                                remove_mats.append(smc_mat)
                            
                            #传递后删除材质切换槽
                            smc_possessable.remove_track(remove_track)

                        mat_index += 1  
        
        #删除an Sequence的重复材质球
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(sequence)
        possessables = sequence.get_possessables()
        for possessable in possessables:
            #获取bp名称
            try:    #跳过识别失败的资产
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue

            if '_AAI' in track_bpname:
                child_possessables = possessable.get_child_possessables()
                for child_possessable in child_possessables:
                    if child_possessable.get_possessed_object_class().get_name() == 'SkeletalMeshComponent':
                        smc_tracks = child_possessable.get_tracks()
                        for smc_track in smc_tracks:
                            #获取对应材质名
                            mat_asset = smc_track.get_sections()[0].get_all_channels()[0].get_default()
                            #当track内的材质球存在于列表则删除track
                            if mat_asset in remove_mats:
                                child_possessable.remove_track(smc_track)


    def versionShaderChange(self,bp_name,version_name,sequence:unreal.MovieSceneSequence):
        
        possessables = sequence.get_possessables()

        for possessable in possessables:
            #获取bp名称
            try:    #跳过识别失败的资产
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
            except:
                continue
            
            if track_bpname.split('_AAI')[0] == bp_name:
                track_bpname = str(possessable.get_possessed_object_class().get_class_path_name().get_editor_property('package_name')).rsplit('/',1)[-1]
                ch_base_name = track_bpname.split('_AAI')[0]
                ch_mesh_path = self.ChAssetPath+ch_base_name+f'/SkeletalMesh/UE_{ch_base_name}'
                ch_mesh_asset = unreal.EditorAssetLibrary.load_asset(ch_mesh_path)

                ch_mesh_materials = ch_mesh_asset.materials

                #获取新版本材质
                mat_index = 0
                new_mat_dict = {}
                for ch_mesh_material in ch_mesh_materials:
                    if ch_mesh_material.material_interface:     #判断材质插槽上是否有材质球,没有则跳过
                        ch_mesh_material_path = ch_mesh_material.material_interface.get_path_name().rsplit('.',1)[0]
                        
                        mat_slot_name = str(ch_mesh_material.material_slot_name)
                        #当存在材质版本文件夹时,材质路径使用版本材质路径
                        mat_base_path = ch_mesh_material_path.rsplit('/',1)[0]
                        new_mat_directory_path = f'{mat_base_path}/{version_name}'
                        
                        mat_basename = ch_mesh_material_path.rsplit('/',1)[-1]
                        if unreal.EditorAssetLibrary.does_directory_exist(new_mat_directory_path):
                            new_mat_path = new_mat_directory_path+'/'+mat_basename.replace('_CH_',f'_{version_name}_CH_')
                        else:
                            new_mat_path = ch_mesh_material_path.replace('_CH_',f'_{version_name}_CH_')
                        if unreal.EditorAssetLibrary.does_asset_exist(new_mat_path):
                            new_mat_asset = unreal.EditorAssetLibrary.load_asset(new_mat_path)
                            new_mat_dict[mat_index] = [new_mat_asset,mat_slot_name]
                        # print(mat_index,ch_mesh_material_path)

                    mat_index += 1

                print(new_mat_dict)
                if new_mat_dict:
                    self.error_lable.setText('')
                    child_possessables = possessable.get_child_possessables()
                    for child_possessable in child_possessables:
                        #清除旧SkeletalMeshComponent0
                        if child_possessable.get_name() == 'SkeletalMeshComponent0':
                            child_possessable.remove()
                            break
                    
                    unreal.LevelSequenceEditorBlueprintLibrary.select_bindings([possessable])
                    actor=editor_actor_subsystem.get_selected_level_actors()[0]
                    SkeletalMeshComponent0 = unreal.find_object(actor, "SkeletalMeshComponent0")
                    skeleta_possessable = sequence.add_possessable(SkeletalMeshComponent0)

                    for mat_index,mat_datas in new_mat_dict.items():
                        
                        new_mat = mat_datas[0]
                        mat_slot_name = mat_datas[1]
                        #设置材质序号
                        mat_track = skeleta_possessable.add_track(unreal.MovieScenePrimitiveMaterialTrack)
                        mat_track.set_property_name_and_path(f"材质槽位:{mat_slot_name}", mat_slot_name)
                        mat_track.set_material_index(mat_index)
                        mat_section = mat_track.add_section()
                        mat_section.set_completion_mode(unreal.MovieSceneCompletionMode.KEEP_STATE) #改为保持状态
                        mat_channel = mat_section.get_all_channels()[0]
                        mat_channel.set_default(new_mat)
                else:
                    # self.error_lable.setText('未找到对应版本材质')
                    print(f'未找到{bp_name}_{version_name}材质')

                unreal.EditorAssetLibrary.save_directory('/Game')













def start():
    with application() as app:
        global test
        test = ChShaderChangeWin()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
    start()


    




    
    

