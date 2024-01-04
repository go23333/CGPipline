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
from dayu_widgets.label import MLabel
from dayu_widgets import dayu_theme
from dayu_widgets.item_model import MSortFilterModel
from dayu_widgets.item_view import MTableModel, MTableView
from dayu_widgets.line_edit import MClickBrowserFolderToolButton, MLineEdit
from dayu_widgets.loading import MLoadingWrapper
from dayu_widgets.menu import MMenu
from dayu_widgets.message import MMessage
from dayu_widgets.spin_box import MDoubleSpinBox, MSpinBox
from dayu_widgets.item_view import MListView
from Qt import QtCore, QtWidgets
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
import uGlobalConfig as UG
reload (UG)


#定义一些共享的widget



class FetchCameraDataWorker(QtCore.QThread):
    def __init__(self,parent=None):
        super(FetchCameraDataWorker,self).__init__(parent)
        self.OnFinished = None
        self.ScanPath = None
    def run(self):
        cameraDatas = UC.getFilesDataFrompath(self.ScanPath,"fbx")
        if self.OnFinished:
            self.OnFinished(cameraDatas)


# 定义一些通用的Widget
class folderSelectGroup(QtWidgets.QHBoxLayout):
    def __init__(self,title):
        super(folderSelectGroup,self).__init__(None)
        self.addWidget(MLabel(title), 0)
        btnBrowserFolder = MClickBrowserFolderToolButton()
        self.leFolderPath = MLineEdit()
        btnBrowserFolder.sig_folder_changed.connect(self.leFolderPath.setText)
        self.addWidget(self.leFolderPath,1)
        self.addWidget(btnBrowserFolder,2)
    def getFolderPath(self):
        return(self.leFolderPath.text())
    def setLineEditText(self,text):
        self.leFolderPath.setText(text)
    def setOnTextChanged(self,onTextChanged):
        self.leFolderPath.textChanged.connect(onTextChanged)

class DateTableView(QtWidgets.QWidget):
    def __init__(self,HeaderData):
        super(DateTableView,self).__init__(parent=None)
        self.dataModle = MTableModel() #数据模型
        self.dataModle.set_header_list(HeaderData) #设置数据模型表头
        self.datas = [] #数据列表
        layMain = QtWidgets.QVBoxLayout() #主布局

        self.tvMain = MTableView(size=dayu_theme.medium, show_row_count=True) #表格控件

        ModelSort = MSortFilterModel()
        ModelSort.setSourceModel(self.dataModle)
        self.tvMain.setModel(ModelSort)
        self.tvMain.header_view.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tvMain.header_view.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ViewWrapper = MLoadingWrapper(widget=self.tvMain,loading=False)
        # leSearch = MLineEdit().search().small()
        # leSearch.textChanged.connect(ModelSort.set_search_pattern)
        # layMain.addWidget(leSearch)
        layMain.addWidget(self.ViewWrapper)
        self.setLayout(layMain)
    def fetchCamera(self,path):
        path = UC.normalizePath(path)
        # 判断该路径是否合法
        if not (UC.isPathValid(path)):
            MMessage.error(parent=self,text="该路径不合法")
            return False
        # 后台刷新路径
        fetchCameraDataWorker = FetchCameraDataWorker(self)
        fetchCameraDataWorker.OnFinished = self.onFinished
        fetchCameraDataWorker.ScanPath = path
        fetchCameraDataWorker.started.connect(functools.partial(self.ViewWrapper.set_dayu_loading,True))
        fetchCameraDataWorker.finished.connect(functools.partial(self.ViewWrapper.set_dayu_loading,False))
        fetchCameraDataWorker.start()
    def onFinished(self,datas):
        self.datas = datas
        self.dataModle.set_data_list(datas)
    def getSelectedRows(self):
        selectedRows = set()
        for item in self.tvMain.selectedIndexes():
            selectedRows.add(item.row())
        return(list(selectedRows))
    def MakeContexMenu(self):
        self.ContexMenu =  MMenu(parent=self.tvMain)  #表格控件的上下文菜单
        self.tvMain.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tvMain.customContextMenuRequested.connect(self.showContexMenu)
        return self.ContexMenu
    def showContexMenu(self,pos):
        self.ContexMenu.exec_(self.tvMain.mapToGlobal(pos))

class CommonMenuBar(QtWidgets.QMenuBar):
    def __init__(self,parent=None):
        super(CommonMenuBar,self).__init__(parent)
        menuEdit = self.addMenu("编辑")
        aSetting = menuEdit.addAction("设置")
        menuHelp = self.addMenu("帮助")
        aHelp = menuHelp.addAction("打开帮助页面")


class SpinBoxWithLabel(QtWidgets.QWidget):
    def __init__(self,Text,layout,valueType,decimals,maxValue,minValue,value,step):
        """
        创建一个附带标签的数字调整框

        Parameters:
        - Text(str):标签的文字
        - layout(int):排布的方式,0为水平排布,1为竖直排布
        - valueType(int)数值的类型,0为int,1为float
        - decimals(int):小数点位数
        - maxValue(int):最大值
        - minValue(int):最小值
        - value(int):默认值
        - step(int):步长
        Returns:
        None
        """
        super(SpinBoxWithLabel,self).__init__(parent=None)
        if layout==0:
            layMain = QtWidgets.QHBoxLayout()
        elif layout==1:
            layMain = QtWidgets.QVBoxLayout()
        if valueType==0:
            self.spinBox = MSpinBox()
        elif valueType==1:
            self.spinBox = MDoubleSpinBox()

        self.spinBox.setMaximum(maxValue)   
        self.spinBox.setMinimum(minValue) 
        self.spinBox.setDecimals(decimals)
        self.spinBox.setSingleStep(step)
        self.spinBox.setValue(value)
        layMain.addWidget(MLabel(Text))
        layMain.addWidget(self.spinBox)

        self.setLayout(layMain)
    def getValue(self):
        return (self.spinBox.value())
    def setOnValueChanged(self,fun):
        self.spinBox.valueChanged.connect(fun)



# # CameraImporter UI
class CameraImporter(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(CameraImporter,self).__init__(parent)
        self.setWindowTitle("相机导入")
        self.resize(600,400)
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()   #定义主布局

        menubar = CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        
        self.folderSelectGroup = folderSelectGroup("相机路径:") #定义路径选择组

        self.wCamera = DateTableView(UT.CameraHeader)  #定义相机数据表格

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
        UU.importCameras(waitImportedQueue)

# Staticmesh Importer UI
class StaticMeshImporter(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(StaticMeshImporter,self).__init__(parent)
        self.setWindowTitle("静态网格体导入")
        self.resize(600,400)
        self.__init_ui()
    def __init_ui(self):

        layMain = QtWidgets.QVBoxLayout()   #定义主布局
        menubar = CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)

        self.folderSelectGroup = folderSelectGroup("网格体文件路径:") #定义路径选择组

        self.wCamera = DateTableView(UT.CameraHeader)  #定义相机数据表格

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
        menubar = CommonMenuBar()  #定义菜单栏
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
        self.wNearClip = SpinBoxWithLabel("近裁剪面:",0,1,6,1000.0,0.00001,0.00001,0.00001)
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
        menubar = CommonMenuBar()  #定义菜单栏
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



class Settings(QtWidgets.QWidget):
    def __init__(self):
        super(Settings,self).__init__(parent=None)
        self.setWindowTitle("全局设置")
        self.resize(600,400)
        self.__init_ui()
        self.loadConfig()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()  #定义Q主布局
        layMain.setSpacing(5)
        menubar = CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        # input
        layMacroInput = QtWidgets.QHBoxLayout()
        self.leMacroInput = MLineEdit()
        self.leMacroInput.textChanged.connect(self.applyMacro)

        layMacroInput.addWidget(MLabel("宏输入:"))
        layMacroInput.addWidget(self.leMacroInput)
        CurrentMacro = ""
        for macro in UC.CameraPathMacros:
            CurrentMacro = CurrentMacro + " | " + macro
        # NOTE output
        layMacroOutput = QtWidgets.QHBoxLayout()
        self.leMacroOutput = MLineEdit()
        self.leMacroOutput.setEnabled(False)
        layMacroOutput.addWidget(MLabel("宏输出:"))
        layMacroOutput.addWidget(self.leMacroOutput)
        # NOTE add to main layout
        layMain.addWidget(MLabel("相机导入路径宏设置:").h4(),alignment=QtCore.Qt.AlignTop)
        layMain.addWidget(MLabel("示例相机名称:Ep000_sc003_001_001_131_cam"),alignment=QtCore.Qt.AlignTop)
        layMain.addLayout(layMacroInput)
        layMain.addWidget(MLabel(f"当前可以使用的宏有:{CurrentMacro}"))
        layMain.addLayout(layMacroOutput)
        layMain.addSpacerItem(QtWidgets.QSpacerItem(20,20,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding))
        self.setLayout(layMain)
    def loadConfig(self):
        self.leMacroInput.setText(UG.globalConfig.CameraImportPathPatten)
    def applyMacro(self):
        parseResult = UC.parseCameraName("Ep000_sc003_001_001_131_cam")
        if parseResult:
            result = UC.applyMacro(self.leMacroInput.text(),parseResult)
            self.leMacroOutput.setText(UC.normalizePath(result))

if __name__ == "__main__":
    pass


