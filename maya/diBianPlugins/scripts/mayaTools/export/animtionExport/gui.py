#coding=utf-8
from maya import cmds,mel
import time
import os

class win():
    def __init__(self):
        self.winName=u"创建动画FBX文件"
        if cmds.window(self.winName,q=1,ex=1):
            cmds.deleteUI(self.winName)
        cmds.window(self.winName,widthHeight=(380,180))
        self.UI1()
        
        
    def UI1(self):
        self.start=1
        self.end=5
        self.column1=cmds.columnLayout( adjustableColumn=True )
        cmds.text( label=u'选择需要烘焙的组',align='left') 
        #起始结束帧
        cmds.rowLayout( numberOfColumns=2)
        cmds.textFieldGrp('start',label=u'设置烘焙起始帧',text='%s'%self.start,cal=(1,'left'),cw2=(100,50))
        cmds.textFieldGrp('end',label=u'设置烘焙结束帧',text='%s'%self.end,cal=(1,'left'),cw2=(100,50))
        cmds.setParent(self.column1)
        cmds.text(label='')
        #预留帧
        cmds.rowLayout( numberOfColumns=2)
        cmds.textFieldGrp('start_offset',label=u'设置整体偏移帧',text=10,cal=(1,'left'),cw2=(100,50))
        cmds.textFieldGrp('end_offset',label=u'设置预留结束帧',text=5,cal=(1,'left'),cw2=(100,50))
        cmds.setParent(self.column1)
        
        #cmds.button( label='烘焙所选物体',command=self.bake)
        #cmds.text('',align='left')
        cmds.text(u'FBX文件导出位置',align='left')
        cmds.setParent(self.column1)
        
        cmds.rowLayout( numberOfColumns=2, columnWidth2=(80, 75))
        
        text_path_sc='_FBX/'+str(cmds.file(q=1,sn=1)).rsplit('_',1)[0].rsplit('/',1)[-1]
        self.text_path=str(cmds.file(q=1,sn=1)).rsplit('_',1)[0]+text_path_sc+'_an_'

        self.text_path_old=self.text_path
        cmds.textField('export',text=self.text_path_old,w=350)
        cmds.symbolButton( image='circle.png',w=20,i="navButtonBrowse.xpm",c=self.openFile)
        cmds.setParent(self.column1)
        
        cmds.button(label=u'导出FBX到指定位置',command=self.exportFBX)
        cmds.setParent(self.column1)
        


    def bake(self,*args):
        obj_select=cmds.ls(sl=1)
        space_name = obj_select[0].split(':',1)[0]    #获取名称空间
        obj = []
        
        if cmds.objExists(space_name+':Root_M'):
            
            cmds.select(space_name+':Root_M')            
            #cmds.select(space_name+':Geometry',add=1)


            
        elif cmds.objExists(space_name+':*_GuGe_G'):
            cmds.select(space_name+':*_GuGe_G')            
            cmds.select(space_name+':*_Pro_Mo',add=1)        
        
        obj=cmds.ls(sl=1)
                
        #导入选定对象引用并删除选定对象的名称空间
        path_reference=cmds.referenceQuery(obj[0], f=True )
        cmds.file(path_reference, ir=1)
        # cmds.parent(obj,world=True)#解除组
        self.obj_namespace=str(obj[0]).split(':',1)[0]+':'
        cmds.select(obj)
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
        
        #获取偏移值
        start_offset=int(cmds.textFieldGrp('start_offset',text=1,q=1))
        end_offset=int(cmds.textFieldGrp('end_offset',text=1,q=1))
        #偏移关键帧
        cmds.keyframe( self.obj_list,relative=True,timeChange=start_offset)
        #获取烘焙起始结束帧
        self.start=int(cmds.textFieldGrp('start',text=1,q=1))
        self.end=int(cmds.textFieldGrp('end',text=1,q=1))
        
        mel.eval('''bakeResults -simulation true -t "%s:%s" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"%s"}'''%(self.start,self.end,self.obj_bake))
        
        #删除多余节点
        #cmds.select( '*lower*ipBC*','*upper*ipBC*','*lower*ipBC*_*' )
        #cmds.delete()

        #选择所有烘焙的对象
        cmds.select(self.obj_new,hi=1)
        #将所有对象放入列表
        frame_list=cmds.ls(sl=1)
        #偏移关键帧
        cmds.keyframe( frame_list,relative=True,timeChange=start_offset)
        
        #烘焙前后帧
        #cmds.bakeResults( frame_list, t=(self.start,self.end+end_offset+start_offset), simulation=True )
        if start_offset!=0:
            cmds.bakeResults( frame_list, t=(self.start,self.start+start_offset+1), simulation=True,preserveOutsideKeys=True )
        if end_offset!=0:
            cmds.bakeResults( frame_list, t=(self.end,self.end+start_offset+end_offset), simulation=True,preserveOutsideKeys=True )

        
        


        #创建文件名称
        # self.text_path_new=self.text_path_old+str(obj[0]).split(':',1)[0]
        #cmds.textField('export',text=self.text_path_new,e=1)
        cmds.select(self.obj_new,hi=1)
        
        
        
    def exportFBX(self,*args):
        
        self.bake()
        
        
        #设置fbx格式
        cmds.FBXResetExport()
        mel.eval('FBXExportFileVersion -v FBX201300')
        mel.eval('FBXExportSmoothingGroups -v true')
        mel.eval('FBXExportSmoothMesh -v true')
        
        #导出fbx
        cmds.select(self.obj_new)
        export_path=cmds.textField('export',text=1,q=1)
        if '.fbx' not in export_path and '.FBX' not in export_path:
            export_path+='.fbx'
        #创建FBX文件夹
        if not os.path.exists(export_path.rsplit('/',1)[0]):
            os.makedirs(export_path.rsplit('/',1)[0])
            
        print(export_path)
        mel.eval('FBXExport -f "%s" -s'%(export_path))

        
        #创建收纳组
        collect_g='%s_g'%self.obj_namespace.split(':',1)[0]
        cmds.group(em=True,n=collect_g)
        cmds.parent(self.obj_new,collect_g)

    def openFile(self,*args):
        file_name_new=str(cmds.fileDialog2(fileFilter="*.fbx",startingDirectory =str(cmds.file(q=1,sn=1)).rsplit('/',1)[0],rf=1)[0])
        cmds.textField('export',text=file_name_new,e=1)
        
        
def showUI():
    win()
    cmds.showWindow()


if __name__=='__main__':
    win()
    cmds.showWindow()
 


