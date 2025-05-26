#coding=utf-8


#导入标准模块
import maya.cmds as cmds
import pymel.core as pm
from pymel.all import *

class editPiplineToolsUI:
    def __init__(self):
        if cmds.window('editPiplineToolsUI',ex=1):
            cmds.deleteUI('editPiplineToolsUI',window=True)
        self.window = cmds.window('editPiplineToolsUI',title=u"地编流程工具",widthHeight=[400,250])
        # process Layout
        MainLayout = cmds.columnLayout( p=self.window,adjustableColumn=True)
        cmds.separator(p = MainLayout,h = 20)
        cmds.text(l=u'模型回归原点工具:',p=MainLayout,al='left')
        rowlayout_PicPath = cmds.rowLayout(numberOfColumns= 3,p=MainLayout,height = 40)
        cmds.button(l =u'顶部中心点', p = rowlayout_PicPath,c=lambda *arg: self.toOrigin(1))
        cmds.separator(p = rowlayout_PicPath,h = 1,width = 10,horizontal=False)
        cmds.button(l =u'底部中心点', p = rowlayout_PicPath,c=lambda *arg: self.toOrigin(0))
        cmds.separator(p = MainLayout,h = 20)
    def show(self):
        cmds.showWindow(self.window)
    def toOrigin(self,pos,*arg):
        selectedOBJ = pm.ls(selection = True)
        for obj in selectedOBJ:
            objCenter = (obj.getBoundingBoxMax() + obj.getBoundingBoxMin())/2
            centtobottom = (obj.getBoundingBoxMax().y - obj.getBoundingBoxMin().y)/2
            if pos == 0:
                objCenter.y = objCenter.y - centtobottom
            elif pos == 1:
                objCenter.y = objCenter.y + centtobottom
            obj.setPivots(objCenter,worldSpace=True)
            currentPosition = obj.getTranslation('object') - objCenter
            obj.setTranslation(currentPosition,'object')
            pm.makeIdentity( apply=True )
            pass
        pass


def showUI():
    UI = editPiplineToolsUI()
    UI.show()


if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
    showUI()