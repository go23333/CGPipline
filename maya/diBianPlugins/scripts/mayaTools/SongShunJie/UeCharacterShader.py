# -*- coding: utf-8 -*-

from maya import cmds,mel
import os

def creB(*args):
	from maya import cmds,mel
	project=cmds.textFieldGrp('pj',text=1,q=1)
	
	cmds.select(all=1,hi=1)
	body_G=cmds.ls(sl=1)
	print(body_G)
	meshs=cmds.listRelatives(body_G,type='mesh')
	shaderBoLiTi=0
	shaderYanJian=0
	shaderYanJian_TouMing=0
	shaderYanQiu=0
	shaderJieMao=0
	shaderKouQiang=0
	shaderBody=0
	
	eyelashShape_set=0
	eyeYanQiu_set=0
	eyeshell_set=0
	eyeEdg_set=0
	cartilage_set=0
	body_set=0
	for i in meshs:
		if '_CH_' in i:
			ch_split=i.split('_CH_')
			i_name=ch_split[1].split('_')
			ch_name=ch_split[0]
			type='CH'
			component=i_name[0]
			for item in i_name:
				if item=='r' or item=='l' :
					component=i_name[1]
				if item=='dn' or item=='up':
					component=i_name[2]
				
				
			if 'body' in component and shaderBody==0:
				body_shader = cmds.shadingNode('RedshiftMaterial', asShader=True, n="%s_%s_%s_Skin"%(project,ch_name,type))
				shaderBody=1
			if 'body' in component:
				if body_set==0:
					sds_body=cmds.sets(empty=True, renderable=True, noSurfaceShader=True, n="%sSG"%body_shader)
					body_set=1
				cmds.connectAttr('%s'%body_shader + ".outColor", sds_body + ".surfaceShader", f=True)
				cmds.sets(i, e=True, forceElement=sds_body)
				
				
			if 'eyeshell' in component and shaderBoLiTi==0:
				boLiTi_shader = cmds.shadingNode('RedshiftMaterial', asShader=True, n="%s_%s_%s_BoLiTi"%(project,ch_name,type))
				shaderBoLiTi=1
			if 'eyeshell' in component:
				if eyeshell_set==0:
					sds_eyeshell=cmds.sets(empty=True, renderable=True, noSurfaceShader=True, n="%sSG"%boLiTi_shader)
					eyeshell_set=1
				cmds.connectAttr('%s'%boLiTi_shader + ".outColor", sds_eyeshell + ".surfaceShader", f=True)
				cmds.sets(i, e=True, forceElement=sds_eyeshell)
				
			from maya import cmds,mel
			if 'eyeEdge' in component and shaderYanJian==0:
				yanJian_shader = cmds.shadingNode('RedshiftMaterial', asShader=True, n="%s_%s_%s_YanJian"%(project,ch_name,type))
				shaderYanJian=1
			if 'eyeEdge' in component:
				if eyeEdg_set==0:
					sds_eyeEdg=cmds.sets(empty=True, renderable=True, noSurfaceShader=True, n="%sSG"%yanJian_shader)
					eyeEdg_set=1
				cmds.connectAttr('%s'%yanJian_shader + ".outColor", sds_eyeEdg + ".surfaceShader", f=True)
				cmds.sets(i, e=True, forceElement=sds_eyeEdg)
				
					
			if 'cartilage' in component and shaderYanJian_TouMing==0:
				touMing_shader = cmds.shadingNode('RedshiftMaterial', asShader=True, n="%s_%s_%s_YanJian_TouMing"%(project,ch_name,type))
				shaderYanJian_TouMing=1
			if 'cartilage' in component:
				if cartilage_set==0:
					sds_cartilage=cmds.sets(empty=True, renderable=True, noSurfaceShader=True, n="%sSG"%touMing_shader)
					cartilage_set=1
				cmds.connectAttr('%s'%touMing_shader + ".outColor", sds_cartilage + ".surfaceShader", f=True)
				cmds.sets(i, e=True, forceElement=sds_cartilage)
				
			if 'saliva' in component and shaderYanJian_TouMing==0:
				touMing_shader = cmds.shadingNode('RedshiftMaterial', asShader=True, n="%s_%s_%s_YanJian_TouMing"%(project,ch_name,type))
				shaderYanJian_TouMing=1
			if 'saliva' in component:
				if cartilage_set==0:
					sds_cartilage=cmds.sets(empty=True, renderable=True, noSurfaceShader=True, n="%sSG"%touMing_shader)
					cartilage_set=1
				cmds.connectAttr('%s'%touMing_shader + ".outColor", sds_cartilage + ".surfaceShader", f=True)
				cmds.sets(i, e=True, forceElement=sds_cartilage)
				
					
			if 'eyeball' in component and shaderYanQiu==0:
				yanQiu_shader = cmds.shadingNode('RedshiftMaterial', asShader=True, n="%s_%s_%s_YanQiu"%(project,ch_name,type))
				shaderYanQiu=1
			if 'eyeball' in component:
				if eyeYanQiu_set==0:
					sds_YanQiu=cmds.sets(empty=True, renderable=True, noSurfaceShader=True, n="%sSG"%yanQiu_shader)
					eyeYanQiu_set=1
				cmds.connectAttr('%s'%yanQiu_shader + ".outColor",sds_YanQiu + ".surfaceShader", f=True)
				cmds.sets(i, e=True, forceElement=sds_YanQiu)
		
					
			if 'eyelash' in component and shaderJieMao==0:
				jieMao_shader = cmds.shadingNode('RedshiftMaterial', asShader=True, n="%s_%s_%s_JieMao"%(project,ch_name,type))
				shaderJieMao=1
			if 'eyelash' in component:
				if eyelashShape_set==0:
					sds_eyelash=cmds.sets(empty=True, renderable=True, noSurfaceShader=True, n="%sSG"%jieMao_shader)
					eyelashShape_set=1
				cmds.connectAttr('%s'%jieMao_shader + ".outColor", sds_eyelash + ".surfaceShader", f=True)
				cmds.sets(i, e=True, forceElement=sds_eyelash)
				
			if 'teeth' in component and shaderKouQiang==0:
				kouQiang_shader = cmds.shadingNode('RedshiftMaterial', asShader=True, n="%s_%s_%s_KouQiang"%(project,ch_name,type))
				shaderKouQiang=1
			if 'teeth' in component:
				sds_teeth=cmds.sets(empty=True, renderable=True, noSurfaceShader=True, n="%sSG"%kouQiang_shader)
				cmds.connectAttr('%s'%kouQiang_shader + ".outColor", sds_teeth + ".surfaceShader", f=True)
				cmds.sets(i, e=True, forceElement=sds_teeth)
	
	
def shadeLink(*args):
	map_path=cmds.textField('texture_path',text=1,q=1)
	if map_path:
		texture_paths=[]
		for dirpath, dirnames, filenames in os.walk(map_path):
			for filename in filenames:
				if '1001' in filename:
					texture_paths.append(dirpath.replace('\\','/')+'/'+filename)
				#�����ļ����Ƿ��������.10xx
				elif len(filename.rsplit('/',1)[-1].rsplit('.'))==2:
					texture_paths.append(dirpath.replace('\\','/')+'/'+filename)
							
	
	cmds.select(all=1,hi=1)
	sel_objs=cmds.ls(sl=1)
	shade_names=[]
	for sel_obj in sel_objs:
		if cmds.nodeType(sel_obj)=='RedshiftMaterial':
			shade_names.append(sel_obj)
			
	#����������ƺ���ͼ·��		
	textureConnect(shade_names,texture_paths)
	
	
#����������ͼ�ڵ�
def textureConnect(shade_names,texture_paths):
	
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
	 

	
	for shade_name in shade_names:
		#�����������ͼ
		for texture_path in texture_paths:
			#�ж���ͼ���������Ƿ���������ƶ�Ӧ
			print(texture_path.split('_CH_',1)[-1].split('_',1)[0],shade_name.split('_CH_',1)[-1].split('_',1)[0])
			if texture_path.split('_CH_',1)[-1].split('_',1)[0]==shade_name.split('_CH_',1)[-1].split('_',1)[0]:
				#������ͼ�����������Ӧ��ͼ�ڵ�
				base_name=shade_name.split('_CH_')[-1]
				if 'BaseColor' in texture_path:
					f_name=base_name+'_BaseColor'
					t_name=base_name+'_BaseColor_Texture'
					#����file�ڵ��2dTexture�ڵ�
					cmds.shadingNode('file',name=f_name,asTexture=True,isColorManaged=True)
					cmds.shadingNode('place2dTexture',name=t_name,asUtility=True)
					#��file�ڵ��2dTexture�ڵ�����
					for attr_name in attr_names:
						cmds.connectAttr(t_name+attr_name[0],f_name+attr_name[1],f=1)
					#��file�ڵ������ͼ·��
					cmds.setAttr(f_name+'.fileTextureName', texture_path, type='string')
					#����file�ڵ�Ͳ�����
					cmds.connectAttr(f_name+'.outColor',shade_name+'.diffuse_color',f=1)
					#�����ͼ��׺Ϊ.1001��ʽ���������ͼ����ΪUDIM
					if '1001' in texture_path:
						cmds.setAttr(f_name+'.uvTilingMode', 3)
					
				if 'Emissive' in texture_path:
					f_name=base_name+'_Emissive'
					t_name=base_name+'_Emissive_Texture'
					cmds.shadingNode('file',name=f_name,asTexture=True,isColorManaged=True)
					cmds.shadingNode('place2dTexture',name=t_name,asUtility=True)
					
					for attr_name in attr_names:
						cmds.connectAttr(t_name+attr_name[0],f_name+attr_name[1],f=1)
						
					cmds.setAttr(f_name+'.fileTextureName', texture_path, type='string')
					cmds.connectAttr(f_name+'.outColor',shade_name+'.emission_color',f=1)
					if '1001' in texture_path:
						cmds.setAttr(f_name+'.uvTilingMode', 3)
						
				if 'ARMS' in texture_path:
					f_name=base_name+'_ARMS'
					t_name=base_name+'_ARMS_Texture'
					cmds.shadingNode('file',name=f_name,asTexture=True,isColorManaged=True)
					cmds.shadingNode('place2dTexture',name=t_name,asUtility=True)
					
					for attr_name in attr_names:
						cmds.connectAttr(t_name+attr_name[0],f_name+attr_name[1],f=1)
						
					cmds.setAttr(f_name+'.fileTextureName', texture_path, type='string')
					cmds.connectAttr(f_name+'.outColor.outColorG',shade_name+'.refl_roughness',f=1)
					cmds.connectAttr(f_name+'.outColor.outColorB',shade_name+'.refl_metalness',f=1)
					if '1001' in texture_path:
						cmds.setAttr(f_name+'.uvTilingMode', 3)
						
				if 'Specular' in texture_path:
					f_name=base_name+'_Specular'
					t_name=base_name+'_Specular_Texture'
					cmds.shadingNode('file',name=f_name,asTexture=True,isColorManaged=True)
					cmds.shadingNode('place2dTexture',name=t_name,asUtility=True)
					
					for attr_name in attr_names:
						cmds.connectAttr(t_name+attr_name[0],f_name+attr_name[1],f=1)
						
					cmds.setAttr(f_name+'.fileTextureName', texture_path, type='string')
					cmds.connectAttr(f_name+'.outColor',shade_name+'.refl_color',f=1)
					if '1001' in texture_path:
						cmds.setAttr(f_name+'.uvTilingMode', 3)
						
				if 'Normal' in texture_path:
					f_name=base_name+'_NormalMap'
					t_name=base_name+'_Normal_Texture'
					cmds.shadingNode('RedshiftNormalMap',name=f_name,asTexture=True,isColorManaged=True)
						
					cmds.setAttr(f_name+'.tex0',texture_path, type='string')
					cmds.connectAttr(f_name+'.outDisplacementVector',shade_name+'.bump_input',f=1)
					if '1001' in texture_path:
						cmds.setAttr(f_name+'.tex0',texture_path.replace('1001','<UDIM>'), type='string')
							

def jsonCreate(json_path):
	#����д��json�ļ����ֵ�
	shade_dict={}
	#ѡ�����ж���
	cmds.select(all=1,hi=1)
	sel_objs=cmds.ls(sl=1)
	#ʶ��redshift���ʣ�����ȡ��ͼ��Ϣ
	for sel_obj in sel_objs:
		if cmds.nodeType(sel_obj)=='RedshiftMaterial':
			print(sel_obj)
			shade_dict[sel_obj]=getTexture(sel_obj)
	
	#���������ƺͰ�������ͼ����Ϊjson�ļ�
	import json
	with open(json_path,'w') as json_file:
		json.dump(shade_dict,json_file)
	
	
def getTexture(shade_name):

	texture_files={}
	#��������
	mat_c=mat_n=mat_arms=mat_e=mat_sp=False
	#�������ӵ��ȡ��Ӧ�Ľڵ�
	if cmds.nodeType( shade_name )=='RedshiftMaterial':
		mat_c=cmds.connectionInfo(shade_name+'.diffuse_color',sfd=1)
		mat_n=cmds.connectionInfo(shade_name+'.bump_input',sfd=1)
		mat_arms=cmds.connectionInfo(shade_name+'.refl_roughness',sfd=1)
		mat_e=cmds.connectionInfo(shade_name+'.emission_color',sfd=1)
		mat_sp=cmds.connectionInfo(shade_name+'.refl_color',sfd=1)
	
	
	#��ȡ��ͼ�ڵ��ϵ���ͼ·��
	if mat_c:
		c_name=mat_c.split('.')[0]
		c_path=[]
		#��file�ڵ���ļ�·����¼
		c_path.append(cmds.getAttr(c_name+'.fileTextureName',x=True))
		#��·��д���ֵ�
		texture_files['c']=c_path

	if mat_n:
		n_name=mat_n.split('.')[0]
		n_path=[]
		n_path.append(cmds.getAttr(n_name+'.tex0',x=True))
		texture_files['n']=n_path

	if mat_arms:
		arms_name=mat_arms.split('.')[0]
		arms_path=[]
		arms_path.append(cmds.getAttr(arms_name+'.fileTextureName',x=True))
		texture_files['arms']=arms_path


	if mat_e:
		e_name=mat_e.split('.')[0]
		e_path=[]
		e_path.append(cmds.getAttr(e_name+'.fileTextureName',x=True))
		texture_files['e']=e_path

	if mat_sp:
		sp_name=mat_sp.split('.')[0]
		sp_path=[]
		sp_path.append(cmds.getAttr(sp_name+'.fileTextureName',x=True))
		texture_files['sp']=sp_path

	#�ռ��������UDIM��ͼ
	for k,v in texture_files.items():
		v_new=[]
		for dirpath, dirnames, filenames in os.walk(v[0].rsplit('/',1)[0]):
			for filename in filenames:
				if v[0].rsplit('/',1)[-1].split('.',1)[0] in filename:
					v_new.append(dirpath+'/'+filename)
					
		texture_files[k]=v_new

	return(texture_files)		
			
	
		
def cleanB(*arg):
	cmds.select(all=1,hi=1)
	sel_objs=cmds.ls(sl=1)
	objs=cmds.listRelatives(sel_objs,type='mesh')
	new_objs=[]
	for obj in objs:
		if 'hair' not in str(obj) and 'Hair' not in str(obj):
			new_objs.append(obj)
	cmds.select(new_objs)
	
	mel.eval('polyCleanupArgList 4 { "0","2","1","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" }')
	
def proPrefix(*args):
	cmds.select(all=1,hi=1)
	sel_objs=cmds.ls(sl=1)
	prefix=''
	for obj in sel_objs:
		if '_CH_Skin' in obj and cmds.nodeType(obj)=='RedshiftMaterial' and 'pasted_' not in obj:
			prefix=obj.split('_CH_',1)[0]+'_CH_'
			
			
			for sel_obj in sel_objs:
				if cmds.nodeType(sel_obj)=='RedshiftMaterial' and '_CH_' not in sel_obj:
					cmds.rename(sel_obj, prefix+sel_obj)
					
			break


def softE(*args):
	cmds.select(all=1,hi=1)
	mel.eval('polySetToFaceNormal')
	cmds.polySoftEdge( a=180 )
	
def exportFBX(*args):
		
	#����fbx��ʽ
	cmds.FBXResetExport()
	mel.eval('FBXExportFileVersion -v FBX201300')
	mel.eval('FBXExportSmoothingGroups -v true')
	mel.eval('FBXExportSmoothMesh -v true')
	
	#����fbx
	export_path=cmds.textField('export',text=1,q=1)
	mel.eval('FBXExport -f "%s" -s'%(export_path))

	#����Json�ļ�
	json_path=export_path.rsplit('.')[0]+'.json'
	jsonCreate(json_path)
	
def openFile(*args):
	file_name_new=str(cmds.fileDialog2(fileFilter="*.fbx",startingDirectory =str(cmds.file(q=1,sn=1)).rsplit('/',1)[0],rf=1)[0])
	cmds.textField('export',text=file_name_new,e=1)

def openFile_texture(*args):
	singleFilter="Ŀ¼"
	texture_path=str(cmds.fileDialog2(fileFilter=singleFilter,startingDirectory =str(cmds.file(q=1,sn=1)).rsplit('/',1)[0],fm=3)[0])
	cmds.textField('texture_path',text=texture_path,e=1)
	
	
def start():
	winName="������ɫ��������"
	if cmds.window(winName,q=1,ex=1):
		cmds.deleteUI(winName)
	win = cmds.window(winName,widthHeight=(380,310))
	column1=cmds.columnLayout( adjustableColumn=True )
	cmds.textFieldGrp('pj', label='��Ŀ������д', pht='��DDCT',w=50,cal=(1,'left'),cw2=(80,80))
	cmds.button( label='����ë����Ķ����',command=cleanB)
	cmds.button( label='����������������������',command=creB)
	
	
	cmds.separator( height=30, style='in' )
	
	cmds.button( label='ΪRS���������ǰ׺(���ȴ����������������)',command=proPrefix)
	cmds.text('ѡ����ͼ·��',align='left')
	cmds.setParent(column1)
	
	cmds.rowLayout( numberOfColumns=2, columnWidth2=(80, 75))
	cmds.textField('texture_path',w=350)
	cmds.symbolButton( image='circle.png',w=20,i="navButtonBrowse.xpm",c=openFile_texture)
	cmds.setParent(column1)
	
	cmds.button(label='Ϊ�������������ɫ��ͼ',command=shadeLink)
	cmds.separator( height=30, style='in' )
	cmds.setParent(column1)
	
	
	cmds.text('����ΪUEʹ�õ�FBX�ļ�',align='left')
	cmds.setParent(column1)
	
	cmds.rowLayout( numberOfColumns=2, columnWidth2=(80, 75))
	cmds.textField('export',w=350)
	cmds.symbolButton( image='circle.png',w=20,i="navButtonBrowse.xpm",c=openFile)
	cmds.setParent(column1)
	
	cmds.button(label='����ѡ���ģ�͵�ָ��λ��',command=exportFBX)
	cmds.setParent(column1)
	
	cmds.showWindow(win)
			
	

if __name__=='__main__':
	start()



