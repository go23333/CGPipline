import maya.api.OpenMaya as om
import maya.cmds as cmds
import numpy as np

import time



def rayMeshIntersection(raySource, pointDirection, mainMeshDagPath,ray_inf,ray_reverse=False ):
    """
    计算射线与网格的交点。

    参数：
        raySource: 一个 MPoint 表示射线的起始点。
        rayDirection: 一个 MVector 表示射线的方向（应归一化）。
        mainMeshDagPath: 一个 MDagPath 指向网格。

    返回：
        一个元组，包含：
            - 一个 MPoint 表示交点（如果没有交点则为 None）。
            - 交叉多边形的索引（如果没有交点则为 None）。
    """
    
    rayDirection = (pointDirection - raySource).normal()
    base_distance = (pointDirection - raySource).length()

    # 创建网格多边形迭代器
    meshIter = om.MItMeshPolygon(mainMeshDagPath)

    closestIntersectionPoint = None
    closestIntersectionPolygonIndex = None
    
    #射线识别距离
    if ray_inf==False:
    #minDistance = float('inf')
        minDistance = base_distance
    else:
        minDistance = float('inf')
        
    #最接近的三角形
    tri_closes=None 
    #三角形顶点 
    tri_points=None
    #三角形顶点uv
    tri_uv=None

    while not meshIter.isDone():
        # 获取当前多边形的三个顶点
        
        for i in range(meshIter.numTriangles()):
            vertexIndex = meshIter.getTriangle(i)
            
            triangleVertices=vertexIndex[0]
    
            # 执行射线-三角形交点测试
            intersectionPoint = rayTriangleIntersection(raySource, rayDirection, triangleVertices,ray_reverse)
            
            #print(meshIter.index())
    
            if intersectionPoint:
                distance = (intersectionPoint - raySource).length()
                if distance < minDistance:
                    minDistance = distance
                    closestIntersectionPoint = intersectionPoint
                    closestIntersectionPolygonIndex = meshIter.index()
                    tri_closes = triangleVertices
                    tri_points = vertexIndex[1]
                    
        
        meshIter.next(1)
        #meshIter.index()
    if tri_points:
        main_fn_mesh = om.MFnMesh(mainMeshDagPath)
        #获取三角形的顶点
        a=main_fn_mesh.getPoint(tri_points[0])
        b=main_fn_mesh.getPoint(tri_points[1])
        c=main_fn_mesh.getPoint(tri_points[2])
        
        #获取三角形的uv顶点
        u_a,v_a,uv_a_id=main_fn_mesh.getUVAtPoint(a)
        u_b,v_b,uv_b_id=main_fn_mesh.getUVAtPoint(b)
        u_c,v_c,uv_c_id=main_fn_mesh.getUVAtPoint(c)
        
        #print(tri_points)
        uv_a = (u_a,v_a)
        uv_b = (u_b,v_b)
        uv_c = (u_c,v_c)
        tri_uv = [uv_a,uv_b,uv_c]
        
        #print(tri_uv)
    


    return closestIntersectionPoint, closestIntersectionPolygonIndex,tri_closes,tri_points,tri_uv
    
    
def worldSpaceToUV(tri,mid_point):
    
    v0, v1, v2 = tri
    
    
    #将三维世界坐标转换为以三角形第一个顶点为二维坐标原点(0,0)的二维三角形
    # 计算a的坐标
    x=(v0 - v1).length()#B到A的距离
    y=(v0 - v2).length()#C到A的距离
    z=(v1 - v2).length()#B到C的距离
    
    y1=(v0 - mid_point).length()#D到A的距离
    z1=(v1 - mid_point).length()#B到D的距离
    
    a = (x**2 + y**2 - z**2) / (2 * x)
    # 计算判别式D的值
    delta = (x + y + z) * (-x + y + z) * (x - y + z) * (x + y - z)
    sqrt_delta = math.sqrt(delta)
    # 计算b的值
    b = sqrt_delta / (2 * x)
    
    
    a1 = (x**2 + y1**2 - z1**2) / (2 * x)
    # 计算判别式D的值
    delta1 = (x + y1 + z1) * (-x + y1 + z1) * (x - y1 + z1) * (x + y1 - z1)
    sqrt_delta1 = math.sqrt(delta1)
    # 计算b的值
    b1 = sqrt_delta1 / (2 * x)
    
    
    tri_axis_a=(0,0)
    tri_axis_b=((v0 - v1).length(),0)
    tri_axis_c=(a,b)
    tri_axis_d=(a1,b1)
    
    #ABCD四个点的坐标
    tri_axis=[tri_axis_a,tri_axis_b,tri_axis_c,tri_axis_d]
    
    
    return tri_axis
    


def rayTriangleIntersection(raySource, rayDirection, triangleVertices,ray_reverse=False):
    """
    使用 Moller–Trumbore 算法执行射线-三角形交点测试。

    参数：
        raySource: 一个 MPoint 表示射线的起始点。
        rayDirection: 一个 MVector 表示射线的方向（应归一化）。
        triangleVertices: 包含三个 MPoint 的列表，表示三角形的顶点。

    返回：
        一个 MPoint 表示交点（如果没有交点则为 None）。
    """

    v0, v1, v2 = triangleVertices
    e1 = v1 - v0
    e2 = v2 - v0
    h = rayDirection ^ e2
    a = e1 * h
    if a > -1e-8 and a < 1e-8:  # 射线与三角形平行
        return None

    f = (raySource - v0) * h
    u = f / a
    if u < 0.0 or u > 1.0:
        return None

    s = (raySource - v0) ^ e1
    v = (rayDirection * s) / a
    if v < 0.0 or u + v > 1.0:
        return None

    t = (e2 * s) / a
    if t < 1e-8 and ray_reverse==False:  # 交点在射线起点后面
        return None

    return raySource + rayDirection * t
    
    
def edgeToPoint(edge_shell,subMeshDagPath,mainMeshDagPath,long_edges):
    
    # Get MFnMesh functions set for both
    fn_Mesh = om.MFnMesh(subMeshDagPath)
    
    # Create an iterator for the edges of the first mesh
    #sub_mesh_edge_iter = om.MItMeshEdge(subMeshDagPath)
        
    points_uv=[]
    
    #while not sub_mesh_edge_iter.isDone():
    for edge in edge_shell:
        # 获取边的顶点索引
        #vertex_ids = fn_Mesh.getEdgeVertices(sub_mesh_edge_iter.index())
        vertex_ids = fn_Mesh.getEdgeVertices(edge)
        
        # 获取边的起始点和结束点
        start_point = fn_Mesh.getPoint(vertex_ids[0], om.MSpace.kWorld)
        end_point = fn_Mesh.getPoint(vertex_ids[1], om.MSpace.kWorld)
        
        
        #获取射线碰撞点,多边形序号,碰撞三角形,碰撞三角形顶点,碰撞三角形顶点uv
        closest_point, polygon_index, tri_closes, tri_points, source_tri_uv = rayMeshIntersection(start_point, end_point, mainMeshDagPath,ray_inf=False)
        
        
        if closest_point:
            tri_world_to_uv = worldSpaceToUV(tri_closes,closest_point)
            #获取uv上的坐标点
            hit_u,hot_v = axisCalculate(tri_world_to_uv,source_tri_uv)
            
            #print("point:", closest_point)
            #print("uv:", hit_u,hot_v)
            point_uv=[hit_u,hot_v]
            #aa=cmds.polySphere(sx=4, sy=4, r=0.03)
            #cmds.move(closest_point[0],closest_point[1],closest_point[2])
            
            points_uv.append(point_uv)
        
        #击中点达到两个时跳出循环,节约算力
        if len(points_uv)>=2:
            break
            
            #print("polygon index:", polygon_index)
            #print("tri_closes index:", tri_closes)
            #print("edge index:", sub_mesh_edge_iter.index())

                
        #sub_mesh_edge_iter.next()
        
        
    #当击中的目标点小于2时,使用无限边缘射线重新计算
    if len(points_uv)<2:
        points_uv=[]
        for long_edge in long_edges:
            edge_to_vertexs = fn_Mesh.getEdgeVertices(long_edge)
            
            #print(long_edge,edge_to_vertexs)
            start_point=fn_Mesh.getPoint(edge_to_vertexs[0], om.MSpace.kWorld)
            end_point=fn_Mesh.getPoint(edge_to_vertexs[1], om.MSpace.kWorld)
            
            closest_point, polygon_index, tri_closes, tri_points, source_tri_uv = rayMeshIntersection(start_point, end_point, mainMeshDagPath,ray_inf=True,ray_reverse=True)
            
            if closest_point:
                tri_world_to_uv = worldSpaceToUV(tri_closes,closest_point)
                #获取uv上的坐标点
                hit_u,hot_v = axisCalculate(tri_world_to_uv,source_tri_uv)
                point_uv=[hit_u,hot_v]
                points_uv.append(point_uv)
        #print(points_uv)
                
            
    if len(points_uv)<2:
        return (None,None)
    
    #计算所有交叉点的平均值
    point_u_sum=0
    point_v_sum=0
    for uv in points_uv:
        point_u_sum+=uv[0]
        point_v_sum+=uv[1]

    point_u_mean=point_u_sum/len(points_uv)
    point_v_mean=point_v_sum/len(points_uv)
    
    return (point_u_mean,point_v_mean)



def axisCalculate(tri,source_tri_uv):

    # 原三角形顶点和点D的坐标
    A = tri[0]
    B = tri[1]
    C = tri[2]
    D = tri[3]
    
    # 新三角形顶点的坐标
    A_new_x,A_new_y=source_tri_uv[0]
    B_new_x,B_new_y=source_tri_uv[1]
    C_new_x,C_new_y=source_tri_uv[2]
    A_new = (0,0)
    B_new = (B_new_x-A_new_x,B_new_y-A_new_y)
    C_new = (C_new_x-A_new_x,C_new_y-A_new_y)
    
    # 解原质心坐标的线性方程组
    # 方程组:
    # 2γ = 1 → γ = 0.5
    # 5β + 3γ = 2 → β = (2 - 1.5)/5 = 0.1
    # α = 1 - β - γ = 0.4
    
    # 定义系数（请根据实际情况替换这些值）
    x_a, x_b, x_c, x_d = A[0], B[0], C[0], D[0]  # 示例值
    y_a, y_b, y_c, y_d = A[1], B[1], C[1], D[1]  # 示例值
    
    # 定义系数矩阵 A 和常数向量 b
    A = np.array([[x_a, x_b, x_c],
                  [y_a, y_b, y_c],
                  [1, 1, 1]])
    
    b = np.array([x_d, y_d, 1])
    
    try:
        x = np.linalg.solve(A, b)
        #print("解: α = %s, β = %s, γ = %s"%(x[0],x[1],x[2]))
        alpha = x[0]  
        beta = x[1]  
        gamma = x[2]  
        
        # 计算新点D的坐标
        D_new_x = alpha * A_new[0] + beta * B_new[0] + gamma * C_new[0] + A_new_x
        D_new_y = alpha * A_new[1] + beta * B_new[1] + gamma * C_new[1] + A_new_y
        
        #print("变形后点D的位置为: (%s, %s)"%(D_new_x, D_new_y))
        
        return (D_new_x, D_new_y)
        
    
    except np.linalg.LinAlgError as e:
        pass
        
        
        
def meshToEdgeShell(mesh_dagPath):

    mesh_vertex_iter=om.MItMeshVertex(mesh_dagPath)
    edge_mit=om.MItMeshEdge(mesh_dagPath)
    
    fn_mesh = om.MFnMesh(mesh_dagPath)
    
    #shell集合
    shells=[]
    new_shell=False
    #shell包含的点
    shell=[]
    vertex_shell=[]
    #根部边
    long_edges=[]
    root_edges=[]
    #shell点
    point_shell=[]
    point_shells=[]
    
    i=0    
    
    while not mesh_vertex_iter.isDone():
        
        #mesh_vertex_iter.index()
        
        connect_edges=mesh_vertex_iter.numConnectedEdges()
        
        edges=mesh_vertex_iter.getConnectedEdges()
        
        if connect_edges==2 and new_shell==False:
            if shell:
                shells.append(shell)
                #print(len(shells))
            if long_edges:
                root_edges.append(long_edges)
                #print(len(root_edges))
            #收集shell点
            if point_shell:
                point_shells.append(point_shell)
                
            shell=[]
            long_edges=[]
            point_shell=[]
            new_shell=True
            
        if connect_edges==2 and i<2:
            i+=1
            vertex_index=mesh_vertex_iter.index()
            test_vertexs=[vertex_index]
            
            edge_count=0
            long_edge=None
            for edge in edges:
                edge_mit.setIndex(edge)
                edge_to_vertexs=fn_mesh.getEdgeVertices(edge)
                for edge_to_vertex in edge_to_vertexs:
                    
                    if edge_to_vertex == vertex_index:
                        
                        pass
                    else:
                        #print(edge,edge_to_vertex)
                        #计算段数的递归函数
                        count=edgeRecursion(mesh_dagPath,edge,edge_to_vertex,index)
                        #比较段数
                        if edge_count<count:
                            edge_count=count
                            long_edge=edge
                        
            long_edges.append(long_edge)
            
        point_shell.append(mesh_vertex_iter.index())
                
                
        if connect_edges==3:
            new_shell=False
            i=0
        
        for edge in edges:
            edge_mit.setIndex(edge)
            if edge not in shell and edge_mit.onBoundary():
                shell.append(edge)
    
        mesh_vertex_iter.next()
        
    shells.append(shell)
    root_edges.append(long_edge)
    point_shells.append(point_shell)
    #print(shell)
    #print(long_edges)
        
        
    mesh_vertex_iter.reset()
        
    
    return shells,root_edges,point_shells
        
        

#通过递归查询面片段数
def edgeRecursion(mesh_dagPath,edge_index,vertex_index,index):
    #meshDag参数,边序号,点序号
    mesh_vertex_iter=om.MItMeshVertex(mesh_dagPath)
    edge_mit=om.MItMeshEdge(mesh_dagPath)
    fn_mesh = om.MFnMesh(mesh_dagPath)
    
    mesh_vertex_iter.setIndex(vertex_index)
    connect_edge_index=mesh_vertex_iter.numConnectedEdges()
    edges=mesh_vertex_iter.getConnectedEdges()
    
    #print(vertex_index)
    #判断点的连接边数量在等于3的时候获取当前点的下一个边
    if connect_edge_index==3:
        for edge in edges:
            edge_mit.setIndex(edge)
            if edge_mit.onBoundary() and edge != edge_index:
                edge_to_vertexs=fn_mesh.getEdgeVertices(edge)
                for edge_to_vertex in edge_to_vertexs:
                    if edge_to_vertex==vertex_index:
                        pass
                    else:
                        index = edgeRecursion(mesh_dagPath,edge,edge_to_vertex,index)
                        index+=1
                        return index

    else:
    
        index+=1
        return index


class Window():
    def __init__(self):
        self.winName="毛发UV映射"
        if cmds.window(self.winName,q=1,ex=1):
            cmds.deleteUI(self.winName)
        cmds.window(self.winName,widthHeight=(300,80))
        self.UI()

    def UI(self):
        
        self.column=cmds.columnLayout( adjustableColumn=True )
        
        cmds.button( label='执行',command=self.execute)
        cmds.text('先选择头发再选择头皮')
        
        
    def execute(self,*args):
        print('')
        start_time =time.time()
        meshs = cmds.ls(sl=1)
        hair_meshs = meshs[:-1]
        main_mesh = meshs[-1]
        for hair_mesh in hair_meshs:
            sel = om.MSelectionList()
            sel.add(main_mesh)
            sel.add(hair_mesh)
            mainMeshDagPath = om.MDagPath()
            hairMeshDagPath = om.MDagPath()
            mainMeshDagPath=sel.getDagPath(0)
            hairMeshDagPath=sel.getDagPath(1)
            
            #获取边缘边和多段起始边
            edge_shells,root_edges,point_shells=meshToEdgeShell(hairMeshDagPath)

            i=0    #列表序号
            for edge_shell in edge_shells:
                root_edge = root_edges[i]
                points = point_shells[i]
                
                hairMesh_u,hairMesh_v=edgeToPoint(edge_shell,hairMeshDagPath,mainMeshDagPath,root_edge)
                
                #print(hairMesh_u,hairMesh_v)
                
                #选择点设置uv值
                mel.eval('select -r %s.vtx[%s:%s] ;'%(hair_mesh,points[0],points[-1]))
                
                if hairMesh_u:
                    cmds.polyEditUV( relative=False, uValue=hairMesh_u, vValue=hairMesh_v )
                
                
                i+=1
                
        end_time =time.time()
        print(end_time-start_time)







if __name__=='__main__':
    Window()
    cmds.showWindow()


