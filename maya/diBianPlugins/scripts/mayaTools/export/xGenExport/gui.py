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

        pb_export_static_groom = MPushButton("导出静态毛发")
        pb_export_static_groom.clicked.connect(self.export_static_groom)
        mainLayout.addWidget(pb_export_static_groom)


        mainLayout.addWidget(widgets.QLine.HLine(self))


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


        pb_export_groom_cache = MPushButton("导出选中的毛发缓存")
        pb_export_groom_cache.clicked.connect(self.export_groom_cache)

        mainLayout.addWidget(pb_export_groom_cache)
        
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
    def export_static_groom(self):
        fileName = self.lle_file_name.text()
        if fileName == "":
            MMessage.warning(parent=self,text="文件名为空")
            return
        fileName = fileName + ".abc"
        exportPath = self.lle_select_folder.text()
        if exportPath == "":
            MMessage.warning(parent=self,text="路径为空")
            return 
        ML.export_static_gromm(os.path.join(exportPath,fileName))
    def assign_group_id(self):
        currentID = self.le_idInput.value()
        print(currentID)
        SLobjects = ML.getSelectNodes(True)
        for obj in SLobjects:
            try:
                cmds.addAttr(obj, longName=self.id_attr_name, attributeType='short', defaultValue=currentID, keyable=True)
            except:
                cmds.setAttr(obj+".{}".format(self.id_attr_name),currentID)
    
    def export_groom_cache(self):
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
        sl = cmds.ls(sl=1)
        if sl == []:
            MMessage.warning(parent=self,text="未选中任何对象")
        ML.export_groom_guide_cache(sl[0],os.path.join(exportPath,fileName),sFrame,eFrame)
        


def showUI():
    global xgenTool
    xgenTool = XgenTool()
    xgenTool.show(dockable=True)


if __name__ == '__main__':
    from mayaTools import reloadModule
    reloadModule()
    showUI()

    pass





