#!/usr/bin/python
# -*- coding:utf-8 -*-
#script name:fileDialog

from mayaTools import PYTHONVERSION
import maya.cmds as mc
from mayaTools.rig.weightsIO.shared_ch.mayaPrint import MayaPrint

class FDialog( MayaPrint ):
    def fileDialog(self,**flags):
        """
        m(fileMode) int: 
            0 for read 
            1 for write 
            2 for write without paths (segmented files) 
            4 for directories have meaning when used with the action 
            +100 for returning short names 
            
        """
        if PYTHONVERSION == 2:
            defineFlags = {"m":(0,int),"wt":('',str,u'',unicode),"ft":('',str,u'',unicode),"okc":('',str,u'',unicode)}
        else:
            defineFlags = {
                "m": (0, int),
                "wt": ('', str),
                "ft": ('', str),
                "okc": ('', str)}
        flagDirect = self.funtionFlag(defineFlags,**flags)
        ##read from flagDirect
        self.path=[]
        m = flagDirect["m"]
        ft = flagDirect["ft"]
        okc = flagDirect["okc"]
        #--------------------
        mayaVersion = mc.about(f=True)
        res = []
        if mayaVersion<="2010":
            if m<=1:
                path = mc.fileDialog(m=m,directoryMask=ft)
                if path!="":
                    res = [path]
                elif path=="":
                    return None
            else:
                mc.fileBrowserDialog( m=m, fc=self.returnPath, an='ZCH', om='Import' )
                res = self.path
        else:
            #make 2001 same like 2008
            mapToOld = {0:1,1:0,4:3}
            m = mapToOld[m]
            path = mc.fileDialog2(fileMode=m, dialogStyle=2,fileFilter=ft,okCaption=okc)
            if path!=None:
                res = path
        return res
        
    def returnPath(self,fileName, fileType):
        "For fileBrowserDialog"
        self.path.append(fileName)

