#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################
import functools
from importlib import reload

from dayu_widgets import dayu_theme
from dayu_widgets.item_model import MSortFilterModel
from dayu_widgets.item_view import MTableModel, MTableView
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MClickBrowserFolderToolButton, MLineEdit
from dayu_widgets.loading import MLoadingWrapper
from dayu_widgets.menu import MMenu
from dayu_widgets.message import MMessage
from dayu_widgets.spin_box import MDoubleSpinBox, MSpinBox
from Qt import QtCore, QtWidgets

# 导入自定义的模块
import CGUtils.uCommon as UC
reload(UC)





class FetchCameraDataWorker(QtCore.QThread):
    def __init__(self,parent=None):
        super(FetchCameraDataWorker,self).__init__(parent)
        self.OnFinished = None
        self.ScanPath = None
    def run(self):
        UU.unrealLog("相机导入插件","开始扫描目录")
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
            UU.unrealLogError("相机导入插件","路径输入不合法")
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