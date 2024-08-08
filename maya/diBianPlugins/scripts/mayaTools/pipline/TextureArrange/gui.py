# -*- coding: utf-8 -*-

from Qt import QtWidgets,QtCore
from Qt.QtCore import QThread,Signal,Slot,QObject
from Qt.QtWidgets import QMenu,QAction
from Qt.QtGui import QCursor
from dayu_widgets.item_view import MTreeView
from dayu_widgets.item_model import MTableModel
from dayu_widgets.item_model import MSortFilterModel
from dayu_widgets.message import MMessage
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MClickBrowserFolderToolButton,MLineEdit
from dayu_widgets.push_button import MPushButton
from dayu_widgets.progress_bar import MProgressBar
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from dayu_widgets.menu import MMenu
from dayu_widgets.combo_box import MComboBox
from dayu_widgets import dayu_theme
import mayaTools.core.pathLibrary as PL
import mayaTools.core.mayaLibrary as ML
import os
import pymel.core as pm
import copy



class WorkerThread(QThread):
    update_signal = Signal(float)
    finish_signal = Signal()
    def __init__(self):
        super(WorkerThread,self).__init__()
        self.funToRun = None
        self.arg = []
    def run(self):
        if self.funToRun == None:
            return
        self.funToRun(self.arg,self.update_signal,self.finish_signal)




def score_color(score, y):
    if score == 0:
        return dayu_theme.error_color
    elif score == 1:
        return dayu_theme.warning_color
    elif score == 2:
        return dayu_theme.success_color
    

header_list = [

    {
        "label":"Name",
        "key"  : "name",
        "width" : 400,
    },
    {
        "label":"Path",
        "key"  : "path",
        "width" : 500,
    },
    {
        "label":"Exist",
        "key"  : "exist",
        "display": "",
        "width" : 15,
        "bg_color" : score_color,
    },
    {
        "label":"Layer",
        "key"  : "layer",
        "width" : 0,
    },

]


class TextureArrange(MayaQWidgetDockableMixin,QtWidgets.QTabWidget):
    def __init__(self):
        super(TextureArrange,self).__init__()
        self.setWindowTitle(u"贴图整理工具")
        self.winWidth = 1000
        self.winHeight = 800
        self.resize(self.winWidth,self.winHeight)

        self.__init_ui()



    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()
        layMain.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.model_1 = MTableModel()
        self.model_1.set_header_list(header_list)
        model_sort = MSortFilterModel()
        model_sort.setSourceModel(self.model_1)
        self.tvFileNodes = MTreeView()
        self.tvFileNodes.clicked.connect(self.onTreeViewClicked)
        self.tvFileNodes.setModel(model_sort)
        self.tvFileNodes.setHeaderHidden(1)
        model_sort.set_header_list(header_list)
        self.tvFileNodes.set_header_list(header_list)
        self.tvFileNodes.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tvFileNodes.customContextMenuRequested.connect(self.__createRightMenu)



        self.ColumWidths = []
        for i in range(len(header_list)):
            self.ColumWidths.append(self.tvFileNodes.columnWidth(i))
        self.ColumScaleRate = [0.8,1.2,0.01,0.0]

        self.treeDatas = []
        self.model_1.set_data_list(self.treeDatas)

        self.tvFileNodes.setSizeAdjustPolicy(
                QtWidgets.QAbstractScrollArea.AdjustToContents)

        laySelectDir = QtWidgets.QHBoxLayout()
        pbSelectTextureDir = MClickBrowserFolderToolButton()
        self.leNewTextureDir = MLineEdit()
        pbSelectTextureDir.sig_folder_changed.connect(self.leNewTextureDir.setText)
        laySelectDir.addWidget(MLabel(u"选择路径"))
        laySelectDir.addWidget(self.leNewTextureDir)
        laySelectDir.addWidget(pbSelectTextureDir)



        layButtons = QtWidgets.QHBoxLayout()
        pbMove = MPushButton(u"复制贴图")
        pbSetPath= MPushButton(u"设置路径")
        layButtons.addWidget(pbMove)
        layButtons.addWidget(pbSetPath)
        pbSetPath.clicked.connect(self.SetPath)
        pbMove.clicked.connect(self.copyTextures)



        self.progress = MProgressBar()
        layMain.addWidget(self.tvFileNodes)
        layMain.addLayout(laySelectDir)
        layMain.addLayout(layButtons)
        layMain.addWidget(self.progress)
        self.setLayout(layMain)
    def __createRightMenu(self):
        self.TreeViewRightMenu = QMenu(self)
        actions = []
        if self.getSelectedRow(1):
           action_SelectMesh = QAction(u"选择相关的模型",self)
           action_SelectMesh.triggered.connect(self.selectRelevantMesh)
           actions.append(action_SelectMesh)
        self.TreeViewRightMenu.addActions(actions)
        self.TreeViewRightMenu.popup(QCursor().pos())
    def selectRelevantMesh(self):
        selectRow = self.getSelectedRow(1)
        if not selectRow:
            return
        selectNode = pm.PyNode(selectRow[0])
        pm.select(ML.GetMeshBaseFileNode(selectNode))


    def onTreeViewClicked(self,arg):
        rowData = self.getSelectedRow(1)
        if rowData:
            pm.select(pm.PyNode(rowData[0]))
    def RefreshList(self):
        self.treeDatas = []
        textureNode = ML.GetAllTextureNodes()
        for node in textureNode:
            rootNode = self.getTreeData(node.TextureDir)
            nodeData = dict(path='',exist=0,children=[],name=node.nodeName,layer=1)
            for item in node.TextureList:
                if item["exist"]:
                    exist = 2
                else:
                    exist = 0
                nodeData['children'].append(dict(path=item["path"],exist=exist,children=[],name=os.path.basename(item["path"]),layer=2))
            nodeData = self.setDataColor(nodeData)
            rootNode['children'].append(nodeData)
            rootNode = self.setDataColor(rootNode)
        self.model_1.set_data_list(self.treeDatas)
    def setDataColor(self,datas):
        flag = True
        flag1 = False
        for data in datas["children"]:
            flag = flag and data['exist'] == 2
            flag1 = flag1 or data['exist'] == 2
        if flag:
            datas["exist"] = 2
        elif flag1:
            datas["exist"] = 1
        else:
            datas["exist"] = 0
        return datas
    def getTreeData(self,dir):
        for treedata in self.treeDatas:
            if treedata['name'] == dir:
                return treedata
        treedata = dict(exist=0,name=dir,path = '',children=[],layer = 0)
        self.treeDatas.append(treedata)
        return copy.copy(treedata)
    def showEvent(self,arg):
        self.RefreshList()
        return super(TextureArrange,self).showEvent(arg)
    def resizeEvent(self,arg):
        scale = float(self.size().width())/float(self.winWidth)
        for i in range(len(self.ColumWidths)):
            newWidth = self.ColumWidths[i]*scale
            newWidth = newWidth * self.ColumScaleRate[i] + (1-self.ColumScaleRate[i]) * self.ColumWidths[i]
            self.tvFileNodes.setColumnWidth(i,newWidth)
        return super(TextureArrange,self).resizeEvent(arg)
    def SetPath(self):
        newRootDir = self.leNewTextureDir.text()
        if newRootDir == "":
            MMessage.warning(parent=self,text="路径为空")
            return
        rootDir = self.getSelectedRow(0)[0]
        if not rootDir:
            return
        textureNode = ML.GetAllTextureNodes()
        for node in textureNode:
            if node.TextureDir!= rootDir:
                continue
            TextureName = os.path.basename(node.TextureValue)
            newTextureName = os.path.join(newRootDir,TextureName)
            if node.nodeType == 'file':
                attrName = "fileTextureName"
            else:
                attrName = "tex0"
            pm.PyNode(node.nodeName).setAttr(attrName,newTextureName)
        self.RefreshList()
        MMessage.info(parent=self,text="路径设置成功")
    def getSelectedRow(self,layer):
        #获取当前选择的index
        arg = self.tvFileNodes.selectedIndexes()
        #判断是否选择节点
        if arg == []:
            MMessage.warning(parent=self,text="未选择任何内容")
            return False
        arg = arg[0]
        if arg.sibling(arg.row(),3).data() != layer:
            return False
        return [arg.sibling(arg.row(),i).data() for i in range(len(header_list))]
    @Slot()
    def copyTextures(self):
        newRootDir = self.leNewTextureDir.text()#获取设置的路径
        #判断路径是否为空
        if newRootDir == "":
            MMessage.warning(parent=self,text="路径为空")
            return
        rootDir = self.getSelectedRow(0)[0]
        if not rootDir:
            return
        textureNode = ML.GetAllTextureNodes()
        texWaitToCopy = []
        for node in textureNode:
            if node.TextureDir!= rootDir:
                continue
            for item in node.TextureList:
                if item['exist']:
                    texWaitToCopy.append(item['path'])
        self.thread = WorkerThread()
        self.thread.funToRun = self.copyTexturesThread
        self.thread.arg = [texWaitToCopy,newRootDir]
        self.thread.update_signal.connect(self.UpdataProgress)
        self.thread.finish_signal.connect(self.onCopyTextureFinsihed)
        self.thread.start()
    def copyTexturesThread(self,arg,update_signal,finish_signal):
        textures = arg[0]
        newDir = arg[1]
        for i in range(len(textures)):
            PL.CopyFileToDir(textures[i],newDir)
            update_signal.emit((i+1)*100/len(textures))
        finish_signal.emit()
    @Slot(float)
    def UpdataProgress(self,value):
        self.progress.setValue(value)
    @Slot()
    def onCopyTextureFinsihed(self):
        self.RefreshList()
        self.progress.setValue(0)
        MMessage.info(parent=self,text="贴图复制完成")

class SetTextureColorSpaceWidget(MComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__init__ui()
    def __init__ui(self):
        colorSpaces = ["sRGB","Raw"]
        menu = MMenu(exclusive=False,parent=self)
        menu.set_data(colorSpaces)
        self.set_menu(menu)

def showUI():
    global textureArrange
    textureArrange = TextureArrange()
    textureArrange.show(dockable=True)




if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
    showUI()











