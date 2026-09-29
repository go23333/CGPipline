#!/usr/bin/python
# -*- coding: utf-8 -*-
import maya.cmds as mc
import re
from maya import OpenMaya as om
import maya.OpenMayaAnim as oma

class Matching:
    
    def getDagByName(self,name):
        """get dag path form a name or full name
        return The dag path of a name."""
        selectionList = om.MSelectionList()
        selectionList.add(name)
        pathNode = om.MDagPath()
        selectionList.getDagPath(0, pathNode)
        return pathNode
    
    def getMObjByName(self,name):
        """get MObject  form a name or full name
        return The MObject of a name.
        """
        selectionList = om.MSelectionList()
        selectionList.add(name)
        oNode = om.MObject()
        selectionList.getDependNode(0, oNode)
        return oNode
    # end getMObject
    
    def getMeshDeformer(self,name=None,_type="skinCluster"):
        """...shared/searchByName
        get skinCLuster from a geo"""
        result = None
        if name==None:
            name = mc.ls(sl=True,ap=1,fl=True)
        fterPoly = mc.filterExpand(name,sm=12)
        meshVertex = mc.filterExpand(name,sm=31)
        
        if fterPoly==None and meshVertex==None:#not polygon object and not polygon vertex
            self.mayaError("No one poly object no vertexs selected!")
            return
        elif fterPoly!=None and len(fterPoly)!=1 and meshVertex==None:#more than one object selected and it isn't poly vertex
            self.mayaError("No one poly object or no vertexs selected!")
            return
        elif meshVertex!=None:#poly vertex selected
            pmesh = mc.listRelatives(meshVertex[0],p=1,f=1)
            try:
                result = mc.ls(mc.listHistory(pmesh),type=_type)[0]#find skincluster
            except:
                #self.mayaError("Can't fint skinCluster!")
                return
        else:
            try:
                result = mc.ls(mc.listHistory(fterPoly[0]),type=_type)[0]#find skincluster
            except:
                #self.mayaError("Can't fint skinCluster!")
                return
        return result
        
    def searchControlShape(self,inObj):
        """
        Creation Date:  2014-04-04
        <doc>
        <name searchByName-->searchControlShape>
        <synopsis>
        		searchControlShape(str inObj)
        <description>
              Script for finding a shape that can deforms.
        <examples>
         // To find the skinCluster for a skin called "GreatZ", type:
         searchControlShape("GreatZ")
        """
        controlShape,controlShapeWithPath,hiddenShape,hiddenShapeWithPath = "","","",""
        #if conponent list input pick first
        if type(inObj)==list or type(inObj)==tuple and len(inObj)>0:
            inObj = inObj[0]
        if None!=re.search("\.",inObj):
            inObj = re.split("\.",inObj)[0]
        cpTest = mc.ls(inObj,type="controlPoint")
        if len(cpTest):
            return inObj
        else:
            rels = mc.listRelatives(inObj)
            if rels==None:
                return
            for r in rels:
                cpTest = mc.ls(inObj+"|"+r,type="controlPoint")
                if 0==len(cpTest):
                    continue
                io = mc.getAttr(inObj+"|"+r+".io")
                if io:
                    continue
                visible = mc.getAttr(inObj+"|"+r+".v")
                if 0==visible:
                    hiddenShape = r
                    hiddenShapeWithPath = (inObj+"|"+r)
                    continue
                controlShape = r
                controlShapeWithPath = (inObj+"|"+r)
                break
        for shape in [controlShape,controlShapeWithPath,hiddenShape,hiddenShapeWithPath]:
            if 0!=len(shape) and len( mc.ls(shape) )==1:
                return shape
                
    def findRelatedSkinCluster(self,skinObj=""):
        """
        Creation Date:  2014-04-04
        <doc>
        <name findRelatedSkinCluster>
        <synopsis>
        		findRelatedSkinCluster(str skinObj)
        <description>
              Script for finding a skin cluster that deforms the specified skin.
        <examples>
         // To find the skinCluster for a skin called "GreatZ", type:
         findRelatedSkinCluster("GreatZ")
        """
        if skinObj=="":
            selObjs = mc.ls(sl=True,ap=1,fl=True)
            if len(selObjs)>0:
                skinObj = selObjs[0]
            else:
                return
        shape = self.searchControlShape(skinObj)
        if shape==None:
            return
        clusters = mc.ls(type="skinCluster")
        for c in clusters:
            geom = []
            geomA = mc.skinCluster(c,q=True,g=True)
            geomB = mc.listConnections("%s.outputGeometry"%c,d=True,s=False,sh=True)
            for lst in [geomA,geomB]:
                if lst!=None:
                    geom+=lst
            for g in geom:
                if g == shape:
                    return c
        return
        
    def findRelatedBlendshape(self,bldObj=""):
        """
        Creation Date:  2014-04-04
        <doc>
        <name findRelatedBlendshape>
        <synopsis>
        		findRelatedBlendshape(str bldObj)
        <description>
              Script for finding a blendshape that deforms the specified blendShape
        <examples>
         // To find the blendShape for a bld called "GreatZ", type:
         findRelatedBlendshape("GreatZ")
        """
        resBls = []
        if bldObj=="":
            selObjs = mc.ls(sl=True,ap=1,fl=True)
            if len(selObjs)>0:
                bldObj = selObjs[0]
            else:
                return []
        shape = self.searchControlShape(bldObj)
        if shape==None:
            return []
        blendShapes = mc.ls(type="blendShape")
        for bls in blendShapes:
            geom = mc.blendShape(bls,q=True,g=True)
            if geom!=None:
                for g in geom:
                    if g == shape:
                        resBls.append(bls)
        return resBls
        
SearchByName = Matching()