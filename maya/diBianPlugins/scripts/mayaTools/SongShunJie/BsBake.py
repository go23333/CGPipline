#cmds.setKeyframe( a[0], attribute='asd2', t=5,v=1 )

from maya import cmds,mel


class win():
	def __init__(self):
		self.winName="创建BlendShape"
		if cmds.window(self.winName,q=1,ex=1):
			cmds.deleteUI(self.winName)
		cmds.window(self.winName,widthHeight=(250,110))
		self.UI1()
		
	def UI1(self):
		self.start=1
		self.end=5
		self.column1=cmds.columnLayout( adjustableColumn=True )
		cmds.textFieldGrp('start',label='设置起始帧',text='%s'%self.start,cal=(1,'left'),cw2=(100,50))
		cmds.textFieldGrp('end',label='设置结束帧',text='%s'%self.end,cal=(1,'left'),cw2=(100,50))
		cmds.text( label='选择需要BlendShape的对象后点击执行', align='left'  )
		cmds.button( label='执行',command=self.bs)

		
		
		
	def bs(self,*args):
		
		cmds.namespace( set=':' )

		a=cmds.ls(sl=1)
		
		self.start=int(cmds.textFieldGrp('start',text=1,q=1))
		self.end=int(cmds.textFieldGrp('end',text=1,q=1))
		
		
		cmds.group(n='%s_group_d'%a[0],em=1 )
		a_bs=cmds.duplicate( '%s'%a[0],name='%s_bs'%a[0].rsplit(':',1)[-1] )
		
		d_list=[]
		i=self.start
		j=0
		while i<=self.end:
			d_name='%s_b_%s'%(a_bs[0],j)
			bs_name='bs_%s%s'%(a[0],i)
			cmds.currentTime( i )

			d_poly=cmds.duplicate( '%s'%a[0],name=d_name )
			cmds.parent( d_name,'%s_group_d'%a[0] )
			d_list.append(d_poly)
			i+=1
			j+=1
			
		
		for i in d_list:
			cmds.select(i,add=1)
		cmds.select(a_bs,add=1)
		mel.eval('blendShape -tc 0 -n "bs_%s"'%a_bs[0])
		i_time=self.start

		for i in d_list:

			cmds.setKeyframe( 'bs_%s'%a_bs[0], attribute='%s'%i[0], t=i_time,v=1 )
			cmds.setKeyframe( 'bs_%s'%a_bs[0], attribute='%s'%i[0], t=i_time-1,v=0 )
			cmds.setKeyframe( 'bs_%s'%a_bs[0], attribute='%s'%i[0], t=i_time+1,v=0 )
			i_time+=1
			
		cmds.select(a_bs)	
		mel.eval('BakeTopologyToTargets')
		print(a_bs[0])
		mel.eval('''bakeResults -simulation true -t "%s:%s"  -hierarchy below -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"bs_%s","%s"}'''%(self.start,self.end,a_bs[0],a_bs[0]))
			
			
	
	
		

def start():
	win()
	cmds.showWindow()


if __name__=='__main__':
	start()







