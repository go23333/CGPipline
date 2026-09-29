import unreal
import openpyxl as op


from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

import UnrealPipeline.core.Config as UC
import UnrealPipeline.core.uSTools as uSTools


from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.item_view import MTreeView
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.switch import MSwitch
from dayu_widgets.label import MLabel
from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

from importlib import reload
reload(uSTools)

print('ChuShiHua57_2.0')

level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level_sequence_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)


class ChuShiHuaWin(QtWidgets.QWidget, MFieldMixin):

    sc=[]
    cam=[]
    startK=[]
    endK=[]
    cam_se=[]
    ep=''
    select_names=[]
    #文件类型
    flie_class=['Light','Animation','Cache','VFX','Modify']
    #文件路径
    excel_path=''
    #偏移帧
    start_offset=UC.globalConfig.get().start_offset
    end_offset=UC.globalConfig.get().end_offset


    def __init__(self, parent=None):
        super().__init__(parent)

        self.aai_shot_path='/Game/Shots/'
        self.asset_shot_path='/Game/Assets/Shots/'
        
        self.__ui()

    def __ui(self):
        self.setWindowTitle('初始化项目基础文件目录')
        self.resize(300,400)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        #导入文件
        create_base_folder=MPushButton(text="创建基础文件夹")
        create_base_folder.clicked.connect(self.baseDirectory)
        self.flie_import=MLineEdit().file().medium()
        self.flie_import.setPlaceholderText(self.tr("选择需要导入信息的Excel文件"))
        self.flie_import.textChanged.connect(self.createTree)                       #创建内容变更事件

        self.tree_map=MTreeView()
        self.tree_map.header().setStretchLastSection(True)
        self.tree_map.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree_map.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.model_map=QtGui.QStandardItemModel()
        self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
        
        self.tree_map.setModel(self.model_map)
        self.tree_map.selectionModel().selectionChanged.connect(self.treeSelect)
        self.tree_map.header().headerDataChanged


        create_folder=MPushButton(text="创建shots文件夹")
        create_folder.clicked.connect(self.excute)

        self.model_radio_group = MRadioButtonGroup()
        self.model_radio_group.set_button_list(['财神流程','踏星流程'])
        self.model_radio_group.set_dayu_checked(0)
        self.model_radio_group.get_button_group().buttonClicked.connect(self.modelChange)
        
        self.pipeline_switch = MSwitch()
        self.pipeline_switch.setChecked(False)
        pipeline_switch_lay = QtWidgets.QFormLayout()
        pipeline_switch_lay.addRow(MLabel("是否创建半流程文件夹"), self.pipeline_switch)    #关卡创建开关

        self.offset_switch = MSwitch()
        self.offset_switch.setChecked(False)
        offset_switch_lay = QtWidgets.QFormLayout()
        offset_switch_lay.addRow(MLabel("是否使用偏移帧"), self.offset_switch)    #关卡创建开关

        folder_lay.addWidget(self.model_radio_group)
        folder_lay.addWidget(create_base_folder)
        folder_lay.addWidget(self.flie_import)
        folder_lay.addWidget(self.tree_map)
        folder_lay.addWidget(create_folder)
        folder_lay.addLayout(pipeline_switch_lay)
        folder_lay.addLayout(offset_switch_lay)

        import_lay=QtWidgets.QVBoxLayout()
        

        lay.addLayout(folder_lay)
        lay.addLayout(import_lay)
        self.setLayout(lay)
    
    def modelChange(self):
        version_index = self.model_radio_group.get_dayu_checked() #财神0,踏星1


    
    def offsetChange(self):
        if self.offset_switch.isChecked():
            self.start_offset=UC.globalConfig.get().start_offset
            self.end_offset=UC.globalConfig.get().end_offset
        else:
            self.start_offset=0
            self.end_offset=1


    def treeSelect(self):
        self.select_names=[]
        tree_map_indexs=self.tree_map.selectedIndexes()
        #获取tree选项名称
        for index in tree_map_indexs:
            item=self.model_map.itemFromIndex(index)
            self.select_names.append(item.text())


    def createTree(self):
        #读取excel
        self.excelToDirectory()

        #创建TreeView数据树
        self.model_map.clear()
        self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])

        cam_data_dict = {}

        for cam_data in self.cam_se:
            try:
                cam_data_dict[cam_data[0].split('_')[1]].append(cam_data[0])
            except:
                cam_data_dict[cam_data[0].split('_')[1]] = []
                cam_data_dict[cam_data[0].split('_')[1]].append(cam_data[0])

        for sc_index,cams in cam_data_dict.items():      
            #创建一级菜单
            tree_1=QtGui.QStandardItem(sc_index)
            for cam in cams:
                tree_2=QtGui.QStandardItem(cam)
                tree_1.appendRow(tree_2)

            self.model_map.appendRow(tree_1)


    def excelToDirectory(self):
        try:
            ep = self.directoryOld()
        except:
            ep = self.directoryPipeline()
        return ep


    def directoryOld(self):

        self.excel_path=self.flie_import.text()

        df=op.load_workbook(self.excel_path,data_only=True)
        sheet=df.get_sheet_by_name('镜头表')
        self.sc=[]
        self.cam=[]
        self.cam_se=[]
        self.startK=[]
        self.endK=[]

        all_list=[]
        i=0
        #确定行和列
        rowcount=sheet.max_row
        colcount=8
        #读取所需的Excel内容
        for i in range(13,rowcount+1):
            list=[]
            for j in range(3,colcount+1):
                list.append(sheet.cell(row=i,column=j).value)
            all_list.append(list)
        # print(all_list)

        #数据分配
        
        ep=all_list[0][0]
        for i in all_list:
            cam_s=[]
            if i[0]==ep and i[1] and i[2] and i[3] and i[4] and i[5]:
                self.sc.append(i[1])
                self.cam.append(i[2])
                cam_s.append(i[2])
                cam_s.append(i[3])
                cam_s.append(i[4])
                self.cam_se.append(cam_s)

        return ep
    
    def directoryPipeline(self):

        self.excel_path=self.flie_import.text()

        df=op.load_workbook(self.excel_path,data_only=True)
        sheet=df.get_sheet_by_name('Sheet')
        self.sc=[]
        self.cam=[]
        self.cam_se=[]
        self.startK=[]
        self.endK=[]

        all_list=[]
        i=0
        #确定行和列
        rowcount=sheet.max_row
        colcount=6
        #读取所需的Excel内容
        for i in range(2,rowcount+1):
            list=[]
            for j in range(1,colcount+1):
                list.append(sheet.cell(row=i,column=j).value)
            all_list.append(list)
        # print(all_list)

        #数据分配
        
        ep=all_list[0][0]
        for i in all_list:
            cam_s=[]
            if i[0]==ep and i[1] and i[2] and i[3] and i[4] and i[5]:
                self.sc.append(i[1])
                self.cam.append(i[2])
                # self.startK.append(i[3])
                # self.endK.append(i[4])
                cam_s.append(i[2])
                cam_s.append(i[3])
                cam_s.append(i[4])
                self.cam_se.append(cam_s)

        return ep

    def oldCreateDirectory(self):
        self.offsetChange()
        if self.pipeline_switch.isChecked():
            shot_path=self.asset_shot_path
        else:
            shot_path=self.aai_shot_path
        

        ep=self.directoryOld()
        shot_ep_path=shot_path+ep
        cam_dict={}
        sc_list=[]

        # print(self.sc)
        # print(len(self.sc))
        #未有选择的镜头时执行全部
        if not self.select_names:
            #简化sc数据内容
            for ii in self.sc:
                if ii.lower() in sc_list:
                    pass
                else:
                    sc_list.append(ii.lower())
            
            #对镜头信息分组
            for sc_list_i in sc_list:
                cam_list=[]
                for cam_i in self.cam_se:
                    if cam_i[0].split('_',2)[1]==sc_list_i:
                        cam_list.append(cam_i)
                #排序列表
                cam_list.sort()
                print(cam_list)
                cam_dict[sc_list_i]=cam_list

        elif self.select_names:
            for select_name in self.select_names:
                for cam_i in self.cam_se:
                    if cam_i[0]==select_name:
                        sc_name = cam_i[0].split('_')[1]
                        try:
                            cam_dict[sc_name].append(cam_i)
                        except:
                            cam_dict[sc_name] = []
                            cam_dict[sc_name].append(cam_i)
                        
                        if sc_name not in sc_list:
                            sc_list.append(sc_name)
            
        
        render_ls_list=[]
        lt_ls_list=[]
        an_ls_list=[]
        groom_seq_list=[]
        vfx_seq_list=[]
        # 创建文件夹和所需的文件
        unreal.EditorAssetLibrary.make_directory('%s/Preview'%(shot_ep_path))
        for sc_name in sc_list:
            #选择模式下不生成Preview
            if not self.select_names:
                preview_path='%s/Preview/%s_%s_Preview'%(shot_ep_path,ep,sc_name)

                if not unreal.EditorAssetSubsystem().does_asset_exist('%s/Preview/%s_%s_Pv_Map'%(shot_ep_path,ep,sc_name)):
                    unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_%s_Pv_Map'%(ep,sc_name),package_path='%s/Preview'%(shot_ep_path),asset_class=unreal.World,factory=unreal.WorldFactory())
                
                #删除旧preview track
                if unreal.EditorAssetSubsystem().does_asset_exist(preview_path):
                    preview_sequence=unreal.EditorAssetLibrary.find_asset_data(preview_path).get_asset()
                    old_tracks=preview_sequence.get_tracks()
                    for old_track in old_tracks:
                        preview_sequence.remove_track(old_track)
                #创建preview_sequence
                else:
                    preview_sequence=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_%s_Preview'%(ep,sc_name),package_path='%s/Preview'%(shot_ep_path),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                    preview_sequence:unreal.LevelSequence
                    preview_sequence.set_display_rate((25,1))
                    preview_sequence=unreal.EditorAssetLibrary.find_asset_data(preview_path).get_asset()

                preview_track=preview_sequence.add_track(unreal.MovieSceneSubTrack)
                preview_track:unreal.MovieSceneSubTrack
                preview_track.set_display_name('%s_%s'%(ep,sc_name))

            start_key = 0
            end_key = 0
                
            unreal.EditorAssetLibrary.save_directory('%s/Preview'%(shot_ep_path))
            level_editor_subsystem.load_level('%s/Preview/%s_%s_Pv_Map'%(shot_ep_path,ep,sc_name))
            for cam_name in cam_dict[sc_name]:
                flie_name = cam_name[0]
                for file_class_name in self.flie_class:
                    if file_class_name=='Lighting' or file_class_name=='Light':
                        file_class_name='Lighting'
                        render_seq_create = False   #当render未存在时将render添加到记录列表,用于添加其余基础序列,否则只修改帧数
                        lt_path='%s/%s/%s/%s_Render'%(shot_ep_path,sc_name,flie_name,flie_name)
                        lt_map_path='%s/%s/%s/%s/%s_lt_Map'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                        if not unreal.EditorAssetSubsystem().does_asset_exist(lt_map_path):
                            unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_lt_Map'%(cam_name[0]),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.World,factory=unreal.WorldFactory())
                        if not unreal.EditorAssetSubsystem().does_asset_exist(lt_path):
                            render_seq_create = True
                            render_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_Render'%(flie_name),package_path='%s/%s/%s'%(shot_ep_path,sc_name,flie_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                        else:
                            render_ls=unreal.EditorAssetLibrary.find_asset_data(lt_path).get_asset()
                            render_ls:unreal.LevelSequence
                        render_ls.set_display_rate((25,1))
                        if cam_name[1]:
                            render_ls.set_playback_start(int(cam_name[1]))                #设置起始帧
                        if cam_name[2]:
                            render_ls.set_playback_end(int(cam_name[2])+self.end_offset+self.start_offset)  #设置结束帧
                        # if render_seq_create:
                        render_ls_list.append(render_ls)
                        unreal.EditorAssetLibrary.save_directory('%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name))
                        #打开其他关卡清理内存
                        level_editor_subsystem.load_level(lt_map_path)

                        lt_map_data = unreal.EditorAssetLibrary.find_asset_data(lt_map_path)

                        
                        
                        if not self.select_names:
                            #将灯光序列放入总序列
                            end_key += render_ls.get_playback_end()
                            # preview_track.set_display_name(lt_ls.get_name())
                            preview_section=preview_track.add_section()
                            preview_section.set_sequence(render_ls)
                            preview_section.set_range(start_key,end_key)
                            preview_section.set_row_index(0)
                            preview_sequence.set_view_range_end(end_key*1.03/25)
                            preview_sequence.set_playback_end(end_key)
                            # preview_sequence.set_work_range_end(end_key)
                            
                            start_key += render_ls.get_playback_end()


                        #创建灯光序列
                        lt_path='%s/%s/%s/%s/%s_lt'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                        if not unreal.EditorAssetSubsystem().does_asset_exist(lt_path):
                            lt_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_lt'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                        else:
                            lt_ls=unreal.EditorAssetLibrary.find_asset_data(lt_path).get_asset()
                        lt_ls.set_display_rate((25,1))
                        if cam_name[1]:
                            lt_ls.set_playback_start(int(cam_name[1]))
                        if cam_name[2]:
                            lt_ls.set_playback_end(int(cam_name[2])+self.end_offset+self.start_offset)
                        lt_ls_list.append(lt_ls)


                    
                    if file_class_name=='Animation':
                        an_path='%s/%s/%s/%s/%s_an'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                        if not unreal.EditorAssetSubsystem().does_asset_exist(an_path):
                            an_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_an'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                        else:
                            an_ls=unreal.EditorAssetLibrary.find_asset_data(an_path).get_asset()
                        an_ls.set_display_rate((25,1))
                        if cam_name[1]:
                            an_ls.set_playback_start(int(cam_name[1]))
                        if cam_name[2]:
                            an_ls.set_playback_end(int(cam_name[2])+self.end_offset+self.start_offset)
                        an_ls_list.append(an_ls)

                        #创建an关卡
                        an_map_path='%s/%s/%s/%s/%s_an_Map'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                        if not unreal.EditorAssetSubsystem().does_asset_exist(an_map_path):
                            an_map = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_an_Map'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.World,factory=unreal.WorldFactory())

                        an_map_data = unreal.EditorAssetLibrary.find_asset_data(an_map_path)
                        

                    if file_class_name=='Cache':
                        # 创建groom关卡序列
                        cache_path='%s/%s/%s/%s/%s_cache'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                        if not unreal.EditorAssetSubsystem().does_asset_exist(cache_path):
                            groom_seq=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_cache'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                        else:
                            groom_seq=unreal.EditorAssetLibrary.find_asset_data(cache_path).get_asset()
                        groom_seq.set_display_rate((25,1))
                        if cam_name[1]:
                            groom_seq.set_playback_start(int(cam_name[1]))
                        if cam_name[2]:
                            groom_seq.set_playback_end(int(cam_name[2])+self.end_offset+self.start_offset)
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
                            vfx_seq.set_playback_end(int(cam_name[2])+self.end_offset+self.start_offset)
                        vfx_seq_list.append(vfx_seq)

                        #创建VFX关卡
                        vfx_map_path='%s/%s/%s/%s/%s_VFX_Map'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                        if not unreal.EditorAssetSubsystem().does_asset_exist(vfx_map_path):
                            vfx_map = unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_VFX_Map'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.World,factory=unreal.WorldFactory())

                        vfx_map_data = unreal.EditorAssetLibrary.find_asset_data(vfx_map_path)

                    if file_class_name=='Modify':
                        unreal.EditorAssetLibrary.make_directory('%s/%s/%s/%s/Scenes'%(shot_ep_path,sc_name,flie_name,file_class_name))
                        unreal.EditorAssetLibrary.make_directory('%s/%s/%s/%s/Character'%(shot_ep_path,sc_name,flie_name,file_class_name))
                        modify_path='%s/%s/%s/%s/%s_Modify'%(shot_ep_path,sc_name,flie_name,file_class_name,flie_name)
                        if not unreal.EditorAssetSubsystem().does_asset_exist(modify_path):
                            modify_ls=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name='%s_Modify'%(flie_name),package_path='%s/%s/%s/%s'%(shot_ep_path,sc_name,flie_name,file_class_name),asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
                        else:
                            modify_ls=unreal.EditorAssetLibrary.find_asset_data(modify_path).get_asset()
                        modify_ls.set_display_rate((25,1))
                        if cam_name[1]:
                            modify_ls.set_playback_start(int(cam_name[1]))
                        if cam_name[2]:
                            modify_ls.set_playback_end(int(cam_name[2])+self.end_offset+self.start_offset)

                    
                #创建总关卡
                overall_level_path = '%s/%s/%s/%s_Map'%(shot_ep_path,sc_name,flie_name,flie_name)
                if not unreal.EditorAssetSubsystem().does_asset_exist(overall_level_path):
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
                        print(level)
                        if '_an_Map' in str(level):
                            an_map_exist = True
                        if '_VFX_Map' in str(level):
                            vfx_map_exist = True
                        if '_lt_Map' in str(level):
                            lt_map_exist = True
                if an_map_data and not an_map_exist:
                    unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=an_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
                if vfx_map_data and not vfx_map_exist:
                    # unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=vfx_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingDynamic)
                    unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=vfx_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
                if lt_map_data and not lt_map_exist:
                    unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=lt_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
                unreal.EditorAssetLibrary.save_directory('/Game')

        
        # print(groom_seq_list)
        #将Light anim cache的sequence组装到总sequence
        for render_seq in render_ls_list:
            
            # for an_seq in an_ls_list:
            #     if render_seq.get_name().rsplit('_',1)[0]==an_seq.get_name().rsplit('_',1)[0]:
            #         render_tracks=render_seq.get_tracks()
            #         #删除原有track
            #         for render_track in render_tracks:
            #             try:
            #                 if render_track.get_sections()[0].get_sequence()==an_seq:
            #                     render_seq.remove_track(render_track)
            #             except:
            #                 pass
            #         # lt.add_spawnable_from_instance(an) 
            #         render_track=render_seq.add_track(unreal.MovieSceneSubTrack)
            #         render_section=render_track.add_section()
            #         render_section.set_sequence(an_seq)
            #         render_section.set_range(an_seq.get_playback_start(),an_seq.get_playback_end())
            #         break
            
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


    def excute(self):
        #当选项为财神时,使用旧版方案
        if self.model_radio_group.get_dayu_checked() == 0: #财神0,踏星1
            self.oldCreateDirectory()
            return False
        self.offsetChange()
        if self.pipeline_switch.isChecked():
            shot_path=self.asset_shot_path
        else:
            shot_path=self.aai_shot_path

        ep=self.excelToDirectory()
        shot_ep_path=shot_path+ep
        cam_dict={}
        sc_list=[]

        
        # print(self.sc)
        # print(len(self.sc))
        #未有选择的镜头时执行全部
        if not self.select_names:
            #简化sc数据内容
            for ii in self.sc:
                if ii.lower() in sc_list:
                    pass
                else:
                    sc_list.append(ii.lower())
            
            #对镜头信息分组
            for sc_list_i in sc_list:
                cam_list=[]
                for cam_i in self.cam_se:
                    if cam_i[0].split('_',2)[1]==sc_list_i:
                        cam_list.append(cam_i)
                #排序列表
                cam_list.sort()
                print(cam_list)
                cam_dict[sc_list_i]=cam_list

        elif self.select_names:
            for select_name in self.select_names:
                for cam_i in self.cam_se:
                    if cam_i[0]==select_name:
                        sc_name = cam_i[0].split('_')[1]
                        try:
                            cam_dict[sc_name].append(cam_i)
                        except:
                            cam_dict[sc_name] = []
                            cam_dict[sc_name].append(cam_i)
                        
                        if sc_name not in sc_list:
                            sc_list.append(sc_name)
        
        start_offset = self.start_offset
        end_offset = self.end_offset
        uSTools.baseAssetCreate(sc_list, shot_ep_path, cam_dict, ep,start_offset,end_offset)
        



    def oldBaseDirectory(self):
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


    def baseDirectory(self):
        #当选项为财神时,使用旧版方案
        if self.model_radio_group.get_dayu_checked(): #财神0,踏星1
            self.oldBaseDirectory()
            return False

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

def start():
    with application() as app:
        global test
        test = ChuShiHuaWin()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":

    start()
