# -*- coding: utf-8 -*-

from maya import cmds,mel
import openpyxl as op
import time
import os
import json


def jsonCreate(path1,path2):
    # home_dir = os.path.expanduser('~').replace('\\','/')  # 获取用户的主目录
    # json_path = home_dir+'/AppData/Local/Temp/mayaModelToUE.json'
    json_path = 'D:/Documents/maya/scripts/mayaModelToUE.json'
    #创建写入json文件的字典
    path_dict=[path1,path2]
    print(json_path)

    #将材质名称和包含的贴图创建为json文件
    with open(json_path,'w') as json_file:
        json.dump(path_dict,json_file)

def openJson():
    json_path = 'D:/Documents/maya/scripts/mayaModelToUE.json'
    if os.path.exists(json_path):
        with open(json_path,'r') as js_file:
            json_data=json.load(js_file)
        if json_data :
            return json_data


def ExportFbx(file_path):
    if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
        pm.loadPlugin("fbxmaya")

    mel.eval("FBXProperty Export|IncludeGrp|Geometry|BlindData -v false")

    fbx_export_options = [
        ("-s",),  # Selection Only
        ("-v", "FBX201400"),  # FBX Version
        ("-f", "MotionBuilder.fbx"),  # File Name
        # ("-es",),  # Embed Textures
        # ("-ea",),  # Embed Media
        ("-fr", "25"),  # Frame Rate
        ("-q",),  # Quiet Mode
        ("-p", "256"),  # Optimization Level
        # ("-axisUp", "y"),  # Up Axis
        # ("-axisFront", "z"),  # Front Axis
        ("-a", "model", "camera"),  # Animation Only (Model and Camera)
        ("-enablePointCache",),  # Point Cache
        ("-enableSampling",),  # Animation Sampling
        ("-stripNamespaces",),  # Strip Namespace
        ("-filterType", "AnimCurve"),  # Filter Type
        # ("-fcp", "0"),  # Bake Start Time
        # ("-fcp", "0"),  # Bake End Time
        ("-tp", "0"),  # Use Default Take
        ("-simplify", "1"),  # Simplify Animation Curves
    ]

    cmds.file(file_path, force=True, options=";".join([str(opt) for opt in fbx_export_options]), type="FBX export", exportSelected=True)

class win():
    def __init__(self):
        self.winName=u"导出FBX文件至UE目录"
        if cmds.window(self.winName,q=1,ex=1):
            cmds.deleteUI(self.winName)
        cmds.window(self.winName,widthHeight=(370,220))
        
        self.a_meshs=[]
        self.b_meshs=[]
        
        self.UI1()
        
        
    def UI1(self):
        #打开temp文件夹中的缓存文件
        path_list=openJson()
        if path_list:
            path1=path_list[0]
            path2=path_list[1]
        else:
            path1=''
            path2=''


        self.start=1
        self.end=5
        self.column1=cmds.columnLayout( adjustableColumn=True )
        
        
        cmds.text(u'选择导出路径A',align='left')
        
        cmds.rowLayout( numberOfColumns=2, columnWidth2=(120, 75))
        cmds.button(label=u'更新A路径导出模型',command=self.updataA)
        cmds.text('a_list',label='')
        cmds.setParent(self.column1)
        
        cmds.rowLayout( numberOfColumns=2, columnWidth2=(80, 75))
        cmds.textField('export',text=path1,w=340)
        cmds.symbolButton( image='circle.png',w=20,i="navButtonBrowse.xpm",c=self.openFile)
        
        cmds.setParent(self.column1)
        
        cmds.text(u'选择导出路径B',align='left')
        
        cmds.rowLayout( numberOfColumns=2, columnWidth2=(120, 75))
        cmds.button(label=u'更新B路径导出模型',command=self.updataB)
        cmds.text('b_list',label='')
        cmds.setParent(self.column1)
        
        cmds.rowLayout( numberOfColumns=2, columnWidth2=(80, 75))
        cmds.textField('export2',text=path2,w=340)
        cmds.symbolButton( image='circle.png',w=20,i="navButtonBrowse.xpm",c=self.openFile2)
        
        cmds.setParent(self.column1)
        
        cmds.radioButtonGrp( 'radio_group', labelArray3=[u'仅导出A', u'仅导出B', u'同时导出'], numberOfRadioButtons=3 )
        
       
        
        cmds.button(label=u'导出FBX到指定位置',command=self.execute)
        cmds.setParent(self.column1)
        
        cmds.text(u'将目录设置为ue工程内部的目录,就可以使模型导出后自动同步到UE',align='left')
        cmds.setParent(self.column1)
                
    def openFile(self,*args):
        
        singleFilter="*.fbx"
        open_path=str(cmds.fileDialog2(fileFilter=singleFilter,startingDirectory =str(cmds.file(q=1,sn=1)).rsplit('/',1)[0],fm=0)[0])
        if ".fbx" not in open_path:
            open_path+=".fbx"
        cmds.textField('export',text=open_path,e=1)
        
    def openFile2(self,*args):
        
        singleFilter="*.fbx"
        open_path=str(cmds.fileDialog2(fileFilter=singleFilter,startingDirectory =str(cmds.file(q=1,sn=1)).rsplit('/',1)[0],fm=0)[0])
        if ".fbx" not in open_path:
            open_path+=".fbx"
        cmds.textField('export2',text=open_path,e=1)


    def execute(self,*args):
        
        file_path1=cmds.textField('export',text=1,q=1)
        file_path2=cmds.textField('export2',text=1,q=1)
        radio_idex=cmds.radioButtonGrp( 'radio_group',select=1,q=1)

        jsonCreate(file_path1,file_path2)
        
        f1_switch=False
        f2_switch=False
        if radio_idex == 1 or radio_idex == 3:
            f1_switch=True
        if radio_idex == 2 or radio_idex == 3:
            f2_switch=True
            
        if file_path1 and f1_switch:
            #ExportFbx(file_path1)
            cmds.select(self.a_meshs)
            mel.eval('file -force -options "" -typ "FBX export" -pr -es "%s";'%(file_path1))
        if file_path2 and f2_switch:
            #ExportFbx(file_path2)
            cmds.select(self.b_meshs)
            mel.eval('file -force -options "" -typ "FBX export" -pr -es "%s";'%(file_path2))


    def updataA(self,*args):
        self.a_meshs=cmds.ls(sl=1)
        cmds.text('a_list',label=";".join([str(mesh) for mesh in self.a_meshs]),e=1)

    def updataB(self,*args):
        self.b_meshs=cmds.ls(sl=1)
        cmds.text('b_list',label=";".join([str(mesh) for mesh in self.b_meshs]),e=1)



def showUI():
    win()
    cmds.showWindow()

if __name__=='__main__':
    showUI()