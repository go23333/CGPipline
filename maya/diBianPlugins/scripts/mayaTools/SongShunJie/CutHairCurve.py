from maya import cmds,mel
import time


class win():
	def __init__(self):
		self.winName="一键剪切毛发曲线"
		if cmds.window(self.winName,q=1,ex=1):
			cmds.deleteUI(self.winName)
		cmds.window(self.winName,widthHeight=(300,80))
		self.UI()
		
	def UI(self):
		
		self.column=cmds.columnLayout( adjustableColumn=True )
		
		cmds.button( label='执行剪切',command=self.cut)
		cmds.text('选择头皮和曲线后点击执行，\n执行前要保证曲线没有重名。\n并不一定一次成功，可多次执行。')
		
	def cut(self,*args):

		ss=cmds.ls(sl=1)
		meshs=cmds.listRelatives(ss,type='mesh')
		curves=cmds.listRelatives(ss,type='curveShape')
		cmds.group(em=True,n='cutCurve_Group' )
		sg=cmds.ls(sl=1)
		
		ct=time.time()
		
		for cu in curves:
		    
			ppc2=0
			ppc2a="polyProjectionCurve1_2"
			
			cmds.select('%s'%cu)
			cmds.extendCurve( em=0, et=0, s=True, d=0.3 )
			#投影
			t1='polyProjectCurve -ch 1 -pointsOnEdges 0 -curveSamples 500 -automatic 0  "%s" "%s"'%(cu,meshs[0])
			mel.eval(t1)
			cmds.select('polyProjectionCurve1',hi=1)
			lsc=cmds.ls(sl=1)
			for item in lsc:
				if item==ppc2a:
					ppc2=1		
			#设置剪切点
			node = cmds.curveIntersect('%s'%cu, 'polyProjectionCurve1_1', ch= True,useDirection=True,direction=(0, 1, 0))
			p1 = cmds.getAttr(node + ".parameter1" )  
			t1=tuple(p1[0])[:1]
			#剪切
			if t1:
				cmds.detachCurve( '%s'%cu, p=(t1), rpo=True,n='cutCurve' )
				sel=cmds.ls(sl=1)
				cmds.parent( '%s'%sel[0], '%s'%sg[0] )
				cu_c=cmds.pickWalk( '%s'%cu, direction='up' )
				cmds.delete( 'polyProjectionCurve1')
				cmds.delete(at=1)
			#容错
			elif ppc2==1:
				node = cmds.curveIntersect('%s'%cu, 'polyProjectionCurve1_2', ch= True,useDirection=True,direction=(0, 1, 0))
				p1 = cmds.getAttr(node + ".parameter1" )   
				t1=tuple(p1[0])[:1]
				cmds.select('%s'%cu)
				if t1:
					cmds.detachCurve( '%s'%cu, p=(t1), rpo=True,n='cutCurve' )
					sel=cmds.ls(sl=1)
					cmds.parent( '%s'%sel[0], '%s'%sg[0] )
				
					cu_c=cmds.pickWalk( '%s'%cu, direction='up' )
					cmds.delete( 'polyProjectionCurve1')
					cmds.delete(at=1)
				else:
					cmds.delete('polyProjectionCurve1')
			else :
				cmds.delete('polyProjectionCurve1')
				
		print(time.time()-ct)



if __name__=='__main__':
	win()
	cmds.showWindow()
 
