import unreal
import json
import sys
import os
import re
import datetime
import pyautogui
import time
from Qt.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QFileDialog, QLabel,
    QMessageBox
)

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


level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def getAllSelectedActor():
    actors = []
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    selected_actors = editor_actor_subsystem.get_selected_level_actors()
    for selected_actor in selected_actors:
        child_actors = selected_actor.get_attached_actors(recursively_include_attached_actors=True)
        actors.append(selected_actor)
        actors.extend(child_actors)
        print(actors)

    return actors


def textToLightData(text):
    # 匹配每个 Actor 块（非贪婪匹配，防止跨块）
    actor_blocks = re.findall(r'Begin Actor.*?End Actor', text, re.DOTALL)

    results = []

    for block in actor_blocks:
        # 提取 ParentActor（值不带引号）
        parent = re.search(r'ParentActor=([^\s]+)', block)
        # 提取 SocketName（值不带引号）
        socket = re.search(r'SocketName=([^\s]+)', block)
        # 提取 ActorLabel（值带双引号）
        label = re.search(r'ActorLabel="([^"]*)"', block)

        if socket and '_LIG' in label.group(1): #判断符合要求的文本
            result = []
            if parent:
                result.append(parent.group(1))
            result.append(socket.group(1))
            if label:
                result.append(label.group(1))
            results.append(result)

        # 按顺序打印结果（逗号分隔）
    return results


def lightToCharacter(character_actor, light_actor, socket_name):
    
    socket = unreal.Name(socket_name)

    light_actor.attach_to_actor(parent_actor=character_actor,socket_name=socket,location_rule=unreal.AttachmentRule.KEEP_RELATIVE,rotation_rule=unreal.AttachmentRule.KEEP_WORLD,scale_rule=unreal.AttachmentRule.KEEP_RELATIVE)

    #在灯光关卡序列中将灯光绑定到角色
    current_world = unreal.LevelEditorSubsystem().get_current_level().get_world()
    current_world_split = current_world.get_path_name().split('/')
    root_path = current_world.get_path_name().rsplit('/', 1)[0]
    lt_seq_path = f'{root_path}/Light/{current_world_split[5]}_lt'
    if not unreal.EditorAssetLibrary.does_asset_exist(lt_seq_path):
        lt_seq_path = f'{root_path}/Lighting/{current_world_split[5]}_lt'
    render_seq_path = f'{root_path}/{current_world_split[5]}_Render'
    
    if unreal.EditorAssetLibrary.does_asset_exist(render_seq_path) and unreal.EditorAssetLibrary.does_asset_exist(lt_seq_path):
        render_seq = unreal.EditorAssetLibrary.load_asset(render_seq_path)
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(render_seq)
        #从总关卡序列获取lt子关卡序列
        current_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        sub_sequence_tracks = current_sequence.get_tracks()
        lt_sub_sequence = None
        for sub_sequence_track in sub_sequence_tracks:
            try:
                sub_sequence_section = sub_sequence_track.get_sections()[0]
                sub_sequence = sub_sequence_section.get_sequence()
                if '_lt' in sub_sequence.get_name():
                    lt_sub_sequence = sub_sequence
                    break
            except:
                pass
        
        lt_seq = unreal.EditorAssetLibrary.load_asset(lt_seq_path)
        ch_bind = lt_seq.add_possessable(character_actor)
        light_bind = lt_seq.add_possessable(light_actor)

        attach_track = light_bind.add_track(unreal.MovieScene3DAttachTrack)
        attach_section = attach_track.add_section()

        attach_section.set_start_frame_bounded(False)
        attach_section.set_end_frame_bounded(False)

        # 使用 MovieSceneSequenceExtensions 来获取正确的 ID
        ch_bind_id = current_sequence.get_portable_binding_id(destination_sequence=lt_sub_sequence, binding=ch_bind)

        # 将约束 ID 应用到附加片段上
        attach_section.set_editor_property('constraint_binding_id', ch_bind_id)

        # 指定要附加到的骨骼名称
        attach_section.set_editor_property('attach_socket_name', socket_name)

        unreal.EditorAssetLibrary.save_directory('/Game')




class LightManagerWin(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_path = None          # 当前选中的文件夹路径
        self.init_ui()

    def init_ui(self):
        # -------- 主布局 ----------
        main_layout = QVBoxLayout()

        # -------- 文件夹选择区域 --------
        folder_layout = QHBoxLayout()
        self.folder_label = MLabel("未选择文件夹")
        self.select_btn = MPushButton("选择文件夹")
        self.select_btn.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.select_btn)
        main_layout.addLayout(folder_layout)

        # -------- 文件列表 --------
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)

        # -------- 操作按钮 --------
        btn_layout = QHBoxLayout()
        self.create_btn = MPushButton("将选择actor保存")
        self.create_btn.clicked.connect(self.create_from_clipboard)
        self.copy_btn = MPushButton("将选择文本创建为actor")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.copy_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self.setWindowTitle("灯光管理器") 
        self.resize(500, 400)

    # ---------- 选择文件夹 ----------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(f"当前文件夹: {folder}")
            self.refresh_file_list()

    # ---------- 刷新 .txt 文件列表 ----------
    def refresh_file_list(self):
        self.list_widget.clear()
        if not self.folder_path:
            return
        try:
            files = [f for f in os.listdir(self.folder_path) if f.endswith('.txt')]
            for f in sorted(files):
                self.list_widget.addItem(f)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取文件夹失败: {e}")

    # ---------- 按钮1：从剪贴板新建文本文档 ----------
    def create_from_clipboard(self):
        if not self.folder_path:
            QMessageBox.warning(self, "警告", "请先选择文件夹")
            return

        # 1获取选择actor的子actor
        actors = getAllSelectedActor()
        editor_actor_subsystem.set_selected_level_actors(actors)

        # 2. 将actor复制为文本
        clipboard = unreal.BrowserBridge.copy_selected_actors_and_get_text()
        # print(clipboard)

        if not clipboard:
            reply = QMessageBox.question(
                self, "剪贴板为空",
                "剪贴板中没有文本，是否创建空文件？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        # 3. 生成文件名并保存
        current_level = unreal.LevelEditorSubsystem().get_current_level()
        current_level_name = current_level.get_path_name().split('.')[0].split('/')[-1]
        timestamp = datetime.datetime.now().strftime("%m%d_%H%M")
        filename = f"{current_level_name}_{timestamp}.txt"
        filepath = os.path.join(self.folder_path, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(clipboard)
            self.refresh_file_list()
            QMessageBox.information(self, "成功", f"已创建文件: {filename}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建文件失败: {e}")

    # ---------- 按钮2：复制选中文件内容到剪贴板 ----------
    def copy_to_clipboard(self):
        if not self.folder_path:
            QMessageBox.warning(self, "警告", "请先选择文件夹")
            return

        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个文本文档")
            return

        filename = current_item.text()
        filepath = os.path.join(self.folder_path, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取文件失败: {e}")
            return

        # 1. 将文件内容写入剪贴板
        clipboard = QApplication.clipboard()
        clipboard.setText(content)

        # 粘贴actor
        unreal.BrowserBridge.paste_actor_from_text(content)

        unreal.EditorAssetLibrary.save_directory('/Game')
        current_level = unreal.LevelEditorSubsystem().get_current_level()
        level_editor_subsystem.load_level(current_level.get_path_name())

        #获取文本中的灯光矩阵信息,为灯光矩阵进行单独处理
        light_datas = textToLightData(content)
        if light_datas:
            all_actors = editor_actor_subsystem.get_all_level_actors()
            for light_data in light_datas:
                parent_actor_str = light_data[0]
                socket_name = light_data[1]
                light_actor_str = light_data[2]
                parent_actor = ''
                light_actor = ''
                for act in all_actors:
                    if parent_actor_str == act.get_name():
                        parent_actor = act
                    if light_actor_str == act.get_actor_label():
                        light_actor = act

                if light_actor and parent_actor:
                    lightToCharacter(parent_actor,light_actor,socket_name)


        # QMessageBox.information(self, "成功", f"已将文件内容粘贴到当前窗口")


def start():
    with application() as app:
        global test
        test = LightManagerWin()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":

    start()


