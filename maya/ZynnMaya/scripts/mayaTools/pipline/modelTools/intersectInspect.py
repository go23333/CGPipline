# coding=utf-8
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import pymel.core as pm
from maya import OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from PySide2.QtWidgets import *




def preciseIntersectPositions(obj1,obj2):

    dag_path1 = OpenMaya.MDagPath()
    dag_path2 = OpenMaya.MDagPath()
    sel = OpenMaya.MSelectionList()
    sel.add(obj1)
    sel.add(obj2)
    sel.getDagPath(0, dag_path1)
    sel.getDagPath(1, dag_path2)
    
    obj1_fn_Mesh = OpenMaya.MFnMesh(dag_path1)
    obj2_fn_Mesh = OpenMaya.MFnMesh(dag_path2)
    
    
    edge2_mit=OpenMaya.MItMeshEdge(pm.PyNode(obj2).__apiobject__())
    
    
    point_list=[]
    
    while not edge2_mit.isDone():
        
        start_point = edge2_mit.point(0,OpenMaya.MSpace.kWorld)
        end_point = edge2_mit.point(1,OpenMaya.MSpace.kWorld)
        
        rayDirection = (end_point - start_point)
        length = (start_point - end_point).length()
    
        hit_points = OpenMaya.MFloatPointArray()
        hit_ray_params = OpenMaya.MFloatArray()
        hit_faces = OpenMaya.MIntArray()
        
        has_int = obj1_fn_Mesh.allIntersections(
            OpenMaya.MFloatPoint(start_point.x,start_point.y,start_point.z), 
            OpenMaya.MFloatVector(rayDirection.x,rayDirection.y,rayDirection.z), 
            None,
            None,
            False,
            OpenMaya.MSpace.kWorld,
            1,
            False,
            None,
            False,
            hit_points,
            hit_ray_params,
            hit_faces,
            None,
            None,
            None,
            0.0001
        )
        if hit_points.length()>0:
            new_x = format(hit_points[0].x, ".3f")
            new_y = format(hit_points[0].y, ".3f")
            new_z = format(hit_points[0].z, ".3f")
            point_list.append([new_x,new_y,new_z])
            # print(hit_points[0].x,hit_points[0].y,hit_points[0].z)
            # print(new_x,new_y,new_z)
    
        edge2_mit.next()
    
    return point_list



def booleanIntersectPositions(obj1, obj2):
    positions_list=[]

    # 验证输入对象存在
    if not cmds.objExists(obj1) or not cmds.objExists(obj2):
        raise ValueError("One or both objects do not exist")


    # 执行布尔交集操作
    cmds.select(obj1, obj2)
    select_objs=cmds.ls(sl=1)
    intersect_name = obj1+'_itst_'+obj2
    new_objs=cmds.duplicate(select_objs)
    
    try:
        cmds.parent(new_objs,world=1)
    except:
        pass
    
    new_obj1=new_objs[0]
    new_obj2=new_objs[1]

    result = mel.eval('polyCBoolOp -op 3 -ch 1 -preserveColor 0 -classification 1 -name %s %s %s;'%(intersect_name,new_obj1,new_obj2))
    mel.eval('DeleteHistory')
     

    # 检查布尔运算结果
    if not result or not cmds.objExists(result[0]):
        print("Warning: No intersection found")
        return []

    intersection_mesh = result[0]
    
    try:
        cmds.polySeparate(intersection_mesh)
    except:
        pass
    mel.eval('DeleteHistory')
    
    new_intersection_meshs=cmds.ls(sl=1)
    
    for mesh in new_intersection_meshs:
            
        # 获取所有顶点世界坐标
        vertices = cmds.ls(mesh+".vtx[*]", flatten=True)
        sum_x=0
        sum_y=0
        sum_z=0
        i=0
        if vertices:
            for vtx in vertices:
                pos = cmds.xform(vtx, query=True, translation=True, worldSpace=True)
                sum_x += pos[0]
                sum_y += pos[1]
                sum_z += pos[2]
                i+=1
                
            average_x = sum_x/i
            average_y = sum_y/i
            average_z = sum_z/i

            positions_list.append([average_x,average_y,average_z])
        
        else:
            positions_list=None

        #删除布尔文件
        cmds.select(mesh)
        mel.eval('doDelete')

    #删除布尔文件   
    if cmds.objExists(intersection_mesh):
        cmds.select(intersection_mesh)
        mel.eval('doDelete')  
    #删除空文件
    for new_obj in new_objs:
        if cmds.objExists(new_obj):
            cmds.select(new_obj)
            mel.eval('doDelete')       

    return positions_list
        
        
        
         
        
class IntersectInspectWin(MayaQWidgetDockableMixin, QWidget):
    
    
    def __init__(self,parent=None):
        super(IntersectInspectWin, self).__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        
        self.setWindowTitle('检测所选模型穿插')
        
        self.resize(420,120)
        
        # 直接设置布局到当前widget
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        base_label=QLabel('选择需要检测的模型后点击执行')
        
        precise_btn = QPushButton("精细执行")
        precise_btn.clicked.connect(self.preciseButton)
        rough_btn = QPushButton("粗略执行")
        rough_btn.clicked.connect(self.roughButton)

        # 创建列表控件
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(160)
        # 连接选择改变信号
        self.list_widget.itemSelectionChanged.connect(self.selection_changed)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)  # 初始隐藏        
        
        
        layout.addWidget(base_label)
        layout.addWidget(precise_btn)
        layout.addWidget(rough_btn)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.progress_bar)

    
    def selection_changed(self,*args):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            selected_text = selected_items[0].text()
            obj1 = selected_text.split('_itst_')[0]
            obj2 = selected_text.split('_itst_')[-1]
            cmds.select(obj1,obj2,selected_text)
            print("Selection changed to: "+selected_text)


    def preciseButton(self,*args):
        self.execute(precise_switch=True)

    def roughButton(self,*args):
        self.execute(precise_switch=False)


    def execute(self,precise_switch):
        select_objs = cmds.ls(sl=1)
        self.progress_bar.setVisible(True)
        # perms = list(itertools.permutations(select_objs,2))
        groups = []
        perms=[]
        i=1
        #对选择的模型进行排列组合
        for select_obj_1 in select_objs[:-1]:
            for select_obj_2 in select_objs[i:]:
                perms.append([select_obj_1,select_obj_2])
            i+=1

        self.progress_bar.setRange(0, len(perms))
        progress_count = 0
        if precise_switch:
            for perm in perms:
                progress_count += 1
                self.progress_bar.setValue(progress_count)
                obj1 = perm[0]
                obj2 = perm[1]
                # print(obj1,obj2)
                intersect_positions = preciseIntersectPositions(obj1,obj2)
                intersect_name = obj1+'_itst_'+obj2
                if intersect_positions:
                    creat_group = self.intersectPointCreate(intersect_positions,intersect_name)
                    if creat_group:
                        groups.append(intersect_name)

        else:
            for perm in perms:
                progress_count += 1
                self.progress_bar.setValue(progress_count)
                obj1 = perm[0]
                obj2 = perm[1]
                # print(obj1,obj2)
                intersect_positions = booleanIntersectPositions(obj1,obj2)

                intersect_name = obj1+'_itst_'+obj2
                if intersect_positions:
                    creat_group = self.intersectPointCreate(intersect_positions,intersect_name)
                    if creat_group:
                        groups.append(intersect_name)
        
        self.list_widget.clear()
        print(groups)
        for group in groups:
            self.list_widget.addItem(group)

        self.progress_bar.setVisible(False)


    def intersectPointCreate(self,intersect_positions,intersect_name):
        create_group = False
        
        if intersect_positions:
            #创建收纳组
            group_name = intersect_name
            if not cmds.objExists(group_name):
                cmds.group(em=1,n=group_name)
            #生成穿插点
            for intersect_position in intersect_positions:
                point_mesh=cmds.polySphere( n=intersect_name+'_point', sx=3, sy=3,radius=0.2)
                cmds.move( intersect_position[0], intersect_position[1], intersect_position[2])
                cmds.parent(point_mesh,group_name)
                create_group = True

        return create_group



    



def showUI():
    global _ui
    try:
        _ui.close()
        _ui.deleteLater()
    except:
        pass

    window = IntersectInspectWin()
    window.show()
    _ui = window

if __name__=='__main__':
    showUI()