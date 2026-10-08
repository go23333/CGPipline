import copy
import os
import tempfile

from PyQt5.QtWidgets import  (QWidget,QVBoxLayout,QPushButton,
							  QListWidget,QHBoxLayout,QLabel,
							  QProgressBar,QSpinBox,QFileDialog,
							  QMessageBox)
from PyQt5.QtCore import Qt,QThread,pyqtSignal
from app.core.style_sheet import StyleSheet
from app import ROOT_PATH

import subprocess

from app.core.nuke_template import nuke_file

class ConvertWorker(QThread):
	progress = pyqtSignal(int)
	finished = pyqtSignal()
	def __init__(self, parent, paths: list[str],frameRate: int, startSkip: int, endSkip: int):
		super().__init__(parent)
		self.paths = paths
		self.frame_rate = frameRate
		self.start_skip = startSkip
		self.end_skip = endSkip
	def run(self):
		script_path = os.path.join(ROOT_PATH,"scripts\\nuke_bathc_render.py")
		nuke_path = r"C:\Program Files\Nuke12.2v5\Nuke12.2.exe"
		temp = tempfile.gettempdir()
		if not os.path.exists(nuke_path):
			return
		index = 0
		for path in self.paths:
			#提取场次信息,生成输出文件路径
			ep, sc, cam = path.split("/")[-1].split("_")[0:3]
			output_file = f"{ep}_{sc}_{cam}.mov"
			output_path = path.replace(path.split("/")[-1], output_file)

			#提取EXR文件列表
			exr_files = [file for file in os.listdir(path) if file.endswith(".exr") or file.endswith(".EXR")]
			base_name,ext = os.path.splitext(exr_files[0])

			#生成要创建的nuke文件路径
			nuke_file_path = os.path.join(temp,output_file.replace(".mov",".nk"))

			start_frame = self.start_skip + 1
			end_frame = len(exr_files) - self.end_skip +1

			#生成nuke文件内容
			nuke_file_new = copy.deepcopy(nuke_file)
			nuke_file_new = nuke_file_new.replace("NUKEFILEPATH",nuke_file_path)
			nuke_file_new = nuke_file_new.replace("FRAMES",path + "/"+base_name.split(".")[0] + ".%04d" + ext)
			nuke_file_new = nuke_file_new.replace("FRAMELAST",str(len(exr_files)))
			nuke_file_new = nuke_file_new.replace("OUTPUTPATH",output_path)
			nuke_file_new = nuke_file_new.replace("FRAMERATE",str(self.frame_rate))

			#写入nuke文件
			with open(nuke_file_path,"w+",encoding='utf-8') as f:
				f.write(nuke_file_new)
			#执行生成命令
			commands = [nuke_path, "-t", "-script", script_path,str(start_frame),str(end_frame),nuke_file_path]
			subprocess.run(commands)

			self.progress.emit(index)
			index += 1
		self.finished.emit()


class ListWidget(QListWidget):
	def __init__(self,parent):
		super().__init__(parent)
		self.setAcceptDrops(True)
		self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()
		else:
			event.ignore()
	def dragMoveEvent(self, event):
		if event.mimeData().hasUrls():
			event.acceptProposedAction()
		else:
			event.ignore()
		pass
	def dropEvent(self, event):
		if event.mimeData().hasUrls():
			urls = event.mimeData().urls()
			for url in urls:
				# 转换为本地文件路径
				path = url.toLocalFile()
				# 检查是否是文件夹 (Windows资源管理器拖拽的文件夹会以/结尾)
				if path.endswith('/') or path.endswith('\\'):
					path = path[:-1]
				if os.path.isdir(path):
					self.addItem(path)
			event.acceptProposedAction()
		else:
			event.ignore()


class F2vInterface(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.__initWidget()
		self.__setQss()
		self.setObjectName("f2v_interface")
	def __initWidget(self):
		layout_main = QHBoxLayout(self)
		self.setLayout(layout_main)
		layout_main.setContentsMargins(50,50,50,50)

		widget_items = QWidget(self)
		layout_items = QVBoxLayout(widget_items)
		layout_items.setContentsMargins(0, 0, 0, 0)
		layout_main.addWidget(widget_items)

		self.list_widget = ListWidget(self)
		layout_items.addWidget(self.list_widget)

		self.progress_bar = QProgressBar(self)
		self.progress_bar.setValue(0)
		self.progress_bar.setRange(0, 1)
		self.progress_bar.setFormat("")
		layout_items.addWidget(self.progress_bar)

		widget_input = QWidget(self)
		widget_input.setMinimumWidth(200)
		layout_input = QVBoxLayout(widget_input)
		layout_input.setContentsMargins(0, 0, 0, 0)
		layout_input.setSpacing(0)
		layout_main.addWidget(widget_input)

		widget_input_top = QWidget(self)
		layout_input_top = QVBoxLayout(widget_input_top)
		layout_input.addWidget(widget_input_top)
		layout_input_top.setContentsMargins(0, 0, 0, 0)
		layout_input_top.setAlignment(Qt.AlignmentFlag.AlignTop)

		self.pb_add_folder = QPushButton(parent=self, text="添加序列帧目录")
		self.pb_add_folder.clicked.connect(self._add_folders_to_list)
		self.pb_remove_folder = QPushButton(parent=self, text="移除选定的目录")
		self.pb_remove_folder.clicked.connect(self._remove_select_floder_from_list)
		layout_input_top.addWidget(self.pb_add_folder)
		layout_input_top.addWidget(self.pb_remove_folder)

		widget_input_buttom = QWidget(self)
		layout_input_button = QVBoxLayout(widget_input_buttom)
		layout_input.addWidget(widget_input_buttom)
		layout_input_button.setContentsMargins(0, 0, 0, 0)
		layout_input_button.setAlignment(Qt.AlignmentFlag.AlignBottom)

		self.pb_execute = QPushButton(parent=self, text="转换为视频")
		self.pb_execute.clicked.connect(self.__convert_to_video)

		self.sb_frame_rate = QSpinBox()
		self.sb_frame_rate.setValue(25)
		self.sb_start_skip = QSpinBox()
		self.sb_start_skip.setValue(10)
		self.sb_end_skip = QSpinBox()
		self.sb_end_skip.setValue(5)

		layout_input_button.addWidget(QLabel("帧率:"))
		layout_input_button.addWidget(self.sb_frame_rate)

		layout_input_button.addWidget(QLabel("开始帧跳过:"))
		layout_input_button.addWidget(self.sb_start_skip)

		layout_input_button.addWidget(QLabel("结束帧跳过:"))
		layout_input_button.addWidget(self.sb_end_skip)

		layout_input_button.addWidget(self.pb_execute, alignment=Qt.AlignmentFlag.AlignBottom)
	def __convert_to_video(self):
		frame_rate = self.sb_frame_rate.value()
		start_skip = self.sb_start_skip.value()
		end_skip = self.sb_end_skip.value()

		jobs = []
		for i in range(self.list_widget.count()):
			jobs.append(self.list_widget.item(i).text())
		if not jobs:
			return
		self.progress_bar.setRange(0, len(jobs))
		self.progress_bar.setFormat("正在执行 %v/%m")
		self.worker = ConvertWorker(self, jobs, frame_rate, start_skip, end_skip)
		self.worker.progress.connect(self.update_progress)
		self.worker.finished.connect(self.finished)
		self.worker.start()
		self.setEnabled(False)

	def _add_folders_to_list(self):
		folder = QFileDialog.getExistingDirectory()
		if folder:
			self.list_widget.addItem(folder)

	def _remove_select_floder_from_list(self):
		for item in reversed(self.list_widget.selectedItems()):
			row = self.list_widget.row(item)
			self.list_widget.takeItem(row)

	def update_progress(self, value):
		self.progress_bar.setValue(value)

	def finished(self):
		self.progress_bar.setValue(0)
		self.progress_bar.setRange(0, 1)
		self.progress_bar.setFormat("")
		self.setEnabled(True)
		self.list_widget.clear()
		QMessageBox.information(self, "提示", "转换完成", QMessageBox.Ok)
	def __setQss(self):
		StyleSheet.F2V_INTERFACE.apply(self)