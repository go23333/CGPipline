from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QToolButton, QHBoxLayout, QListWidget, QCheckBox, \
	QPushButton, QListView, QProgressBar, QMessageBox, QAbstractItemView, QTabWidget, QTableWidget, QTableWidgetItem, \
	QComboBox
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


logger = Log.get().getLogger("Batch")
logger.setLevel(Log.Level.debug)


def IsLevelSequence(path:str)->bool:
	seq_key_word = b"\x2f\x53\x63\x72\x69\x70\x74\x2f\x4c\x65\x76\x65\x6c\x53\x65\x71\x75\x65\x6e\x63\x65"
	with open(path,"rb") as f:
		str_data = f.read()
		if str_data.find(seq_key_word)>0:
			return True
	return False


class RenderState:
	Wait = 0
	Runing = 1
	Finished = 2
	Error = 3
#datas
class RenderQueueItem:
	seq_path:str
	level_path:str
	file_name :str
	render_state:RenderState
	output_path:str
	def __init__(self,seq,level,work_path:str):
		baseName = os.path.basename(seq)
		self.file_name,_ = os.path.splitext(baseName)
		self.seq_path = seq.replace(work_path,"\\Game\\Shots").replace("\\","/").replace(".uasset","")
		self.seq_path = self.seq_path + "." +self.seq_path.split("/")[-1]
		self.level_path = level.replace(work_path,"\\Game\\Shots").replace("\\","/").replace(".umap","")
		self.level_path = self.level_path + "." + self.level_path.split("/")[-1]
		self.render_state = 0
		self.output_path = ""
	def __repr__(self):
		return f"<RenderQueue Object Path:{self.seq_path}>"

#threads
class WorkerGetRenderJobs(QThread):
	getCount = pyqtSignal(int)
	getJob = pyqtSignal(RenderQueueItem)
	tickProgress = pyqtSignal()
	finished = pyqtSignal()
	workDir = ""
	isWorked = False
	def __init__(self,parent=None):
		super().__init__(parent)
	def setWorkDir(self,dirName):
		self.workDir = dirName
	def run(self):
		if self.workDir == "":
			return
		self.isWorked = True
		eps = [os.path.join(self.workDir, ep) for ep in os.listdir(self.workDir) if ep.lower().startswith("ep") and "." not in ep]
		scs = []
		cams = []
		for ep in eps:
			scs.extend([os.path.join(ep, sc) for sc in os.listdir(ep) if sc.lower().startswith("sc") and "." not in sc])
		for sc in scs:
			cams.extend([os.path.join(sc, cam) for cam in os.listdir(sc) if "." not in cam])
		self.getCount.emit(len(cams))
		for cam in cams:
			self.tickProgress.emit()
			map_path = ""
			seq_path = ""
			for file in os.listdir(cam):
				file_path = os.path.join(cam, file)
				if file_path.endswith(".umap"):
					map_path = file_path
				elif file_path.endswith("Render.uasset") and IsLevelSequence(file_path):
					seq_path = file_path
			if not map_path or not seq_path:
				continue
			self.getJob.emit(RenderQueueItem(seq_path,map_path,self.workDir))
		self.finished.emit()
		self.isWorked = False

class WorkerSocket(QThread):
	onMessageRevive = pyqtSignal(str)
	def __init__(self,parent=None):
		super().__init__(parent)
		self.host = "127.0.0.1"
		self.port = 5060
		self.__isListening = True

	def run(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind((self.host,self.port))
		self.socket.listen()
		logger.info(f"开启端口监听在:{self.host}:{self.port}")
		while self.__isListening:
			try:
				conn,addr = self.socket.accept()
			except OSError as e:
				logger.error(f"端口监听发生错误:{e}")
				break
			with conn:
				logger.info(f"Connected by {addr}")
				while True:
					try:
						data = conn.recv(4)
						if not data:
							break
						size = struct.unpack("<i",data)[0]
						data = conn.recv(size)
						logger.info(f"接收到来自UE的信息:{data.decode()}")
						self.onMessageRevive.emit(data.decode())
					except Exception as e:
						break

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
class TabForSequence(QTableWidget):
	def __init__(self,parent=None):
		super().__init__(parent)
		self.setColumnCount(3)
		self.setHorizontalHeaderLabels(["名称","状态","输出路径"])
		self.setEditTriggers(QTableWidget.NoEditTriggers)
		self.setSelectionBehavior(QTableWidget.SelectRows)
	def resizeEvent(self, e):
		width = self.width() - 50
		self.setColumnWidth(0,int(width*0.25))
		self.setColumnWidth(1,int(width*0.05))
		self.setColumnWidth(2,int(width*0.70))
		return super().resizeEvent(e)
	def mouseDoubleClickEvent(self, e):
		items = self.selectedItems()
		for item in items:
			if not item.row() != 2:
				continue
			if os.path.exists(item.text()):
				os.startfile(item.text())
		return super().mouseDoubleClickEvent(e)

class BatchRenderInterface(QWidget):

	def __init__(self,parent=None):
		super().__init__(parent)
		self.selected_jobs = None
		self.current_job = None
		self.setObjectName("BatchRenderInterface")
		self.queues:dict[str:RenderQueueItem] = {}
		self.eps = []
		self.scs = []
		self.is_render_pipeline_finished = False

		self.getQueuesWorker = WorkerGetRenderJobs(self)
		self.getQueuesWorker.getCount.connect(self.OnProgressStart)
		self.getQueuesWorker.getJob.connect(self.OnGetAJob)
		self.getQueuesWorker.finished.connect(self.OnGetSequenceFinished)
		self.getQueuesWorker.tickProgress.connect(self.OnTickProgress)

		self.__initUI()
		self.__setQss()
		#监听端口
		self.socketThread = WorkerSocket(self)
		self.socketThread.onMessageRevive.connect(self.onMessageRecive)
		self.socketThread.start()
		self.worker_for_call_unreal = WorkerPullUnreal()
		self.worker_for_call_unreal.onUnrealClosed.connect(self.OnUnrealClosed)

		#拼接脚本路径
		self.scriptPath  = os.path.join(ROOT_PATH,"scripts/UEBatchRender.py")

	def __initUI(self):
		layoutMain = QVBoxLayout(self)
		layoutMain.setContentsMargins(30,50,30,50)
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
		#配置文件路径
		self.psg_config_path = FileSelectGroup(
			"配置文件路径:",
			"选择UE项目路径",
			"UE项目(*.uasset)",
			parent=self,
			textMaxWidth=100
		)

		layoutMain.addWidget(self.psg_project_path)
		layoutMain.addWidget(self.psg_config_path)

		self.psg_ue_path.onSelectPath.connect(self.__saveConfig)
		self.psg_project_path.onSelectPath.connect(self.__saveConfig)
		self.psg_config_path.onSelectPath.connect(self.__saveConfig)
		#刷新列表
		pb_refreshList = QPushButton(text="刷新列表")
		pb_refreshList.clicked.connect(self._refresh_list)
		layoutMain.addWidget(pb_refreshList,alignment=Qt.AlignRight)

		#进度条
		self.pg_progress = QProgressBar(self)
		layoutMain.addWidget(self.pg_progress)


		w_filter = QWidget(self)
		layoutMain.addWidget(w_filter)
		ly_filter = QHBoxLayout(w_filter)
		ly_filter.setAlignment(Qt.AlignLeft)
		ly_filter.setContentsMargins(0,0,0,0)

		self.cb_ep = QComboBox(self)
		self.cb_ep.currentTextChanged.connect(self.onFilterChanged)
		self.cb_ep.setFixedWidth(100)

		self.cb_sc = QComboBox(self)
		self.cb_sc.currentTextChanged.connect(self.onFilterChanged)
		self.cb_sc.setFixedWidth(100)


		ly_filter.addWidget(self.cb_ep)
		ly_filter.addWidget(self.cb_sc)


		w_list = QWidget(self)
		ly_list = QHBoxLayout(w_list)
		ly_list.setContentsMargins(0,0,0,0)
		layoutMain.addWidget(w_list)

		# 渲染队列
		self.lw_queue = TabForSequence(self)

		self.lw_queue.setAlternatingRowColors(True)
		ly_list.addWidget(self.lw_queue)

		w_render = QWidget(self)
		layoutMain.addWidget(w_render)
		ly_render = QHBoxLayout(w_render)


		self.cb_retry = QCheckBox(text="渲染失败后重试")
		ly_render.addWidget(self.cb_retry)

		pb_render = QPushButton(text="渲染队列")
		pb_render.clicked.connect(self.renderSelectedQueue)
		ly_render.addWidget(pb_render)

	def _refresh_list(self):
		projectDir = self.psg_project_path.text()
		if projectDir == "":
			QMessageBox.warning(self,"警告","未选择UE项目路径")
			return False
		queueDir = os.path.dirname(projectDir) + r"\Content\Shots"
		if not self.getQueuesWorker.isWorked:
			self.queues.clear()
			self.getQueuesWorker.setWorkDir(queueDir)
			self.getQueuesWorker.start()
		return True

	def renderSelectedQueue(self):
		EditorQueuePaths = []
		self.selected_jobs = []
		#提取选择的列表项目的第一列的项目
		sls = [item for item in self.lw_queue.selectedItems() if item.column()==0]
		for sl in sls:
			job = self.queues.get(sl.text(),None)
			if job:
				self.selected_jobs.append(job)
				EditorQueuePaths.append(job.level_path)
				EditorQueuePaths.append(job.seq_path)
		if not EditorQueuePaths:
			return
		self.__render_queues(EditorQueuePaths)
	def __render_queues(self,EditorQueuePaths):
		EnginePath = self.psg_ue_path.text().replace(".exe","-Cmd.exe")
		ProjectPath = self.psg_project_path.text()
		config_path = self.psg_config_path.text()
		if not EnginePath or not ProjectPath or not config_path:
			QMessageBox.warning(self,"警告","路径设置不全")
			return

		if not os.path.exists(EnginePath) or not os.path.exists(ProjectPath) or not os.path.exists(config_path):
			QMessageBox.warning(self,"警告","路径设置中的文件不存在")
			return

		root_dir = os.path.dirname(ProjectPath) + "/Content"
		config_path = config_path.replace(root_dir,"\\Game").replace("\\","/").replace(".uasset","")
		config_path = config_path + "." + config_path.split("/")[-1]
		self.worker_for_call_unreal.command  = f'"{EnginePath}" "{ProjectPath}" -unattended -log -ExecutePythonScript="{self.scriptPath}" -queue={",".join(EditorQueuePaths)} -config="{config_path}"'
		self.worker_for_call_unreal.start()
		self.is_render_pipeline_finished = False
	####### 一些回调函数 #################
	def OnUnrealClosed(self):
		if self.is_render_pipeline_finished:
			return
		if not self.cb_retry.isChecked():
			return
		#跳过当前的任务
		self.current_job.render_state = RenderState.Error


		logger.info("渲染过程中UE崩溃,重新启动UE")
		EditorQueuePaths = []
		for job in self.selected_jobs:
			if job.render_state != RenderState.Finished and job.render_state != RenderState.Error:
				EditorQueuePaths.append(job.level_path)
				EditorQueuePaths.append(job.seq_path)
		if not EditorQueuePaths:
			return
		self.__render_queues(EditorQueuePaths)
	def OnProgressStart(self, maximum):
		self.pg_progress.setValue(0)
		self.pg_progress.setMaximum(maximum)
	def OnGetAJob(self, job:RenderQueueItem):
		name = job.file_name
		ep,sc = name.split("_")[0:2]
		if ep not in self.eps:
			self.eps.append(ep)
		if sc not in self.scs:
			self.scs.append(sc)
		self.queues[job.file_name] = job
	def OnTickProgress(self):
		currentValue = self.pg_progress.value()
		self.pg_progress.setValue(currentValue+1)
	def OnGetSequenceFinished(self):
		self.cb_ep.clear()
		self.cb_sc.clear()
		self.cb_ep.addItems(self.eps)
		self.cb_sc.addItems(self.scs)
	def onFilterChanged(self,*arg):
		current_ep = self.cb_ep.currentText()
		current_sc = self.cb_sc.currentText()
		filtered_jobs = [job for job in self.queues.values() if job.file_name.startswith(f"{current_ep}_{current_sc}")]

		self.lw_queue.setRowCount(0)
		self.lw_queue.setRowCount(len(filtered_jobs))
		for i,job in enumerate(filtered_jobs):
			item = QTableWidgetItem()
			item.setText(job.file_name)
			self.lw_queue.setItem(i,0,item)
			item = QTableWidgetItem()
			item.setText(job.output_path)
			self.lw_queue.setItem(i,2,item)
			if job.render_state == RenderState.Wait:
				item = QTableWidgetItem()
				item.setText("等待")
				self.lw_queue.setItem(i, 1, item)
			elif job.render_state == RenderState.Runing:
				item = QTableWidgetItem()
				item.setText("渲染中")
				item.setBackground(QColor(255,255,0))
				self.lw_queue.setItem(i, 1, item)
			elif job.render_state == RenderState.Finished:
				item = QTableWidgetItem()
				item.setText("完成")
				item.setBackground(QColor(0,255,0))
				self.lw_queue.setItem(i, 1, item)
				item  = QTableWidgetItem()
				item.setText(job.output_path)
				self.lw_queue.setItem(i,2,item)
			elif job.render_state == RenderState.Error:
				item = QTableWidgetItem()
				item.setText("错误")
				item.setBackground(QColor(255,0,0))
				self.lw_queue.setItem(i, 1, item)

	def onMessageRecive(self,message):
		try:
			message_data = json.loads(message)
		except json.decoder.JSONDecodeError as e:
			return
		if message_data['stage'] == "job":
			self.onRenderStateUpdate(message_data)
			pass
		elif message_data['stage'] == "Queue":
			self.onUnrealRenderFinished(message_data)
	##########UE回调函数
	def onRenderStateUpdate(self,message):
		self.current_job = self.queues.get(message["job_name"],None)
		if not self.current_job:
			return
		if message["state"] == "start":
			self.current_job.render_state = RenderState.Runing
		elif message["state"] == "finish":
			self.current_job.render_state = RenderState.Finished
			self.current_job.output_path = message["output_dir"]
		self.onFilterChanged()
	def onUnrealRenderFinished(self,message):
		self.is_render_pipeline_finished = True
		pass
	####### 其他函数 #################
	def __loadFromConfig(self):
		self.psg_ue_path.setText(Config.Get().CurrentUnrealPath)
		self.psg_project_path.setText(Config.Get().CurrentUnrealProjectPath )
		self.psg_config_path.setText(Config.Get().CurrentRenderConfigPath)
	def __saveConfig(self):
		#保存当前配置文件
		Config.Get().CurrentUnrealPath = self.psg_ue_path.text()
		Config.Get().CurrentUnrealProjectPath =self.psg_project_path.text()
		Config.Get().CurrentRenderConfigPath = self.psg_config_path.text()
		Config.Get().saveConfig()
	def showEvent(self, a0):
		self.__loadFromConfig()
		return  super().showEvent(a0)
	def hideEvent(self, a0):
		self.__saveConfig()
		return super().hideEvent(a0)
	def __setQss(self):
		StyleSheet.BATCH_RENDER.apply(self)








