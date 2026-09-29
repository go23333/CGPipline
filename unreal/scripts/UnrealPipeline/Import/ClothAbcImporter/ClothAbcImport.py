import unreal

import os
import json

from importlib import reload
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


print('ClothAbcImport 1.1')

editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level_sequence_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)



# def clearClothPossessable(possessable:unreal.MovieSceneBindingProxy):
#     current_event=None
#     tracks=possessable.get_tracks()
#     for track in tracks:
#         #删除事件track
#         if track.get_class().get_name()=='MovieSceneEventTrack':
#             event_section = track.get_sections()[0]
#             event_channel = event_section.get_all_channels()[0]
#             # current_event = event_section.get_editor_property('event')
#             current_event = event_channel.get_keys()[0].get_value()
#             possessable.remove_track(track)
#         #删除自定义track
#         # elif track.get_class().get_name()=='MovieSceneObjectPropertyTrack' or track.get_display_name()=='显示头发':
#         elif track.get_display_name()=='解算缓存' or track.get_display_name()=='显示头发':
#             possessable.remove_track(track)
#     #删除子GeometryCacheComponent
#     for sub_possessable in possessable.get_child_possessables():
#         if sub_possessable.get_possessed_object_class():
#             if sub_possessable.get_possessed_object_class().get_name() == 'GeometryCacheComponent':
#                 sub_possessable.remove()
#     # sub_possessables=possessable.get_child_possessables()
#     # if sub_possessables:
#     #     sub_possessables[0].remove()

#     return current_event





class ClothAbcImport(QtWidgets.QWidget, MFieldMixin):


    def __init__(self, parent=None):
            super().__init__(parent)
            self.uii()

            self.assets_path=None


            
    def uii(self):   
        self.setWindowTitle('布料缓存导入V1')
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
        uSTools.mountClothAbc(cloth_abc_list,self.offset_switch.isChecked())




    def excute(self,only_import_switch=False):
        
        self.error_lable.setText('')
        abc_import_path=self.flie_import.text()

        import_error_paths,mat_error_asset_paths,md5_same_list = uSTools.clothImportMount(abc_import_path,only_import_switch=only_import_switch,offset_switch=self.offset_switch.isChecked())

        
        #显示报错
        import_error_text = ''
        if import_error_paths:
            import_error_text += '以下abc文件导入失败:\n'
            for error_data in import_error_paths:
                import_error_text += f'{error_data}\n'
        if mat_error_asset_paths:
            import_error_text += '以下abc文件未找到所有材质:\n'
            for error_data in mat_error_asset_paths:
                import_error_text += f'{error_data}\n'
        if import_error_text:
            error_dialog = uSTools.ErrorDialog(self,initialText = import_error_text)
            error_dialog.exec_()

        














def start():
    with application() as app:
        global test
        test = ClothAbcImport()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
   start()
    #添加缓存到sequence中并k帧
    # current_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    # possessables = current_sequence.get_possessables()
    # object_track = possessables[1].add_track(unreal.MovieSceneObjectPropertyTrack)
    # object_track.set_property_name_and_path("解算缓存", "解算缓存")
    # object_section = object_track.add_section()
    # object_channel = object_section.get_all_channels()[0]
    # object_default = object_channel.get_default()
    # object_default = possessables[1].get_tracks()[1].get_sections()[0].get_all_channels()[0].get_default()
    # object_channel.add_key(time=unreal.FrameNumber(0),new_value=object_default)

    # print(possessables[1].get_tracks()[1].get_display_name())
    # print(possessables[1].get_tracks()[1].get_sections()[0].get_all_channels()[0].get_default())