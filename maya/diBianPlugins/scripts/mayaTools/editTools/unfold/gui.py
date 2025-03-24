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
import mayaTools.core.callThirdpart as ct
import mayaTools.core.mayalibrary2 as ml2


class UnfoldTool(MayaQWidgetDockableMixin,QWidget):
    def __init__(self):
        super(UnfoldTool,self).__init__()
        self.setWindowTitle(u"Unfold Tool")
        self.resize(250,80)
        self.__initUI()
        MayaScriptDir = cmds.internalVar(userScriptDir=True)
        self.ObjectDir = MayaScriptDir + ('RizomUVBridge/') + ('data/RBMObject.fbx')
        self.LoaderDir = MayaScriptDir + ('RizomUVBridge/') + ('data/Loader.lua')
        self.objects = []

    def __initUI(self):
        layout_main = QVBoxLayout(self)


        pb_export_to_unfold = MPushButton(u"导出到Unfold")
        pb_export_to_unfold.clicked.connect(self.export_to_unfold)

        layout_main.addWidget(pb_export_to_unfold)

        pb_import_to_maya = MPushButton(u"导入到Maya")
        pb_import_to_maya.clicked.connect(self.import_to_maya)

        layout_main.addWidget(pb_import_to_maya)

    def export_to_unfold(self):
        self.objects = cmds.ls( sl=True )
        ml2.export_fbx(self.objects,self.ObjectDir,'groups=1')
        print ('Export FBX complete!')
        ct.call_unfold_export(self.ObjectDir,self.LoaderDir) 
    def import_to_maya(self):
        for item in self.objects:
            cmds.delete()
        ml2.import_fbx(self.ObjectDir,'RBMObject')
        print ('Import FBX complete!')

def showUI():
    global unfoldtool
    unfoldtool = UnfoldTool()
    unfoldtool.show(dockable=True)


if __name__ == '__main__':
    from mayaTools import reloadModule
    reloadModule()
    showUI()
    pass





