import unreal
import os

from Qt import QtCore
from Qt import QtWidgets

import UnrealPipeline.core.Config as UC


from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application



def buildImportTask(file_path,destination_path,options=None,automated=True):
    task=unreal.AssetImportTask()
    task.set_editor_property('automated',automated)
    task.set_editor_property('destination_name','')
    task.set_editor_property('destination_path',destination_path)
    task.set_editor_property('filename',file_path)
    task.set_editor_property('replace_existing',True)
    task.set_editor_property('save',True)
    task.set_editor_property('options',options)
    return task


def buildGroomImportOptions():

    options=unreal.GroomImportOptions()

    options.conversion_settings = unreal.GroomConversionSettings(rotation=[90.0, 0.0, 0.0],scale=[1.0, -1.0, 1.0])


    return options


def listClassAsset(path,class_name):

    assets=[]
    if unreal.EditorAssetLibrary.does_directory_exist(path):
        asset_list=unreal.EditorAssetLibrary.list_assets(path)
        for asset_info in asset_list:
            asset_class=unreal.EditorAssetLibrary.find_asset_data(asset_info).get_class().get_name()
            asset=unreal.EditorAssetLibrary.find_asset_data(asset_info).get_asset()

            if '_BD' in asset.get_name() and asset_class==class_name:
                assets.append(asset)

    return assets



def buildGroomCacheImportOptions(groom_asset_soft,start_frame,end_frame):
    options=unreal.GroomCacheImportOptions()

    # options.import_settings.override_conversion_settings=True

    # rotation_vector=unreal.Vector(0.0,0.0,0.0)
    # scale_vector=unreal.Vector(1.0,1.0,1.0)
    
    # options.import_settings.conversion_settings.rotation=rotation_vector
    # options.import_settings.conversion_settings.scale=scale_vector
    

    options.import_settings.import_groom_asset=False
    options.import_settings.groom_asset=groom_asset_soft

    #是否导入cache
    options.import_settings.import_groom_cache=True

    # # #只导入STRANDS
    # options.import_settings.import_type=unreal.GroomCacheImportType.STRANDS
    # #设置导入的起始结束帧
    options.import_settings.frame_start=start_frame
    options.import_settings.frame_end=end_frame


    return options



class GroomImportWindow(QtWidgets.QWidget, MFieldMixin):


    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.ui()

    def ui(self):   
        self.setWindowTitle('groom导入工具')
        self.resize(300,200)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        #导入文件
        self.folder_import=MLineEdit().folder().medium()
        self.folder_import.setPlaceholderText(self.tr("选择需要导入的groom文件夹"))
        create_folder=MPushButton(text="导入groom")
        
        create_folder.clicked.connect(self.importGroom)

        folder_lay.addWidget(self.folder_import)
        folder_lay.addWidget(create_folder)

        import_lay=QtWidgets.QVBoxLayout()
    


        lay.addLayout(folder_lay)
        lay.addLayout(import_lay)
        self.setLayout(lay)

    def groomCacheToChDirectory(self,abc_path,main_path):
        asset_basename=abc_path.split('/')[-1].split('_',3)[3].rsplit('_',3)[0]
        if unreal.EditorAssetLibrary.does_directory_exist(main_path+asset_basename):
            ch_base_path=main_path+asset_basename
            return ch_base_path


    def importGroom(self):


        asset_ch_path='/Game/Assets/Character/'
        

        groom_folder_path=self.folder_import.text()
        groom_paths=[]
        for dirpath, dirnames, filenames in os.walk(groom_folder_path):
            for filename in filenames:
                if '.abc' in filename :
                    groom_path=str(os.path.join(dirpath, filename)).replace('\\','/')
                    groom_paths.append(groom_path)

        first_count=True
        #创建groom文件夹
        if groom_paths:
            groom_split=groom_paths[0].split('/')[-1].split('_')
        unreal.EditorAssetLibrary.make_directory(f'/Game/Shots/{groom_split[0]}/{groom_split[1]}/{groom_split[0]}_{groom_split[1]}_{groom_split[2]}/Cache/Groom')


        old_groom_asset_basepath=None
        groom_assets=None

        for groom_import_path in groom_paths:
            #通过文件名获取对应ue路径
            abc_asset_frame=groom_import_path.split('_')[-2].split('.')[0].split('-')
            abc_asset=groom_import_path.split('/')[-1].split('.')[0]
            abc_split = abc_asset.split('_')

            #获取cache的起始结束帧
            start_frame=int(abc_asset_frame[0])
            end_frame=int(abc_asset_frame[1])

            base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'

            des_path = base_path+'Cache/Groom'    #缓存目标文件夹
            seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_hcache'   #动画序列对象路径

            an_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取动画序列

            #创建groom task
            if first_count:
                groom_task=buildImportTask(groom_import_path,des_path,buildGroomImportOptions(),automated=False)
                first_count=False   #当第一次导入groom时打开设置框
            else:
                groom_task=buildImportTask(groom_import_path,des_path,buildGroomImportOptions(),automated=True)
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([groom_task])

            groom_asset_path=des_path+'/'+abc_asset

            #获取角色文件夹
            ch_path=self.groomCacheToChDirectory(abc_asset,asset_ch_path)
            #获取groom部件名称
            asset_partname=groom_import_path.split('/')[-1].split('_',3)[3].rsplit('_',2)[0]
            #角色目录下的groom文件夹
            groom_asset_basepath=ch_path+'/Groom'
            
            #判断新旧路径名称,防止重复运行
            if not groom_asset_basepath==old_groom_asset_basepath:

                groom_assets=listClassAsset(groom_asset_basepath,'GroomAsset')

            old_groom_asset_basepath=groom_asset_basepath   #记录文件夹名称

            #遍历绑定的groom资产
            for groom_asset in groom_assets:

                #判断绑定的groom和导入的cache命名是否一致
                if groom_asset.get_name().split('_BD')[0]==asset_partname:
                    print(groom_asset.get_name())

                    #获取用于添加cache的groom soft信息
                    groom_asset_soft=unreal.EditorAssetLibrary.find_asset_data(groom_asset_path).to_soft_object_path()
                    #创建cache
                    groom_cache_task=buildImportTask(groom_import_path,des_path,buildGroomCacheImportOptions(groom_asset_soft,start_frame,end_frame))
                    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([groom_cache_task])

                    #获取用于添加关卡序列的strands_cache
                    groom_cache_path=groom_asset_path+'_strands_cache'
                    groom_cache=unreal.EditorAssetLibrary.find_asset_data(groom_cache_path).get_asset()

                    #打开动画序列
                    unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(an_seq)
                    #添加绑定groom
                    spawnable=an_seq.add_spawnable_from_instance(groom_asset)

                    #创建可生成按钮
                    spawnable.get_tracks()[0].add_section()

                    #创建section
                    spawnable_track = spawnable.add_track(unreal.MovieSceneGroomCacheTrack)
                    animation_section = spawnable_track.add_section()
                    

                    #groom缓存添加设置
                    groom_cache_params=unreal.MovieSceneGroomCacheParams()
                    groom_cache_params.set_editor_property('groom_cache',groom_cache)

                    animation_section.set_editor_property('params',groom_cache_params)

                    animation_section.set_range(0,end_frame-start_frame)


                    break

        unreal.EditorAssetLibrary.save_directory('/Game/Shots')



# seq_path ='/Game/Shots/Ep002/sc001/Ep002_sc001_001/Cache/Ep002_sc001_001_hcache.Ep002_sc001_001_hcache'

# an_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取动画序列
# spawnables = an_seq.get_spawnables()
# for spawnable in spawnables:
#     asset_name=spawnable.get_object_template().get_name().rsplit('_',1)[0]
#     print(asset_name)

# abc_asset='Ep001_sc001_001_DouZhanLong_ErShiSui_Hair01_1-130_hCache'
# asset_ch_path='/Game/Assets/Character/'

# asset_basename=abc_asset.split('_',3)[3].rsplit('_',3)[0]
# asset_partname=abc_asset.split('_',3)[3].rsplit('_',2)[0]
# # print(asset_ch_path+asset_partname)








def start():
    with application() as app:
        global test
        test = GroomImportWindow()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":

    start()


