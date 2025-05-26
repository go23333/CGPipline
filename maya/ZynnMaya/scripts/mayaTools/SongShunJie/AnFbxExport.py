# -*- coding: utf-8 -*-

from maya import cmds,mel
# import time
import json
import os
import sys

from PySide2.QtWidgets import *
from PySide2.QtGui import *



class win(QWidget):
    def __init__(self,parent=None):
        super(win,self).__init__(parent)

        self.uii()
        self.json_data=self.getJson()

    def uii(self):
        

        self.setWindowTitle('导出动画fbx')
        self.resize(320,120)
        self.setStyleSheet("QWidget { background-color: #333333; }")
        lay=QVBoxLayout()

        label=QLabel('Redshift版本不能为V.2.6.41,不然打开文件可能会出错')
        label.setStyleSheet("color: #cccccc; ")

        self.create_folder=QPushButton(text="开始")
        self.create_folder.setStyleSheet("color: #cccccc; ")
        self.create_folder.clicked.connect(self.execute)


        lay.addStretch(1)
        lay.addWidget(label)
        lay.addWidget(self.create_folder)
        lay.addStretch(2)

        
        self.setLayout(lay)

    


    def getJson(self):
        json_path='d:/an_export_fbx.json'
        if os.path.exists(json_path):
            with open(json_path,'r') as json_file:
                json_data=json.load(json_file)
            os.remove(json_path)

            for k,v in json_data.items():

                folder_name=str(k)
                #设置UI显示
                self.setWindowTitle('导出%s'%folder_name)
                self.create_folder.setText('开始导出文件夹%s中的角色动画FBX'%folder_name)

            return json_data
        else :
            return False

		
			
    def execute(self,*args):

        import maya.standalone as standalone
        standalone.initialize()
        
        
        for dir_path,self.start_endK_d in self.json_data.items():
            #获取文件路径
            ma_path=[]
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    if filename.split('.')[-1]=='ma'  or filename.split('.')[-1]=='mb':
                        new_dirpath=dirpath.replace('\\', '/')
                        ma_path.append(new_dirpath+'/'+filename)
            
            self.start(ma_path)

        


 

    def start(self,ma_path):   
                        
        if ma_path:
            #通过文件路径打开ma文件			
            for ma in ma_path:
                    
                try:

                    cmds.file(modified=0)
                    cmds.file(ma,open=1,force=1)
                    print(ma)
                except:
                    print(ma+' open error')
                    continue
                # time.sleep(5)
                #获取当前场景的场次信息
                key=cmds.file(q=1,sn=1).rsplit('/',1)[-1].rsplit('_',1)[0]
                if key in self.start_endK_d:
                    self.start=self.start_endK_d[key][0]#获取关键帧起始信息
                    self.end=self.start_endK_d[key][1]

                    #获取全部名称空间名
                    space_names=cmds.namespaceInfo( lon=True )
                    for self.space_name in space_names:
                        if cmds.objExists(self.space_name+':Geometry'):
                            cmds.pickWalk(self.space_name+':DeformationSystem', direction='down' )
                            cmds.select(self.space_name+':Geometry',add=1)
                            self.bake()
                            self.exportFBX()
                else :
                    pass

    def bake(self,*args):
        
        self.obj=cmds.ls(sl=1)

        #导入选定对象引用并删除选定对象的名称空间
        path_reference=cmds.referenceQuery(self.obj[0], f=True )
        cmds.file(path_reference, ir=1)
        cmds.parent(self.obj,world=True)#解除组
        self.obj_namespace=str(self.obj[0]).split(':',1)[0]+':'
        cmds.namespace(removeNamespace = self.obj_namespace, mergeNamespaceWithParent = True)
        self.obj_new=cmds.ls(sl=1)
        
        #选择需要烘焙的对象
        cmds.select(self.obj_new,hi=1)
        cmds.select(cmds.ls(type= "blendShape"),add=1)
        
        #烘焙
        self.obj_bake_l=[]
        self.obj_list=cmds.ls(sl=1)
        i=0
        while i<len(self.obj_list):
            self.obj_bake_l.append(str(self.obj_list[i]))
            i+=1
        self.obj_bake_a=str(self.obj_bake_l)[2:-2]
        self.obj_bake=self.obj_bake_a.replace("'",'"')
        mel.eval('''bakeResults -simulation true -t "%s:%s" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"%s"}'''%(self.start,self.end,self.obj_bake))
        
        #删除多余节点
        cmds.select( '*lower*ipBC*','*upper*ipBC*','*lower*ipBC*_*' )
        cmds.delete()
        
        #选择所有需要导出的对象
        cmds.select(self.obj_new,hi=1)


        
    def exportFBX(self,*args):
        
        #设置FBX文件名
        text_path=str(cmds.file(q=1,sn=1)).rsplit('_',1)[0]+'_FBX'
        if 'Mb' in text_path:
            text_path_old=text_path.replace('Mb','FBX',1)
        elif 'Lighting/File' in text_path:
            text_path_old=text_path.replace('Lighting/File','Animation/FBX',1)#创建路径
        else :
            text_path_old=text_path
        save_file_name='/'+str(cmds.file(q=1,sn=1)).rsplit('_',1)[0].rsplit('/',1)[-1]+'_an_'+self.space_name#创建文件名
        self.export_path=text_path_old+save_file_name
        print(self.export_path)
        #导出fbx
        cmds.select(self.obj_new)
        cmds.FBXResetExport()
        mel.eval('FBXExportFileVersion -v FBX201300')
        mel.eval('FBXExportSmoothingGroups -v true')
        mel.eval('FBXExportSmoothMesh -v true')
        #创建对应FBX文件夹
        if not os.path.exists(self.export_path.rsplit('/',1)[0]):
            os.makedirs(self.export_path.rsplit('/',1)[0])
        
        mel.eval('FBXExport -f "%s" -s'%(self.export_path))
        
        #创建收纳组
        collect_g='%s_g'%self.obj_namespace.split(':',1)[0]
        cmds.group(em=True,n=collect_g)
        cmds.parent(self.obj_new,collect_g)



def start():
	app=QApplication(sys.argv)
	cam=win()
	cam.show()
	app.exec_()
    


start()



