import unreal

import os
import json
import hashlib

from importlib import reload
import UnrealPipeline.core.Config as UC
import UnrealPipeline.core.uSTools as uSTools
reload(uSTools)

from Qt import QtWidgets
from Qt.QtGui import QPalette, QColor

from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.label import MLabel
from dayu_widgets.switch import MSwitch
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application


print('SemiClothAbcImporter 1.0')

editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level_sequence_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)





def clothImportMount(abc_import_path,only_import_switch=False,offset_switch=True):
    
    import_error_paths = []
    mat_error_asset_paths = []
    md5_same_list = []
    abc_paths=[]
    for dirpath, dirnames, filenames in os.walk(abc_import_path):
        for filename in filenames:
            if '.abc' in filename and 'UE_' in filename and len(filename.split('_'))==4:    #过滤文件
                groom_path=str(os.path.join(dirpath, filename)).replace('\\','/')
                abc_paths.append(groom_path)
    
    abc_assets = []
    for abc_path in abc_paths:
        abc_asset_name = abc_path.split('/')[-1].split('.')[0]
        abc_split = abc_asset_name.split('_')

        #获取对应镜头文件夹
        base_path = f'/Game/Shots/{abc_split[1]}/{abc_split[2]}/{abc_split[1]}_{abc_split[2]}_{abc_split[3]}/'
        des_path = base_path+'Cache'    #缓存目标文件夹

        # 导入abc文件
        abc_task=uSTools.ClothAbcImport.buildImportTask(abc_path,des_path,uSTools.ClothAbcImport.buildClothImportOptions())
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([abc_task])

        abc_asset=unreal.EditorAssetLibrary.find_asset_data(des_path+'/'+abc_asset_name).get_asset()
        abc_asset:unreal.GeometryCache


        if abc_asset:
            #判断abc仅导入判定
            if only_import_switch==False:
                try:
                    mountClothAbc([abc_asset],offset_switch)
                except:
                    import_error_paths.append(abc_path)
            #收集abc资产
            abc_assets.append(abc_asset)
        else:
            import_error_paths.append(abc_path)


        #保存文件
        unreal.EditorAssetLibrary.save_directory(des_path, only_if_is_dirty=False)

    
    #保存文件
    unreal.EditorAssetLibrary.save_directory('/Game')

    return import_error_paths,mat_error_asset_paths,md5_same_list



def mountClothAbc(cloth_abc_list=None, offset_switch=True):
    
    #如果没有导入列表则按照选择的abc缓存进行执行
    if not cloth_abc_list:
        select_assets=unreal.EditorUtilityLibrary.get_selected_assets()
        abc_assets=[]
        for select_asset in select_assets:
            if select_asset.get_class().get_name()=='GeometryCache':
                abc_assets.append(select_asset)
                print(select_asset.get_name())
    
    else:
        abc_assets = cloth_abc_list
    
    for abc_asset in abc_assets:

        abc_asset_name = abc_asset.get_name()

        #判断命名规则
        if 'UE_' not in abc_asset_name:
            continue
        
        abc_split = abc_asset_name.split('_')
        base_path = f'/Game/Shots/{abc_split[1]}/{abc_split[2]}/{abc_split[1]}_{abc_split[2]}_{abc_split[3]}/'
        des_path = base_path+'Cache'    #缓存目标文件夹
        seq_path = base_path+f'Cache/{abc_split[1]}_{abc_split[2]}_{abc_split[3]}_cache'   #动画序列对象路径
 

        #获取cache的起始结束帧
        if offset_switch:
            start_frame = int(abc_asset.start_frame)+UC.globalConfig.get().start_offset
            end_frame = int(abc_asset.end_frame)+UC.globalConfig.get().start_offset
        else:
            start_frame = int(abc_asset.start_frame)
            end_frame = int(abc_asset.end_frame)
        


        #打开对应level
        an_level_path = base_path+f'Animation/{abc_split[1]}_{abc_split[2]}_{abc_split[3]}_an_Map'
        if unreal.EditorAssetSubsystem().does_asset_exist(an_level_path):
            unreal.LevelEditorSubsystem().load_level(an_level_path)
        else:
            continue


        #获取当前关卡
        current_level = level_editor_subsystem.get_current_level()
        #解锁当前关卡
        unreal.PythonExtensionBPLibrary.unlock_level(current_level)
        

        #打开动画序列
        cache_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取动画序列
        unreal.LevelSequenceEditorBlueprintLibrary().open_level_sequence(cache_seq)
        #获取当前打开的关卡序列
        current_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        #关闭锁定
        unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(False)

        print(an_level_path,cache_seq)
    
        #删除全部possessables
        bindings = current_sequence.get_bindings()
        for binding in bindings:
            binding.remove()


        #添加GeometryCache到关卡序列中的对应BP中
        cache_actor = unreal.EditorLevelLibrary.spawn_actor_from_object(abc_asset, unreal.Vector(0.0, 0.0, 0.0))
        geo_cache_possessable=cache_seq.add_possessable(cache_actor)
        #添加解算缓存
        geo_cache_track = geo_cache_possessable.add_track(unreal.MovieSceneGeometryCacheTrack)
        geo_cache_section = geo_cache_track.add_section()

        #解算缓存设置
        geo_cache_params = unreal.MovieSceneGeometryCacheParams()
        geo_cache_params.set_editor_property('geometry_cache_asset',abc_asset)
        geo_cache_section.set_editor_property('params',geo_cache_params)
        #设置起始结束帧
        geo_cache_section.set_range(start_frame,end_frame)

        level_sequence_subsystem.convert_to_spawnable(geo_cache_possessable)


        #获取所有actor
        actors=unreal.EditorActorSubsystem().get_all_level_actors()
        for act in actors:
            if '_AAI' in act.get_actor_label() or 'BP_CH_' in act.get_actor_label():
                try:
                    skeletal_mesh_component = act.get_component_by_class(unreal.SkeletalMeshComponent)
                except:
                    continue
                skeletal_mesh = skeletal_mesh_component.get_editor_property("skeletal_mesh")
                nosk_path = skeletal_mesh.get_path_name().split('.')[0]+'_NoSK'
                if unreal.EditorAssetLibrary.does_asset_exist(nosk_path):
                    print(nosk_path,act)
                    nosk_asset = unreal.load_asset(nosk_path)
                    skeletal_mesh_component.set_editor_property("skeletal_mesh", nosk_asset)



        unreal.EditorAssetLibrary.save_directory('/Game')
            







class SemiClothAbcImport(QtWidgets.QWidget, MFieldMixin):


    def __init__(self, parent=None):
            super().__init__(parent)
            self.uii()

            self.assets_path=None


            
    def uii(self):   
        self.setWindowTitle('半流程布料缓存导入')
        self.resize(320,120)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        self.flie_import=MLineEdit().folder().medium()
        self.flie_import.setPlaceholderText(self.tr("选择布料缓存路径"))
        create_only_import=MPushButton(text="仅导入布料缓存")
        create_only_import.clicked.connect(self.importClothAbc)
        create_only_mount=MPushButton(text="挂载选中布料缓存")
        create_only_mount.clicked.connect(self.mountClothAbc)
        create_import_mount=MPushButton(text="导入并挂载布料缓存")
        create_import_mount.clicked.connect(self.excute)

        self.offset_switch = MSwitch()
        self.offset_switch.setChecked(True)
        offset_switch_lay = QtWidgets.QFormLayout()
        offset_switch_lay.addRow(MLabel("是否使用偏移帧"), self.offset_switch)    #关卡创建开关

        self.error_lable = MLabel('')
        self.error_lable.setStyleSheet("color: red;")
        


        folder_lay.addWidget(self.flie_import)
        folder_lay.addWidget(create_only_import)
        folder_lay.addWidget(create_only_mount)
        folder_lay.addWidget(create_import_mount)
        folder_lay.addWidget(self.error_lable)
        folder_lay.addLayout(offset_switch_lay)

        
        lay.addLayout(folder_lay)
        self.setLayout(lay)



    def groomCacheToChDirectory(self,abc_path,main_path):
        asset_basename=abc_path.split('/')[-1].split('_',3)[3].rsplit('_',3)[0]
        if unreal.EditorAssetLibrary.does_directory_exist(main_path+asset_basename):
            ch_base_path=main_path+asset_basename
            return ch_base_path


    def importClothAbc(self):
        only_import_switch=True
        self.excute(only_import_switch)

    
    
    
    def mountClothAbc(self,cloth_abc_list=None):
        mountClothAbc(cloth_abc_list,self.offset_switch.isChecked())




    def excute(self,only_import_switch=False):
        
        self.error_lable.setText('')
        abc_import_path=self.flie_import.text()

        import_error_paths,mat_error_asset_paths,md5_same_list = clothImportMount(abc_import_path,only_import_switch,self.offset_switch.isChecked())
        

        
        #显示报错
        import_error_text = ''
        if import_error_paths:
            import_error_text += '以下abc文件导入失败:\n'
            for error_data in import_error_paths:
                import_error_text += f'{error_data}\n'
        

        














def start():
    with application() as app:
        global test
        test = SemiClothAbcImport()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
   start()
