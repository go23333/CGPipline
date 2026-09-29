#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.8
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################

from Qt import QtWidgets,QtCore
import functools
import unreal
import importlib


from dayu_widgets.push_button import MPushButton
from dayu_widgets.switch import MSwitch
from dayu_widgets.label import MLabel
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.qt import application
from dayu_widgets import dayu_theme


from UnrealPipeline.core.CommonWidget import CommonMenuBar,folderSelectGroup,DateTableView
import UnrealPipeline.core.utilis as UU
import UnrealPipeline.core.Config as UC
import UnrealPipeline.core.UnrealHelper as UH
importlib.reload(UH)





class CameraImporter(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.start_offset=0
        self.end_offset=1
        self.setWindowTitle(u"相机导入")
        self.resize(600,400)
        self.move(800,400)
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()   #定义主布局

        menubar = CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        layMain.menuBar = menubar
        
        self.folderSelectGroup = folderSelectGroup(u"相机路径:") #定义路径选择组

        self.wCamera = DateTableView(UU.CameraHeader)  #定义相机数据表格

        context_menu = self.wCamera.MakeContexMenu()   # 获取相机表格的上下文菜单并自定义
        maImportSelectedItems = context_menu.addAction(u"导入选中项目")
        maImportSelectedItems.triggered.connect(
            functools.partial(self.importCameras,True)
            )
        self.folderSelectGroup.setOnTextChanged(self.wCamera.fetchCamera)        # 文字框改变时刷新

        self.offset_switch = MSwitch()
        self.offset_switch.setChecked(False)
        self.offset_switch.toggled.connect(self.offsetChange)
        offset_switch_lay = QtWidgets.QFormLayout()
        offset_switch_lay.addRow(MLabel("是否使用偏移帧"), self.offset_switch)

        layImport = QtWidgets.QHBoxLayout()  #用于防止导入按钮的布局
        btnImport = MPushButton(u"导入相机")
        btnImport.clicked.connect(
            functools.partial(self.importCameras,False)
            )
        layImport.addLayout(offset_switch_lay)
        layImport.addWidget(btnImport,alignment=QtCore.Qt.AlignRight)


        # 依次添加布局
        layMain.addLayout(self.folderSelectGroup)
        layMain.addWidget(self.wCamera)
        layMain.addLayout(layImport)
        self.setLayout(layMain)
    def closeEvent(self, event):
        return super().closeEvent(event)
    def showEvent(self, event):
        return super().showEvent(event)
    def offsetChange(self):
        if self.offset_switch.isChecked():
            self.start_offset=UC.globalConfig.get().start_offset
            self.end_offset=UC.globalConfig.get().end_offset
        else:
            self.start_offset=0
            self.end_offset=1
        print(self.start_offset,self.end_offset)
    def importCameras(self,selected):
        waitImportedQueue = []
        if selected:
            for name in self.wCamera.getSelectNames():
                for data in self.wCamera.datas:
                    if data["name"] == name:
                        waitImportedQueue.append(data)
        else:
            for data in self.wCamera.datas:
                if not data["imported"]:
                    waitImportedQueue.append(data)
        UH.importCameras(waitImportedQueue, self.start_offset, self.end_offset)


def Start():
    with application() as app:
        global w
        w = CameraImporter()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()
