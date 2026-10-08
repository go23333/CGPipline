from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QToolButton, QHBoxLayout, QListWidget, QCheckBox, \
	QPushButton, QListView, QProgressBar, QMessageBox, QAbstractItemView, QTabWidget, QTableWidget, QTableWidgetItem, \
	QComboBox,QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import json
from app.core.common_widgets import FileSelectGroup
from app.core.style_sheet import StyleSheet
from app.core.config import Config
import time
import subprocess
import os
import socket
import  struct
from ..core.Log import Log
from app import ROOT_PATH


logger = Log.get().getLogger("AbcImport")
logger.setLevel(Log.Level.debug)

PROJECTINFO = {
	"财神":"SSDSY_CS",
  	"择日飞升":"ZRFS",
	"踏星":"TX"
}


#workers

class WorkerPullUnreal(QThread):
	command = ""
	onUnrealClosed = pyqtSignal()

	def __init__(self,parent=None):
		super().__init__(parent)

	def run(self):
		if not self.command:
			return
		subprocess.run(self.command)
		time.sleep(5)
		self.onUnrealClosed.emit()


#ui
class AbcBatchImport(QWidget):
	def __init__(self,parent=None):
		super().__init__(parent)
		self.selected_jobs = None
		self.current_job = None
		self.setObjectName("AbcBatchImport")
		self.__initUI()
		self.__setQss()
		self.over_file_path = "D:\over.file"
		self.scriptPath  = os.path.join(ROOT_PATH,"scripts/AbcBatchImport.py")
		self.worker_for_call_unreal = WorkerPullUnreal()
		self.worker_for_call_unreal.onUnrealClosed.connect(self.OnUnrealClosed)

		self.is_importing = False

	def __initUI(self):
		layoutMain = QVBoxLayout(self)
		layoutMain.setContentsMargins(30,50,30,50)
		layoutMain.setAlignment(Qt.AlignTop)
		self.setLayout(layoutMain)

		#UE软件路径
		self.psg_ue_path = FileSelectGroup(
			"UE路径:",
			"选择UE启动器路径",
			"UE启动器(*.exe)",
			parent=self,
			textMaxWidth=100
		)
		layoutMain.addWidget(self.psg_ue_path)
		#ue项目路径
		self.psg_project_path = FileSelectGroup(
			"项目路径:",
			"选择UE项目路径",
			"UE项目(*.uproject)",
			parent=self,
			textMaxWidth=100
		)
		layoutMain.addWidget(self.psg_ue_path)
		layoutMain.addWidget(self.psg_project_path)

		self.psg_ue_path.onSelectPath.connect(self.__saveConfig)
		self.psg_project_path.onSelectPath.connect(self.__saveConfig)

		layoutMain.addWidget(QLabel("选择项目"))

		self.cb_project = QComboBox(self)
		self.cb_project.addItems(PROJECTINFO.keys())
		self.cb_project.setMaximumWidth(80)
		layoutMain.addWidget(self.cb_project)

		self.text_edit = QTextEdit(self)
		self.text_edit.setReadOnly(True)
		layoutMain.addWidget(self.text_edit)


		pb_import = QPushButton(self,text="开始批量导入")
		pb_import.clicked.connect(self.__start_import)
		layoutMain.addWidget(pb_import)

	####### 其他函数 #################
	def add_log(self,text:str):
		text = text + "\n"
		self.text_edit.append(text)
	def __loadFromConfig(self):
		self.psg_ue_path.setText(Config.Get().CurrentUnrealPath)
		self.psg_project_path.setText(Config.Get().CurrentUnrealProjectPath )
	def __saveConfig(self):
		#保存当前配置文件
		Config.Get().CurrentUnrealPath = self.psg_ue_path.text()
		Config.Get().CurrentUnrealProjectPath =self.psg_project_path.text()
		Config.Get().saveConfig()
	def __setQss(self):
		StyleSheet.BATCH_RENDER.apply(self)
	def __start_import(self):
		if self.is_importing:
			return
		ue_path = self.psg_ue_path.text()
		project_path = self.psg_project_path.text()

		if not os.path.exists(ue_path):
			self.add_log("UE路径设置错误")
			return

		if not os.path.exists(project_path):
			self.add_log("项目路径设置错误")
			return

		project = PROJECTINFO[self.cb_project.currentText()]
		project_root_path = f"Y:\\{project}\\"

		self.worker_for_call_unreal.command  = f'"{ue_path}" "{project_path}" -unattended -log -ExecutePythonScript="{self.scriptPath}" -project_root={project_root_path}"'
		self.worker_for_call_unreal.start()
		self.is_importing = True
		#删除flag文件
		if os.path.exists(self.over_file_path):
			os.remove(self.over_file_path)
	def OnUnrealClosed(self):
		self.is_importing = False
		if os.path.exists(self.over_file_path):
			self.print_import_result()
			self.add_log("所有abc导入完成")
			return
		self.add_log("导入过程中UE崩溃,正在重启UE")
		self.__start_import()
	def print_import_result(self):
		with open(self.over_file_path, 'r', encoding="utf-8") as file:
			data = json.loads(file.read())

			error_cloth = data['cloth']['error']
			error_material_cloth = data['cloth']['mat_error']
			successful_cloth = data['cloth']['successful']

			error_groom = data['groom']['error']
			successful_groom = data['groom']['successful']
		self.add_log("以下的布料abc导入错误:")
		for item in error_cloth:
			self.add_log(item)
		self.add_log("以下的布料abc材质导入错误:")
		for item in error_material_cloth:
			self.add_log(item)
		self.add_log("以下的毛发abc导入错误:")
		for item in error_groom:
			self.add_log(item)

	def showEvent(self, a0):
		self.__loadFromConfig()
		return  super().showEvent(a0)



