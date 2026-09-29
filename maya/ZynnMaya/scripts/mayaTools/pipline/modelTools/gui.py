#coding=utf-8

from maya import cmds,mel

import mayaTools.pipline.modelTools.CutHairCurve as MSCut
import mayaTools.pipline.modelTools.modelExportUE as MSModel
import mayaTools.pipline.modelTools.modelPolygonCount as MSPolygonCount



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

        cmds.button( label=u'模型面数统计工具',command=self.polygonCount)
        
        
    def cutHair(self,*args):
        
        MSCut.showUI()

    def modelExportUE(self,*args):

        MSModel.showUI()

    def polygonCount(self,*args):
        MSPolygonCount.showUI()




def showUI():
    win()
    cmds.showWindow()

if __name__=='__main__':
    showUI()
