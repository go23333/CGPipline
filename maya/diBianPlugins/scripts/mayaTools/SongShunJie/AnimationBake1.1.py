 # encoding= utf-8
from maya import cmds,mel
import time

class win():
	def __init__(self):
		self.winName="��������FBX�ļ�"
		if cmds.window(self.winName,q=1,ex=1):
			cmds.deleteUI(self.winName)
		cmds.window(self.winName,widthHeight=(380,200))
		self.UI1()
		
		
	def UI1(self):
		self.start=1
		self.end=5
		self.column1=cmds.columnLayout( adjustableColumn=True )
		cmds.text( label='ѡ����Ҫ�決����',align='left')
		cmds.textFieldGrp('start',label='���ú決��ʼ֡',text='%s'%self.start,cal=(1,'left'),cw2=(100,50))
		cmds.textFieldGrp('end',label='���ú決����֡',text='%s'%self.end,cal=(1,'left'),cw2=(100,50))
		cmds.button( label='�決��ѡ����',command=self.bake)
		cmds.text('',align='left')
		cmds.text('FBX�ļ�����λ��',align='left')
		cmds.setParent(self.column1)
		
		cmds.rowLayout( numberOfColumns=2, columnWidth2=(80, 75))
		
		text_path_sc='_FBX/'+str(cmds.file(q=1,sn=1)).rsplit('_',1)[0].rsplit('/',1)[-1]
		self.text_path=str(cmds.file(q=1,sn=1)).rsplit('_',1)[0]+text_path_sc+'_an_'
		self.text_path_old=self.text_path.replace('Lighting/File','Animation/FBX',1)
		cmds.textField('export',text=self.text_path_old,w=350)
		cmds.symbolButton( image='circle.png',w=20,i="navButtonBrowse.xpm",c=self.openFile)
		cmds.setParent(self.column1)
		
		cmds.button(label='����FBX��ָ��λ��',command=self.exportFBX)
		cmds.setParent(self.column1)
		

	def bake(self,*args):
		obj=cmds.ls(sl=1)
		
				
		#����ѡ���������ò�ɾ��ѡ����������ƿռ�
		path_reference=cmds.referenceQuery(obj[0], f=True )
		cmds.file(path_reference, ir=1)
		cmds.parent(obj,world=True)#�����
		self.obj_namespace=str(obj[0]).split(':',1)[0]+':'
		cmds.namespace(removeNamespace = self.obj_namespace, mergeNamespaceWithParent = True)
		self.obj_new=cmds.ls(sl=1)
		
		#ѡ����Ҫ�決�Ķ���
		cmds.select(self.obj_new,hi=1)
		cmds.select(cmds.ls(type= "blendShape"),add=1)
		
		#�決
		self.obj_bake_l=[]
		self.obj_list=cmds.ls(sl=1)
		i=0
		while i<len(self.obj_list):
			self.obj_bake_l.append(str(self.obj_list[i]))
			i+=1
		self.obj_bake_a=str(self.obj_bake_l)[2:-2]
		self.obj_bake=self.obj_bake_a.replace("'",'"')
		self.start=int(cmds.textFieldGrp('start',text=1,q=1))
		self.end=int(cmds.textFieldGrp('end',text=1,q=1))
		mel.eval('''bakeResults -simulation true -t "%s:%s" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"%s"}'''%(self.start,self.end,self.obj_bake))
		
		#ɾ������ڵ�
		#cmds.select( '*lower*ipBC*','*upper*ipBC*','*lower*ipBC*_*' )
		#cmds.delete()
		
		#�����ļ�����
		self.text_path_new=self.text_path_old+str(obj[0]).split(':',1)[0]
		cmds.textField('export',text=self.text_path_new,e=1)
		cmds.select(self.obj_new,hi=1)
		
		
		
	def exportFBX(self,*args):
		
		
		#����fbx��ʽ
		cmds.FBXResetExport()
		mel.eval('FBXExportFileVersion -v FBX201300')
		mel.eval('FBXExportSmoothingGroups -v true')
		mel.eval('FBXExportSmoothMesh -v true')
		
		#����fbx
		cmds.select(self.obj_new)
		self.export_path=cmds.textField('export',text=1,q=1)
		if '.fbx' not in self.export_path and '.FBX' not in self.export_path:
			self.export_path+='.fbx'
		print(self.export_path)
		mel.eval('FBXExport -f "%s" -s'%(self.export_path))

		
		#����������
		collect_g='%s_g'%self.obj_namespace.split(':',1)[0]
		cmds.group(em=True,n=collect_g)
		cmds.parent(self.obj_new,collect_g)

	def openFile(self,*args):
		file_name_new=str(cmds.fileDialog2(fileFilter="*.fbx",startingDirectory =str(cmds.file(q=1,sn=1)).rsplit('/',1)[0],rf=1)[0])
		cmds.textField('export',text=file_name_new,e=1)
		
		
def start():
	win()
	cmds.showWindow()


if __name__=='__main__':
	win()
	cmds.showWindow()
 


