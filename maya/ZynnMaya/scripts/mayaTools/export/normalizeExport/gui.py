#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
##################################################################

from Qt import QtWidgets,QtCore
from dayu_widgets.message import MMessage
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MClickBrowserFolderToolButton,MLineEdit
from dayu_widgets.push_button import MPushButton
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import os

#custom modules
import mayaTools.core.uMaya as UM

class exportPipline(MayaQWidgetDockableMixin,QtWidgets.QWidget):
    def __init__(self):
        super(exportPipline,self).__init__()
        self.resize(400,300)
        self.setWindowTitle(u"规范化导出工具")
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()
        layMain.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        layExportPath = QtWidgets.QHBoxLayout()
        pbSelectExprotPath = MClickBrowserFolderToolButton()
        self.leExportPath = MLineEdit()
        self.leExportPath.setText(UM.getRootPath())
        pbSelectExprotPath.sig_folder_changed.connect(self.leExportPath.setText)
        layExportPath.addWidget(MLabel(u"导出路径:"))
        layExportPath.addWidget(self.leExportPath)
        layExportPath.addWidget(pbSelectExprotPath)

        layFilename = QtWidgets.QHBoxLayout()
        self.leFileName = MLineEdit()
        self.leFileName.setText(UM.getFileName())
        layFilename.addWidget(MLabel(u"导出文件名称:"))
        layFilename.addWidget(self.leFileName)

        pbExport = MPushButton(u"导出")
        pbExport.clicked.connect(self.export)

        layMain.addLayout(layExportPath)
        layMain.addLayout(layFilename)
        layMain.addWidget(pbExport)
        self.setLayout(layMain)
    def getFullPath(self):
        path = self.leExportPath.text()
        fileName = self.leFileName.text()
        if path == "":
            MMessage.error(parent=self,text="路径为空")
            return 0
        if fileName == "":
            MMessage.error(parent=self,text="文件名为空")
            return 0
        fullName = os.path.join(path,fileName,fileName)
        return fullName
    def export(self):
        fullName = self.getFullPath()
        if not fullName:
            return False
        flag,message = UM.exportPipline(fullName)
        if flag:
            MMessage.info(parent=self,text=message)
        else:
            MMessage.error(parent=self,text=message)

def showUI():
    global txExportPage
    txExportPage = exportPipline()
    txExportPage.show(dockable=True)
    
if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
    global txExportPage
    txExportPage = exportPipline()
    txExportPage.show(dockable=True)