from maya import cmds,mel


shade_select=[]
shade_names=[]
def udim_shade(shade,Texture_ds):
	cmds.hyperShade(objects=shade)
	mel.eval('ConvertSelectionToFaces')
	shade_select=cmds.ls(sl=1,fl=1)
	if shade_select:
		cmds.select(shade_select[0])
		mel.eval('ConvertSelectionToUVs')
		uv_list=cmds.polyEditUV( query=True )
		uv_x=int(uv_list[0])+1
		uv_y=int(uv_list[1])
		uv_xy=uv_y*10+uv_x
		
		#创建分离材质的贴图字典
		texture_path={}
		for k,v in Texture_ds.items():
			texture_path[k]=v[uv_xy-1]
		
		#数字转字母
		uv_udim=chr(64+uv_xy)
		mel.eval('ConvertSelectionToFaces')
		mel.eval('SelectUVShell')
		target_object=cmds.ls(sl=1,fl=1)
		if not cmds.objExists('%s_%s'%(shade,uv_udim)):
			cmds.sets( name='%s_%sGroup'%(shade,uv_udim), renderable=True, empty=True )
			cmds.shadingNode( 'RedshiftMaterial', name='%s_%s'%(shade,uv_udim), asShader=True )
			
			print(texture_path)
			textureConnect('%s_%s'%(shade,uv_udim),texture_path)
			
			cmds.surfaceShaderList( '%s_%s'%(shade,uv_udim), add='%s_%sGroup'%(shade,uv_udim) )
		
		cmds.select(target_object)
		cmds.hyperShade( assign='%s_%s'%(shade,uv_udim) )
	return(shade_select)

def execute(*args):
	i=0
	shade_names=cmds.ls(sl=1,fl=1)
	print(shade_names)
	for shade_name in shade_names:
		if cmds.objectType(shade_name, isType='transform'):
			cmds.text('detection',label='请只选择材质',ebg=1,bgc=[1,0,0],e=1)
			i=1
	if i==0:
		for shade_name in shade_names:
			Texture_ds=getTexture(shade_name)
			while 1:
				data=udim_shade(shade_name,Texture_ds)
				if not data:
					break


#创建材质贴图节点
def textureConnect(shade_name,texture_path):
	
	attr_names=[['.translateFrame', '.translateFrame'],
	 ['.rotateFrame', '.rotateFrame'],
	 ['.mirrorU', '.mirrorU'],
	 ['.mirrorV', '.mirrorV'],
	 ['.stagger', '.stagger'],
	 ['.wrapU', '.wrapU'],
	 ['.wrapV', '.wrapV'],
	 ['.repeatUV', '.repeatUV'],
	 ['.offset', '.offset'],
	 ['.rotateUV', '.rotateUV'],
	 ['.noiseUV', '.noiseUV'],
	 ['.vertexUvOne', '.vertexUvOne'],
	 ['.vertexUvTwo', '.vertexUvTwo'],
	 ['.vertexUvThree', '.vertexUvThree'],
	 ['.vertexCameraOne', '.vertexCameraOne'],
	 ['.outUV', '.uv'],
	 ['.coverage', '.coverage'],
	 ['.outUvFilterSize', '.uvFilterSize']]
	
	for k,v in texture_path.items():
		#将1001格式转换为ABC格式
		v_ABC=v.split('.')[0]+'_'+chr(64+int(v.split('.')[1])-1000)+'.'+v.rsplit('.')[-1]
		#贴图重命名
		if not os.path.isfile(v_ABC):
			os.rename(v,v_ABC)
		
		#根据贴图类型来赋予对应贴图节点
		if k =='c':
			f_name=shade_name+'_'+k+'_file'
			t_name=shade_name+'_'+k+'_texture'
			cmds.shadingNode('file',name=f_name,asTexture=True,isColorManaged=True)
			cmds.shadingNode('place2dTexture',name=t_name,asUtility=True)
			
			for attr_name in attr_names:
				cmds.connectAttr(t_name+attr_name[0],f_name+attr_name[1],f=1)
				
			cmds.setAttr(f_name+'.fileTextureName', v_ABC, type='string')
			cmds.connectAttr(f_name+'.outColor',shade_name+'.diffuse_color',f=1)
		if k =='e':
			f_name=shade_name+'_'+k+'_file'
			t_name=shade_name+'_'+k+'_texture'
			cmds.shadingNode('file',name=f_name,asTexture=True,isColorManaged=True)
			cmds.shadingNode('place2dTexture',name=t_name,asUtility=True)
			
			for attr_name in attr_names:
				cmds.connectAttr(t_name+attr_name[0],f_name+attr_name[1],f=1)
				
			cmds.setAttr(f_name+'.fileTextureName', v_ABC, type='string')
			cmds.connectAttr(f_name+'.outColor',shade_name+'.emission_color',f=1)
		if k =='arms':
			f_name=shade_name+'_'+k+'_file'
			t_name=shade_name+'_'+k+'_texture'
			cmds.shadingNode('file',name=f_name,asTexture=True,isColorManaged=True)
			cmds.shadingNode('place2dTexture',name=t_name,asUtility=True)
			
			for attr_name in attr_names:
				cmds.connectAttr(t_name+attr_name[0],f_name+attr_name[1],f=1)
				
			cmds.setAttr(f_name+'.fileTextureName', v_ABC, type='string')
			cmds.connectAttr(f_name+'.outColor.outColorG',shade_name+'.refl_roughness',f=1)
			cmds.connectAttr(f_name+'.outColor.outColorB',shade_name+'.refl_metalness',f=1)
		if k =='n':
			f_name=shade_name+'_'+k+'_normalMap'
			t_name=shade_name+'_'+k+'_texture'
			cmds.shadingNode('RedshiftNormalMap',name=f_name,asTexture=True,isColorManaged=True)
				
			cmds.setAttr(f_name+'.tex0',v_ABC, type='string')
			cmds.connectAttr(f_name+'.outDisplacementVector',shade_name+'.bump_input',f=1)
			
		




 #获取贴图路径
def getTexture(shade_name):

	texture_files={}
	#根据连接点获取对应的节点
	if cmds.nodeType( shade_name )=='RedshiftMaterial':
		mat_c=cmds.connectionInfo(shade_name+'.diffuse_color',sfd=1)
		mat_n=cmds.connectionInfo(shade_name+'.bump_input',sfd=1)
		mat_arms=cmds.connectionInfo(shade_name+'.refl_roughness',sfd=1)
		mat_e=cmds.connectionInfo(shade_name+'.emission_color',sfd=1)
	
	#elif cmds.nodeType( shade_names[0] )=='lambert':
	#	mat_class.append(cmds.connectionInfo(shade_names[0]+'.color',sfd=1))
	
	#获取贴图节点上的贴图路径
	c_name=mat_c.split('.')[0]
	c_path=[]
	if c_name:
		c_path.append(cmds.getAttr(c_name+'.fileTextureName',x=True))
		texture_files['c']=c_path

	n_name=mat_n.split('.')[0]
	n_path=[]
	if n_name:
		n_path.append(cmds.getAttr(n_name+'.tex0',x=True))
		texture_files['n']=n_path

	arms_name=mat_arms.split('.')[0]
	arms_path=[]
	if arms_name:
		arms_path.append(cmds.getAttr(arms_name+'.fileTextureName',x=True))
		texture_files['arms']=arms_path

	e_name=mat_e.split('.')[0]
	e_path=[]
	if e_name:
		e_path.append(cmds.getAttr(e_name+'.fileTextureName',x=True))
		texture_files['e']=e_path


	for k,v in texture_files.items():
		v_new=[]
		for dirpath, dirnames, filenames in os.walk(v[0].rsplit('/',1)[0]):
			for filename in filenames:
				if v[0].rsplit('/',1)[-1].split('.',1)[0] in filename:
					v_new.append(dirpath+'/'+filename)
					
		texture_files[k]=v_new

	return(texture_files)


		
def start():
	win="UDIM材质分离"
	if cmds.window(win,q=1,ex=1):
		cmds.deleteUI(win)
	cmds.window(win,widthHeight=(260,60))
	column1=cmds.columnLayout( adjustableColumn=True )
	cmds.text('选择需要分离的材质后点击执行',align='left')
	cmds.button(label='执行',c=execute)
	cmds.text('detection',label='',align='left',ebg=0,bgc=[1,0,0])
	cmds.showWindow()


		
if __name__=='__main__':
	win="UDIM材质分离"
	if cmds.window(win,q=1,ex=1):
		cmds.deleteUI(win)
	cmds.window(win,widthHeight=(260,60))
	column1=cmds.columnLayout( adjustableColumn=True )
	cmds.text('选择需要分离的材质后点击执行',align='left')
	cmds.button(label='执行',c=execute)
	cmds.text('detection',label='',align='left',ebg=0,bgc=[1,0,0])
	cmds.showWindow()







