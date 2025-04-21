# -*- coding: utf-8 -*-

import maya.cmds as cmds
import pymel.core as pm


def bsToJoin(join_name,bs_name):
    join_name=join_name
    bs_name=bs_name
    bs_sel = cmds.aliasAttr(bs_name,q=1)
    index = 0 
    bs_list = [] 
    num = len(bs_sel)
    #将模型的blendshape名添加到列表中
    for i in bs_sel: 
        if(index %2 ==0): 
            bs_list.append(bs_sel[index])
        index+=1 
    for j in bs_list:
        
        if not cmds.objExists(join_name+'.'+j):
            print(bs_name+'.'+j,join_name+'.'+j)
            cmds.addAttr(join_name,ln = j,at = 'double',min = 0,max = 1,dv = 0)
            cmds.setAttr(join_name+'.'+j,keyable=True) 
            cmds.connectAttr(bs_name+'.'+j,join_name+'.'+j)
            
            




class win():
    def __init__(self):
        self.winName=u"模型BS链接到骨骼工具"
        if cmds.window(self.winName,q=1,ex=1):
            cmds.deleteUI(self.winName)
        cmds.window(self.winName,widthHeight=(300,80))
        self.UI()
        
    def UI(self):
        
        self.column=cmds.columnLayout(adjustableColumn=True)
        
        cmds.button( label=u'执行',command=self.execute)
        cmds.text(u'对所有选择的模型的BlendShape连接到Head_M骨骼,\n若未选择模型,则对所有模型进行操作')
        
    def execute(self,*args):
        meshs=[]
        print('===================================')
        #获取所有mesh
        sl_nodes=cmds.ls(sl=1)
        #判断是否选中模型,若没选中则选择所有模型
        if sl_nodes:
            meshs=sl_nodes
            
        else:
            if cmds.objExists('Geometry'):
                cmds.select('Geometry',hi=1)
                
            sel_meshs=pm.ls(sl=1,type='mesh')
            for sel_mesh in sel_meshs:
                
                mesh = sel_mesh.getParent()
                #pm.select(mesh,add=1)
                meshs.append(str(mesh))
            
            cmds.select(meshs)

        
        
        join_name=''
        if cmds.objExists('Head_M'):
            join_name='Head_M'
        else:
            pass
        
        for mesh in meshs:
            mesh_nodes=cmds.listHistory( mesh )
            cmds.select(mesh_nodes)
            if pm.ls(sl=1,type='blendShape'):
                bs_name=str(pm.ls(sl=1,type='blendShape')[0])
                print(bs_name)
            
                #bs_name=mesh+'_bs'
                if cmds.objExists(bs_name):
                    bsToJoin(join_name,bs_name)
    



def showUI():
    win()
    cmds.showWindow()

if __name__=='__main__':
    showUI()
 












