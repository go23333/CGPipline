import maya.api.OpenMaya as om2







if __name__ == "__main__":
    sel_list = om2.MGlobal.getActiveSelectionList()
    #sel_list:om2.MSelectionList
    attrFromMesh = om2.MFnMesh(sel_list.getDagPath(0))
    attrToMesh = om2.MFnMesh(sel_list.getDagPath(1))

    for point in attrFromMesh.getPoints():
        u,v,faceid = attrFromMesh.getUVAtPoint(point)
        print(attrToMesh.getPointAtUV(faceid,u,v,tolerance = 0.0001))
