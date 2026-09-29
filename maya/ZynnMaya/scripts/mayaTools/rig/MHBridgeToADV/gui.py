#-*- coding:utf-8 -*-
import  os
import maya.cmds as cmds
from PySide2.QtWidgets import QWidget,QVBoxLayout,QPushButton
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.mel as mel


def AddPhonemes(inputPlug,OriginNode,inMin,inMax,outMin,outMax):
	remap = cmds.createNode("remapValue")
	cmds.setAttr(remap+".inputMin",inMin)
	cmds.setAttr(remap+".inputMax",inMax)
	cmds.setAttr(remap+".outputMin",outMin)
	cmds.setAttr(remap+".outputMax",outMax)
	cmds.connectAttr(inputPlug,remap+".inputValue",f=1)

	try:
		conn = cmds.listConnections(OriginNode+'.translateY', source=False, destination=True,plugs=True)[0]
		nodeType = cmds.nodeType(conn.split(".")[0])
	except TypeError:
		print(OriginNode)
		return

	if "animCurve" in str(nodeType):
		plusNode = cmds.createNode("plusMinusAverage")
		cmds.connectAttr(OriginNode+'.translateY',plusNode+".input1D[0]",f=1)
		cmds.connectAttr(remap+".outValue",plusNode+".input1D[1]",f=1)
		cmds.connectAttr(plusNode+".output1D",conn,f=1)
	elif "plusMinusAverage" in str(nodeType):
		print("plusMinusAverage")
		plusNode = conn.split(".")[0]
		inputCount = len(cmds.listConnections(plusNode+".input1D", source=True, destination=False, plugs=True))
		cmds.connectAttr(remap+".outValue",plusNode+".input1D[{0}]".format(inputCount),f=1)
	else:
		print("un supported node:{0}".format(nodeType))
		return


def MixWithNewNode(input_plug,target_node,inMin,inMax,outMin,outMax):
	remap = cmds.createNode("remapValue")
	cmds.setAttr(remap+".inputMin",inMin)
	cmds.setAttr(remap+".inputMax",inMax)
	cmds.setAttr(remap+".outputMin",outMin)
	cmds.setAttr(remap+".outputMax",outMax)
	cmds.connectAttr(input_plug,remap+".inputValue",f=1)

	plus_node = cmds.listConnections(target_node,source=1,destination=0,type="plusMinusAverage")
	index = 1

	if plus_node:
		plus_node = plus_node[0]
		connected_nodes = cmds.listConnections(plus_node, source=1, destination=0)
		if connected_nodes:
			index = len(connected_nodes)
	else:
		plus_node = cmds.createNode("plusMinusAverage")
		origin_plug = cmds.listConnections(target_node, source=1, destination=0,plugs=1)[0]
		cmds.connectAttr(origin_plug, plus_node + ".input1D[0]", f=1)
		cmds.connectAttr(plus_node + ".output1D", target_node+".input", f=1)

	cmds.connectAttr(remap+".outValue", plus_node + ".input1D[{0}]".format(index), f=1)




def load_adv_face_gui(gui_file_path):
	#如果存在先删除已经存在的
	if cmds.objExists("ctrlBox"):
		cmds.delete("ctrlBox")
	# 导入脸部控制UI
	faceGUI_pos_rel = (50,10,0)

	cmds.file(gui_file_path, i=True, namespace=":")
	cmds.parent("ctrlBox","FRM_faceGUI")
	cmds.setAttr("ctrlBox.translateX",faceGUI_pos_rel[0])
	cmds.setAttr("ctrlBox.translateY",faceGUI_pos_rel[1])
	cmds.setAttr("ctrlBox.translateZ",faceGUI_pos_rel[2])

	#表情和口型
	#ctrlPhonemes_M
	#a
	AddPhonemes("ctrlPhonemes_M.aaa","CTRL_C_jaw",0.0,10.0,0,1)
	#e
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_jawOpen",0,10,0,0.364)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthDimpleR",0,10,0,0.217)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthCornerPullR",0,10,0,0.222)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthUpperLipRaiseR",0,10,0,0.058)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthUpperLipRaiseL",0,10,0,0.058)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthCornerPullL",0,10,0,0.222)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthDimpleL",0,10,0,0.213)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthLowerLipDepressR",0,10,0,0.082)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthLowerLipDepressL",0,10,0,0.082)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthUp",0,10,0,0.369)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_teethUpU",0,10,0,0.183)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthCornerWideR",0,10,0,0.189)
	MixWithNewNode("ctrlPhonemes_M.eh","CTRL_expressions_mouthCornerWideL",0,10,0,0.189)
	#o
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthUp",0,10,0.0,0.42)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_jawOpen",0,10,0.0,1)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthUpperLipRaiseR",0,10,0.0,0.103)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthUpperLipRaiseL",0,10,0.0,0.103)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthLowerLipDepressR",0,10,0.0,0.092)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthLowerLipDepressL",0,10,0.0,0.092)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthLipsPurseUR",0,10,0.0,0.286)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthLipsPurseUL",0,10,0.0,0.286)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthLipsPurseDR",0,10,0.0,0.286)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthLipsPurseDL",0,10,0.0,0.286)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthCornerWideR",0,10,0.0,0.05)
	MixWithNewNode("ctrlPhonemes_M.ohh","CTRL_expressions_mouthCornerWideL",0,10,0.0,0.05)
	#u
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthUpperLipRaiseR",0,10,0.0,0.071)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthUpperLipRaiseL",0,10,0.0,0.071)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLowerLipDepressR",0,10,0.0,0.021)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLowerLipDepressL",0,10,0.0,0.021)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsTowardsUR",0,10,0.0,0.3)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsTowardsUL",0,10,0.0,0.3)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsTowardsDR",0,10,0.0,0.3)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsTowardsDL",0,10,0.0,0.3)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsPurseUR",0,10,0.0,0.693)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsPurseUL",0,10,0.0,0.693)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsPurseDR",0,10,0.0,0.693)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsPurseDL",0,10,0.0,0.693)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsTightenUR",0,10,0.0,0.6)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsTightenUL",0,10,0.0,0.6)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsTightenDR",0,10,0.0,0.6)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthLipsTightenDL",0,10,0.0,0.6)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthCornerSharpenUR",0,10,0.0,0.16)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthCornerSharpenUL",0,10,0.0,0.16)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthCornerSharpenDR",0,10,0.0,0.16)
	MixWithNewNode("ctrlPhonemes_M.uuu","CTRL_expressions_mouthCornerSharpenDL",0,10,0.0,0.16)
	#iee
	MixWithNewNode("ctrlPhonemes_M.iee","CTRL_expressions_jawOpen",0,10,0.0,0.153)
	MixWithNewNode("ctrlPhonemes_M.iee","CTRL_expressions_mouthDimpleR",0,10,0.0,0.491)
	MixWithNewNode("ctrlPhonemes_M.iee","CTRL_expressions_mouthUpperLipRaiseR",0,10,0.0,0.158)
	MixWithNewNode("ctrlPhonemes_M.iee","CTRL_expressions_mouthUpperLipRaiseL",0,10,0.0,0.158)
	MixWithNewNode("ctrlPhonemes_M.iee","CTRL_expressions_mouthDimpleL",0,10,0.0,0.491)
	MixWithNewNode("ctrlPhonemes_M.iee","CTRL_expressions_mouthLowerLipDepressR",0,10,0.0,0.125)
	MixWithNewNode("ctrlPhonemes_M.iee","CTRL_expressions_mouthLowerLipDepressL",0,10,0.0,0.125)
	#fff
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthCornerPullR",0,10,0.0,0.186)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthCornerPullL",0,10,0.0,0.186)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLipsPurseUR",0,10,0.0,0.172)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLipsPurseUL",0,10,0.0,0.172)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_jawOpen",0,10,0.0,0.309)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLowerLipBiteR",0,10,0.0,0.388)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLowerLipBiteL",0,10,0.0,0.388)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLipsTogetherUR",0,10,0.0,0.124)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLipsTogetherUL",0,10,0.0,0.124)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLipsTogetherDR",0,10,0.0,0.924)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLipsTogetherDL",0,10,0.0,0.924)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLipsThinDR",0,10,0.0,0.23)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLipsThinDL",0,10,0.0,0.23)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLowerLipRollInR",0,10,0.0,0.743)
	MixWithNewNode("ctrlPhonemes_M.fff","CTRL_expressions_mouthLowerLipRollInL",0,10,0.0,0.743)
	#mbp
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthDown",10,0,-0.012,0.0)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthUpperLipBiteR",0,10,0.0,0.173)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthUpperLipBiteL",0,10,0.0,0.173)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLowerLipBiteR",0,10,0.0,0.173)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLowerLipBiteL",0,10,0.0,0.173)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLipsTightenUR",0,10,0.0,1)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLipsTightenUL",0,10,0.0,1)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLipsTightenDR",0,10,0.0,1)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLipsTightenDL",0,10,0.0,1)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLipsTogetherUR",0,10,0.0,0.486)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLipsTogetherUL",0,10,0.0,0.486)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLipsTogetherDR",0,10,0.0,0.486)
	MixWithNewNode("ctrlPhonemes_M.mbp","CTRL_expressions_mouthLipsTogetherDL",0,10,0.0,0.486)
	#Szz
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthDimpleR",0,10,0.0,0.334)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthUpperLipRaiseR",0,10,0.0,0.3)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthUpperLipRaiseL",0,10,0.0,0.3)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthDimpleL",0,10,0.0,0.334)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthLowerLipDepressR",0,10,0.0,0.47)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthLowerLipDepressL",0,10,0.0,0.47)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthCornerSharpenUR",0,10,0.0,0.062)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthCornerSharpenUL",0,10,0.0,0.062)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthCornerSharpenDR",0,10,0.0,0.056)
	MixWithNewNode("ctrlPhonemes_M.Szz","CTRL_expressions_mouthCornerSharpenDL",0,10,0.0,0.056)

	#ctrlEye_R.blink
	MixWithNewNode("ctrlEye_R.blink","CTRL_expressions_eyeBlinkR",0,1,0,1)
	MixWithNewNode("ctrlEye_L.blink","CTRL_expressions_eyeBlinkL",0,1,0,1)
	#ctrlBrow_R
	MixWithNewNode("ctrlBrow_R.translateX","CTRL_expressions_browLateralR",-1,1,-1,1)
	MixWithNewNode("ctrlBrow_R.translateY","CTRL_expressions_browRaiseInR",0,1,0,1)
	MixWithNewNode("ctrlBrow_R.translateY","CTRL_expressions_browDownR",0,-1,0,1)

	#ctrlBrow_L
	MixWithNewNode("ctrlBrow_L.translateX","CTRL_expressions_browLateralL",-1,1,1,-1)
	MixWithNewNode("ctrlBrow_L.translateY","CTRL_expressions_browRaiseInL",0,1,0,1)
	MixWithNewNode("ctrlBrow_L.translateY","CTRL_expressions_browDownL",0,-1,0,1)

	#ctrlEye_R
	MixWithNewNode("ctrlEye_R.translateX","LOC_R_eyeUIDriver_rotateY",-1,1,-1,1)
	MixWithNewNode("ctrlEye_R.translateY","LOC_R_eyeUIDriver_rotateX",-1,1,-1,1)

	#ctrlEye_L
	MixWithNewNode("ctrlEye_L.translateX","LOC_L_eyeUIDriver_rotateY",-1,1,-1,1)
	MixWithNewNode("ctrlEye_L.translateY","LOC_L_eyeUIDriver_rotateX",-1,1,-1,1)

	#ctrlCheek_R
	MixWithNewNode("ctrlCheek_R.translateX","CTRL_expressions_mouthCheekSuckR",-1,1,1,-1)
	MixWithNewNode("ctrlCheek_R.translateX","CTRL_expressions_mouthCheekBlowR",-1,1,1,-1)
	MixWithNewNode("ctrlCheek_R.translateY","CTRL_expressions_eyeCheekRaiseR",0,1,0,1)

	#ctrlCheek_L
	MixWithNewNode("ctrlCheek_L.translateX","CTRL_expressions_mouthCheekSuckL",-1,1,-1,1)
	MixWithNewNode("ctrlCheek_L.translateX","CTRL_expressions_mouthCheekBlowL",-1,1,-1,1)

	MixWithNewNode("ctrlCheek_L.translateY","CTRL_expressions_eyeCheekRaiseL",0,1,0,1)
	#ctrlNose_R
	MixWithNewNode("ctrlNose_R.translateX","CTRL_expressions_noseNostrilDilateR",-1,1,1,-1)
	MixWithNewNode("ctrlNose_R.translateX","CTRL_expressions_noseNostrilCompressR",-1,1,1,-1)

	MixWithNewNode("ctrlNose_R.translateY","CTRL_expressions_noseWrinkleR",0,1,0,1)
	MixWithNewNode("ctrlNose_R.translateY","CTRL_expressions_noseNostrilDepressR",0,1,0,1)

	#ctrlNose_L

	MixWithNewNode("ctrlNose_L.translateX","CTRL_expressions_noseNostrilDilateL",-1,1,-1,1)
	MixWithNewNode("ctrlNose_L.translateX","CTRL_expressions_noseNostrilCompressL",-1,1,-1,1)

	MixWithNewNode("ctrlNose_L.translateY","CTRL_expressions_noseWrinkleL",0,1,0,1)
	MixWithNewNode("ctrlNose_L.translateY","CTRL_expressions_noseNostrilDepressL",0,1,0,1)

	#ctrlLips_M

	MixWithNewNode("ctrlLips_M.translateX","CTRL_expressions_mouthRight",-1,1,-1,1)
	MixWithNewNode("ctrlLips_M.translateX","CTRL_expressions_mouthLeft",-1,1,-1,1)

	MixWithNewNode("ctrlLips_M.translateY","CTRL_expressions_mouthUp",-1,1,-1,1)
	MixWithNewNode("ctrlLips_M.translateY","CTRL_expressions_mouthDown",-1,1,-1,1)

	#ctrlMouth_M
	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthLipsPurseDL",-1,1,1,-1)
	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthLipsPurseDR",-1,1,1,-1)
	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthLipsPurseUL",-1,1,1,-1)

	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthCornerPullL",-1,1,-1,1)
	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthCornerDepressL",-1,1,-1,1)
	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthCornerDepressR",-1,1,-1,1)
	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthCornerPullR",-1,1,-1,1)
	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthCornerPullR",-1,1,-1,1)
	MixWithNewNode("ctrlMouth_M.translateX","CTRL_expressions_mouthDimpleL",-1,1,-1,1)

	MixWithNewNode("ctrlMouth_M.translateY","CTRL_expressions_jawOpen",-1,0,1,0)

	#ctrlMouthCorner_R
	MixWithNewNode("ctrlMouthCorner_R.translateX","CTRL_expressions_mouthCornerNarrowR",-1,1,-1,1)
	MixWithNewNode("ctrlMouthCorner_R.translateX","CTRL_expressions_mouthCornerWideR",-1,1,-1,1)

	MixWithNewNode("ctrlMouthCorner_R.translateY","CTRL_expressions_mouthCornerUpR",-1,1,-1,1)
	MixWithNewNode("ctrlMouthCorner_R.translateY","CTRL_expressions_mouthCornerDownR",-1,1,-1,1)

	#ctrlMouthCorner_L
	MixWithNewNode("ctrlMouthCorner_L.translateX","CTRL_expressions_mouthCornerNarrowL",-1,1,-1,1)
	MixWithNewNode("ctrlMouthCorner_L.translateX","CTRL_expressions_mouthCornerWideL",-1,1,-1,1)

	MixWithNewNode("ctrlMouthCorner_L.translateY","CTRL_expressions_mouthCornerUpL",-1,1,-1,1)
	MixWithNewNode("ctrlMouthCorner_L.translateY","CTRL_expressions_mouthCornerDownL",-1,1,-1,1)


	#修正metahuman表达式节点的最大值
	cmds.keyframe("CTRL_expressions_browRaiseInR", index=(1,), a=1, fc=2, vc=2)
	cmds.keyframe("CTRL_expressions_browRaiseInL", index=(1,), a=1, fc=2, vc=2)




def get_downstream_nodes(start_node, node_type=None, visited=None):
	"""
	获取指定节点的所有下游节点

	参数:
		start_node: 起始节点
		node_type: 过滤节点类型（如'mesh', 'transform', 'nurbsCurve'等）
		visited: 已访问节点集合（内部使用）

	返回:
		下游节点列表
	"""
	if visited is None:
		visited = set()

	# 如果节点已经被访问过，返回空列表
	if start_node in visited:
		return []

	visited.add(start_node)

	# 获取直接下游连接
	connections = cmds.listConnections(
		start_node,
		destination=True,  # 下游方向
		source=False,  # 不是上游
		skipConversionNodes=False,  # 包含转换节点
		connections=False,  # 不返回连接属性，只返回节点
		plugs=False
	) or []

	downstream_nodes = []

	# 遍历所有下游节点
	for node in connections:
		if node not in visited:
			# 递归获取更深层次的下游节点
			downstream_nodes.extend(get_downstream_nodes(node, node_type, visited))
			downstream_nodes.append(node)

	# 如果指定了节点类型，进行过滤
	if node_type:
		downstream_nodes = [node for node in downstream_nodes if cmds.nodeType(node) == node_type]

	return list(set(downstream_nodes))  # 去重



class MainWindow(MayaQWidgetDockableMixin,QWidget):
	def __init__(self,parent=None):
		super().__init__(parent)
		self.setWindowTitle("生成MH-ADV桥接")
		self.resize(400,200)
		self.__initUI()
	def __initUI(self):
		lay_main = QVBoxLayout(self)
		pb_generate_ui = QPushButton(self,text="生成ADV脸部控制")
		pb_generate_ui.clicked.connect(self.GenerateADVUI)
		pb_delete_ui = QPushButton(self,text="删除ADV面板")
		pb_delete_ui.clicked.connect(self.deleteADVUI)
		lay_main.addWidget(pb_generate_ui)
		lay_main.addWidget(pb_delete_ui)
		self.setLayout(lay_main)
	def GenerateADVUI(self):
		from mayaTools import MODELPATH
		load_adv_face_gui(os.path.join(MODELPATH,"template/Ctrl.ma"))
	def deleteADVUI(self):
		ctrls = [
			"ctrlBrow_R",
			"ctrlBrow_L",
			"ctrlEye_R",
			"ctrlEye_L",
			"ctrlCheek_R",
			"ctrlCheek_L",
			"ctrlNose_R",
			"ctrlNose_L",
			"ctrlLips_M",
			"ctrlMouth_M",
			"ctrlMouthCorner_R",
			"ctrlMouthCorner_L",
			"ctrlPhonemes_M"
		]
		for ctrl in ctrls:
			plus_nodes = get_downstream_nodes(ctrl, "plusMinusAverage")
			if plus_nodes is None:
				continue
			for plus_node in plus_nodes:
				origin_ctrl = \
				[node for node in cmds.listConnections(plus_node, source=1, destination=0, plugs=1, type="transform") if
				 node.split(".")[0] not in ctrls][0]
				anim = cmds.listConnections(plus_node, destination=1, source=0,
											type="animCurveUU") or cmds.listConnections(plus_node, destination=1,
																						source=0, type="animCurveUA")
				if anim is None:
					continue
				if len(anim) > 1:
					origin_ctrl = origin_ctrl.split(".")[0]
					for a in anim:
						p = str(cmds.listConnections(a, destination=0, source=1, plugs=1, type="plusMinusAverage")[0])
						if "x" in p.lower():
							cmds.connectAttr(origin_ctrl + ".translateX", a + ".input", f=1)
						elif "y" in p.lower():
							cmds.connectAttr(origin_ctrl + ".translateY", a + ".input", f=1)
				else:
					anim = anim[0]
					cmds.connectAttr(origin_ctrl, anim + ".input", f=1)
				cmds.delete(plus_node)
		cmds.delete("ctrlBox")
		#清理场景
		if "MAYA_TESTING_CLEANUP" not in os.environ:
			os.environ["MAYA_TESTING_CLEANUP"] = "enable"
			mel.eval("cleanUpScene 1;")
			del os.environ["MAYA_TESTING_CLEANUP"]
		else:
			mel.eval("cleanUpScene 1;")

		# 修正metahuman表达式节点的最大值
		cmds.keyframe("CTRL_expressions_browRaiseInR", index=(1,), a=1, fc=1, vc=1)
		cmds.keyframe("CTRL_expressions_browRaiseInL", index=(1,), a=1, fc=1, vc=1)

def show():
	window = MainWindow()
	window.show()



if __name__ == "__main__":
	show()











