# -*- coding:utf-8 -*-
import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import sys


class MayaPrint:
    def __init__(self):
        self.printerWinName = "self_printerWinName"
        if mc.window(self.printerWinName,exists=1):
            mc.deleteUI(self.printerWinName)
    def mayaPrint(self,*arg,**args):#newWin=False,colour=[0,0.5,0],addResult=True,command="pass"):
        """
        """
        argList = ["newWin","colour","addResult","command","autoShow"]
        for key in args:
            if key not in argList:
                raise TypeError(" Invalid flag: {} # ".format( key ))
        #set flag default value
        if argList[0] not in args:
            args["newWin"]=False

        if argList[1] not in args:
            args["colour"]=[0,0.5,0]
        if argList[2] not in args:
            args["addResult"]=True
        if argList[3] not in args:
            args["command"]="pass"
        if argList[4] not in args:
            args["autoShow"]=True
        #make old command can using
        string = arg[0]
        if len(arg)>1:
            args["newWin"] = arg[1]
        if len(arg)>2:
            args["colour"] = arg[2]
        if len(arg)>3:
            args["addResult"] = arg[3]
        if len(arg)>4:
            args["command"] = arg[4]
        if len(arg)>5:
            args["autoShow"] = arg[5]

        if args["addResult"]:
            result = 'Result:{}\n'.format(string)
            self.printerWin('Result:{}'.format(string),args["newWin"],args["colour"],args["command"],args["autoShow"])
        else:
            result = '{}\n'.format(string)
            self.printerWin( string, args["newWin"], args["colour"], args["command"] ,args["autoShow"])
        sys.stderr.write(result)
    def mayaWarning(self,*arg,**args):#def mayaWarning(self,string,newWin=False,colour=[0.5,0,0.5],command="pass"):
        """
        """
        argList = ["newWin","colour","command","autoShow"]
        for key in args:
            if key not in argList:
                raise TypeError(" Invalid flag: {} # ".format( key ))
        #set flag default value
        if argList[0] not in args:
            args["newWin"]=False
        if argList[1] not in args:
            args["colour"]=[0.5,0,0.5]
        if argList[2] not in args:
            args["command"]="pass"
        if argList[3] not in args:
            args["autoShow"]=True
        #make old command can using
        string = arg[0]
        if len(arg)>1:
            args["newWin"] = arg[1]
        if len(arg)>2:
            args["colour"] = arg[2]
        if len(arg)>3:
            args["command"] = arg[3]
        if len(arg)>4:
            args["autoShow"] = arg[4]
        OpenMaya.MGlobal.displayWarning("{}".format(string))
        self.printerWin("#Warning:{}".format(string), args["newWin"], args["colour"], args["command"] ,args["autoShow"])
    def mayaError(self,*arg,**args):#def mayaError(self,string,newWin=False,colour=[.5,0,0],command="pass"):
        """
        """
        argList = ["newWin","colour","command","autoShow"]
        for key in args:
            if key not in argList:
                raise TypeError(" Invalid flag: {} # ".format( key ))
        #set flag default value
        if argList[0] not in args:
            args["newWin"]=False
        if argList[1] not in args:
            args["colour"]=[.5,0,0]
        if argList[2] not in args:
            args["command"]="pass"
        if argList[3] not in args:
            args["autoShow"]=True
        #make old command can using
        string = arg[0]
        if len(arg)>1:
            args["newWin"] = arg[1]
        if len(arg)>2:
            args["colour"] = arg[2]
        if len(arg)>3:
            args["command"] = arg[3]
        if len(arg)>4:
            args["autoShow"] = arg[4]
        OpenMaya.MGlobal.displayError("{}".format(string))
        self.printerWin("# Error:{}".format(string), args["newWin"], args["colour"], args["command"] ,args["autoShow"])

    def printerWin(self,string,onOff,colour,command,autoShow):
        if onOff:
            winName = self.printerWinName
            rootlayout = "of3d_printerRootLayout_Win"
            if not mc.window(winName,exists=True):
                win = mc.window(winName,title=" | Print Window ...")
                scroLayout = mc.scrollLayout( childResizable=True )
                mc.columnLayout( rootlayout ,adj=True)
                mc.window(winName,e=True,w=1,h=1)
                mc.window(winName,e=True,w=400,h=260)
            mc.iconTextButton(label=string,c=command,bgc=colour,p=rootlayout,align="left",style="iconAndTextHorizontal",h=20,labelOffset=1,font="smallPlainLabelFont")
            if autoShow==True:
                mc.showWindow(winName)

    def funtionFlag(self,flagAndValue,**flags):
        flagList = list(flagAndValue.keys())
        defaultValueList = list(flagAndValue.values())

        for flag in flags:
            #check Invalid flag
            if flag not in flagList:
                raise TypeError( " Invalid flag: {} # ".format( flag ) )
            #check value type
            else:
                type_value = type( flags[ flag ] )
                raiseIt = True
                for i in range(1, len(flagAndValue[ flag ]) , 2):
                    type_ = flagAndValue[ flag ][i]
                    if type_value == type_:
                        raiseIt = False
                    elif flags[ flag ]==None and flags[ flag ] == flagAndValue[ flag ][i]:
                        raiseIt = False
                if raiseIt == True:
                    stype = [flagAndValue[ flag ][i] for i in range(1, len(flagAndValue[ flag ]) , 2)]
                    raise TypeError( " Flag '{}' must be passed a {} argument # ".format( flag, stype ) )
        #set flag value
        flagDirect = {}
        for i in range( len(flagList) ):
            flag = flagList[i]
            if flag not in flags:
                #default value
                flagDirect[ flag ] = defaultValueList[i][0]
            else:
                #user set value
                flagDirect[ flag ] = flags[flag]
        return flagDirect