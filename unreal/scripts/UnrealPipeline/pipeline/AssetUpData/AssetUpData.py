import unreal
import sys
import os
import time
import json
import importlib
from Qt.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QPushButton, QSplitter, QHeaderView, QComboBox, QLabel, QLineEdit
)
from Qt.QtCore import Qt, QTimer, Signal
from Qt.QtGui import QColor

from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.item_view import MTreeView
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.tab_widget import MTabWidget
from dayu_widgets.switch import MSwitch
from dayu_widgets.label import MLabel
from dayu_widgets.button_group import MCheckBox
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

import UnrealPipeline.core.uSTools as uSTools
importlib.reload(uSTools)
import UnrealPipeline.core.Config as UC
import UnrealPipeline.core.UnrealHelper as UH
importlib.reload(UH)


editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


# ========== 两组测试数据 ==========
FILE_DATA_1 = {
    "Ep001": [
        {"fileName": "ep001_opening.mov", "time": "2024-01-01 10:00:00", "path": "/data/Ep001/ep001_opening.mov", "mask": 0},
        {"fileName": "ep001_credits.mov", "time": "2024-01-01 10:05:00", "path": "/data/Ep001/ep001_credits.mov", "mask": 1},
        {"fileName": "AA_ep001_poster.png", "time": "2024-01-01 10:10:00", "path": "/data/Ep001/AA_ep001_poster.png", "mask": 0},
    ],
    "Ep001_sc001": [
        {"fileName": "sc001_take1.mov", "time": "2024-01-02 09:00:00", "path": "/data/Ep001/sc001/sc001_take1.mov", "mask": 0},
        {"fileName": "sc001_take2.mov", "time": "2024-01-02 09:15:00", "path": "/data/Ep001/sc001/sc001_take2.mov", "mask": 2},
        {"fileName": "sc001_audio.wav", "time": "2024-01-02 09:30:00", "path": "/data/Ep001/sc001/sc001_audio.wav", "mask": 1},
        {"fileName": "SK_sc001_character", "time": "2024-01-02 09:45:00", "path": "/data/Ep001/sc001/SK_sc001_character", "mask": 1},
    ],
    "Ep001_sc002": [
        {"fileName": "sc002_main.mov", "time": "2024-01-03 14:00:00", "path": "/data/Ep001/sc002/sc002_main.mov", "mask": 0},
        {"fileName": "sc002_plate.png", "time": "2024-01-03 14:20:00", "path": "/data/Ep001/sc002/sc002_plate.png", "mask": 2},
        {"fileName": "AA_effect.mov", "time": "2024-01-03 14:30:00", "path": "/data/Ep001/sc002/AA_effect.mov", "mask": 1},
    ],
    "Ep002": [
        {"fileName": "ep002_intro.mov", "time": "2024-02-01 11:00:00", "path": "/data/Ep002/ep002_intro.mov", "mask": 0},
        {"fileName": "ep002_script.pdf", "time": "2024-02-01 11:30:00", "path": "/data/Ep002/ep002_script.pdf", "mask": 1},
    ],
    "Ep002_sc001": [
        {"fileName": "sc001_fx.mov", "time": "2024-02-03 16:00:00", "path": "/data/Ep002/sc001/sc001_fx.mov", "mask": 2},
        {"fileName": "sc001_bg.jpg", "time": "2024-02-03 16:10:00", "path": "/data/Ep002/sc001/sc001_bg.jpg", "mask": 0},
        {"fileName": "SK_sc001_model.fbx", "time": "2024-02-03 16:20:00", "path": "/data/Ep002/sc001/SK_sc001_model.fbx", "mask": 2},
    ],
}

# 新增第二组测试数据（集数和场次不同，文件名也不同）
FILE_DATA_2 = {
    "Ep003": [
        {"fileName": "ep003_intro.mp4", "time": "2024-03-01 08:00:00", "path": "/data/Ep003/ep003_intro.mp4", "mask": 0},
        {"fileName": "ep003_outro.mp4", "time": "2024-03-01 08:15:00", "path": "/data/Ep003/ep003_outro.mp4", "mask": 2},
    ],
    "Ep003_sc001": [
        {"fileName": "sc001_takeA.mov", "time": "2024-03-02 10:00:00", "path": "/data/Ep003/sc001/sc001_takeA.mov", "mask": 1},
        {"fileName": "sc001_takeB.mov", "time": "2024-03-02 10:20:00", "path": "/data/Ep003/sc001/sc001_takeB.mov", "mask": 0},
        {"fileName": "AA_sc001_log.txt", "time": "2024-03-02 10:30:00", "path": "/data/Ep003/sc001/AA_sc001_log.txt", "mask": 1},
    ],
    "Ep003_sc002": [
        {"fileName": "sc002_main.mp4", "time": "2024-03-03 13:00:00", "path": "/data/Ep003/sc002/sc002_main.mp4", "mask": 0},
        {"fileName": "sc002_bg.png", "time": "2024-03-03 13:30:00", "path": "/data/Ep003/sc002/sc002_bg.png", "mask": 2},
    ],
    "Ep004": [
        {"fileName": "ep004_start.mov", "time": "2024-04-01 09:00:00", "path": "/data/Ep004/ep004_start.mov", "mask": 1},
        {"fileName": "ep004_end.mov", "time": "2024-04-01 09:20:00", "path": "/data/Ep004/ep004_end.mov", "mask": 0},
    ],
    "Ep004_sc001": [
        {"fileName": "sc001_vfx.mov", "time": "2024-04-02 11:00:00", "path": "/data/Ep004/sc001/sc001_vfx.mov", "mask": 2},
        {"fileName": "sc001_model.fbx", "time": "2024-04-02 11:15:00", "path": "/data/Ep004/sc001/sc001_model.fbx", "mask": 1},
        {"fileName": "SK_sc001_anim.mov", "time": "2024-04-02 11:30:00", "path": "/data/Ep004/sc001/SK_sc001_anim.mov", "mask": 0},
    ],
}

# 文件名过滤器映射
FILTER1_MAP = {
    "全部": '',
    "FBX": ".fbx",
    "ABC": ".abc",
}
FILTER2_MAP = {
    # "全部": None,
    "踏星": "TX",
    "财神": "CS",
    "万相": "WX",
}
# mask 值过滤器选项
MASK_FILTER_MAP = {
    "全部": None,
    "未更改": 0,
    "已更改": 1,
    "未创建": 2,
    "错误": 3,
}
# 环节 值过滤器选项
SEGMENT_FILTER_MAP = {
    "动画": 'an',
    "groom缓存(guid)": 'groom',
    "布料缓存": 'cloth',
    "摄像机": 'cam',
}


def getProjectName():
    project_dir = unreal.Paths.project_dir()
    try:
        project_name = project_dir.split('/')[-3]
    except:
        project_name = ''

    return project_name


def localPathToFileData(path,version,process):
    file_datas = {}
    ep_sc_paths = {}
    if process == 'an':
        old_process_path = '/Animation/fbx/'
        tx_process_path = '/FBX'
    elif process == 'cam':
        old_process_path = '/Animation/cam/'
        tx_process_path = '/Cam'
    elif process == 'groom':
        # TX:/EP001/sc001/Ep001_sc001_001/CFX/nHair_nCache
        # WXZW:/EP001/Effect/nCache/UE_nCloth_nCache
        old_process_path = '/Effect/nCache/nHair_nCache/'  
        tx_process_path = ''
    elif process == 'cloth':
        # TX:/EP001/sc001/Ep001_sc001_001/CFX/nHair_nCache
        # WXZW:/EP001/Effect/nCache/UE_nCloth_nCache
        # Y:\SSDSY_CS\EP003\Effect\nCache\nCloth_nCache\sc006\Ep003_sc006_015
        old_process_path = '/Effect/nCache/nCloth_nCache/'    
        tx_process_path = ''
    
    with os.scandir(path) as entries:
        for entry in entries:
            # entry.name 是文件名/文件夹名
            # entry.is_dir() 判断是否为文件夹（默认不跟随符号链接）
            if entry.is_dir() and 'ep' in entry.name.lower():
                ep_path = path+entry.name

                if version == 'CS':     #万相暂不开启缓存更新功能
                    asset_folder_path = ep_path+old_process_path
                    if not os.path.exists(asset_folder_path):
                        continue
                    with os.scandir(asset_folder_path) as sub_entries:
                        for sub_entrie in sub_entries:
                            if sub_entrie.is_dir() and 'sc0' in sub_entrie.name.lower():
                                ep_sc_paths[entry.name+'_'+sub_entrie.name] = asset_folder_path+sub_entrie.name
                # Y:\TX\EP001\sc004\FBX
                elif version == 'TX':
                    with os.scandir(ep_path) as sub_entries:
                        for sub_entrie in sub_entries:
                            if sub_entrie.is_dir() and 'sc0' in sub_entrie.name.lower():
                                asset_folder_path = f'{ep_path}/{sub_entrie.name}{tx_process_path}'
                                if not os.path.exists(asset_folder_path):
                                    continue
                                ep_sc_paths[entry.name+'_'+sub_entrie.name] = asset_folder_path

    
    for sc_name,folder in ep_sc_paths.items():
        for dirpath, dirnames, filenames in os.walk(folder):
            for filename in filenames:
                file_path=str(os.path.join(dirpath, filename)).replace('\\','/')
                #获取文件数据
                file_data = {}
                mtime = os.path.getmtime(file_path)
                readable_time = time.ctime(mtime)
                file_data["fileName"] = filename
                file_data["mtime"] = int(mtime)
                file_data["time"] = readable_time
                file_data["path"] = file_path

                if process == 'an':
                    mask = anFbxCompare(filename,int(mtime))
                    file_data["mask"] = mask
                elif process == 'cam':
                    #摄像机文件默认为0
                    file_data["mask"] = 0
                elif process == 'groom':
                    if 'nHair_nCache' not in file_path:
                        continue
                    mask = groomAssetCompare(file_path,int(mtime))
                    file_data["mask"] = mask
                elif process == 'cloth':
                    if 'nCloth_nCache' not in file_path:
                        continue
                    mask = clothAssetCompare(file_path,int(mtime))
                    file_data["mask"] = mask
                try:
                    file_datas[sc_name].append(file_data)
                except:
                    file_datas[sc_name] = [file_data]
    
    return file_datas


def pipPathToFileData(pip_an_fbx_path, version, process):
    path_split = pip_an_fbx_path.split('/')
    if process == 'an':
        filter_list = ['_an']
        # EP001_sc001'
        if version == 'TX':
            folder_name = f'{path_split[0]}_{path_split[1]}'
        elif version == 'WX':
            folder_name = f'{path_split[0]}_{path_split[3]}'
    if process == 'groom':
        filter_list = ['_hCache']
        if version == 'TX':
            folder_name = f'{path_split[0]}_{path_split[1]}'
        elif version == 'WX':
            folder_name = f'{path_split[0]}_{path_split[4]}'
    if process == 'cloth':
        filter_list = ['_Cache']
        if version == 'TX':
            folder_name = f'{path_split[0]}_{path_split[1]}'
        elif version == 'WX':
            folder_name = f'{path_split[0]}_{path_split[4]}'
    if process == 'cam':
        filter_list = ['_cam']
        if version == 'TX':
            folder_name = f'{path_split[0]}_{path_split[1]}'
        elif version == 'WX':
            folder_name = f'{path_split[0]}_{path_split[4]}'


    file_datas = {}
    #获取pipeline最新文件
    try:
        project_id, headers, project_name = uSTools.getProjectId()
    except:
        project_id = None

    # pip_an_fbx_path = 'EP000/sc001/FBX'
    if project_id:
        new_files_info = []
        files_info = uSTools.getFilesInfo(project_id, headers, pip_an_fbx_path)
        if not files_info:
            return file_datas
        for file_info in files_info:
            filename = file_info['fileName']
            # print(filename)
            if all(item in filename for item in filter_list):
                #增加一些自定义参数
                packageName = file_info['packageName']
                file_info['projectName'] = project_name
                file_info['pipelineMask'] = 1
                file_info['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_info['mtime']))
                file_info['path'] = f'Y:/{project_name}/{packageName}'

                #获取对应的UE资产信息,并比对文件时间
                ue_asset_path,asset_mask = pAssetDataToUeData(file_info['fileName'],file_info['mtime'],process)
                file_info['mask'] = asset_mask
                
                # print(file_info)
                new_files_info.append(file_info)

                file_datas[folder_name] = new_files_info

    return file_datas



def getAnSubDirs(version):
    #获取pipeline最新文件
    try:
        project_id, headers, project_name = uSTools.getProjectId()
    except:
        project_id = None

    cam_dirs_path = []
    if version == 'WX':
        #WXZW:/EP001/Animation/fbx/cam/sc001
        keywords=['ep', 'animation', 'fbx', 'cam', 'sc']
        cam_dirs_path = findDirsByPathChain(project_id, headers, keywords)

    elif version == 'TX':
        # TX:/EP001/sc001/Cam
        keywords=['ep', 'sc', 'cam']
        cam_dirs_path = findDirsByPathChain(project_id, headers, keywords)

    cam_dirs_path.sort()
    return cam_dirs_path


def findDirsByPathChain(project_id, headers, keywords, parent_id=0):
    """
    按 keywords 逐层下钻查找目录，返回最终匹配目录的 path 列表。
    例如 keywords=['ep', 'sc', 'cam']
    """
    if not keywords:
        return []

    keyword, rest = keywords[0], keywords[1:]
    dirs = uSTools.pipGetDir(project_id, headers, parent_id)
    matched = [d for d in dirs if keyword in d['path'].lower()]

    if not rest:
        return [d['path'] for d in matched]

    result = []
    for d in matched:
        result.extend(findDirsByPathChain(project_id, headers, rest, d['id']))
    return result



def getCamSubDirs(version):
    #获取pipeline最新文件
    try:
        project_id, headers, project_name = uSTools.getProjectId()
    except:
        project_id = None

    fbx_dirs_path = []
    if version == 'WX':
        # WXZW:/EP001/Animation/fbx/sc001/Ep001_sc001_009
        keywords=['ep', 'animation', 'fbx', 'sc']
        fbx_dirs_path = findDirsByPathChain(project_id, headers, keywords)

    elif version == 'TX':
        # TX:/EP001/sc001/FBX/Ep001_sc001_002
        keywords=['ep', 'sc', 'fbx']
        fbx_dirs_path = findDirsByPathChain(project_id, headers, keywords)

    fbx_dirs_path.sort()
    return fbx_dirs_path

def getGroomSubDirs(version):
    #获取pipeline最新文件
    try:
        project_id, headers, project_name = uSTools.getProjectId()
    except:
        project_id = None

    fbx_dirs_path = []
    # if version == 'WX':
    #     # WXZW:/EP001/Animation/fbx/sc001/Ep001_sc001_009
    #     keywords=['ep', 'animation', 'fbx', 'sc']
    #     fbx_dirs_path = findDirsByPathChain(project_id, headers, keywords)

    if version == 'TX':
        # TX:/EP001/sc008/Ep001_sc008_006/CFX/nHair_nCache
        keywords=['ep', 'sc']
        fbx_dirs_path = findDirsByPathChain(project_id, headers, keywords)

    fbx_dirs_path.sort()
    return fbx_dirs_path

def getClothSubDirs(version):
    #获取pipeline最新文件
    try:
        project_id, headers, project_name = uSTools.getProjectId()
    except:
        project_id = None

    fbx_dirs_path = []
    # if version == 'WX':
    #     # WXZW:/EP001/Animation/fbx/sc001/Ep001_sc001_009
    #     keywords=['ep', 'animation', 'fbx', 'sc']
    #     fbx_dirs_path = findDirsByPathChain(project_id, headers, keywords)

    if version == 'TX':
        # TX:/EP001/sc008/Ep001_sc008_006/CFX/nCloth_nCache
        keywords=['ep', 'sc']
        fbx_dirs_path = findDirsByPathChain(project_id, headers, keywords)

    fbx_dirs_path.sort()
    return fbx_dirs_path



def dirToDirData(fbx_dirs, project_name):
    dir_datas = {}
    if project_name == 'TX':
        for fbx_dir in fbx_dirs:
            dir_split = fbx_dir.split('/')
            ep_name = dir_split[0]
            sc_name = dir_split[1]
            sc_key = f'{ep_name.upper()}_{sc_name}'
            if sc_key not in dir_datas:
                dir_datas[sc_key] = []
            dir_datas[sc_key].append(fbx_dir)
    elif project_name == 'WX':
        for fbx_dir in fbx_dirs:
            dir_split = fbx_dir.split('/')
            ep_name = dir_split[0]
            sc_name = dir_split[3]
            sc_key = f'{ep_name.upper()}_{sc_name}'
            if sc_key not in dir_datas:
                dir_datas[sc_key] = []
            dir_datas[sc_key].append(fbx_dir)
    dir_datas = dict(sorted(dir_datas.items()))
    return dir_datas




def pAssetDataToUeData(p_file_path,p_mtime,process):
    asset_name = p_file_path.split('.')[0].split('/')[-1]
    asset_name_split = asset_name.split('_')
    #/Game/Shots/EP001/sc002/Ep001_sc002_015/Animation
    cam = f'{asset_name_split[0]}_{asset_name_split[1]}_{asset_name_split[2]}'
    if process == 'cam':
        #摄像机默认为0
        return None,0
    if process == 'an':
        ue_path = f'/Game/Shots/{asset_name_split[0]}/{asset_name_split[1]}/{cam}/Animation/{asset_name}'
    
    if process == 'cloth':
        # '/Game/Shots/EP001/sc008/Ep001_sc008_006/Cache/Ep001_sc008_006_XiaoNvHai_1-54_Cache'
        ue_path = f'/Game/Shots/{asset_name_split[0]}/{asset_name_split[1]}/{cam}/Cache/{asset_name}'
    if process != 'groom':
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
    #groom模式下要判断两个资产
    if process == 'groom':
        # '/Game/Shots/EP001/sc008/Ep001_sc008_006/Cache/Groom/Ep001_sc008_006_XiaoNvHai_Hair02_1-54_hCache_guides_cache'
        ue_path = f'/Game/Shots/{asset_name_split[0]}/{asset_name_split[1]}/{cam}/Cache/Groom'
        guid_cache_asset_path = f'{ue_path}/{asset_name}_guides_cache'
        strand_cache_asset_path = f'{ue_path}/{asset_name}_strands_cache'
        if unreal.EditorAssetLibrary.does_asset_exist(guid_cache_asset_path):
            asset_tag = unreal.EditorAssetLibrary.get_tag_values(guid_cache_asset_path)
            asset_import_data = asset_tag.get('AssetImportData')
            data = json.loads(asset_import_data)
            mtime = data[0]['Timestamp']
            if int(mtime) == int(p_mtime):
                asset_mask = 0              #mask类型,0:时间相同,1:时间不同,2:UE对象不存在
            else:
                asset_mask = 1
        elif unreal.EditorAssetLibrary.does_asset_exist(strand_cache_asset_path):
            asset_tag = unreal.EditorAssetLibrary.get_tag_values(strand_cache_asset_path)
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


def anFbxCompare(filename,mtime):
    
    cam_split = filename.split('_')
    if len(cam_split) < 6 and '.fbx' not in filename.lower():
        return 3        #命名不合规
    ep_name = cam_split[0]
    sc_name = cam_split[1]
    cam_name = f'{ep_name}_{sc_name}_{cam_split[2]}'
    an_base_path = f'/Game/Shots/{ep_name}/{sc_name}/{cam_name}/Animation/'
    an_asset_path = an_base_path+filename.split('.')[0]
    
    if unreal.EditorAssetLibrary.does_asset_exist(an_asset_path):
        asset_tag = unreal.EditorAssetLibrary.get_tag_values(an_asset_path)
        asset_import_data = asset_tag.get('AssetImportData')
        data = json.loads(asset_import_data)
        Timestamp = data[0]['Timestamp']
        if mtime == int(Timestamp):
            return 0    #资产无变化
        else:
            return 1    #资产被更改
    
    else:
        return 2        #资产未被创建


def clothAssetCompare(abc_path,mtime):
    abc_split = abc_path.split('_')
    if len(abc_split) < 6 and '.abc' not in abc_path.lower():
        return 3        #命名不合规
    asset_ch_path=UC.globalConfig.get().AssetPath+'Character/'
    abc_asset_name = abc_path.split('/')[-1].split('.')[0]
    abc_base_name = abc_asset_name.rsplit('_',2)[0].split('_',3)[-1]
    abc_split = abc_asset_name.split('_')
    if '-' in abc_base_name:
        abc_base_name = abc_base_name.split('-')[0]

    abc_base_name = abc_base_name.rstrip('0123456789')      #清除cache后缀数字
    mat_path=asset_ch_path+abc_base_name+'/Material'

    cache_asset_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/Cache/{abc_asset_name}'
    if unreal.EditorAssetLibrary.does_asset_exist(cache_asset_path):
        asset_tag = unreal.EditorAssetLibrary.get_tag_values(cache_asset_path)
        asset_import_data = asset_tag.get('AssetImportData')
        data = json.loads(asset_import_data)
        Timestamp = data[0]['Timestamp']
        if mtime == int(Timestamp):
            return 0    #资产无变化
        else:
            return 1    #资产被更改
    
    else:
        return 2        #资产未被创建


def groomAssetCompare(abc_path,mtime):
    abc_split = abc_path.split('_')
    if len(abc_split) < 6 and '.abc' not in abc_path.lower():
        return 3        #命名不合规
    abc_asset_name = abc_path.split('/')[-1].split('.')[0]
    abc_base_name = abc_asset_name.rsplit('_',2)[0].split('_',3)[-1]
    abc_split = abc_asset_name.split('_')
    if '-' in abc_base_name:
        abc_base_name = abc_base_name.split('-')[0]

    abc_base_name = abc_base_name.rstrip('0123456789')      #清除cache后缀数字

    base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'
    des_path = base_path+'Cache/Groom'    #缓存目标文件夹
    guid_cache_asset_path = f'{des_path}/{abc_asset_name}_guides_cache'
    strand_cache_asset_path = f'{des_path}/{abc_asset_name}_strands_cache'
    if unreal.EditorAssetLibrary.does_asset_exist(guid_cache_asset_path):
        asset_tag = unreal.EditorAssetLibrary.get_tag_values(guid_cache_asset_path)
        asset_import_data = asset_tag.get('AssetImportData')
        data = json.loads(asset_import_data)
        Timestamp = data[0]['Timestamp']
        if mtime == int(Timestamp):
            return 0    #资产无变化
        else:
            return 1    #资产被更改
    
    elif unreal.EditorAssetLibrary.does_asset_exist(strand_cache_asset_path):
        asset_tag = unreal.EditorAssetLibrary.get_tag_values(strand_cache_asset_path)
        asset_import_data = asset_tag.get('AssetImportData')
        data = json.loads(asset_import_data)
        Timestamp = data[0]['Timestamp']
        if mtime == int(Timestamp):
            return 0    #资产无变化
        else:
            return 1    #资产被更改
    else:
        return  2


def pathToSequence(an_paths):
    for an_path in an_paths:
        an_path_split = an_path.split('/')[-1].split('_')
        ep_name = an_path_split[0]
        sc_name = an_path_split[1]
        cam_name = f'{ep_name}_{sc_name}_{an_path_split[2]}'
        an_asset_path = f'/Game/Shots/{ep_name}/{sc_name}/{cam_name}/Animation'

        asset_list = unreal.EditorAssetLibrary.list_assets(an_asset_path)
    
        anim_list=[]
        level_sequnce=None
        
        for asset in asset_list:
            asset_class=unreal.EditorAssetLibrary.find_asset_data(asset).get_class().get_name()
            asset_name=str(unreal.EditorAssetLibrary.find_asset_data(asset).asset_name)
    
            if asset_class=='AnimSequence' and '_an' in asset_name:
                anim_list.append(unreal.EditorAssetLibrary.find_asset_data(asset).get_asset())
            if asset_class=='LevelSequence' and '_an' in asset_name:
                level_sequnce=unreal.EditorAssetLibrary.find_asset_data(asset).get_asset()

        unuse_an_assets = uSTools.pathToSequenceAnim(an_asset_path,0)

        #当存在未被挂载的动画资产时,为场景添加对应bp,并挂载未被挂载的动画资产
        anAgainAttach(level_sequnce,unuse_an_assets,an_asset_path)



def anAgainAttach(level_sequnce,unuse_an_assets,an_asset_path):

    if unuse_an_assets:
        type_name = '_an_'
        for unuse_an_asset in unuse_an_assets:
            anim_name = unuse_an_asset.get_name()
            asset_type = ''
            bp = None
            if '_CH' in anim_name:
                anim_base_name=anim_name.split('_CH')[0].split(type_name)[-1]
                # '/Game/AAI/Reference/Character/AZheChangFuBan/AZheChangFuBan_AAI_BP'
                ch_asset_path = UC.globalConfig.get().AssetPath + f'Character/{anim_base_name}/BP_CH_{anim_base_name}'
                ch_aai_path = UC.globalConfig.get().ReferencePath + f'Character/{anim_base_name}/{anim_base_name}_AAI_BP'
                asset_type = 'CH'
                if unreal.EditorAssetLibrary.does_asset_exist(ch_aai_path):
                    bp = unreal.EditorAssetLibrary.load_asset(ch_aai_path)
                elif unreal.EditorAssetLibrary.does_asset_exist(ch_asset_path):
                    bp = unreal.EditorAssetLibrary.load_asset(ch_asset_path)
                else:
                    continue

            elif '_Pro' in anim_name:
                anim_base_name=anim_name.split('_Pro')[0].split(type_name)[-1]
                asset_type = 'Pro'
                pro_asset_path = UC.globalConfig.get().AssetPath + f'Pro/{anim_base_name}/BP_Pro_{anim_base_name}'
                pro_aai_path = UC.globalConfig.get().ReferencePath + f'Pro'
                if unreal.EditorAssetLibrary.does_asset_exist(pro_asset_path):
                    bp = unreal.EditorAssetLibrary.load_asset(pro_asset_path)
                else:
                    bp_asset_datas = uSTools.assetFilter('Blueprint',pro_aai_path)
                    for bp_asset_data in bp_asset_datas:
                        bp_name = uSTools.assetDataToAssetName(bp_asset_data)
                        if anim_base_name == bp_name.split('_AAI_BP')[0]:
                            bp = unreal.EditorAssetLibrary.load_asset(uSTools.assetDataToAssetPath(bp_asset_data)+'/'+bp_name)
                            break

            else:
                continue
            # elif '_BG' in anim_name:
            #     anim_base_name=anim_name.split('_BG')[0].split(type_name)[-1]
            
            if bp:      #挂载bp到sequence,并添加到层
                layers_subsystem = unreal.get_editor_subsystem(unreal.LayersSubsystem)
                # ch_layer_name = 'CH'
                # ch_tag = 'ch' 
                sequence_path = level_sequnce.get_path_name()
                level_path = sequence_path.rsplit('/',1)[0]+sequence_path.split('.')[-1].replace('_an','_an_Map')
                unreal.LevelEditorSubsystem().load_level(level_path)
                add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(bp,unreal.Vector(0.0, 0.0, 0.0))
                layers_subsystem.add_actor_to_layer(add_actor, asset_type)      #添加actor到层
                uSTools.actorAddTag(add_actor,asset_type.lower())
                uSTools.setLightChannel(add_actor,[False,False,True,False])  #设置灯光通道
                level_sequnce.add_possessable(add_actor)
                unreal.EditorAssetLibrary.save_directory('/Game')

    uSTools.pathToSequenceAnim(an_asset_path,0)

        



class MainWindow(QMainWindow):
    pathUpdateRequested = Signal(str)

    def __init__(self):
        super().__init__()
        self.version = 'TX'
        self.__ui()
        self.on_update_path_clicked()
        
    
    def __ui(self):
        self.setWindowTitle("资产批量更新工具")
        self.resize(1100, 600)

        # 当前使用的数据集（默认第一组）
        self.current_file_data = FILE_DATA_1

        # 主分割器
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        # 左侧树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("集数 / 场次")
        self.tree.setIndentation(20)
        self.tree.setStyleSheet("""
            QHeaderView::section {
                background-color: #333333;  /* 背景色 */
                border: none;
                color: white;               /* 文字颜色 */
                font: bold 12px;            /* 字体样式（可选） */
                padding: 4px;               /* 内边距（可选） */
            }
            QTreeWidget  {
            border: 1px solid #222222;   /* 宽度2像素，实线，黑色 */
            }
        """)
        
        self.splitter.addWidget(self.tree)

        # 右侧区域
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.splitter.addWidget(right_widget)

        # ========== 顶部：项目名称 ==========
        path_layout = QHBoxLayout()
        path_layout.addWidget(MLabel("项目名称:"))
        self.path_line_edit = MLineEdit()
        self.path_line_edit.setPlaceholderText("输入项目名称缩写")
        self.path_line_edit.setText(getProjectName())
        # self.path_line_edit.textChanged.connect(self.upDataPath)
        path_layout.addWidget(self.path_line_edit)
        self.update_path_btn = MPushButton("更新文件信息")
        self.update_path_btn.clicked.connect(self.on_update_path_clicked)
        path_layout.addWidget(self.update_path_btn)
        self.pip_path_btn = MCheckBox()
        self.pip_path_btn.setText("获取pipeline文件")
        path_layout.addWidget(self.pip_path_btn)


        path_layout.addStretch()
        right_layout.addLayout(path_layout)

        # ========== 过滤器栏 ==========
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(MLabel("资产类型:"))
        self.filter1_combo = MComboBox()
        self.filter1_combo.addItems(list(FILTER1_MAP.keys()))
        filter_layout.addWidget(self.filter1_combo)
        filter_layout.addWidget(MLabel("流程:"))
        self.filter2_combo = MComboBox()
        self.filter2_combo.addItems(list(FILTER2_MAP.keys()))
        filter_layout.addWidget(self.filter2_combo)
        filter_layout.addWidget(MLabel("状态类型:"))
        self.mask_filter_combo = MComboBox()
        self.mask_filter_combo.addItems(list(MASK_FILTER_MAP.keys()))
        filter_layout.addWidget(self.mask_filter_combo)
        filter_layout.addWidget(MLabel("环节:"))
        self.segment_filter_combo = MComboBox()
        self.segment_filter_combo.addItems(list(SEGMENT_FILTER_MAP.keys()))
        filter_layout.addWidget(self.segment_filter_combo)
        filter_layout.addWidget(MLabel("过滤:"))
        self.text_filter_le = MLineEdit()
        self.text_filter_le.setPlaceholderText("输入过滤关键词")
        filter_layout.addWidget(self.text_filter_le)
        self.textfilter_btn = MCheckBox()
        self.textfilter_btn.setText("反向过滤")
        filter_layout.addWidget(self.textfilter_btn)
        filter_layout.addStretch()
        right_layout.addLayout(filter_layout)

        # ========== 表格 ==========
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["文件名称", "时间", "路径"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #333333;
                border: none;
                border-right: 1px solid #222222;
                border-bottom: 1px solid #222222;
                padding: 4px;
                color: white;
            }
            QTableCornerButton::section {   /* 处理左上角区域 */
                background-color: #333333;
                border: 1px solid #111111;
            }
            QTableWidget {
            border: 1px solid #111111;   /* 宽度1像素，实线，黑色 */
    }
        """)
        font_metrics = self.table.fontMetrics()
        row_height = font_metrics.height() + 2   # 加2像素避免文字被裁剪
        self.table.verticalHeader().setDefaultSectionSize(row_height)
        right_layout.addWidget(self.table)

        # 打印按钮
        self.print_btn = MPushButton("更新选中资产")
        self.print_btn.clicked.connect(self.updataSelectedFiles)
        right_layout.addWidget(self.print_btn)

        # 构建左侧树
        self.build_tree()

        # 当前显示的原始文件列表
        self.current_raw_files = []

        # 信号连接
        self.pip_path_btn.stateChanged.connect(self.upDataPipline)
        self.tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.filter1_combo.currentTextChanged.connect(self.apply_filters)
        self.filter2_combo.currentTextChanged.connect(self.on_update_path_clicked)
        self.mask_filter_combo.currentTextChanged.connect(self.apply_filters)
        self.segment_filter_combo.currentTextChanged.connect(self.on_update_path_clicked)
        self.text_filter_le.textChanged.connect(self.apply_filters)
        self.textfilter_btn.clicked.connect(self.apply_filters)


        # 设置分割器初始比例
        QTimer.singleShot(0, self.set_initial_splitter_sizes)

    def set_initial_splitter_sizes(self):
        total_width = self.width()
        if total_width > 0:
            self.splitter.setSizes([int(total_width * 0.15), int(total_width * 0.85)])
        else:
            self.splitter.setSizes([300, 600])

    def build_tree(self):
        """基于 current_file_data 构建树"""
        self.tree.clear()
        episode_items = {}
        for key in self.current_file_data.keys():
            if "_sc" in key:
                ep_part = key.split("_sc")[0]
                sc_part = f"sc{key.split('_sc')[1]}"
                if ep_part not in episode_items:
                    ep_item = QTreeWidgetItem(self.tree)
                    ep_item.setText(0, ep_part)
                    episode_items[ep_part] = ep_item
                sc_item = QTreeWidgetItem(episode_items[ep_part])
                sc_item.setText(0, sc_part)
                sc_item.setData(0, Qt.UserRole, key)
            else:
                if key not in episode_items:
                    ep_item = QTreeWidgetItem(self.tree)
                    ep_item.setText(0, key)
                    episode_items[key] = ep_item
        for ep_key, ep_item in episode_items.items():
            ep_item.setData(0, Qt.UserRole, ep_key)
        self.tree.expandAll()

    def get_files_for_key(self, key):
        """根据键从 current_file_data 获取文件列表"""
        if "_sc" in key:
            return self.current_file_data.get(key, [])
        else:
            files = []
            files.extend(self.current_file_data.get(key, []))
            for data_key, data_files in self.current_file_data.items():
                if data_key.startswith(key + "_sc"):
                    files.extend(data_files)
            return files


    def on_tree_selection_changed(self):
        self.table.clearSelection()
        selected = self.tree.selectedItems()
        if not selected:
            self.current_raw_files = []
            self.table.setRowCount(0)
            return
        key = selected[0].data(0, Qt.UserRole)
        if not key:
            key = selected[0].text(0)

        if self.pip_path_btn.isChecked():   #pipline模式下根据所选sc更新数据
            #当使用pipeline模式时,改为实时获取数据,不使用缓存数据
            self.pipUpdateToCurrentData(key)
                
        self.current_raw_files = self.get_files_for_key(key)
        self.apply_filters()

    
    def versionChange(self):
        self.version = FILTER2_MAP.get(self.filter2_combo.currentText())
        print(self.version)

    def upDataPipline(self):
        self.on_update_path_clicked()

    def pipUpdateToCurrentData(self,key):
        path_split = key.split('_')
        if len(path_split) <2:  #层级选择错误时跳过
            self.current_file_data = {}
            return False
        #获取pipline路径内的资产信息
        if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'an':
            if self.version == 'TX':
                pip_an_fbx_path = f'{path_split[0]}/{path_split[1]}/FBX'
            elif self.version == 'WX':
                pip_an_fbx_path = f'{path_split[0]}/Animation/fbx/{path_split[1]}'
            self.current_file_data = pipPathToFileData(pip_an_fbx_path,self.version,'an')
        if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'groom':
            if self.version == 'TX':
                pip_an_fbx_path = f'{path_split[0]}/{path_split[1]}'
            self.current_file_data = pipPathToFileData(pip_an_fbx_path,self.version,'groom')
        if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'cloth':
            if self.version == 'TX':
                pip_an_fbx_path = f'{path_split[0]}/{path_split[1]}'    
            self.current_file_data = pipPathToFileData(pip_an_fbx_path,self.version,'cloth')
        if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'cam':
            # TX:/EP001/sc001/Cam
            if self.version == 'TX':
                pip_an_fbx_path = f'{path_split[0]}/{path_split[1]}/Cam'
            elif self.version == 'WX':
                # WXZW:/EP001/Animation/fbx/cam/sc001
                pip_an_fbx_path = f'{path_split[0]}/Animation/fbx/cam/{path_split[1]}'
            self.current_file_data = pipPathToFileData(pip_an_fbx_path,self.version,'cam')

    def apply_filters(self):
        if not self.current_raw_files:
            self.table.setRowCount(0)
            return

        #根据过滤器获取过滤条件
        keyword1 = FILTER1_MAP.get(self.filter1_combo.currentText())
        keyword2 = self.text_filter_le.text()
        mask_val = MASK_FILTER_MAP.get(self.mask_filter_combo.currentText())

        filtered = []
        for file_info in self.current_raw_files:
            name = file_info["fileName"].lower()
            if keyword1 and keyword1.lower() not in name:
                continue
            if mask_val is not None and file_info["mask"] != mask_val:
                continue

            if self.textfilter_btn.isChecked():
                if keyword2 and keyword2.lower() in name:
                    continue
            else:
                if keyword2 and keyword2.lower() not in name:
                    continue
            filtered.append(file_info)

        self.update_table(filtered)

    def update_table(self, files):
        # 临时禁用排序，防止填充数据时行错位
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(files))
        for row, info in enumerate(files):
            name_item = QTableWidgetItem(info["fileName"])
            time_item = QTableWidgetItem(info["time"])
            path_item = QTableWidgetItem(info["path"])

            name_item.setData(Qt.UserRole, info)

            mask_val = info["mask"]
            if mask_val == 1:
                color = QColor(255, 255, 0)   # 黄色
            elif mask_val == 2:
                color = QColor(0, 255, 0)     # 绿色
            elif mask_val == 3:
                color = QColor(255, 0, 0)     # 红色
            else:
                color = None

            if color:
                name_item.setForeground(color)
                time_item.setForeground(color)
                path_item.setForeground(color)

            self.table.setItem(row, 0, name_item)
            self.table.setItem(row, 1, time_item)
            self.table.setItem(row, 2, path_item)

        # self.table.resizeRowsToContents()0
        # 重新启用排序（会按当前排序列自动排序）
        self.table.setSortingEnabled(True)


    def updataSelectedFiles(self):
        selected_ranges = self.table.selectedIndexes()
        if not selected_ranges:
            print("提示：未选择任何文件。")
            return

        if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'an':
            self.updataFiles(selected_ranges,'an')
        if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'groom':
            self.updataFiles(selected_ranges,'groom')
        if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'cloth':
            self.updataFiles(selected_ranges,'cloth')
        if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'cam':
            self.updataFiles(selected_ranges,'cam')


    def updataFiles(self,selected_ranges,process):
        asset_paths = []
        asset_datas = []
        rows = sorted(set(index.row() for index in selected_ranges))
        for row in rows:
            # 从第一列单元格获取存储的完整文件信息
            item = self.table.item(row, 0)
            info = item.data(Qt.UserRole) if item else None
            if info and isinstance(info, dict):
                # print(info)
                if self.pip_path_btn.isChecked():   #pipline模式下先下载
                    uSTools.downloadFiles([info], info['projectName'])
                an_path = info['path']
                asset_data = {}
                asset_data['path'] = info['path']
                asset_data['name'] = info['fileName']
                asset_datas.append(asset_data)

                asset_paths.append(an_path)
                # print(an_path)
                # # 遍历所有字段，打印全部信息
                # for key, value in info.items():
                #     print(f"  {key}：{value}")
        
        print(asset_paths)
        import_error_text = ''
        if process == 'an':
            if self.version == 'TX':
                import_sk_error_list = uSTools.anFbxImport(asset_paths,1)
            if self.version == 'CS':
                import_sk_error_list = uSTools.anFbxImport(asset_paths,0)
            if self.version == 'WX':
                import_sk_error_list = uSTools.anFbxImport(asset_paths,1)            
            pathToSequence(asset_paths)
            #显示报错
            import_error_text = ''
            if import_sk_error_list:
                import_error_text += '以下动画未正常导入:\n'
                for error_data in import_sk_error_list:
                    import_error_text += f'{error_data}\n'

            # #创建导入失败excel表格
            # excelCreate(import_sk_error_list)
        
        elif process == 'cam':
            import_cam_error_list = UH.importCameras(asset_datas)    
            #显示报错
            import_error_text = ''
            if import_cam_error_list:
                import_error_text += '以下摄像机与原序列帧数不匹配:\n'
                for error_data in import_cam_error_list:
                    import_error_text += f'{error_data}\n'

        elif process == 'groom':
            if self.version == 'TX':
                version_index = 574
            else:
                version_index = 0
            #暂时默认使用guid模式
            import_error_datas,md5_same_list = uSTools.CacheImportTool.groomMount(groom_folder_path=None,assets_path=asset_paths,groom_type_index=0,version=version_index)
            if import_error_datas:
                import_error_text += '以下Groom缓存导入时出现了问题:\n'
                for error_data in import_error_datas:
                    import_error_text += f'{error_data}\n'

        elif process == 'cloth':
            if self.version == 'TX':
                version_index = 574
            else:
                version_index = 0
            import_error_paths,mat_error_asset_paths,md5_same_list,error_nosk_assets = uSTools.clothImportMount(abc_import_path=None,assets_path=asset_paths,offset_switch=False,version=version_index)
            if import_error_paths:
                import_error_text += '以下布料缓存导入时出现了问题:\n'
                for error_data in import_error_paths:
                    import_error_text += f'{error_data}\n'
            if mat_error_asset_paths:
                import_error_text += '以下布料缓存未找到对应材质球:\n'
                for error_data in mat_error_asset_paths:
                    import_error_text += f'{error_data}\n'
            if error_nosk_assets:
                import_error_text += '以下布料缓存未找到对应NoSk骨骼网格体:\n'
                for error_data in error_nosk_assets:
                    import_error_text += f'{error_data}\n'


        if import_error_text:
            error_dialog = uSTools.ErrorDialog(self,initialText = import_error_text)
            error_dialog.exec_()



    def on_update_path_clicked(self):
        #更新流程类型
        self.versionChange()
        project_name = self.path_line_edit.text()
        if not self.pip_path_btn.isChecked():   #查询本地文件
            project_local_path = 'Y:/'+project_name+'/'
            
            # print(project_local_path)
            if os.path.exists(project_local_path):
                if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'an':
                    file_datas = localPathToFileData(project_local_path,self.version,'an')
                    self.current_file_data = file_datas
                    self.build_tree()
                if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'groom':
                    file_datas = localPathToFileData(project_local_path,self.version,'groom')
                    self.current_file_data = file_datas
                    self.build_tree()
                if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'cloth':
                    file_datas = localPathToFileData(project_local_path,self.version,'cloth')
                    self.current_file_data = file_datas
                    self.build_tree()
                if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'cam':
                    file_datas = localPathToFileData(project_local_path,self.version,'cam')
                    self.current_file_data = file_datas
                    self.build_tree()
            else:
                print(project_local_path+'不存在')

        else:   #查询pipline文件
            if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'an':
                fbx_dirs = getAnSubDirs(self.version)
                fbx_dirs_data = dirToDirData(fbx_dirs,self.version)
                self.current_file_data = fbx_dirs_data
                self.build_tree()
                
            if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'groom':
                groom_dirs = getGroomSubDirs(self.version)
                groom_dirs_data = dirToDirData(groom_dirs,self.version)
                self.current_file_data = groom_dirs_data
                self.build_tree()

            if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'cloth':
                cam_dirs = getClothSubDirs(self.version)
                cam_dirs_data = dirToDirData(cam_dirs,self.version)
                self.current_file_data = cam_dirs_data
                self.build_tree()
                
            if SEGMENT_FILTER_MAP.get(self.segment_filter_combo.currentText()) == 'cam':
                cam_dirs = getCamSubDirs(self.version)
                cam_dirs_data = dirToDirData(cam_dirs,self.version)
                self.current_file_data = cam_dirs_data
                self.build_tree()





def start():
    with application() as app:
        global test
        test = MainWindow()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":

    start()