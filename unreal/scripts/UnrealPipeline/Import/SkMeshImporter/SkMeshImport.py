# -*- coding: utf-8 -*-

import unreal

import os
import json
import sys
import time

from importlib import reload
import functools

import UnrealPipeline.core.Config as UC
import UnrealPipeline.core.utilis as UU
import UnrealPipeline.core.UnrealHelper as UH
import UnrealPipeline.core.CommonWidget as UCW
# from UnrealPipeline.core.CommonWidget import CommonMenuBar,folderSelectGroup,DateTableView
import UnrealPipeline.core.uSTools as uSTools
reload(uSTools)
reload(UCW)
reload(UC)
reload(UH)

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

from dayu_widgets.label import MLabel
from dayu_widgets.switch import MSwitch
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.progress_bar import MProgressBar
from dayu_widgets.item_view import MTableView
from dayu_widgets.item_model import MSortFilterModel
from dayu_widgets.push_button import MPushButton
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application



print('skImport 1.1')


skeletal_mesh_editor_subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
subobject_subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

SUB_SKELETON_MESHS_CLASS = ['_nCloth','_NoSK','_NoSkHight','_Hight']

#排序材质插槽
def sort_key(material:unreal.StaticMaterial):
    return material.material_slot_name

def resort_mesh_material(sl_assets=[]):
    if not sl_assets:
        sl_assets = unreal.EditorUtilityLibrary.get_selected_assets()
    for mesh in sl_assets:
        if isinstance(mesh,unreal.StaticMesh):
            material_slots = mesh.static_materials
            # 创建新的插槽列表
            new_slots = list(material_slots)
            new_slots.sort(key=sort_key)
            mesh.static_materials = new_slots
        elif isinstance(mesh,unreal.SkeletalMesh):
            material_slots = mesh.materials
            # 创建新的插槽列表
            new_slots = list(material_slots)
            new_slots.sort(key=sort_key)
            mesh.materials = new_slots
        else:
            pass



def assetReplace(asset_path1,asset_path2):

    asset1=unreal.EditorAssetLibrary.find_asset_data(asset_path1).get_asset()
    asset2=unreal.EditorAssetLibrary.find_asset_data(asset_path2).get_asset()


    unreal.EditorAssetLibrary.consolidate_assets(asset1,[asset2])
    unreal.EditorAssetLibrary.delete_asset(asset_path2)



def importSkGroom(sk_mesh,sk_local_path):
    ch_path = sk_mesh.get_path_name().rsplit('/',2)[0]
    groom_path = ch_path+'/Groom/YD_Hair'
    groom_asset_datas = uSTools.assetFilter('GroomAsset',groom_path)
    local_base_path = sk_local_path.rsplit('/',1)[0]
    for groom_asset_data in groom_asset_datas:
        groom_asset = groom_asset_data.get_asset()
        groom_asset_name = groom_asset.get_name()
        local_groom_path = f'{local_base_path}/{groom_asset_name}.abc'
        if os.path.exists(local_groom_path):
            groom_task=uSTools.GroomAbcImport.buildImportTask(local_groom_path,groom_path,uSTools.GroomAbcImport.buildGroomImportOptions())
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([groom_task])
            print(local_groom_path)



def importSkMesh(fbx_path,sk_type,tx_version,parent_skmesh=None):
    old_scence_path = False
    
    if tx_version:
        split_prefix = 'SK_'
        if sk_type == 'Character':
            skeleton_mesh_type_path = 'Character/'
        elif sk_type == 'Pro':
            skeleton_mesh_type_path = 'Pro/'
        elif sk_type == 'Scence':
            skeleton_mesh_type_path = 'Scence/Scence_Pro/'
        skmesh_base_path = UC.globalConfig().AssetPath+skeleton_mesh_type_path
        
    else:
        split_prefix = 'UE_'
        if sk_type == 'Character':
            skeleton_mesh_type_path = 'Character/'
        elif sk_type == 'Pro':
            ep = fbx_path.rsplit('/')[-3].replace('EP','Ep')
            skeleton_mesh_type_path = f'Pro/{ep}/'
        elif sk_type == 'Scence':
            #/Content/AAI/Reference/Scenes/DouJiaCiTang_HuanJing/Scenes_Pro
            fbx_basename = fbx_path.rsplit('/')[-1].split('.')[0].split(split_prefix)[-1]
            skeleton_mesh_type_path = f'Scenes/{fbx_basename}/Scenes_Pro/'
            old_scence_path = True

        skmesh_base_path = UC.globalConfig().ReferencePath+skeleton_mesh_type_path
    mesh_material_basepath = UC.globalConfig().AssetPath+skeleton_mesh_type_path

    
    #当导入的是子骨骼网格体时,使用父骨骼网格体的路径
    if parent_skmesh:
        fbx_create_path = parent_skmesh.get_path_name().rsplit('/',1)[0]+'/'
        asset_base_name = parent_skmesh.get_path_name().rsplit('/')[-3]
        filename = fbx_path.rsplit('/',1)[-1]
        fbx_name = filename.split('.')[0] 

    else:
        filename = fbx_path.rsplit('/',1)[-1]
        fbx_name = filename.split('.')[0] 
        asset_base_name = fbx_name.split(split_prefix)[-1]

        if old_scence_path:
            fbx_create_path=f'{skmesh_base_path}SkeletalMesh/'       #创建基础文件夹路径
        else:
            fbx_create_path=f'{skmesh_base_path}{asset_base_name}/SkeletalMesh/'       #创建基础文件夹路径

    print(f'导入骨骼网格体路径:{fbx_path},  {fbx_create_path}')
    if parent_skmesh:
        uSTools.fbxImport().skeletonMeshImport(fbx_path,fbx_create_path,parent_skmesh)
    else:
        uSTools.fbxImport().skeletonMeshImport(fbx_path,fbx_create_path)
    skeleton_asset_path = fbx_create_path+fbx_name
    skeleton_mesh_asset = unreal.EditorAssetLibrary.load_asset(skeleton_asset_path)
    skeleton_mesh_asset:unreal.SkeletalMesh
    if not skeleton_mesh_asset:
        print(f'导入骨骼网格体失败,请检查FBX文件:{fbx_path},  创建路径:{fbx_create_path}')
        return None
    #开启全精度uv
    sk_build_settings = skeletal_mesh_editor_subsystem.get_lod_build_settings(skeleton_mesh_asset,0)
    sk_build_settings.use_full_precision_u_vs = True
    skeletal_mesh_editor_subsystem.set_lod_build_settings(skeleton_mesh_asset,0,sk_build_settings)

    #设置计算切线类型
    lod_index = 0           # 目标 LOD 级别
    mask_channel = 0        # 0 = 红色通道
    section_count = skeletal_mesh_editor_subsystem.get_num_sections(skeleton_mesh_asset,lod_index)
    for section_index in range(section_count):
        #开启重计算切线
        skeletal_mesh_editor_subsystem.set_section_recompute_tangent(skeleton_mesh_asset, lod_index, section_index, recompute_tangent=True)
        #设置重计算切线蒙版通道
        skeletal_mesh_editor_subsystem.set_section_recompute_tangents_vertex_mask_channel(skeleton_mesh_asset, lod_index, section_index, mask_channel)

    physics_asset_name = fbx_name+'_PhysicsAsset'
    physics_asset_path = fbx_create_path+physics_asset_name
    #如果未成功自动生成物理资产则创建物理资产
    if not unreal.EditorAssetLibrary.does_asset_exist(physics_asset_path):
        skeletal_mesh_editor_subsystem.create_physics_asset(skeleton_mesh_asset)
    
    material_slots = skeleton_mesh_asset.materials
    new_material_slots = []

    #赋予材质
    skeleton_mesh_material_path = mesh_material_basepath+asset_base_name+'/Material'
    mesh_materials = uSTools.pathToMaterial(skeleton_mesh_material_path)
    for material_slot in material_slots:
        append_mat = False
        for mesh_material in mesh_materials:
            if mesh_material.get_name() == material_slot.material_slot_name:
                material_slot.material_interface = mesh_material
                new_material_slots.append(material_slot)
                append_mat = True
        if not append_mat:
            new_material_slots.append(material_slot)

    skeleton_mesh_asset.materials = new_material_slots

    #存在父骨骼网格体时,将子骨骼网格体的骨骼和物理资产设置为父骨骼网格体的骨骼和物理资产
    if parent_skmesh:
        parent_physics_asset = parent_skmesh.get_editor_property("physics_asset")
        #删除子骨骼网格体的骨骼和物理资产
        sub_physics_asset = skeleton_mesh_asset.get_editor_property("physics_asset")
        unreal.EditorAssetLibrary.delete_asset(sub_physics_asset.get_path_name())
        #将子骨骼网格体的物理资产设置为父骨骼网格体的物理资产
        skeletal_mesh_editor_subsystem.assign_physics_asset(skeleton_mesh_asset, parent_physics_asset)
        
        unreal.EditorAssetLibrary.save_directory('/Game')

    # #重新排序材质插槽
    # resort_mesh_material([skeleton_mesh_asset])

    return skeleton_mesh_asset


def createBluePrint(skmesh,tx_version,sk_type):
    if tx_version:
        split_prefix = 'SK_'
        base_bp_path = UC.globalConfig().AssetPath+'Common/BP/BP_Character'
        base_bp_asset = unreal.EditorAssetLibrary.load_asset(base_bp_path)
        if sk_type == 'Character':
            bp_basename = skmesh.get_name().replace(split_prefix,'BP_CH_')
        elif sk_type == 'Pro':
            bp_basename = skmesh.get_name().replace(split_prefix,'BP_Pro_')
        elif sk_type == 'Scence':
            bp_basename = skmesh.get_name().replace(split_prefix,'BP_BG_')
    else:
        split_prefix = 'UE_'
        base_bp_path = UC.globalConfig().ReferencePath+'BP/BP_Character'
        base_bp_asset = unreal.EditorAssetLibrary.load_asset(base_bp_path)
        bp_basename = skmesh.get_name().split(split_prefix,1)[-1]+'_AAI_BP'

    bp_base_path = skmesh.get_path_name().rsplit('SkeletalMesh',1)[0]
    
    #判断bp是否已经存在
    if not unreal.EditorAssetLibrary.does_asset_exist(bp_base_path+'/'+bp_basename):
        base_bp_class = unreal.load_class(None,base_bp_asset.get_path_name()+'_C')
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("ParentClass", base_bp_class)
        bp_asset = asset_tools.create_asset(
        bp_basename,          # 资产名称
        bp_base_path,         # 目标路径
        None,                 # 可选的类（通常为 None）
        factory               # 配置好的工厂
        )
        
        bp_class = unreal.load_class(None,bp_asset.get_path_name()+'_C')
        blueprint_cdo = unreal.get_default_object(bp_class)
        skeletal_mesh_comp = blueprint_cdo.get_editor_property("SkeletalMeshComponent")
        skeletal_mesh_comp.set_editor_property("SkeletalMesh", skmesh)
        unreal.EditorAssetLibrary.save_directory('/Game')
        #更新资产
        package = bp_asset.get_outer()
        result = unreal.EditorLoadingAndSavingUtils.reload_packages([package])
        # print(result)


def pSkDataToUeData(p_file_path,p_mtime):
    if 'Assets' in p_file_path:
        asset_name = p_file_path.split('.')[0].split('/')[-1]
        asset_type = p_file_path.split('/')[1]
        asset_basename = asset_name.split('SK_')[-1]
        ue_path = f'/Game/Assets/{asset_type}/{asset_basename}/SkeletalMesh/{asset_name}'
        
        if unreal.EditorAssetLibrary.does_asset_exist(ue_path):
            asset_tag = unreal.EditorAssetLibrary.get_tag_values(ue_path)
            asset_import_data = asset_tag.get('AssetImportData')
            data = json.loads(asset_import_data)
            mtime = data[0]['Timestamp']
            
            if int(mtime) == int(p_mtime):
                asset_mask = 0              #mask类型,0:时间相同,1:时间不同,2:UE对象不存在
            else:
                asset_mask = 1
                
        else:
            asset_mask = 2
        
        return ue_path,asset_mask
    
    else:
        None,None


def importFbxToUe(fbx_path,tx_version=1):
    if os.path.exists(fbx_path):
        fbx_path = fbx_path.replace('\\','/')
        dirpath = fbx_path.rsplit('/', 1)[0].replace('\\','/')
        dirpath_split_list = dirpath.split('/')
        if 'Character' in dirpath_split_list:
            sk_type = 'Character'
        elif 'Pro' in dirpath_split_list:
            sk_type = 'Pro'
        elif 'Scence' in dirpath_split_list:
            sk_type = 'Scence'
        skmesh = importSkMesh(fbx_path,sk_type,tx_version)

        createBluePrint(skmesh,tx_version,sk_type)

        #保存全部创建的文件
        unreal.EditorAssetLibrary.save_directory('/Game')
    if skmesh:
        return skmesh

def importSubFbxToUe(fbx_path,tx_version=1,parent_skmesh=None):
    if os.path.exists(fbx_path):
        fbx_path = fbx_path.replace('\\','/')
        dirpath = fbx_path.rsplit('/', 1)[0].replace('\\','/')
        dirpath_split_list = dirpath.split('/')
        if 'Character' in dirpath_split_list:
            sk_type = 'Character'
        elif 'Pro' in dirpath_split_list:
            sk_type = 'Pro'
        elif 'Scence' in dirpath_split_list:
            sk_type = 'Scence'
        skmesh = importSkMesh(fbx_path,sk_type,tx_version,parent_skmesh)


        #保存全部创建的文件
        unreal.EditorAssetLibrary.save_directory('/Game')

        
def skFbxCompare(filename,mtime,version):   #version  0:财神,1踏星

    if version == 0:
        ch_name = filename.split('UE_')[-1].split('.')[0]
        sk_base_path = UC.globalConfig().ReferencePath+f'/Character/{ch_name}/SkeletalMesh/'
    elif version == 1:
        ch_name = filename.split('SK_')[-1].split('.')[0]
        sk_base_path = UC.globalConfig().AssetPath+f'/Character/{ch_name}/SkeletalMesh/'
    sk_asset_path = sk_base_path+filename.split('.')[0]

    print(sk_asset_path)
    if unreal.EditorAssetLibrary.does_asset_exist(sk_asset_path):
        asset_tag = unreal.EditorAssetLibrary.get_tag_values(sk_asset_path)
        asset_import_data = asset_tag.get('AssetImportData')
        data = json.loads(asset_import_data)
        Timestamp = data[0]['Timestamp']
        if mtime == int(Timestamp):
            return 0    #资产无变化
        else:
            return 1    #资产被更改
    
    else:
        return 2        #资产未被创建





class FileTableModel(QtCore.QAbstractTableModel):
    def __init__(self,data):
        super().__init__()
        self._data = data
        self._headers = ["名称", "路径", "子骨骼类型", "时间"]
        # 中文表头到英文字典键的映射
        self._field_mapping = {
            "名称": "fileName",
            "路径": "packageName",
            "子骨骼类型": "subSkeletonMeshcount",
            "时间": "modifyTime"
        }

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers) + 1

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        item = self._data[row]

        if role == QtCore.Qt.DisplayRole:
            if col == 0:
                return str(row + 1)
            else:
                field = self._headers[col - 1]
                key = self._field_mapping.get(field, field)
                return item.get(key, "")
        elif role == QtCore.Qt.ForegroundRole:
            if item.get('mask', 0) == 1:
                return QtGui.QColor(QtCore.Qt.yellow)
            elif item.get('mask', 0) == 2:
                return QtGui.QColor(QtCore.Qt.green)
            else:
                return QtGui.QColor(QtCore.Qt.white)
        return None

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return ""  # 行号列表头留空
            else:
                return self._headers[section - 1]
        return None

    def getRowData(self, row_index):
        """返回指定行的完整字典（包含 name/path/time/mask）"""
        if 0 <= row_index < len(self._data):
            return self._data[row_index]
        return None
    
    def replaceData(self, new_data):
        """替换全部数据并刷新视图"""
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()


class FileTableWindow(QtWidgets.QWidget):
    """主窗口，包含表格和交互按钮"""
    def __init__(self):
        super().__init__()
        self.data = []
        self.NameFilters = ["SK_", ".fbx"]
        self.path = ''
        self._ui()

    def _ui(self):
        self.setWindowTitle("骨骼网格体导入工具")
        self.resize(750, 400)

        self.folderSelectGroup = UCW.folderSelectGroup("网格体文件路径:") #定义路径选择组
        self.folderSelectGroup.leFolderPath.textChanged.connect(self.pathToFilses)        # 文字框改变时刷新

        # 创建模型和视图
        self.model = FileTableModel(self.data)
        self.ModelSort = QtCore.QSortFilterProxyModel()
        self.ModelSort.setSourceModel(self.model)
        self.table_view = MTableView(size=dayu_theme.medium, show_row_count=True)
        self.table_view.setModel(self.ModelSort)

        # 设置字体
        font = QtGui.QFont()
        font.setPointSize(20)
        self.table_view.setFont(font)
        self.table_view.horizontalHeader().setFont(font)
        self.table_view.verticalHeader().setFont(font)
        
        # 选择整行 + 多选
        self.table_view.setSelectionBehavior(MTableView.SelectRows)
        self.table_view.setSelectionMode(MTableView.ExtendedSelection)

        # 调整列宽
        self.table_view.resizeColumnsToContents()
        self.table_view.setColumnWidth(0, 10)
        self.table_view.setColumnWidth(1, 180)
        self.table_view.setColumnWidth(2, 400)
        self.table_view.setColumnWidth(3, 100)
        self.table_view.setColumnWidth(4, 160)

        # 按钮
        self.ver_switch = MSwitch()
        self.ver_switch.setChecked(True)
        self.ver_switch.clicked.connect(self.verChange)
        ver_switch_lay = QtWidgets.QFormLayout()
        ver_switch_lay.addRow(MLabel("启用踏星流程"), self.ver_switch)

        self.btn_print = MPushButton("导入选中网格体")
        self.btn_print.clicked.connect(lambda:self.createSelectedAsset(selected = True))

        self.btn_print1 = MPushButton("导入全部网格体")
        self.btn_print1.clicked.connect(lambda:self.createSelectedAsset(selected = False))

        # 布局
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(ver_switch_lay)
        main_layout.addLayout(self.folderSelectGroup)
        main_layout.addWidget(self.table_view)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.btn_print)
        button_layout.addWidget(self.btn_print1)
        main_layout.addLayout(button_layout)


    def pathToFilses(self):
        path = self.folderSelectGroup.getFolderPath()
        sk_files_data = []
        filter_files = []
        groom_files = []
        path_cont = len(path.split(':')[0])
        if path and path_cont==1:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    #判断文件名是否包含指定的子骨骼网格体类名
                    if any(ch in filename for ch in SUB_SKELETON_MESHS_CLASS):
                        file_info = {}
                        file_path=str(os.path.join(dirpath, filename)).replace('\\','/')
                        file_info['localPath'] = file_path
                        file_info['subSkeletonMesh'] = None
                        filter_files.append(file_info)
                        continue
                    #名称过滤
                    if all(NameFilter in filename for NameFilter in self.NameFilters):
                        file_info = {}
                        #增加一些自定义参数
                        file_path=str(os.path.join(dirpath, filename)).replace('\\','/')
                        file_info['fileName'] = filename
                        file_info['pipelineMask'] = 0
                        file_info['packageName'] = file_path
                        file_info['localPath'] = file_path
                        mtime = os.path.getmtime(file_path)
                        file_info['mtime'] = int(mtime)
                        file_info['modifyTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                        file_info['subSkeletonMesh'] = []
                        file_info['subSkeletonMeshcount'] = ''
                        file_info['groomAssets'] = []

                        mask = skFbxCompare(filename,int(mtime),self.ver_switch.isChecked())
                        file_info['mask'] = mask

                        sk_files_data.append(file_info)
            
            #将子骨骼网格体信息添加到对应的主网格体数据中
            for filter_file in filter_files:
                for file_info in sk_files_data:
                    if filter_file['localPath'].rsplit('_',1)[0] == file_info['localPath'].rsplit('.',1)[0]:
                        file_info['subSkeletonMesh'].append(filter_file)
                        file_info['subSkeletonMeshcount'] += filter_file['localPath'].rsplit('_',1)[-1].rsplit('.',1)[0]+' '
        
            self.filesToData(sk_files_data)

        elif path and '/Assets' in path:
            pipeline_path = 'Assets'+path.split('/Assets')[-1]
            #获取pipeline最新文件
            try:
                project_id, headers, project_name = uSTools.getProjectId()
            except:
                project_id = None
            if project_id:
                new_files_info = []
                if self.path == path:       #判断路径是否与旧路径相同,相同则使用上一次的检索数据
                    files_info = self.files_info
                else:
                    self.files_info = uSTools.getFilesInfo(project_id, headers, pipeline_path)
                    files_info = self.files_info
                    self.path = path
                
                for file_info in files_info:
                    filename = file_info['fileName']
                    #判断文件名是否包含指定的子骨骼网格体类名
                    if any(ch in filename for ch in SUB_SKELETON_MESHS_CLASS):
                        file_info['projectName'] = project_name
                        packageName = file_info['packageName']
                        file_info['subSkeletonMesh'] = None
                        file_info['localPath'] = f'Y:/{project_name}/{packageName}'
                        filter_files.append(file_info)
                        continue
                    #判断文件是否为groom
                    if 'BD.abc' in filename:
                        file_info['projectName'] = project_name
                        packageName = file_info['packageName']
                        file_info['localPath'] = f'Y:/{project_name}/{packageName}'
                        groom_files.append(file_info)
                        continue
                    if all(NameFilter in filename for NameFilter in self.NameFilters):
                        #增加一些自定义参数
                        packageName = file_info['packageName']
                        file_info['projectName'] = project_name
                        file_info['pipelineMask'] = 1
                        file_info['modifyTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_info['mtime']))
                        file_info['localPath'] = f'Y:/{project_name}/{packageName}'
                        file_info['subSkeletonMesh'] = []
                        file_info['subSkeletonMeshcount'] = ''
                        file_info['groomAssets'] = []

                        #获取对应的UE资产信息
                        ue_asset_path,asset_mask = pSkDataToUeData(file_info['packageName'],file_info['mtime'])
                        file_info['mask'] = asset_mask
                        # print(file_info)
                        new_files_info.append(file_info)
                for file_info in new_files_info:
                    #将子骨骼网格体信息添加到对应的主网格体数据中
                    for filter_file in filter_files:
                            if filter_file['localPath'].rsplit('_',1)[0] == file_info['localPath'].rsplit('.',1)[0]:
                                file_info['subSkeletonMesh'].append(filter_file)
                                file_info['subSkeletonMeshcount'] += filter_file['localPath'].rsplit('_',1)[-1].rsplit('.',1)[0]+' '
                    #将groom资产信息添加到对应的主网格体数据中
                    for groom_file in groom_files:
                            if groom_file['localPath'].rsplit('/',1)[0] == file_info['localPath'].rsplit('/',1)[0]:
                                file_info['groomAssets'].append(groom_file)
                self.filesToData(new_files_info)
                # print(new_files_info)
                # if files_info:
                #     uSTools.downloadFiles(files_info, project_name)
    
    def filesToData(self,datas):
        # self.model.setData(self.datas)
        # print(datas)
        # for data in datas:
        #     path = data['path']

        self.model.replaceData(datas)
        

    def verChange(self):
        if self.ver_switch.isChecked():
            self.NameFilters = ["SK_", ".fbx"]
        else:
            self.NameFilters = ["UE_", ".fbx"]

        self.pathToFilses()



    def createSelectedAsset(self,selected = False):
        """获取表格中所有选中行的完整数据并打印"""
        if selected:
            selection_model = self.table_view.selectionModel()
            selected_indexes = selection_model.selectedRows()

            for proxy_idx in selected_indexes:
                source_idx = self.ModelSort.mapToSource(proxy_idx)  # 获取排序后的序号
                row_info = self.model.getRowData(source_idx.row())   # 获取原始数据            
                print(row_info)
                if row_info['pipelineMask'] == 1:   #判断当前行是否为pipeline地址
                    uSTools.downloadFiles([row_info], row_info['projectName'])
                    groom_assets = row_info['groomAssets']
                    print(groom_assets)
                    if groom_assets:
                        for groom_asset in groom_assets:
                            uSTools.downloadFiles([groom_asset], row_info['projectName'],asset_type='abc')

                skmesh = importFbxToUe(row_info['localPath'],self.ver_switch.isChecked())
                importSkGroom(skmesh,row_info['localPath'])
                #导入完成主骨骼网格体后,导入子骨骼网格体
                if row_info['subSkeletonMesh']:
                    for sub_mesh in row_info['subSkeletonMesh']:
                        importSubFbxToUe(sub_mesh['localPath'],self.ver_switch.isChecked(),skmesh)
        else:
            visible_rows = self.model.rowCount()
            for row in range(visible_rows):
                row_info = self.model.getRowData(row)
                # print(row_info)
                if row_info['pipelineMask'] == 1:   #判断当前行是否为pipeline地址
                    uSTools.downloadFiles([row_info], row_info['projectName'])
                    groom_assets = row_info['groomAssets']
                    print(groom_assets)
                    if groom_assets:
                        for groom_asset in groom_assets:
                            uSTools.downloadFiles([groom_asset], row_info['projectName'],asset_type='abc')

                skmesh = importFbxToUe(row_info['localPath'],self.ver_switch.isChecked())
                importSkGroom(skmesh,row_info['localPath'])
                #导入完成主骨骼网格体后,导入子骨骼网格体
                if row_info['subSkeletonMesh']:
                    for sub_mesh in row_info['subSkeletonMesh']:
                        importSubFbxToUe(sub_mesh['localPath'],self.ver_switch.isChecked(),skmesh)




def start():
    with application() as app:
        global test
        test = FileTableWindow()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))




if __name__ == "__main__":

    # data = [
    #     {'fileName': 'xxx', 'packageName': '/home/xxx', 'modifyTime': '2026-05-18', 'mask': 1},
    #     {'fileName': 'aaa', 'packageName': '/opt/aaa',  'modifyTime': '2026-05-17', 'mask': 0},
    #     {'fileName': 'bbb', 'packageName': '/var/bbb',  'modifyTime': '2026-05-16', 'mask': 1},
    #     {'fileName': 'ccc', 'packageName': '/tmp/ccc',  'modifyTime': '2026-05-15', 'mask': 0},
    # ]

    start()






