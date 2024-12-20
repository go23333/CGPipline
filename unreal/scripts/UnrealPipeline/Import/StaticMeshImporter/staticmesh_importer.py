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


from dayu_widgets.push_button import MPushButton
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.switch import MSwitch
from dayu_widgets.label import MLabel
from dayu_widgets.qt import application
from dayu_widgets import dayu_theme


from UnrealPipeline.core.CommonWidget import CommonMenuBar,folderSelectGroup,DateTableView
import UnrealPipeline.core.utilis as UU
import UnrealPipeline.core.UnrealHelper as UH





class StaticMeshImporter(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("静态网格体导入")
        self.resize(600,400)
        self.move(800,400)
        self.__init_ui()
    def __init_ui(self):

        layMain = QtWidgets.QVBoxLayout()   #定义主布局
        menubar = CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        layMain.menuBar = menubar

        self.folderSelectGroup = folderSelectGroup("网格体文件路径:") #定义路径选择组

        self.wCamera = DateTableView(UU.CameraHeader)  #定义相机数据表格

        context_menu = self.wCamera.MakeContexMenu()   # 获取相机表格的上下文菜单并自定义
        maImportSelectedItems = context_menu.addAction("导入选中项目")
        maImportSelectedItems.triggered.connect(
            functools.partial(self.importCameras,True)
            )
        self.folderSelectGroup.setOnTextChanged(self.wCamera.fetchCamera)        # 文字框改变时刷新

        layImport = QtWidgets.QHBoxLayout()  #用于防止导入按钮的布局
        btnImport = MPushButton("导入模型")
        btnImport.clicked.connect(
            functools.partial(self.importCameras,False)
            )
        

        # self.cbSceneName = MComboBox()

        self.cbSceneName = QtWidgets.QComboBox()
        self.cbSceneName.addItems(UH.getAllScenesName())
        self.cbSceneName.setMinimumWidth(100)
        self.cbSceneName.setMinimumHeight(30)
        self.cbSceneName.setEditable(True)

        self.cbSceneName.setStyleSheet(
                                    "QComboBox{"
                                    "border-style: solid;" 
                                    "border-width: 1px;" 
                                    "border-color: #222222;"
                                    "}"
                                    "QComboBox QAbstractItemView{"
                                    "border-radius:0px 0px 5px 5px;"
                                    "}"
                                    )
        
        # self.cbSceneName=MLineEdit().medium()
        # self.cbSceneName.setPlaceholderText(self.tr("输入资产文件夹名称,不输入则使用网格自身名称"))
        # self.cbSceneName.setMinimumWidth(280)

        self.switch = MSwitch()
        self.switch.setChecked(False)
        switch_lay = QtWidgets.QFormLayout()
        switch_lay.addRow(MLabel("导入时是否创建关卡"), self.switch)    #关卡创建开关
        


        layImport.addWidget(self.cbSceneName,alignment=QtCore.Qt.AlignLeft)
        layImport.addLayout(switch_lay,alignment=QtCore.Qt.AlignLeft)
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
        UH.importStaticmeshs(waitImportedQueue,self.cbSceneName.currentText(),self.switch.isChecked())

def Start():
    with application() as app:
        global w
        w = StaticMeshImporter()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()
