import copy
import os
import tempfile

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
							 QHBoxLayout, QLabel,
							 QProgressBar, QSpinBox, QFileDialog,
							 QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from app.core.style_sheet import StyleSheet

def FindAnFile(mov_path:str):
	project_name = mov_path.split("/")[1]
	file_name,ext = os.path.splitext(os.path.basename(mov_path))
	try:
		ep, sc, cam = file_name.split("_")[0:3]
	except ValueError as e:
		return  False
	
	an_file_path = os.path.join("Y:\\",project_name,ep,"Animation\\avi",sc,f"{ep}_{sc}_{cam}_an.avi")
	if os.path.exists(an_file_path):
		return  an_file_path
	else:
		#Y:\TX\EP001\Video\Lt_Video\sc001
		#Y:\TX\EP001\Video\An_Video\sc001
		an_file_path = os.path.join("Y:\\",project_name,ep,"Video\\An_Video",sc,f"{ep}_{sc}_{cam}_an.mov")
		if os.path.exists(an_file_path):
			return  an_file_path
	return False

def GetVideoFrameCount(video_path):
	import cv2
	cap = cv2.VideoCapture(video_path)
	frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	return frame_count




class TableWidget(QTableWidget):
	def __init__(self,parent):
		super().__init__(parent)
		self.__initTable()
	def __initTable(self):
		self.setAcceptDrops(True)
		self.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
		self.setColumnCount(3)
		self.setHorizontalHeaderLabels(["mov文件","动画拍屏","是否正确"])
		self.setColumnWidth(0,800)
		self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
		header = self.horizontalHeader()
		header.setSectionResizeMode(1,QHeaderView.Fixed)
		header.setSectionResizeMode(2,QHeaderView.Fixed)
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.files = []
	def clearAll(self):
		self.clear()
		self.setRowCount(0)
		self.__initTable()
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
			files = [url.toLocalFile() for url in urls if (os.path.isfile(url.toLocalFile()) and url.toLocalFile() not in self.files)]
			current_row_count = self.rowCount()
			self.setRowCount(current_row_count+len(files))
			for i in range(current_row_count,current_row_count+len(files)):
				item = QTableWidgetItem(str(files[i-current_row_count]))
				self.setItem(i, 0, item)
				item = QTableWidgetItem()
				self.setItem(i, 1, item)
				item = QTableWidgetItem()
				self.setItem(i, 2, item)
				self.files.append(files[i-current_row_count])
			event.acceptProposedAction()
		else:
			event.ignore()


class VINFInterface(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.__initWidget()
		self.__setQss()
		self.setObjectName("vinfo_interface")
	def __initWidget(self):
		layout_main = QVBoxLayout(self)
		self.setLayout(layout_main)
		layout_main.setContentsMargins(50,50,50,50)

		self.table_widget = TableWidget(self)
		layout_main.addWidget(self.table_widget)

		self.pb_execute = QPushButton(parent=self, text="开始比对")
		self.pb_execute.clicked.connect(self.compare_with_animation)

		self.pb_clear_list = QPushButton(parent=self, text="清空列表")
		self.pb_clear_list.clicked.connect(self.clear_list)
		layout_main.addWidget(self.pb_execute)
		layout_main.addWidget(self.pb_clear_list)
	def clear_list(self):
		self.table_widget.clearAll()
	def compare_with_animation(self):
		rows = self.table_widget.rowCount()
		red = QColor(255,0,0)
		green = QColor(0,255,0)

		for i in range(rows):
			item = self.table_widget.item(i,0)
			path = item.text()
			print(path)
			anim_path = FindAnFile(path)

			right = False
			sub = 0
			if anim_path:
				sub =  GetVideoFrameCount(path) - GetVideoFrameCount(anim_path)
				right = sub == 0

			item = self.table_widget.item(i,1)
			if anim_path:
				item.setBackground(green)
			else:
				item.setBackground(red)

			item = self.table_widget.item(i,2)
			if right:
				item.setBackground(green)
			else:
				item.setText(str(sub))
				item.setBackground(red)

	def update_progress(self, value):
		self.progress_bar.setValue(value)

	def __setQss(self):
		StyleSheet.VIN_INTERFACE.apply(self)