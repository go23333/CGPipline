#coding=utf-8
#导入标准模块
import maya.cmds as cmds
import pymel.core as pm

#导入自定义模块
import mayaTools.core.mayaLibrary as ML
import mayaTools.core.mayalibrary2 as ML2


#define global vir
from mayaTools.core.pathLibrary import getWorkDir


tempFilePath = getWorkDir() + r"temp\\toReduceMesh.fbx"

resFilePath =  getWorkDir() + r"temp\\Results\\toReduceMesh1.fbx"

class reducefaceUI:
    def __init__(self):
        if cmds.window('reducefaceUI',ex=1):
            cmds.deleteUI('reducefaceUI',window=True)
        self.window = cmds.window('reducefaceUI',title=u"模型减面工具v0.1",widthHeight=[400,250])
        # process Layout
        MainLayout = cmds.columnLayout( p=self.window,adjustableColumn=True)
        #percentage
        rowlayout_Aspect = cmds.rowLayout(numberOfColumns= 2,p=MainLayout)
        cmds.text(l=u'比例:')
        self.FF_Aspect = cmds.floatField(p = rowlayout_Aspect,value=90,annotation=u'模型减少的面数的比例',max=100,min=1)
        #normal
        self.cb_pnormals = cmds.checkBox(p = MainLayout,l=u'保护法线',annotation=u'是否保护模型法线',value=True)
        #UV
        self.cb_pUV = cmds.checkBox(p = MainLayout,l=u'保护UV',annotation=u'是否保护模型UV',value=True)
        #delete origin
        self.cb_deleteOrigin = cmds.checkBox(p = MainLayout,l=u'删除原有',value=False)
        #button
        cmds.separator(p=MainLayout)
        BTN_PickPath = cmds.button(l=u'执行',p=MainLayout,c=self.reduceface)
        cmds.separator(p=MainLayout)

        #BTN_back = cmds.button(l=u'将模型回退到减面前',p=MainLayout,c=self.rollback)
        #help
        cmds.separator(p = MainLayout )
        cmds.helpLine(p = MainLayout )
        cmds.separator(p=MainLayout)
        cmds.text(l=u'在使用前请进行重命名排查,以防止出现模型丢失的情况',p=MainLayout)
    def show(self):
        cmds.showWindow(self.window)
    def reduceface(self,*arg):
        selectedObjs = pm.ls(selection=True,l=1)
        for obj in selectedObjs:
            ML2.export_fbx(str(obj),tempFilePath)
            import mayaTools.core.callThirdpart as ct
            ct.callPolygonCruncher(cmds.checkBox(self.cb_pnormals,q=1,v=1),cmds.checkBox(self.cb_pUV,q=1,v=1),tempFilePath,cmds.floatField(self.FF_Aspect,q=1,v=1))
            if cmds.checkBox(self.cb_deleteOrigin,q=1,v=1):
                pm.delete(obj)
            else:
                pm.rename(obj,str(obj)+"_Origin")
            self.newNodes = ML2.import_fbx(resFilePath,1)
    # def rollback(self,*arg):
    #     import pymel.core as pm
    #     for newNode in self.newNodes:
    #         pm.delete(newNode)
    #     self.importfile = ML.importobjfile(tempFilePath)
def showUI():
    UI = reducefaceUI()
    UI.show()



if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
    showUI()
