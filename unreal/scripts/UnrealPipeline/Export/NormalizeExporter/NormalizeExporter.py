#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################

from dayu_widgets.message import MMessage
from Qt import QtWidgets,QtCore
from dayu_widgets.push_button import MPushButton
from dayu_widgets.qt import application
from dayu_widgets import dayu_theme
import unreal

from UnrealPipeline.core.CommonWidget import folderSelectGroup
import UnrealPipeline.core.UnrealHelper as UH

class NormalizeExporter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("规范化导出工具")
        self.resize(500,100)
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()
        self.folderSelectGroup = folderSelectGroup(u"选择导出路径:") 
        btnImport = MPushButton(u"导出选中的资产")
        btnImport.clicked.connect(self.__export)
        layMain.addLayout(self.folderSelectGroup)
        layMain.addWidget(btnImport)
        self.setLayout(layMain)
    def __export(self):
        exportPath = self.folderSelectGroup.getFolderPath()
        if exportPath == '':
            MMessage.error(parent=self,text="当前路径不合法")
            return False
        UH.NormalizeExport(exportPath)
        MMessage.info(parent=self,text="导出完成")


def Start():
    with application() as app:
        global w
        w = NormalizeExporter()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()