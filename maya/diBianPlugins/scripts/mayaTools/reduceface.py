#coding=utf-8
#auther=zcx
#data=20220721

from imp import reload

#导入自定义模块
import lib.mayaLibrary as ML
#导入标准模块
import maya.cmds as cmds

reload(ML)
import lib.pathLibrary as PL

reload(PL)
import lib.callThirdpart as CT

reload(CT)
#define global vir
tempFilePath = r'D:/reduceTempMesh.fbx'
resFilePath = r'D:/Results/reduceTempMesh1.fbx'

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
        #button
        cmds.separator(p=MainLayout)
        BTN_PickPath = cmds.button(l=u'执行',p=MainLayout,c=self.reduceface)
        cmds.separator(p=MainLayout)
        cmds.separator(p=MainLayout)
        cmds.separator(p=MainLayout)
        cmds.separator(p=MainLayout)
        BTN_back = cmds.button(l=u'将模型回退到减面前',p=MainLayout,c=self.rollback)
        #help
        cmds.separator(p = MainLayout )
        cmds.helpLine(p = MainLayout )
        cmds.separator(p=MainLayout)
        cmds.text(l=u'在使用前请进行重命名排查,以防止出现模型丢失的情况',p=MainLayout)
    def show(self):
        cmds.showWindow(self.window)
    def reduceface(self,*arg):
        sl = ML.getSelectNodes(True)
        ML.exportFBXStatic(sl,tempFilePath)


        CT.callPolygonCruncher(cmds.checkBox(self.cb_pnormals,q=1,v=1),cmds.checkBox(self.cb_pUV,q=1,v=1),tempFilePath,cmds.floatField(self.FF_Aspect,q=1,v=1))



        cmds.delete(sl[0])
        self.importfile = ML.importobjfile(resFilePath)

    def rollback(self,*arg):
        cmds.delete(self.importfile)
        self.importfile = ML.importobjfile(tempFilePath)

def reducefaceMain():
    UI = reducefaceUI()
    UI.show()