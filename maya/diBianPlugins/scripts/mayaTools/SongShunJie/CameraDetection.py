
# -*- coding: utf-8 -*-

import sys
import threading

from PySide2.QtWidgets import *
from PySide2.QtGui import *

from maya import cmds,mel

import os





class CameraJudge(QWidget):

	def __init__(self,parent=None):
		super(CameraJudge,self).__init__(parent)

		self.uii()


	def uii(self):
  
		self.setWindowTitle('摄像机坐标轴偏移检测')
		self.resize(320,120)
		self.setStyleSheet("QWidget { background-color: #333333; }")
		lay=QVBoxLayout()

		folder_lay=QHBoxLayout()

		self.flie_import=QPlainTextEdit()
		self.flie_import.setStyleSheet("color: #cccccc; border :1px solid black")
		self.flie_import.setMaximumHeight(25)
		self.flie_import.setPlaceholderText(self.tr("请选择需检测的MAYA文件夹"))

		create_folder=QPushButton(text="开始检测")
		create_folder.setStyleSheet("color: #cccccc; ")
		create_folder.clicked.connect(self.start)

		open_folder=QToolButton()
		open_folder.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon))
		open_folder.setStyleSheet("color: #cccccc; border :3px ")
		open_folder.clicked.connect(self.openFile)

		self.progress = QProgressBar()
		self.progress.setRange(0, 100)
		self.progress.setStyleSheet('''QProgressBar {
            border: 1px solid #111111;
            border-radius: 2px;
            background-color: #333333;
			height: 10px;
			text-align:center
        }
			QProgressBar::chunk {
            border-radius: 2px;
            background-color: #dc8828;
							  

        }''')

		self.progress.hide()

		self.execute_data=QPlainTextEdit()
		self.execute_data.setStyleSheet("color: #cccccc; border :1px solid black")
		self.execute_data.setMinimumHeight(50)
		self.execute_data.setReadOnly(True)
		

		folder_lay.addWidget(self.flie_import)
		folder_lay.addWidget(open_folder)
		

		lay.addLayout(folder_lay)
		lay.addWidget(create_folder)
		lay.addWidget(self.progress)
		lay.addWidget(self.execute_data)

		
		self.setLayout(lay)


	def openFile(self):
        # 弹出文件对话框
		filename = QFileDialog.getExistingDirectory(self, '选择需要执行的文件夹')
		if filename:
			# 如果选择了文件，显示文件路径
			self.flie_import.setPlainText(filename)

	
	def cam_detection(self):

		cmds.select(all=True,hi=True)
		objs=cmds.ls(sl=True)
		cam_shapes=cmds.listRelatives(objs,type='camera')
		err_cam=[]
		if cam_shapes:
			for cam_shape in cam_shapes:
				cmds.select(cam_shape)
				#选择摄像机
				cam=cmds.pickWalk(d='up')[0]
				#复制摄像机
				cmds.Duplicate(cam)
				cam_new=cmds.ls(sl=True)[0]
				try:
					#将复制的摄像机移出组
					cmds.parent(cam_new,world=True)
				except:
					pass
				#将坐标轴移动到原点
				cmds.setAttr("%s.rx"%cam_new,lock=0)
				cmds.setAttr("%s.ry"%cam_new,lock=0)
				cmds.setAttr("%s.rz"%cam_new,lock=0)
				cmds.setAttr("%s.tx"%cam_new,lock=0)
				cmds.setAttr("%s.ty"%cam_new,lock=0)
				cmds.setAttr("%s.tz"%cam_new,lock=0)

				cmds.move( 0, 0, 0 ,rpr=1)
				cmds.setAttr('%s.rotate'%cam_new,0,0,0)
				
				#读取物体坐标信息
				axials=['.tx','.ty','.tz']
				
				for axial in axials:
					data=cmds.getAttr('%s%s'%(cam_new,axial))
					print(data)
					if data <= -1e-8 or data >= 1e-8:
						#将坐标轴异常的摄像机收集
						err_cam.append(cam)
						break
				cmds.delete(cam_new)
		
		return err_cam
	


	def mayaFile(self):

		dir_path=self.flie_import.toPlainText()
		
		maya_path=[]
		i=0
		for dirpath, dirnames, filenames in os.walk(dir_path):
			for filename in filenames:
				if filename.split('.')[-1]=='ma'  or filename.split('.')[-1]=='mb':
					new_dirpath=dirpath.replace('\\', '/')
					maya_path.append(new_dirpath+'/'+filename)
					i+=1
		if i>0:
			self.num=int(80/i)+20
		else:
			self.num=80

		if maya_path:
			print(maya_path)
			return maya_path
		else :
			self.execute_data.setPlainText('未在该文件夹中找到maya文件')
			self.progress.hide()



	def groupDict(self,*args):

		

		maya_files=self.mayaFile()
		cam_dict={}

		
		self.progress.setValue(self.num)

		for maya_file in maya_files:
			#修改文件关闭方式
			cmds.file(modified=0)
			try:
				#打开新文件,关闭引用文件导入
				cmds.file(maya_file,o=1,loadReferenceDepth='none')
			except:
				cam_dict[maya_name]=['File read error']
				continue

			#获取错误摄像机名称
			maya_name=str(maya_file).split('/')[-1]
			cam_data=self.cam_detection()

			self.num+=self.num
			self.progress.setValue(self.num)

			cam_dict[maya_name]=cam_data

		self.progress.setValue(100)
		return cam_dict
	

	def txtPath(self):

		if os.path.exists('D:/Desktop'):
			txt_path='D:/Desktop/a.txt'
		else:
			txt_path='C:/Desktop/a.txt'

		return txt_path


	def startThread(self):
		
		t1=threading.Thread(target=self.start,group=None)
		t1.start()
		

	def start(self):

		self.execute_data.setPlainText('')

		if self.flie_import.toPlainText():

			self.progress.show()
			self.progress.setValue(20)


			import maya.standalone as standalone
			standalone.initialize()

			cam_txt=''

			self.cam_datas=self.groupDict()
			if self.cam_datas:
				for maya_name,cams in self.cam_datas.items():
					if cams:
						cam_txt+=maya_name+'\n'
						for cam in cams:
							cam_txt+=cam+' '
						cam_txt+='\n\n'

				self.execute_data.setPlainText(cam_txt)

		





def start():
	app=QApplication(sys.argv)
	cam=CameraJudge()
	cam.show()
	app.exec_()


start()
	
	
	




	
	
	
	