#coding=utf-8

import maya.cmds as cmds
import maya.api.OpenMaya as om

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from functools import partial

from dayu_widgets.message import MMessage
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MClickBrowserFolderToolButton,MLineEdit
from dayu_widgets.push_button import MPushButton



def polygonCount():
    sel_nodes = cmds.ls(sl=1)
    cmds.select(sel_nodes,hi=1)
    sel_nodes = cmds.ls(sl=1)
    
    tri = 0
    quad = 0
    many = 0
    tri_id_dict = {}
    quad_id_dict = {}
    many_id_dict = {}
    for sel_node in sel_nodes:
        #判断对象是否为mesh
        if cmds.objectType(sel_node) == 'mesh':
            sel = om.MSelectionList()
            sel.add(sel_node)
            meshDagPath = om.MDagPath()
            meshDagPath = sel.getDagPath(0)
            fn_mesh = om.MFnMesh(meshDagPath)
            tris_count = fn_mesh.getTriangles()[0]
            faces = fn_mesh.getTriangles()[1]
            i = 0
            tri_id_dict[sel_node]=[]
            quad_id_dict[sel_node]=[]
            many_id_dict[sel_node]=[]
            for tri_count in tris_count:
                if tri_count==1:
                    tri += 1
                    tri_id_dict[sel_node].append(faces[i])
                elif tri_count==2:
                    quad += 1
                    quad_id_dict[sel_node].append(faces[i])
                else:
                    many += 1
                    many_id_dict[sel_node].append(faces[i])
                i+=1
                
    return(tri,quad,many,tri_id_dict,quad_id_dict,many_id_dict)



def faceCount():
    
    sel_nodes = cmds.ls(sl=1)
    cmds.select(sel_nodes,hi=1)
    sel_nodes = cmds.ls(sl=1)
    
    tri = 0
    quad = 0
    many = 0
    tri_id_dict = {}
    quad_id_dict = {}
    many_id_dict = {}
    for mesh in sel_nodes:
        # 获取网格形状节点的父变换节点
        #transform_node = cmds.listRelatives(mesh, parent=True, fullPath=True)[0]
        if cmds.objectType(mesh) == 'mesh':
            # 创建一个选择列表和迭代器用于遍历网格的面
            sel_list = om.MSelectionList()
            meshDagPath = om.MDagPath()
            sel_list.add(mesh)
            meshDagPath = sel_list.getDagPath(0)
            #meshDagPath.extendToShape()
            
            iter_poly = om.MItMeshPolygon(meshDagPath)
            
            tri_id_dict[mesh]=[]
            quad_id_dict[mesh]=[]
            many_id_dict[mesh]=[]
            
            # 遍历当前网格的每个面
            while not iter_poly.isDone():
                # 获取当前面的顶点数
                num_vertices = iter_poly.polygonVertexCount()
                if num_vertices == 3:
                    tri += 1
                    tri_id_dict[mesh].append(iter_poly.index())
                elif num_vertices == 4:
                    quad += 1
                    quad_id_dict[mesh].append(iter_poly.index())
                else:
                    many += 1
                    many_id_dict[mesh].append(iter_poly.index())
                    
                iter_poly.next(1)
                
    return(tri,quad,many,tri_id_dict,quad_id_dict,many_id_dict)


tri_count,quad_count,many_count,tri_id_dict,quad_id_dict,many_id_dict = faceCount()



cmds.select(clear=1)
for mesh,faces in quad_id_dict.items():
    if faces:
        for face in faces:
            cmds.select(mesh+'.f['+str(face)+']', add=True)




class ModelPolygonCountWindow(QWidget):

    def __init__(self,parent=None):
        super(ModelPolygonCountWindow,self).__init__(parent)

        self.tri_id_dict = None
        self.quad_id_dict = None
        self.many_id_dict = None

        self.ui()


    def ui(self):
  
        self.setWindowTitle(u'模型面数统计工具')
        self.resize(400,150)
        self.setStyleSheet("QWidget { background-color: #333333; }")
        lay=QVBoxLayout()

        tri_lay=QHBoxLayout()
        tri_label=MLabel(u'三边面数量')
        self.tri_count_label=MLabel(u'')
        tri_select_btn=MPushButton(u'选择三边面')
        tri_select_btn.clicked.connect(partial(self.selectFace,3))

        quad_lay=QHBoxLayout()
        quad_label=MLabel(u'四边面数量')
        self.quad_count_label=MLabel(u'')
        quad_select_btn=MPushButton(u'选择四边面')
        quad_select_btn.clicked.connect(partial(self.selectFace,4))

        many_lay=QHBoxLayout()
        many_label=MLabel(u'多边面数量')
        self.many_count_label=MLabel(u'')
        many_select_btn=MPushButton(u'选择多边面')
        many_select_btn.clicked.connect(partial(self.selectFace,5))
        
        tri_lay.addWidget(tri_label)
        tri_lay.addWidget(self.tri_count_label)
        tri_lay.addWidget(tri_select_btn)

        quad_lay.addWidget(quad_label)
        quad_lay.addWidget(self.quad_count_label)
        quad_lay.addWidget(quad_select_btn)

        many_lay.addWidget(many_label)
        many_lay.addWidget(self.many_count_label)
        many_lay.addWidget(many_select_btn)
        
        
        start_button=MPushButton(text=u"统计所选模型各类面的面数")
        start_button.clicked.connect(self.execute)
        
        
        hint_label=MLabel(u'')


        self.execute_data=QPlainTextEdit()
        self.execute_data.setStyleSheet("color: #cccccc; border :1px solid black")
        self.execute_data.setMinimumHeight(50)
        self.execute_data.setReadOnly(True)
                

        lay.addLayout(tri_lay)
        lay.addLayout(quad_lay)
        lay.addLayout(many_lay)
        lay.addWidget(start_button)
        # lay.addWidget(hint_label)
        
        
        self.setLayout(lay)

    def execute(self):
        tri_count,quad_count,many_count,tri_id_dict,quad_id_dict,many_id_dict = faceCount()
        self.tri_count_label.setText(str(tri_count))
        self.quad_count_label.setText(str(quad_count))
        self.many_count_label.setText(str(many_count))

        self.tri_id_dict = tri_id_dict
        self.quad_id_dict = quad_id_dict
        self.many_id_dict = many_id_dict


    def selectFace(self,e_count=None):
        if e_count==3:
            cmds.select(clear=1)
            for mesh,faces in self.tri_id_dict.items():
                if faces:
                    for face in faces:
                        cmds.select(mesh+'.f['+str(face)+']', add=True)
        elif e_count==4:
            cmds.select(clear=1)
            for mesh,faces in self.quad_id_dict.items():
                if faces:
                    for face in faces:
                        cmds.select(mesh+'.f['+str(face)+']', add=True)
        elif e_count==5:
            cmds.select(clear=1)
            for mesh,faces in self.many_id_dict.items():
                if faces:
                    for face in faces:
                        cmds.select(mesh+'.f['+str(face)+']', add=True)




def showUI():
    app=QApplication.instance()
    global win
    win=ModelPolygonCountWindow()
    win.show()
    win.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
    win.show()
    app.exec_()




if __name__=='__main__':
    showUI()



