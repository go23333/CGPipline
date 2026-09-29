import unreal
import openpyxl as op
import os


from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

import UnrealPipeline.core.Config as UC
import UnrealPipeline.core.uSTools as uSTools
import UnrealPipeline.core.UnrealHelper as UH
from importlib import reload
reload(uSTools)


from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.item_view import MTreeView
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.switch import MSwitch
from dayu_widgets.label import MLabel
from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application


print('AutoAssembly')

level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level_sequence_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)


class AutoAssemblyWin(QtWidgets.QWidget, MFieldMixin):

    #文件路径
    excel_path=''


    def __init__(self, parent=None):
        super().__init__(parent)
        all_sc_list=[]
        self.cam=[]
        self.startK=[]
        self.endK=[]
        self.cam_se=[]
        self.ep=''
        self.select_names=[]
        self.flie_class=['Light','Animation','Cache','VFX','Modify']
        #偏移帧
        self.start_offset=UC.globalConfig.get().start_offset
        self.end_offset=UC.globalConfig.get().end_offset
        self.aai_shot_path=UC.globalConfig.get().ShotPath
        
        self.__ui()

    def __ui(self):
        self.setWindowTitle('自动化组装工具')
        self.resize(350,480)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        #导入文件
        create_base_folder=MPushButton(text="创建基础文件夹")
        create_base_folder.clicked.connect(self.baseDirectory)
        self.cam_excel_le=MLineEdit().file().medium()
        self.cam_excel_le.setPlaceholderText(self.tr("选择镜头Excel文件"))
        self.cam_excel_le.textChanged.connect(self.createTree)                       #创建内容变更事件

        self.assembly_excel_le=MLineEdit().file().medium()
        self.assembly_excel_le.setPlaceholderText(self.tr("选择组装Excel文件(不选择则不组装BP及动画)"))

        # self.import_cam_le=MLineEdit().folder().medium()
        # self.import_cam_le.setPlaceholderText(self.tr("选择摄像机文件夹(不选择则不创建摄像机)"))

        self.tree_map=MTreeView()
        self.tree_map.header().setStretchLastSection(True)
        self.tree_map.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree_map.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.model_map=QtGui.QStandardItemModel()
        self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
        
        self.tree_map.setModel(self.model_map)
        self.tree_map.selectionModel().selectionChanged.connect(self.treeSelect)
        self.tree_map.header().headerDataChanged


        create_folder=MPushButton(text="执行")
        create_folder.clicked.connect(self.excute)

        self.model_radio_group = MRadioButtonGroup()
        self.model_radio_group.set_button_list(['财神流程','踏星流程'])
        self.model_radio_group.set_dayu_checked(1)

        self.seq_type_radio_group = MRadioButtonGroup()
        self.seq_type_radio_group.set_button_list(['挂载到an','挂载到Ly'])
        self.seq_type_radio_group.set_dayu_checked(1)
        

        folder_lay.addWidget(self.model_radio_group)
        folder_lay.addWidget(self.seq_type_radio_group)
        folder_lay.addWidget(create_base_folder)
        folder_lay.addWidget(self.cam_excel_le)
        folder_lay.addWidget(self.assembly_excel_le)
        # folder_lay.addWidget(self.import_cam_le)
        folder_lay.addWidget(self.tree_map)
        folder_lay.addWidget(create_folder)
        

        lay.addLayout(folder_lay)
        self.setLayout(lay)



    def treeSelect(self):
        self.select_names=[]
        tree_map_indexs=self.tree_map.selectedIndexes()
        #获取tree选项名称
        for index in tree_map_indexs:
            item=self.model_map.itemFromIndex(index)
            self.select_names.append(item.text())

    def baseDirectory(self):
        #当选项为财神时,使用旧版方案
        if self.model_radio_group.get_dayu_checked() == 0: #财神0,踏星1
            uSTools.oldBaseDirectory()
        elif self.model_radio_group.get_dayu_checked() == 1: #财神0,踏星1
            uSTools.baseDirectory()
            

    def directoryOld(self):

        self.excel_path=self.cam_excel_le.text()

        df=op.load_workbook(self.excel_path,data_only=True)
        sheet=df.get_sheet_by_name('镜头表')
        all_sc_list=[]
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
                all_sc_list.append(i[1])
                self.cam.append(i[2])
                cam_s.append(i[2])
                cam_s.append(i[3])
                cam_s.append(i[4])
                self.cam_se.append(cam_s)

        return ep,all_sc_list
    

    def directoryPipeline(self):

        self.excel_path=self.cam_excel_le.text()

        df=op.load_workbook(self.excel_path,data_only=True)
        sheet=df.get_sheet_by_name('Sheet')
        all_sc_list=[]
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
                all_sc_list.append(i[1])
                self.cam.append(i[2])
                # self.startK.append(i[3])
                # self.endK.append(i[4])
                cam_s.append(i[2])
                cam_s.append(i[3])
                cam_s.append(i[4])
                self.cam_se.append(cam_s)

        return ep,all_sc_list
    

    def createTree(self):
        #读取excel
        try:
            self.directoryPipeline()
        except:
            self.directoryOld()


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



    def excute(self):
        #当选项为财神时,使用旧版方案
        if self.model_radio_group.get_dayu_checked() == 0: #财神0,踏星1
            self.oldPipelineAssembly()
            return False
        
        shot_path=self.aai_shot_path

        try:
            ep, all_sc_list = self.directoryPipeline()
        except:
            ep, all_sc_list = self.directoryOld()
        shot_ep_path=shot_path+ep
        cam_dict={}
        sc_list=[]


        #未有选择的镜头时执行全部
        if not self.select_names:
            #简化sc数据内容
            for ii in all_sc_list:
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
        if self.assembly_excel_le.text():
            examine_data = self.dataExamine()
            if not examine_data:
                return False
        
        uSTools.baseAssetCreate(sc_list, shot_ep_path, cam_dict, ep,start_offset,end_offset)    #初始化文件夹
        if self.assembly_excel_le.text():
            self.importCameras()                                #摄像机挂载
            bp_miss_dict = self.bpAssembly()                    #bp组装
            import_sk_error_list = self.anFbxAccessibly()       #动画挂载

            #显示报错
            import_error_text = ''
            if import_sk_error_list:
                import_error_text += '以下动画未找到正确骨骼:\n'
                for error_data in import_sk_error_list:
                    if '_BG' not in error_data:             #跳过对场景道具的识别
                        import_error_text += f'{error_data}\n'

            #创建导入失败excel表格
            if bp_miss_dict:
                uSTools.bpMissExcelCreate(bp_miss_dict)
            if import_sk_error_list:
                uSTools.excelCreate(import_sk_error_list)

            if import_error_text:
                error_dialog = uSTools.ErrorDialog(self,initialText = import_error_text)
                error_dialog.exec_()
        
        #保存全部创建的文件
        unreal.EditorAssetLibrary.save_directory('/Game/Shots')


    def oldPipelineAssembly(self):
        shot_path=self.aai_shot_path

        try:
            ep, all_sc_list = self.directoryPipeline()
        except:
            ep, all_sc_list = self.directoryOld()
        shot_ep_path=shot_path+ep
        cam_dict={}
        sc_list=[]


        #未有选择的镜头时执行全部
        if not self.select_names:
            #简化sc数据内容
            for ii in all_sc_list:
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
        
        if self.assembly_excel_le.text():
            examine_data = self.dataExamine()
            if not examine_data:
                return False
        
        self.oldCreateDirectory()   #创建初始化文件夹
        if self.assembly_excel_le.text():
            self.oldImportCameras()                                #摄像机挂载
            bp_miss_dict = self.bpAssembly()                        #bp组装
            import_sk_error_list = self.oldAnFbxAccessibly()       #动画挂载

            #显示报错
            import_error_text = ''
            if import_sk_error_list:
                import_error_text += '以下动画未找到正确骨骼:\n'
                for error_data in import_sk_error_list:
                    if '_BG' not in error_data:             #跳过对场景道具的识别
                        import_error_text += f'{error_data}\n'

            #创建导入失败excel表格
            if bp_miss_dict:
                uSTools.bpMissExcelCreate(bp_miss_dict)
            if import_sk_error_list:
                uSTools.excelCreate(import_sk_error_list)

            if import_error_text:
                error_dialog = uSTools.ErrorDialog(self,initialText = import_error_text)
                error_dialog.exec_()
        
        #保存全部创建的文件
        unreal.EditorAssetLibrary.save_directory('/Game/Shots')



    def dataExamine(self):
        #判断是否存在inter change插件,存在则停止执行
        plugin_examine = uSTools.interChangeExamine(self)
        if not plugin_examine:
            return False
        
        #获取选择的镜头
        selected_cams = self.select_names
        #获取excel文件路径
        excel_path = self.assembly_excel_le.text()
        asset_excel_dict = uSTools.excelRead(excel_path)
        # 获取缺少对应镜头缺少资产,并为asset_excel_dict的asset列表的[2]添加assetData属性
        if self.model_radio_group.get_dayu_checked() == 1:    #财神0,踏星1
            error_dict,asset_excel_dict = uSTools.assetExamine57(asset_excel_dict)
        else:
            error_dict,asset_excel_dict = uSTools.assetExamine(asset_excel_dict)

        

        error_list = []
        #收集缺少资产名称
        if error_dict:
            for error_cam,error_assets in error_dict.items():
                #判断是否存在选择镜头号,不存在则全部查询
                if selected_cams:
                    if error_cam in selected_cams:
                        for error_asset in error_assets:
                            if error_asset not in error_list:
                                error_list.append(error_asset)
                else:
                    for error_asset in error_assets:
                        if error_asset not in error_list:
                            error_list.append(error_asset)
        
        error_log = ''
        if error_list:
            new_error_list = []
            for error in error_list:        #过滤BG文件
                if '_BG' not in error:
                    new_error_list.append(error)
            if new_error_list:
                error_log = '要执行的镜头缺少以下资产:'
                for error_asset in new_error_list:
                    error_log += f'\n{error_asset}'
        
        if error_log:
            #当存在缺少资产时弹窗提示
            dialog = uSTools.ContinueErrorDialog(self,initialText=error_log)
            result = dialog.exec_()
            if result == QtWidgets.QDialog.Accepted:    #当用户点击确定按钮时继续执行挂载
                return True
            else:
                return False
        
        return True
        
    

    def oldImportCameras(self):
        cams_data = []
        selected_cams = self.select_names
        all_cams = self.cam_se
        project_dir = unreal.Paths.project_dir()
        project_name = project_dir.split('/')[-3]
        if not selected_cams:       #未选择cam时执行全部
            selected_cams = [cam[0] for cam in all_cams]

        for selected_cam in selected_cams:
            cam_data = {}
            cam_split = selected_cam.split('_')
            ep_name = cam_split[0]
            sc_name = cam_split[1]
            # TX:/EP001/Layout/Final/FBX/CamPath
            # TX:/EP000/Animation/cam/sc001
            # Y:\SSDSY_CS\EP003\Animation\cam\sc001

            cam_name = f'{selected_cam}_cam'
            local_path = f'Y:/{project_name}/{ep_name}/Animation/cam/{sc_name}/{selected_cam}_cam.fbx'
            
            
            #摄像机被下载后才添加到列表中进行导入
            if os.path.exists(local_path):
                cam_data['name'] = cam_name
                cam_data['path'] = local_path
                cams_data.append(cam_data)
            
        if cams_data:
            #导入摄像机
            UH.importCameras(cams_data)

            
    

    def importCameras(self):
        cams_data = []
        selected_cams = self.select_names
        all_cams = self.cam_se
        project_dir = unreal.Paths.project_dir()
        project_name = project_dir.split('/')[-3]
        if not selected_cams:       #未选择cam时执行全部
            selected_cams = [cam[0] for cam in all_cams]

        for selected_cam in selected_cams:
            cam_data = {}
            cam_split = selected_cam.split('_')
            ep_name = cam_split[0]
            sc_name = cam_split[1]
            # TX:/EP001/Layout/Final/FBX/CamPath
            # TX:/EP000/Animation/cam/sc001
            if self.seq_type_radio_group.get_dayu_checked() == 1:    #挂载到Ly 1,挂载到an 0
                pipeline_path = f'{ep_name}/Layout/Final/FBX/CamPath'
                cam_name = f'{selected_cam}_cam'
                local_path = f'Y:/{project_name}/{ep_name}/Layout/Final/FBX/CamPath/{selected_cam}_cam.fbx'
            elif self.seq_type_radio_group.get_dayu_checked() == 0:
                pipeline_path = f'{ep_name}/{sc_name}/cam'
                cam_name = f'{selected_cam}_cam'
                local_path = f'Y:/{project_name}/{ep_name}/{sc_name}/cam/{selected_cam}_cam.fbx'
            
            
            #下载pipeline最新文件
            project_id, headers, project_name = uSTools.getProjectId()
            if project_id:
                files_info = uSTools.getFilesInfo(project_id, headers, pipeline_path)
                print(files_info)
                if files_info:
                    uSTools.downloadFiles(files_info, project_name)
                    #摄像机被下载后才添加到列表中进行导入
                    if os.path.exists(local_path):
                        cam_data['name'] = cam_name
                        cam_data['path'] = local_path
                        cams_data.append(cam_data)
            
        if cams_data:
            #导入摄像机
            UH.importCameras(cams_data)


    def oldAnFbxAccessibly(self):
        selected_cams = self.select_names
        all_cams = self.cam_se
        project_dir = unreal.Paths.project_dir()
        project_name = project_dir.split('/')[-3]
        import_sk_error_list = []
        if not selected_cams:       #未选择cam时执行全部
            selected_cams = [cam[0] for cam in all_cams]

        for selected_cam in selected_cams:
            cam_split = selected_cam.split('_')
            ep_name = cam_split[0]
            sc_name = cam_split[1]
            #Y:\SSDSY_CS\EP006\Animation\fbx\sc001
            # if self.seq_type_radio_group.get_dayu_checked() == 1:    #挂载到Ly 1,挂载到an 0
            #     local_path = f'Y:/{project_name}/{ep_name}/Layout/Final/FBX/{sc_name}/{selected_cam}'
            # elif self.seq_type_radio_group.get_dayu_checked() == 0:

            local_path = f'Y:/{project_name}/{ep_name}/Animation/FBX/{sc_name}/{selected_cam}'
            
            #文件不存在时跳过
            if not os.path.exists(local_path):
                continue
            
            #导入fbx文件
            import_sk_error_list = uSTools.anFbxImport(local_path,self.model_radio_group.get_dayu_checked())

            an_path = f'/Game/Shots/{ep_name}/{sc_name}/{selected_cam}/Animation'
            #挂载animation到序列
            uSTools.pathToSequenceAnim(an_path)   #财神流程强制只挂载an序列

        return import_sk_error_list



    def anFbxAccessibly(self):
        selected_cams = self.select_names
        all_cams = self.cam_se
        project_dir = unreal.Paths.project_dir()
        project_name = project_dir.split('/')[-3]
        if not selected_cams:       #未选择cam时执行全部
            selected_cams = [cam[0] for cam in all_cams]

        for selected_cam in selected_cams:
            cam_split = selected_cam.split('_')
            ep_name = cam_split[0]
            sc_name = cam_split[1]
            cam_name = cam_split[2]
            if self.seq_type_radio_group.get_dayu_checked() == 1:    #挂载到Ly 1,挂载到an 0
                pipeline_path = f'{ep_name}/Layout/Final/FBX/{sc_name}/{selected_cam}'
                local_path = f'Y:/{project_name}/{ep_name}/Layout/Final/FBX/{sc_name}/{selected_cam}'
            elif self.seq_type_radio_group.get_dayu_checked() == 0:
                pipeline_path = f'{ep_name}/{sc_name}/FBX/{selected_cam}'
                local_path = f'Y:/{project_name}/{ep_name}/{sc_name}/FBX/{selected_cam}'
            
            
            #下载pipeline最新文件
            project_id, headers, project_name = uSTools.getProjectId()

            if project_id:
                files_info = uSTools.getFilesInfo(project_id, headers, pipeline_path)
                if files_info:
                    uSTools.downloadFiles(files_info, project_name)
            
            #导入fbx文件
            # import_sk_error_list = uSTools.anFbxImport(local_path,self.version_switch.isChecked())
            import_sk_error_list = uSTools.anFbxImport(local_path,self.model_radio_group.get_dayu_checked())

            an_path = f'/Game/Shots/{ep_name}/{sc_name}/{selected_cam}/Animation'
            #挂载animation到序列
            uSTools.pathToSequenceAnim(an_path,self.seq_type_radio_group.get_dayu_checked())

        return import_sk_error_list



    def bpAssembly(self):
        #获取选择的镜头
        selected_cams = self.select_names
        #获取excel文件路径
        excel_path = self.assembly_excel_le.text()
        asset_excel_dict = uSTools.excelRead(excel_path)
        #获取缺少对应镜头缺少资产,并为asset_excel_dict的asset列表的[2]添加assetData属性
        if self.model_radio_group.get_dayu_checked() == 1:    #财神0,踏星1
            groom_switch = True                     #踏星流程自动挂载毛发
            error_dict,asset_excel_dict = uSTools.assetExamine57(asset_excel_dict)
        else:
            groom_switch = False
            error_dict,asset_excel_dict = uSTools.assetExamine(asset_excel_dict)

        # error_dict,asset_excel_dict = uSTools.assetExamine57(asset_excel_dict)
        
        if self.seq_type_radio_group.get_dayu_checked() == 1:    #挂载到Ly 1,挂载到an 0
            sequence_type = 'ly'
        elif self.seq_type_radio_group.get_dayu_checked() == 0:
            sequence_type = 'an'

        error_list = []
        #收集缺少资产名称
        if error_dict:
            for error_cam,error_assets in error_dict.items():
                #判断是否存在选择镜头号,不存在则全部查询
                if selected_cams:
                    if error_cam in selected_cams:
                        for error_asset in error_assets:
                            if error_asset not in error_list:
                                error_list.append(error_asset)
                else:
                    for error_asset in error_assets:
                        if error_asset not in error_list:
                            error_list.append(error_asset)
        
        print(selected_cams)
        uSTools.assetAssembly(selected_cams,asset_excel_dict,error_list,sequence_type,groom_switch)
        
        # error_log = ''
        # if error_list:
        #     new_error_list = []
        #     for error in error_list:        #过滤BG文件
        #         if '_BG' not in error:
        #             new_error_list.append(error)
        #     if new_error_list:
        #         error_log = '要执行的镜头缺少以下资产:'
        #         for error_asset in new_error_list:
        #             error_log += f'\n{error_asset}'
        
        # if error_log:
            
        #     #当存在缺少资产时弹窗提示
        #     dialog = uSTools.ContinueErrorDialog(self,initialText=error_log)
        #     result = dialog.exec_()
        #     if result == QtWidgets.QDialog.Accepted:    #当用户点击确定按钮时继续执行挂载
        #         uSTools.assetAssembly(selected_cams,asset_excel_dict,error_list,sequence_type)

        # else:
        #     print(selected_cams)
        #     uSTools.assetAssembly(selected_cams,asset_excel_dict,error_list,sequence_type)
        
        return error_dict
    
    def oldCreateDirectory(self):
        shot_path=self.aai_shot_path
        ep,all_sc_list=self.directoryOld()
        shot_ep_path=shot_path+ep
        cam_dict={}
        sc_list=[]

        # print(self.sc)
        # print(len(self.sc))
        #未有选择的镜头时执行全部
        if not self.select_names:
            #简化sc数据内容
            for ii in all_sc_list:
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
                    unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=vfx_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingDynamic)
                if lt_map_data and not lt_map_exist:
                    unreal.EditorLevelUtils().add_level_to_world(overall_level_data.get_asset(),level_package_name=lt_map_data.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
                unreal.EditorAssetLibrary.save_directory('/Game')

        
        # print(groom_seq_list)
        #将Light anim cache的sequence组装到总sequence
        for render_seq in render_ls_list:

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
        





def start():
    with application() as app:
        global test
        test = AutoAssemblyWin()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":

    start()
