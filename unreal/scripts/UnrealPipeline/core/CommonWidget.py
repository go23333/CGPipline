#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 20240828
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################


from Qt import QtWidgets,QtCore

from Qt.QtGui import QPixmap,QPainter,QColor
from Qt.QtCore import QRect

from dayu_widgets.label import MLabel
from dayu_widgets.spin_box import MSpinBox,MDoubleSpinBox
from dayu_widgets.item_view import MTableView,MTableModel
from dayu_widgets.item_model import MSortFilterModel
from dayu_widgets.line_edit import MClickBrowserFolderToolButton, MLineEdit

from dayu_widgets import dayu_theme
from dayu_widgets.message import MMessage
from dayu_widgets.loading import MLoadingWrapper
import os
from dayu_widgets.menu import MMenu
import functools


import UnrealPipeline.core.utilis as UU
from Qt.QtWidgets import QMainWindow,QApplication,QWidget


class FetchCameraDataWorker(QtCore.QThread):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.OnFinished = None
        self.ScanPath = None
    def run(self):
        cameraDatas = UU.getFilesDataFrompath(self.ScanPath,"fbx")
        if self.OnFinished:
            self.OnFinished(cameraDatas)



class CommonMenuBar(QtWidgets.QMenuBar):
    def __init__(self,parent=None):
        from UnrealPipeline.Settings.Settings import Start
        super().__init__(parent)
        menuEdit = self.addMenu("编辑")
        aSetting = menuEdit.addAction("设置")
        aSetting.triggered.connect(Start) 
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
        super().__init__(parent=None)
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



class folderSelectGroup(QtWidgets.QHBoxLayout):
    def __init__(self,title):
        super().__init__(None)
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
        super().__init__(parent=None)
        self.dataModle = MTableModel() #数据模型
        self.dataModle.set_header_list(HeaderData) #设置数据模型表头
        self.datas = [] #数据列表
        layMain = QtWidgets.QVBoxLayout() #主布局

        self.tvMain = MTableView(size=dayu_theme.medium, show_row_count=True) #表格控件

        self.ModelSort = MSortFilterModel()
        self.ModelSort.setSourceModel(self.dataModle)
        self.tvMain.setModel(self.ModelSort)
        self.tvMain.header_view.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.tvMain.header_view.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.ViewWrapper = MLoadingWrapper(widget=self.tvMain,loading=False)
        # leSearch = MLineEdit().search().small()
        # leSearch.textChanged.connect(ModelSort.set_search_pattern)
        # layMain.addWidget(leSearch)
        layMain.addWidget(self.ViewWrapper)
        self.setLayout(layMain)
    def fetchCamera(self,path):
        path = os.path.normpath(path)
        # 判断该路径是否合法
        if not (UU.isPathValid(path)):
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
    def getSelectNames(self):
        selectedNames = set()
        currentRow = -1
        for item in self.tvMain.selectedIndexes():
            if item.row() != currentRow:
                currentRow = item.row()
                selectedNames.add(item.data())
        return(list(selectedNames))
    def MakeContexMenu(self):
        self.ContexMenu =  MMenu(parent=self.tvMain)  #表格控件的上下文菜单
        self.tvMain.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tvMain.customContextMenuRequested.connect(self.showContexMenu)
        return self.ContexMenu
    def showContexMenu(self,pos):
        self.ContexMenu.exec_(self.tvMain.mapToGlobal(pos))




class CommonMainWindow(QMainWindow):
    def __init__(self, parent = None)->None:
        super().__init__(parent)
        self.__initMenu()
    def MoveToCenter(self):
        desktop_width = QApplication.desktop().width()/4
        desktop_height = QApplication.desktop().height()/2
        self.move(int(desktop_width-self.width()/2.0),int(desktop_height-self.height()/2.0))
    def __initMenu(self):
        menuBar = CommonMenuBar()
        self.setMenuBar(menuBar)
        self.menuBar = menuBar


def scaleMap(width:int,height:int,mapPath:str)-> QPixmap:
    original_pixelmap = QPixmap(mapPath)

    scaled_pixmap = QPixmap(width,height)
    scaled_pixmap.fill(QColor(80,80,80,0))


    painter = QPainter(scaled_pixmap)
    
    try:
        scaled_factor = min(width / float(original_pixelmap.width()+0.1), height / float(original_pixelmap.height()+0.1))
    except ZeroDivisionError:
        scaled_factor = 0.3
        pass

    scaled_size = original_pixelmap.size() * scaled_factor

    x = (width - scaled_size.width()) / 2
    y = (height - scaled_size.height()) / 2
    
    painter.drawPixmap(QRect(int(x), int(y), scaled_size.width(), scaled_size.height()), original_pixelmap)

    painter.end()

    return scaled_pixmap