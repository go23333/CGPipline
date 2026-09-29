#-*- coding:utf-8 -*-
from __future__ import division,print_function
from pydoc import text

from PySide2.QtWidgets import QWidget, QListWidget,QHBoxLayout,QLabel,QScrollArea,QSizePolicy,QPushButton
from PySide2.QtCore import Qt

from maya.app. general.mayaMixin import MayaQWidgetDockableMixin

from mayaTools.core.widgets import BezierWidget,ValueInputGroup, ValueInputGroupType,WidgetGroup,BezierPoint
import maya.cmds as cmds



class BatchEdit(MayaQWidgetDockableMixin,QWidget):
	def __init__(self,parent=None):
		super(BatchEdit,self).__init__(parent)
		self.setWindowTitle(u"Maya解算批量编辑工具")
		self.input_widgets = {}
		self.__initUI()
		self.__update_list()
	def __initUI(self):
		ly_main = QHBoxLayout(self)
		self.setLayout(ly_main)

		left_group = WidgetGroup(False,self)
		ly_main.addWidget(left_group)
		self.lw_hairsystem = QListWidget()
		self.lw_hairsystem.itemSelectionChanged.connect(self.on_select_item)
		self.lw_hairsystem.setSelectionMode(QListWidget.ExtendedSelection)
		self.lw_hairsystem.setMaximumWidth(300)
		left_group.addWidget(self.lw_hairsystem)
		left_group.setMaximumWidth(300)

		btn_apply = QPushButton(parent=self,text=u"应用")
		btn_apply.clicked.connect(self.__apply_changes)
		left_group.addWidget(btn_apply)

		scroll = QScrollArea(self)
		ly_main.addWidget(scroll)


		scroll.setWidgetResizable(True)  # 允许内容部件调整大小
		scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		scroll.setAlignment(Qt.AlignCenter)  # 内容居中显示
		scroll.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
	


		right_group =  WidgetGroup(False,self)
		right_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		right_group.setContentsMargins(20,20,20,20)
		scroll.setWidget(right_group)

		right_group.addWidget(QLabel("Dynamic Properties:"))

		self.input_widgets = dict(
			stretchResistance     = ValueInputGroup(self,"Stretch Resistance:",200,0,0.1),
			compressionResistance = ValueInputGroup(self,"Compression Resistance",200,0,0.1),
			bendResistance        = ValueInputGroup(self,"Bend Resistance:",200,0,0.1),
			twistResistance       = ValueInputGroup(self,"Twist Resistance:",200,0,0.1),
			extraBendLinks        = ValueInputGroup(self,"Extra BendLinks:",20,0,0.01,ValueInputGroupType.INT),
			restLengthScale       = ValueInputGroup(self,"Rest Length Scale:",200,0,0.1),
			startCurveAttract     = ValueInputGroup(self,"Start Curve Attract:",1,0,0.001),
			attractionDamp        = ValueInputGroup(self,"AttractionDamp:",10,0,0.01),
			mass                  = ValueInputGroup(self,"Mass:",1,0,0.001),
			drag                  = ValueInputGroup(self,"Drag:",1,0,0.001),
			tangentialDrag        = ValueInputGroup(self,"Tangential Drag:",1,0,0.001),
			motionDrag            = ValueInputGroup(self,"Motion Drag:",1,0,0.001),
			damp                  = ValueInputGroup(self,"Damp:",10,0,0.01),
			stretchDamp           = ValueInputGroup(self,"Stretch Damp:",10,0,0.01),
			dynamicsWeight        = ValueInputGroup(self,"Dynamics Weight:",1,0,0.001),
			stiffnessScale        = BezierWidget(self),
			attractionScale       = BezierWidget(self)
		)

		right_group.addWidget(self.input_widgets["stretchResistance"])
		right_group.addWidget(self.input_widgets["compressionResistance"])
		right_group.addWidget(self.input_widgets["bendResistance"])
		right_group.addWidget(self.input_widgets["twistResistance"])
		right_group.addWidget(self.input_widgets["extraBendLinks"])
		right_group.addWidget(self.input_widgets["restLengthScale"])


		right_group.addWidget(QLabel("Stiffness Scale:"))

		right_group.addWidget(self.input_widgets["stiffnessScale"])
		
		right_group.addWidget(QLabel("Start Curve Attract:"))

		right_group.addWidget(self.input_widgets["startCurveAttract"])
		right_group.addWidget(self.input_widgets["attractionDamp"])


		right_group.addWidget(QLabel("Attraction Scale:"))
		right_group.addWidget(self.input_widgets["attractionScale"])



		right_group.addWidget(QLabel("Forces"))

		right_group.addWidget(self.input_widgets["mass"])
		right_group.addWidget(self.input_widgets["drag"])
		right_group.addWidget(self.input_widgets["tangentialDrag"])
		right_group.addWidget(self.input_widgets["motionDrag"])
		right_group.addWidget(self.input_widgets["damp"])
		right_group.addWidget(self.input_widgets["stretchDamp"])
		right_group.addWidget(self.input_widgets["dynamicsWeight"])

	def __update_list(self):
		hair_systems = cmds.ls(type="hairSystem")
		self.lw_hairsystem.addItems(hair_systems)
	def on_select_item(self,*args):
		items = self.lw_hairsystem.selectedItems()
		sl_objs = [item.text() for item in items]
		if len(sl_objs) == 0:
			return
		
		cmds.select(sl_objs)
		self.__update_object_to_win(sl_objs[0])
	def __update_object_to_win(self,obj):
		for key,value in self.input_widgets.items():
			if isinstance(value,ValueInputGroup):
				v = cmds.getAttr(obj+"."+key)
				value.setValue(v)
			else:
				count = cmds.getAttr(obj+"."+key,size=True)
				value.bezier.points = []
				for i in range(count):
					value_name = "{}.{}[{}].{}_FloatValue".format(obj,key,i,key)
					pos_name = "{}.{}[{}].{}_Position".format(obj,key,i,key)
					inter_type_name = "{}.{}[{}].{}_Interp".format(obj,key,i,key)
					type = cmds.getAttr(inter_type_name)
					point = BezierPoint()
					point.setX(cmds.getAttr(pos_name))
					point.setY(cmds.getAttr(value_name))
					point.type = type
					value.bezier.add_new_point(point)
	def __apply_changes(self):
		items = self.lw_hairsystem.selectedItems()
		sl_objs = [item.text() for item in items]
		for obj in sl_objs:
			self.__apply_change(obj)
	def __apply_change(self,obj):
		for key,value in self.input_widgets.items():
			if isinstance(value,ValueInputGroup):
				cmds.setAttr(obj+"."+key,value.value())
			else:
				try:
					cmds.removeMultiInstance(obj+"."+key,all=1)
				except:
					pass
				for i,point in enumerate(value.bezier.points):
					value_name = "{}.{}[{}].{}_FloatValue".format(obj,key,i,key)
					pos_name = "{}.{}[{}].{}_Position".format(obj,key,i,key)
					inter_type_name = "{}.{}[{}].{}_Interp".format(obj,key,i,key)
					cmds.setAttr(value_name,point.y())
					cmds.setAttr(pos_name,point.x())
					cmds.setAttr(inter_type_name,point.type)
	


def show():
	edit = BatchEdit()
	edit.show(dockable=True)


if __name__ == "__main__":
	# from mayaTools import reloadModule
	# reloadModule()
	edit = BatchEdit()
	edit.show(dockable=True)
