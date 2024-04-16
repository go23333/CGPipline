#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
##################################################################
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import pymel.core as pm
import maya.cmds as cmds

from Qt import QtWidgets,QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.item_view import MListView

class testWindow(MayaQWidgetDockableMixin,QtWidgets.QWidget):
    def __init__(self):
        super(testWindow,self).__init__()
        self.resize(400,300)
        self.setWindowTitle(u"测试工具")
        self.__init_ui()
        self.stateA = []
        self.stateB = []
    def __init_ui(self):
        layMain = QtWidgets.QHBoxLayout()

        layLeft = QtWidgets.QHBoxLayout()
        self.layerList =MListView()
        layLeft.addWidget(self.layerList)

        layRight = QtWidgets.QVBoxLayout()
        btnLoadFromMesh = MPushButton(u"从选中的模型载入")
        btnaddLayer = MPushButton(u"新建层")

        layRight.addWidget(btnLoadFromMesh)
        layRight.addWidget(btnaddLayer)




        layMain.addLayout(layLeft)
        layMain.addLayout(layRight)
        self.setLayout(layMain)








def n( name ):
    sellist = om.MGlobal.getSelectionListByName( name )
    try:
        return sellist.getDagPath(0)
    except:
        return sellist.getDependNode(0)




def test():
    import time
    currenttime = time.time()



    selectList = om.MGlobal.getActiveSelectionList()
    mfnMesh0 = om.MFnMesh(selectList.getDagPath(0))
    mfnMesh1 = om.MFnMesh(selectList.getDagPath(0))

    iterVertexCount = min(mfnMesh0.numVertices,mfnMesh1.numVertices)

    

    for verID in range(iterVertexCount):
        u,v,_  = mfnMesh0.getUVAtPoint(mfnMesh0.getPoint(verID))
        closestPoints = mfnMesh1.getClosestUVs(u,v)
        print(closestPoints)



    # colors = om.MColorArray()
    
    # for verID in range(mfnMesh0.numVertices):
    #    #u,v,_ = mfnMesh0.getUVAtPoint(mfnMesh0.getPoint(verID))
    #    normal = mfnMesh0.getVertexNormal(verID,False)

    #    colors.append(om.MColor((normal.x,normal.y,normal.z)))


    # mfnMesh0.setVertexColors(colors,om.MIntArray(range(mfnMesh0.numVertices)))
       



    print(u"耗时:{0}".format(time.time()-currenttime))
    




    


    # sourceSkinfn = oma.MFnSkinCluster(n("skinCluster1"))

    # sourceMeshDagPath = n("meshSource")
    # sourceMeshVerItfn = om.MItMeshVertex(sourceMeshDagPath)

    # sourceVertexComp = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
    # sourceWeightData = sourceSkinfn.getWeights(sourceMeshDagPath,sourceVertexComp)

    # data = sourceWeightData[0]
    # jointCount = sourceWeightData[1]

    


    # targetSkinfn = oma.MFnSkinCluster(n("skinCluster2"))

    # targetMeshDagPath = n("meshTarget")

    # targetMesh = om.MFnMesh(targetMeshDagPath)
    # targetMeshVerItfn = om.MItMeshVertex(targetMeshDagPath)


    # targetWeightData = [i for i in range(len(data))]
    # while not sourceMeshVerItfn.isDone():
    #     currentIndex = sourceMeshVerItfn.index()
    #     u,v = sourceMeshVerItfn.getUV()
    #     closestPoint = targetMesh.getPointsAtUV(u,v,tolerance=0.001)
    #     closestPointIndex = closestPoint[0][0]
    #     for jc in range(jointCount):
    #         targetWeightData[closestPointIndex * jointCount+jc] = data[currentIndex * jointCount+jc]
    #     break
    #     sourceMeshVerItfn.next()
    # print(targetWeightData)


def tests():

    skinCluster = "skinCluster103"
    meshShape = "face_facebs1Shape"

    skinNode = n(skinCluster)
    skinfn = oma.MFnSkinCluster(skinNode)

    meshPath = n(meshShape)

    meshNode = meshPath.node()


    meshVerItfn = om.MItMeshVertex(meshNode)
    indices = range(meshVerItfn.count())


    singleIdComp = om.MFnSingleIndexedComponent()
    vertexComp = singleIdComp.create(om.MFn.kMeshVertComponent)
    singleIdComp.addElements(indices)

    infDags = skinfn.influenceObjects()
    infIndexes = om.MIntArray(len(infDags),0)
    for x in range(len(infDags)):
        infIndexes[x] = int(skinfn.indexForInfluenceObject(infDags[x]))

    weightData = skinfn.getWeights(meshPath,vertexComp)

    weights = weightData[0]
    offset = weightData[1]
    skinfn.setWeights( meshPath , vertexComp , infIndexes , weightData[0] )
    
    
    
        # win = testWindow()
    # win.show(dockable=True)
    selection = om.MGlobal.getActiveSelectionList()
    dagPath = selection.getDagPath(0)

    mfnMesh = om.MFnMesh(dagPath)
    cmds.meshRemap
    points = mfnMesh.getPoints(om.MSpace.kWorld)
    rpoints = reversed(points)
    mfnMesh.setPoints(rpoints,om.MSpace.kWorld)
    
