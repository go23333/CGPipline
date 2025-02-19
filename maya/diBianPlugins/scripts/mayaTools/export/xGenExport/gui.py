# -*- coding: utf-8 -*-

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.cmds as cmds
from Qt.QtWidgets import *
from Qt.QtCore import Qt
import mayaTools.core.widgets as widgets
from dayu_widgets.line_edit import MClickBrowserFolderToolButton,MLineEdit
from dayu_widgets.push_button import MPushButton
from dayu_widgets.message import MMessage
import os

#导入自定义模块
import mayaTools.core.mayaLibrary as ML
import mayaTools.core.pathLibrary as PL



class XgenTool(MayaQWidgetDockableMixin,QWidget):
    def __init__(self):
        super(XgenTool,self).__init__()
        self.setWindowTitle(u"xgen工具")
        self.resize(250,300)
        self.currentIDs = []
        self.id_attr_name = 'groom_group_id'
        self.__initUI()
        self.__setQss()
    def __initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.setContentsMargins(10,20,10,0)
        self.setLayout(mainLayout)
        self.lab_ids = QLabel(u"当前选择的ID:")
        mainLayout.addWidget(self.lab_ids)

        widget_assignid = QWidget(self)
        layout_assignid = QHBoxLayout(widget_assignid)
        layout_assignid.setContentsMargins(0,0,0,0)
        mainLayout.addWidget(widget_assignid)


        self.le_idInput = QSpinBox(parent=widget_assignid)
        layout_assignid.addWidget(self.le_idInput)
        pb_assignid = QPushButton(parent=widget_assignid,text=u"指定ID")
        pb_assignid.clicked.connect(self.assign_group_id)
        layout_assignid.addWidget(pb_assignid)

        mainLayout.addWidget(widgets.QLine.HLine(self))


        pb_convert_to_interactive = MPushButton("转换为交互式毛发")
        pb_convert_to_interactive.clicked.connect(self.convert_to_interactive)
        mainLayout.addWidget(pb_convert_to_interactive)


        mainLayout.addWidget(widgets.QLine.HLine(self))

        self.lle_file_name = widgets.LabelLineEditGroup(text=u"文件名称",parent=self)
        mainLayout.addWidget(self.lle_file_name)


        widget_select_folder = QWidget(self)
        layout_select_folder = QHBoxLayout(widget_select_folder)
        layout_select_folder.setContentsMargins(0,0,0,0)
        layout_select_folder.setSpacing(0)
        mainLayout.addWidget(widget_select_folder)


        self.lle_select_folder = widgets.LabelLineEditGroup(text=u"导出路径",parent=self)
        pbSelectfolder = MClickBrowserFolderToolButton()
        pbSelectfolder.sig_folder_changed.connect(self.lle_select_folder.setText)

        layout_select_folder.addWidget(self.lle_select_folder)
        layout_select_folder.addWidget(pbSelectfolder)


        widget_frame_range = QWidget(self)
        layout_frame_range = QHBoxLayout(widget_frame_range)
        layout_frame_range.setContentsMargins(0,0,0,0)

        mainLayout.addWidget(widget_frame_range)

        layout_frame_range.addWidget(QLabel("开始帧:"))

        self.sb_frame_start = QSpinBox()
        self.sb_frame_start.setMaximum(999999)

        layout_frame_range.addWidget(self.sb_frame_start)

        layout_frame_range.addWidget(QLabel("结束帧:"))


        self.sb_frame_end = QSpinBox()
        self.sb_frame_end.setMaximum(999999)
        layout_frame_range.addWidget(self.sb_frame_end)


        pb_export = MPushButton("导出选中的毛发")
        pb_export.clicked.connect(self.export_groom)

        mainLayout.addWidget(pb_export)
        
    def __setQss(self):
        self.setStyleSheet('''
                    QLabel{
                           font: 12px 'Segoe UI', 'PingFang SC';
                           }
                    QPushButton{
                           font: 12px 'Segoe UI', 'PingFang SC';
                           }
                    QLineEdit{
                           font: 12px 'Segoe UI', 'PingFang SC';
                           }
                            ''')

    def refreshIDs(self):
        for id in self.currentIDs:
            self.lab_ids.setText(u"当前选择的ID:" + str(id) + ',')
    def convert_to_interactive(self):
        cmds.xgmGroomConvert(prefix="")
        xgms = cmds.ls(sl=1)
        for xgm in xgms:
            try:
                id = cmds.getAttr(xgm+".{}".format(self.id_attr_name))
            except:
                id = 0
            name = "{}_splineDescription".format(xgm)
            objs = cmds.ls(name)
            for obj in objs:
                try:
                    cmds.addAttr(obj, longName=self.id_attr_name, attributeType='short', defaultValue=id, keyable=True)
                except:
                    cmds.setAttr(obj+".{}".format(self.id_attr_name),id)
    def assign_group_id(self):
        currentID = self.le_idInput.value()
        print(currentID)
        SLobjects = ML.getSelectNodes(True)
        for obj in SLobjects:
            try:
                cmds.addAttr(obj, longName=self.id_attr_name, attributeType='short', defaultValue=currentID, keyable=True)
            except:
                cmds.setAttr(obj+".{}".format(self.id_attr_name),currentID)
    def export_groom(self):
        fileName = self.lle_file_name.text()
        if fileName == "":
            MMessage.warning(parent=self,text="文件名为空")
            return
        fileName = fileName + ".abc"
        exportPath = self.lle_select_folder.text()
        if exportPath == "":
            MMessage.warning(parent=self,text="路径为空")
            return 
        sFrame = self.sb_frame_start.value()
        eFrame = self.sb_frame_end.value()
        if sFrame > eFrame:
            MMessage.warning(parent=self,text="帧范围设置错误")
            return 
        #临时目录
        tempabc = r"d:\temp.abc"
        # 第一次导出
        SLobjects = ML.getSelectNodes(True)
        ML.exportxgenABC(tempabc,SLobjects,sFrame,eFrame)
        # 反导入回maya
        newnodes = ML.importgroomabc(tempabc)
        crvenodes = []
        for node in newnodes:
           if cmds.nodeType(node) == 'transform' and cmds.listRelatives(node,type = 'nurbsCurve'):
                crvenodes.append(node)
        #从交互式毛发中继承ID信息
        for group_name in crvenodes:
            for obj in SLobjects:
                if group_name.split("|")[1] in obj:
                    try:
                        groom_group_id = cmds.getAttr(obj+".{}".format(self.id_attr_name))
                    except:
                        groom_group_id = 0
                                                      
            # 用组id标记组
            cmds.addAttr(group_name, longName=self.id_attr_name, attributeType='short', defaultValue=groom_group_id, keyable=True)
            # 添加属性范围
            # 强制Maya的alembic将数据导出为GeometryScope::kConstantScope
            cmds.addAttr(group_name, longName='{}_AbcGeomScope'.format(self.id_attr_name), dataType='string', keyable=True)
            cmds.setAttr('{}.{}_AbcGeomScope'.format(group_name, self.id_attr_name), 'con', type='string')

        # 添加ID信息
        # for groom_group_id, group_name in enumerate(crvenodes):

        #     # 获取xgGroom下的曲线
        #     curves = cmds.listRelatives(group_name, ad=True, type='nurbsCurve')

        #     # 用组id标记组
        #     cmds.addAttr(group_name, longName=self.id_attr_name, attributeType='short', defaultValue=groom_group_id, keyable=True)

        #     # 添加属性范围
        #     # 强制Maya的alembic将数据导出为GeometryScope::kConstantScope
        #     cmds.addAttr(group_name, longName='{}_AbcGeomScope'.format(self.id_attr_name), dataType='string', keyable=True)
        #     cmds.setAttr('{}.{}_AbcGeomScope'.format(group_name, self.id_attr_name), 'con', type='string')

        # 导出Groom曲线
        # 将要导出的曲线添加到新的组中,同时将曲线节点新的名字保存在一个列表中
        curgroup = cmds.createNode( 'transform', n='forcurexportgroup' )
        newnamenodes = []
        for crvenode in crvenodes:
            newnamenodes.append(cmds.parent(crvenode,curgroup))
        ML.exportABC_gromm(curgroup,sFrame,eFrame,os.path.join(exportPath,fileName))
        # 删除多余节点
        fordeletelist = newnodes+newnamenodes
        fordeletelist.append(curgroup)
        for node in fordeletelist:
            try:
                cmds.delete(node)
            except:
                pass
    # def mouseMoveEvent(self,a0):
    #     print("done")
    #     return super(XgenTool,self).moveEvent(a0)

def showUI():
    global xgenTool
    xgenTool = XgenTool()
    xgenTool.show(dockable=True)


if __name__ == '__main__':
    from mayaTools import reloadModule
    reloadModule()
    showUI()

    pass





