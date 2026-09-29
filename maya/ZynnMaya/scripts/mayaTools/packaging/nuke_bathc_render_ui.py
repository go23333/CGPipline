import copy
import os
import tempfile
import sys
import logging


from PyQt5 import QtWidgets
from PyQt5 import QtCore
import subprocess

ROOT_PATH = r'Y:\scripts\mayaTools\mayaBlackBox'


nuke_file = '''
#! C:/Program Files/Nuke11.1v3/nuke-11.1.3.dll -nx
#write_info Write1 file:"D:/Desktop/test.mov" format:"3072 1287 1" chans:":rgba.red:rgba.green:rgba.blue:" framerange:"11 26" fps:"0" colorspace:"sRGB" datatype:"unknown" transfer:"unknown" views:"main" colorManagement:"Nuke"
version 11.1 v3
define_window_layout_xml {<?xml version="1.0" encoding="UTF-8"?>
<layout version="1.0">
	<window x="0" y="0" w="1904" h="1001" screen="0">
		<splitter orientation="1">
			<split size="40"/>
			<dock id="" hideTitles="1" activePageId="Toolbar.1">
				<page id="Toolbar.1"/>
			</dock>
			<split size="1241" stretch="1"/>
			<splitter orientation="2">
				<split size="559"/>
				<dock id="" activePageId="Viewer.1">
					<page id="Viewer.1"/>
				</dock>
				<split size="394"/>
				<dock id="" activePageId="DAG.1" focus="true">
					<page id="DAG.1"/>
					<page id="Curve Editor.1"/>
					<page id="DopeSheet.1"/>
				</dock>
			</splitter>
			<split size="615"/>
			<dock id="" activePageId="Properties.1">
				<page id="Properties.1"/>
				<page id="uk.co.thefoundry.backgroundrenderview.1"/>
			</dock>
		</splitter>
	</window>
</layout>
}
Root {
 inputs 0
 fps FRAMERATE
 name NUKEFILEPATH
 frame 11
 first_frame 11
 last_frame 26
 lock_range true
 format "2048 858 0 0 2048 858 1 A1"
 proxy false
 proxy_type scale
 proxy_format "1024 778 0 0 1024 778 1 1K_Super_35(full-ap)"
 colorManagement Nuke
 OCIO_config aces_0.1.1
 customOCIOConfigPath "C:/Program Files/Nuke12.2v5/plugins/OCIOConfigs/configs/aces_1.1/config.ocio"
 workingSpaceLUT linear
 monitorLut sRGB
 int8Lut sRGB
 int16Lut sRGB
 logLut Cineon
 floatLut linear
}
Read {
 inputs 0
 file FRAMES
 format "3072 1287 0 0 3072 1287 1 "
 last FRAMELAST
 origlast FRAMELAST
 origset true
 name Read1
 xpos -134
 ypos -105
}
Reformat {
 name Reformat1
 xpos -134
 ypos -8
}
Write {
 file OUTPUTPATH
 file_type mov
 colorspace sRGB
 mov64_codec appr
 mov_prores_codec_profile "ProRes 4:4:4:4 12-bit"
 mov_h264_codec_profile "High 4:2:0 8-bit"
 mov64_pixel_format {{0} "yuv420p\tYCbCr 4:2:0 8-bit"}
 mov64_quality High
 mov64_fast_start true
 mov64_write_timecode true
 mov64_gop_size 12
 mov64_b_frames 0
 mov64_bitrate 20000
 mov64_bitrate_tolerance 4000000
 mov64_quality_min 1
 mov64_quality_max 3
 checkHashOnRead false
 name Write1
 xpos -116
 ypos -20
}
'''


class ConvertWorker(QtCore.QThread):
	progress = QtCore.pyqtSignal(int)
	finished = QtCore.pyqtSignal()
	def __init__(self, parent, paths,frameRate, startSkip, endSkip):
		super().__init__(parent)
		self.paths = paths
		self.frame_rate = frameRate
		self.start_skip = startSkip
		self.end_skip = endSkip
	def run(self):
		script_path = os.path.join(ROOT_PATH,"nuke_bathc_render.py")
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


class ListWidget(QtWidgets.QListWidget):
	def __init__(self,parent):
		super().__init__(parent)
		self.setAcceptDrops(True)
		self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
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


class F2vInterface(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.__initWidget()
		self.setObjectName("f2v_interface")
	def __initWidget(self):
		self.setWindowTitle('序列转为视频')
		self.resize(800,600)
		layout_main = QtWidgets.QHBoxLayout(self)
		self.setLayout(layout_main)
		layout_main.setContentsMargins(50,50,50,50)

		widget_items = QtWidgets.QWidget(self)
		layout_items = QtWidgets.QVBoxLayout(widget_items)
		layout_items.setContentsMargins(0, 0, 0, 0)
		layout_main.addWidget(widget_items)

		self.list_widget = ListWidget(self)
		layout_items.addWidget(self.list_widget)

		self.progress_bar = QtWidgets.QProgressBar(self)
		self.progress_bar.setValue(0)
		self.progress_bar.setRange(0, 1)
		self.progress_bar.setFormat("")
		layout_items.addWidget(self.progress_bar)

		widget_input = QtWidgets.QWidget(self)
		widget_input.setMinimumWidth(200)
		layout_input = QtWidgets.QVBoxLayout(widget_input)
		layout_input.setContentsMargins(0, 0, 0, 0)
		layout_input.setSpacing(0)
		layout_main.addWidget(widget_input)

		widget_input_top = QtWidgets.QWidget(self)
		layout_input_top = QtWidgets.QVBoxLayout(widget_input_top)
		layout_input.addWidget(widget_input_top)
		layout_input_top.setContentsMargins(0, 0, 0, 0)
		layout_input_top.setAlignment(QtCore.Qt.AlignTop)

		self.pb_add_folder = QtWidgets.QPushButton(parent=self, text="添加序列帧目录")
		self.pb_add_folder.clicked.connect(self._add_folders_to_list)
		self.pb_remove_folder = QtWidgets.QPushButton(parent=self, text="移除选定的目录")
		self.pb_remove_folder.clicked.connect(self._remove_select_floder_from_list)
		layout_input_top.addWidget(self.pb_add_folder)
		layout_input_top.addWidget(self.pb_remove_folder)

		widget_input_buttom = QtWidgets.QWidget(self)
		layout_input_button = QtWidgets.QVBoxLayout(widget_input_buttom)
		layout_input.addWidget(widget_input_buttom)
		layout_input_button.setContentsMargins(0, 0, 0, 0)
		layout_input_button.setAlignment(QtCore.Qt.AlignBottom)

		self.pb_execute = QtWidgets.QPushButton(parent=self, text="转换为视频")
		self.pb_execute.clicked.connect(self.__convert_to_video)

		self.sb_frame_rate = QtWidgets.QSpinBox()
		self.sb_frame_rate.setValue(25)
		self.sb_start_skip = QtWidgets.QSpinBox()
		self.sb_start_skip.setValue(10)
		self.sb_end_skip = QtWidgets.QSpinBox()
		self.sb_end_skip.setValue(5)

		layout_input_button.addWidget(QtWidgets.QLabel("帧率:"))
		layout_input_button.addWidget(self.sb_frame_rate)

		layout_input_button.addWidget(QtWidgets.QLabel("开始帧跳过:"))
		layout_input_button.addWidget(self.sb_start_skip)

		layout_input_button.addWidget(QtWidgets.QLabel("结束帧跳过:"))
		layout_input_button.addWidget(self.sb_end_skip)

		layout_input_button.addWidget(self.pb_execute, alignment=QtCore.Qt.AlignBottom)
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
		folder = QtWidgets.QFileDialog.getExistingDirectory()
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
		QtWidgets.QMessageBox.information(self, "提示", "转换完成", QtWidgets.QMessageBox.Ok)



def showWindow():
	
	app = QtWidgets.QApplication(sys.argv)
	window = F2vInterface()
	window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	showWindow()

	#nuitka --standalone --onefile --windows-disable-console nuke_bathc_render_ui.py