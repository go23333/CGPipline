#coding=utf-8

from maya import cmds,mel

import mayaTools.SongShunJie.CutHairCurve as MSCut
import mayaTools.SongShunJie.modelExportUE as MSModel



class win():
    def __init__(self):
        self.winName=u"模型工具"
        if cmds.window(self.winName,q=1,ex=1):
            cmds.deleteUI(self.winName)
        cmds.window(self.winName,widthHeight=(300,80))
        self.UI()
        
    def UI(self):
        
        self.column=cmds.columnLayout( adjustableColumn=True )
        
        cmds.button( label=u'剪切毛发曲线',command=self.cutHair)
        
        cmds.button( label=u'模型快速导出到UE工程工具',command=self.modelExportUE)

        cmds.button( label=u'功能3',command=self.cut)
        
        
    def cutHair(self,*args):
        
        MSCut.showUI()

    def modelExportUE(self,*args):

        MSModel.showUI()

    def cut(self,*args):
        pass




def showUI():
    win()
    cmds.showWindow()

if __name__=='__main__':
    showUI()
