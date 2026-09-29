import unreal
import os
import importlib

from Qt import QtCore
from Qt import QtWidgets


from UnrealPipeline.core.Config import globalConfig
import UnrealPipeline.core.uSTools as uSTools
importlib.reload(uSTools)

from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

level_sequence_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)





class GroomImportWindow(QtWidgets.QWidget, MFieldMixin):


    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.ui()

    def ui(self):   
        self.setWindowTitle('groom导入工具V1')
        self.resize(300,100)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        #导入文件
        self.folder_import=MLineEdit().folder().medium()
        self.folder_import.setPlaceholderText(self.tr("选择需要导入的groom文件夹"))


        self.model_radio_group = MRadioButtonGroup()
        self.model_radio_group.set_button_list(['导入导线(guides)','导入发束(strands)'])
        self.model_radio_group.set_dayu_checked(0)

        radio_grp_lay = QtWidgets.QHBoxLayout()
        radio_grp_lay.addWidget(self.model_radio_group)

        import_mount_btn=MPushButton(text="导入并挂载groom缓存")
        import_mount_btn.clicked.connect(self.importMountGroom)

        only_import_btn=MPushButton(text="仅导入groom缓存")
        only_import_btn.clicked.connect(self.onlyImportGroom)

        only_mount_btn=MPushButton(text="仅挂载选中groom缓存")
        only_mount_btn.clicked.connect(self.onlyMountGroom)



        folder_lay.addWidget(self.folder_import)
        folder_lay.addLayout(radio_grp_lay)
        
        folder_lay.addWidget(only_import_btn)
        folder_lay.addWidget(only_mount_btn)
        folder_lay.addWidget(import_mount_btn)

        import_lay=QtWidgets.QVBoxLayout()
    


        lay.addLayout(folder_lay)
        lay.addLayout(import_lay)
        self.setLayout(lay)

    


    def importMountGroom(self):
        groom_folder_path=self.folder_import.text()
        groom_type_index = self.model_radio_group.get_dayu_checked()
        import_error_datas,md5_same_list = uSTools.CacheImportTool.groomMount(groom_folder_path,groom_type_index,is_offset=False,old_vision=True)
        

        unreal.EditorAssetLibrary.save_directory('/Game/Shots')

        #显示错误信息
        if import_error_datas:
            error_text = '以下毛发导入失败:\n'
            for import_error_data in import_error_datas:
                error_text += import_error_data+'\n'

            self.dialog = uSTools.ErrorDialog(self,error_text)
            self.dialog.exec_()
        
    def onlyImportGroom(self):
        groom_folder_path=self.folder_import.text()
        groom_type_index = self.model_radio_group.get_dayu_checked()
        import_error_datas,md5_same_list = uSTools.CacheImportTool.groomMount(groom_folder_path,groom_type_index,is_offset=False)
        

        unreal.EditorAssetLibrary.save_directory('/Game/Shots')

        #显示错误信息
        if import_error_datas:
            error_text = '以下毛发导入失败:\n'
            for import_error_data in import_error_datas:
                error_text += import_error_data+'\n'

            self.dialog = uSTools.ErrorDialog(self,error_text)
            self.dialog.exec_()
    
    def onlyMountGroom(self):
        
        selected_assets=unreal.EditorUtilityLibrary.get_selected_assets()
        abc_assets=[]
        for selected_asset in selected_assets:
            if selected_asset.get_class().get_name()=='GroomCache':
                abc_assets.append(selected_asset)
                print(selected_asset.get_name())

        for abc_asset in abc_assets:
            groom_cache_path = abc_asset.get_path_name()
            #根据名称判断groom类型
            if '_strands_' in groom_cache_path:
                groom_type_index = 1
            elif '_guides_' in groom_cache_path:
                groom_type_index = 0
            #通过文件名获取对应ue路径
            abc_asset=groom_cache_path.split('/')[-1]
            abc_split = abc_asset.split('_')
            base_path = f'/Game/Shots/{abc_split[0]}/{abc_split[1]}/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}/'

            seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_hcache'   #动画序列路径,若不存在hcache则用cache路径
            if not unreal.EditorAssetLibrary.does_asset_exist(seq_path):
                seq_path = base_path+f'Cache/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_cache'

            an_seq=unreal.EditorAssetLibrary.find_asset_data(seq_path).get_asset()  #获取动画序列

            #打开对应level
            level_path = base_path+f'{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_Map'
            an_level_path = base_path+f'Animation/{abc_split[0]}_{abc_split[1]}_{abc_split[2]}_an_Map'
            if unreal.EditorAssetSubsystem().does_asset_exist(an_level_path):
                unreal.LevelEditorSubsystem().load_level(an_level_path)
            else:
                unreal.LevelEditorSubsystem().load_level(level_path)


            uSTools.CacheImportTool.groomToSequence(groom_cache_path,an_seq,groom_type_index,is_offset=False)
        
        unreal.EditorAssetLibrary.save_directory('/Game/Shots')












def start():
    with application() as app:
        global test
        test = GroomImportWindow()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":

    start()


