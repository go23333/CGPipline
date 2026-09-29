#coding=utf-8
import maya.cmds as cmds
import maya.mel as mel
import os

from PySide2.QtWidgets import QWidget,QVBoxLayout,QPushButton,QHBoxLayout,QLineEdit,QLabel,QToolButton,QFileDialog,QMessageBox
from PySide2.QtCore import Qt
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


name_space = "MaterialInfo"

class ShapeType:
	Mesh = 0
	Hair = 1


def get_material_info(mode):
	relationships = {}
	if mode == ShapeType.Mesh:
		sgs = cmds.ls(typ="shadingEngine")
		for sg in sgs:
			shapes = cmds.sets(sg,query=1)
			if not shapes:
				continue
			for shape in shapes:
				mesh_name = shape.split(".")
				if len(mesh_name) > 1:
					comp = mesh_name[1]
					mesh_name = mesh_name[0]
				else:
					mesh_name = mesh_name[0]
					comp = ""
				info = dict(
					comp = comp,
					sg = sg,
					type = ShapeType.Mesh
				)
				if mesh_name not in relationships.keys():
					relationships[mesh_name] = []
				relationships[mesh_name].append(info)
	elif mode == ShapeType.Hair:
		#获取所有的头发信息
		hairsystems = cmds.ls(typ="hairSystem")
		for hairSystem in hairsystems:
			shaders = cmds.listConnections(hairSystem + ".rsHairShader")
			if shaders:
				shader = shaders[0]
			else:
				shader = None
			info = dict(
				type = ShapeType.Hair,
				shader = shader,
			)
			relationships[hairSystem]  = info
	print(relationships)
	return relationships
def clean_scene():
	#command = 'scOpt_performOneCleanup( { "animationCurveOption", "deformerOption", "unusedSkinInfsOption","groupIDnOption","shaderOption" ,"brushOption","referencedOption","snapshotOption","pbOption"} );'
	#清理场景
	if "MAYA_TESTING_CLEANUP" not in os.environ:
		os.environ["MAYA_TESTING_CLEANUP"] = "enable"
		mel.eval("cleanUpScene 1;")
		del os.environ["MAYA_TESTING_CLEANUP"]
	else:
		mel.eval("cleanUpScene 1;")



def reset_scene_to_default_shader(mode):
	if mode == ShapeType.Mesh:
		#将整个场景的材质设置为初始材质
		sgs = cmds.ls(typ="shadingEngine")
		for sg in sgs:
			shapes = cmds.sets(sg,query=1)
			if not shapes:
				continue
			cmds.sets(shapes, edit=True, forceElement="initialShadingGroup")
	elif mode == ShapeType.Hair:
		#删除所有头发的材质
		hairsystems = cmds.ls(typ="hairSystem")
		for hairSystem in hairsystems:
			shaders = cmds.listConnections(hairSystem + ".rsHairShader")
			if shaders:
				cmds.delete(shaders[0])
	clean_scene()

def load_material_from_file(file_path):
	Mode = ShapeType.Mesh
	if "hair" in file_path.lower():
		Mode = ShapeType.Hair

	#获取当前的文件的路径
	current_path = cmds.file(q=True, sn=True)
	print(u"当前路径为:{}".format(current_path))
	#清除当前场景的材质信息
	reset_scene_to_default_shader(Mode)
	#打开要读取材质信息的场景文件
	cmds.file(file_path,open=1,f=1)
	print(u"打开要读取材质信息的场景文件")
	#获取材质信息
	relation_ships = get_material_info(Mode)
	#打开原来的场景
	print(u"打开原来的场景")
	cmds.file(current_path,open=1,f=1)
	#导入要读取材质信息的场景文件
	new_nodes = cmds.file(file_path, 
							i=True,
							ignoreVersion=True,
							namespace=name_space,
							returnNewNodes=True,
							preserveReferences=False)
	print(u"删除无用的节点")
	#删除无用的节点
	for new_ndoe in new_nodes:
		if not cmds.objExists(new_ndoe):
			continue
		if cmds.nodeType(new_ndoe) == "transform":
			cmds.delete(new_ndoe)
		
	#删除命名空间
	cmds.namespace(removeNamespace=name_space, mergeNamespaceWithRoot=True,f=1)

	print(u"重新连接材质信息")
	for mesh in relation_ships.keys():
		if Mode == ShapeType.Mesh:
			first = True
			for shader_info in relation_ships[mesh]:
				if first:
					first = False
					cmds.sets(mesh, edit=True, forceElement=shader_info["sg"])
				cmds.sets(mesh+"."+shader_info["comp"], edit=True, forceElement=shader_info["sg"])
		elif Mode == ShapeType.Hair:
			shader = relation_ships[mesh]['shader']
			cmds.connectAttr(shader +".outColor",mesh+".rsHairShader",f=1)

	#刷新所有的结果
	cmds.evalDeferred("mel.eval('LowQualityDisplay')")
	#清理场景
	clean_scene()


class LoadShaderFromFile(MayaQWidgetDockableMixin,QWidget):
	def __init__(self,parent=None):
		super(LoadShaderFromFile,self).__init__(parent)
		self.setWindowTitle(u"从文件中读取材质")
		self.resize(400,200)
		self.__initUI()
	def __initUI(self):
		lay_main = QVBoxLayout()
		self.setLayout(lay_main)


		#选择文件
		widget_select_file = QWidget(self)
		lay_main.addWidget(widget_select_file)
		lay_select_file = QHBoxLayout(widget_select_file)
		lay_select_file.setContentsMargins(0,0,0,0)
		lay_select_file.setSpacing(5)


		lay_select_file.addWidget(QLabel(text=u"路径"))
		self.le_path = QLineEdit()
		self.le_path.setPlaceholderText(u"选择一个mb文件路径")
		lay_select_file.addWidget(self.le_path)
		pb_select_path = QPushButton("    ")
		pb_select_path.clicked.connect(self.__select_path)
		lay_select_file.addWidget(pb_select_path)


		lay_main.setAlignment(Qt.AlignTop)


		btn_action = QPushButton(text=u"执行")
		btn_action.clicked.connect(self._execute)
		lay_main.addWidget(btn_action)
	def __select_path(self):
		file = QFileDialog.getOpenFileName(self,u"选择要导入材质的mb文件",".","Maya Binary (*.mb)")
		if not file:
			return
		self.le_path.setText(file[0])
	def _execute(self):
		file_path = self.le_path.text()
		if not file_path:
			QMessageBox.warning(self,u"错误",u"请先选择一个文件")
			return
		load_material_from_file(file_path)

def show():
	window = LoadShaderFromFile()
	window.show()
if __name__ == "__main__":
	show()

	pass

