#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################
# 导入第三方库
from Qt import QtWidgets,QtCore

from dayu_widgets.push_button import MPushButton

from dayu_widgets.combo_box import MComboBox

from dayu_widgets.check_box import MCheckBox
from dayu_widgets.divider import MDivider
import functools
import os
from importlib import reload
#导入自定义库
import uUnreal as UU
reload(UU)
import CGUtils.uCommon as UC
reload(UC)
import CGUtils.uTemplates as UT
reload(UT)
import CGUtils.uGlobalConfig as UG
reload (UG)
import CGUtils.uwidgets as W
reload(W)



# # CameraImporter UI
class CameraImporter(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(CameraImporter,self).__init__(parent)
        self.setWindowTitle("相机导入")
        self.resize(600,400)
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()   #定义主布局

        menubar = W.CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        
        self.folderSelectGroup = W.folderSelectGroup("相机路径:") #定义路径选择组

        self.wCamera = W.DateTableView(UT.CameraHeader)  #定义相机数据表格

        context_menu = self.wCamera.MakeContexMenu()   # 获取相机表格的上下文菜单并自定义
        maImportSelectedItems = context_menu.addAction("导入选中项目")
        maImportSelectedItems.triggered.connect(
            functools.partial(self.importCameras,True)
            )
        self.folderSelectGroup.setOnTextChanged(self.wCamera.fetchCamera)        # 文字框改变时刷新

        layImport = QtWidgets.QHBoxLayout()  #用于防止导入按钮的布局
        btnImport = MPushButton("导入相机")
        btnImport.clicked.connect(
            functools.partial(self.importCameras,False)
            )
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
            for row in self.wCamera.getSelectedRows():
                waitImportedQueue.append(self.wCamera.datas[row])
            pass
        else:
            for data in self.wCamera.datas:
                if not data["imported"]:
                    waitImportedQueue.append(data)
        print (waitImportedQueue)

# Staticmesh Importer UI
class StaticMeshImporter(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(StaticMeshImporter,self).__init__(parent)
        self.setWindowTitle("静态网格体导入")
        self.resize(600,400)
        self.__init_ui()
    def __init_ui(self):

        layMain = QtWidgets.QVBoxLayout()   #定义主布局
        menubar = W.CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)

        self.folderSelectGroup = W.folderSelectGroup("网格体文件路径:") #定义路径选择组

        self.wCamera = W.DateTableView(UT.CameraHeader)  #定义相机数据表格

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
        cbSceneName = MComboBox()
        cbSceneName.setDisabled(True)


        layImport.addWidget(cbSceneName,alignment=QtCore.Qt.AlignLeft)
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
            for row in self.wCamera.getSelectedRows():
                waitImportedQueue.append(self.wCamera.datas[row])
            pass
        else:
            for data in self.wCamera.datas:
                if not data["imported"]:
                    waitImportedQueue.append(data)
        print (waitImportedQueue)


#灯光常用工具
class LightTools(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(LightTools,self).__init__(parent)
        self.setWindowTitle("灯光工具")
        self.resize(300,400)
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()   #定义主布局
        menubar = W.CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        # 添加一些按钮
        pbAutoID = MPushButton("自动ID(包括植物)")
        pbAutoID.clicked.connect(self.autoID)
        pbPoolSize = MPushButton("无限纹理流送池")
        pbPoolSize.clicked.connect(self.poolSize)
        pbPopEmmissive = MPushButton("弹出自发光材质")
        pbPopEmmissive.clicked.connect(self.popEmmissive)
        pbOpenImportCameraUI = MPushButton("打开相机导入窗口")
        pbOpenImportCameraUI.clicked.connect(self.openImportCameraUI)
        self.wNearClip = W.SpinBoxWithLabel("近裁剪面:",0,1,6,1000.0,0.00001,0.00001,0.00001)
        self.wNearClip.setOnValueChanged(self.nearClip)
        layMain.addWidget(pbAutoID)
        layMain.addWidget(pbPoolSize)
        layMain.addWidget(pbPopEmmissive)
        layMain.addWidget(pbOpenImportCameraUI)
        layMain.addWidget(self.wNearClip,alignment=QtCore.Qt.AlignTop)
        self.setLayout(layMain)
    def autoID(self):
        UU.autoID()
        pass
    def poolSize(self):
        UU.poolSize()
        pass
    def popEmmissive(self):
        UU.popEmmissive()
        pass
    def openImportCameraUI(self):
        UU.openImportCameraUI()
        pass
    def nearClip(self):
        value = self.wNearClip.getValue()
        UU.nearClip(value)
        pass


# 地编工具
class LevelDesignTool(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(LevelDesignTool,self).__init__(parent)
        self.setWindowTitle("地编工具")
        self.resize(300,400)
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()   #定义主布局
        menubar = W.CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        # 添加一些按钮
        pbOpenSelectedFoliage = MPushButton(text="打开选中植物窗口")
        pbOpenSelectedFoliage.clicked.connect(self.openSelectedFoliage)
        pbConvertFoliageToStaticMesh = MPushButton(text="转换植物为静态网格体")
        pbConvertFoliageToStaticMesh.clicked.connect(self.convertFoliageToStaticMesh)
        pbEnalbeFullPercisionUV = MPushButton(text="开启全精度UV")
        pbEnalbeFullPercisionUV.clicked.connect(self.enableFullPercisionUV)
        pbSimpleLight = MPushButton(text="简单光照")
        pbSimpleLight.clicked.connect(self.simpleLight)
        pbSelectSimilarActor = MPushButton(text="选择相似Actor")
        pbSelectSimilarActor.clicked.connect(self.selectSimilarActor)

        layBreakBlueprint = QtWidgets.QHBoxLayout()
        self.cboxDeleteOriginalBlueprint = MCheckBox(text="删除原来蓝图")
        pbBreakBlueprint = MPushButton(text="执行蓝图拆分")
        pbBreakBlueprint.clicked.connect(self.breakBlueprint)
        layBreakBlueprint.addWidget(self.cboxDeleteOriginalBlueprint)
        layBreakBlueprint.addWidget(pbBreakBlueprint)


        layMain.addWidget(pbOpenSelectedFoliage)
        layMain.addWidget(pbConvertFoliageToStaticMesh)
        layMain.addWidget(pbEnalbeFullPercisionUV)
        layMain.addWidget(pbSimpleLight)
        layMain.addWidget(pbSelectSimilarActor)
        layMain.addWidget(MDivider("蓝图拆分工具"),alignment=QtCore.Qt.AlignTop)
        layMain.addLayout(layBreakBlueprint)
        self.setLayout(layMain)
    def openSelectedFoliage(self):
        UU.openSelectedFoliage()
    def convertFoliageToStaticMesh(self):
        UU.FoliageToSMActor()
    def enableFullPercisionUV(self):
        UU.enableFullPercisionUV()
    def simpleLight(self):
        UU.simpleLight()
    def selectSimilarActor(self):
        UU.selectSimilarActor()
    def breakBlueprint(self):
        UU.breakBlueprint(self.cboxDeleteOriginalBlueprint.isChecked())

if __name__ == "__main__":
    pass


