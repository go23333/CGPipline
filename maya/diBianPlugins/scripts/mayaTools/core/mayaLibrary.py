#coding=utf-8
import math
import re

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om

import mayaTools.core.pathLibrary as PL
from mayaTools.core.log import log
import os




class TextureNode(object):
    def __init__(self):
        self.nodeName = None
        self.nodeType = None
        self.TextureDir = None
        self.TextureValue = None
        self.TextureList = []
 


materialNodeNames = ['lambert','blinn','RedshiftMaterial','RedshiftArchitectural']

def getScenename():
    scenename = cmds.file(q=True, sn=True).split('/')[-1]
    suffix = scenename.split('_CH')[-1]
    return(scenename.replace(suffix,''))

def getScenename_real():
    scenename = cmds.file(q=True, sn=True).split('/')[-1]
    return(scenename.split('.')[0])

def getSelectNodes(long=False):
    return(cmds.ls(selection=True,l=long))

def filterNode(Nodes,NodeType):
    filteredNode = []
    for node in Nodes:
        if cmds.nodeType(node) == NodeType:
            filteredNode.append(node)
    return(filteredNode)


def getShape(TransformNode):
    shape = cmds.listRelatives(TransformNode,type='mesh')
    if shape == None:
        return shape
    else:
        return shape[0]

def getshapes(transformNodes):
    shapeNodes = []
    for Node in transformNodes:
        if getShape(Node) == None:
            continue
        shapeNodes.append(getShape(Node))
    return(shapeNodes)

def getOneMeshMaterials(shapeNode):
    sg = cmds.listConnections(shapeNode,type='shadingEngine')
    shaders = cmds.ls(cmds.listConnections(sg),materials=1)
    return(shaders)

def getOneMeshSG(shapeNode):
    sg = cmds.listConnections(shapeNode,type='shadingEngine')
    return(list(set(sg)))

def getMaterials(shapeNodes):
    materialList = []
    for shapeNode in shapeNodes:
        for material in getOneMeshMaterials(shapeNode):
            if material not in materialList:
                materialList.append(material)
    return(materialList)

def SearchKeyWordFromPaths(Paths,KeyWord):
    filteredPaths = []
    for Path in Paths:
        if KeyWord in Path:
            filteredPaths.append(Path)
    return(filteredPaths)

def DelAllInputConnections(Node):
    if cmds.listConnections(Node,d=False) != None:
        for node in cmds.listConnections(Node,d=False):
            try:
                cmds.delete(node)
            except:
                pass

def createFileTexture(fileTextureName, p2dName):
    tex = pm.shadingNode('file', name=fileTextureName, asTexture=True, isColorManaged=True)
    if not pm.objExists(p2dName):
        pm.shadingNode('place2dTexture', name=p2dName, asUtility=True)
    p2d = pm.PyNode(p2dName)
    tex.filterType.set(0)
    pm.connectAttr(p2d.outUV, tex.uvCoord)
    pm.connectAttr(p2d.outUvFilterSize, tex.uvFilterSize)
    pm.connectAttr(p2d.vertexCameraOne, tex.vertexCameraOne)
    pm.connectAttr(p2d.vertexUvOne, tex.vertexUvOne)
    pm.connectAttr(p2d.vertexUvThree, tex.vertexUvThree)
    pm.connectAttr(p2d.vertexUvTwo, tex.vertexUvTwo)
    pm.connectAttr(p2d.coverage, tex.coverage)
    pm.connectAttr(p2d.mirrorU, tex.mirrorU)
    pm.connectAttr(p2d.mirrorV, tex.mirrorV)
    pm.connectAttr(p2d.noiseUV, tex.noiseUV)
    pm.connectAttr(p2d.offset, tex.offset)
    pm.connectAttr(p2d.repeatUV, tex.repeatUV)
    pm.connectAttr(p2d.rotateFrame, tex.rotateFrame)
    pm.connectAttr(p2d.rotateUV, tex.rotateUV)
    pm.connectAttr(p2d.stagger, tex.stagger)
    pm.connectAttr(p2d.translateFrame, tex.translateFrame)
    pm.connectAttr(p2d.wrapU, tex.wrapU)
    pm.connectAttr(p2d.wrapV, tex.wrapV)
    return tex
def createNormalMap(NormalMapname):
    tex = pm.shadingNode('RedshiftNormalMap', name = NormalMapname,asTexture=True, isColorManaged=True)
    return tex
def createRSMaterial(name=None):
    if name == None:
        material = pm.shadingNode('RedshiftMaterial',asShader=True)
    else:
        material = pm.shadingNode('RedshiftMaterial', name = name,asShader=True)
    return(material)
def connectMaterial(material,TexturePaths,Type):
    if TexturePaths == []:
        return False
    TexturePath = TexturePaths[0]
    UDIMMode = 0
    if len(TexturePaths) > 1:
        TexturePath = TexturePath.replace(PL.IsUDIMFormate(TexturePath),'.<UDIM>.')
        UDIMMode = 3
    fileName = TexturePath.split('/')[-1].split('.')[0]
    if Type == 'BaseColor':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.connectAttr(TexNode+'.outColor',material+'.diffuse_color')
        return True
    elif Type == 'ARMS':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.connectAttr(TexNode+'.outColorG',material+'.refl_roughness')
        cmds.connectAttr(TexNode+'.outColorB',material+'.refl_metalness')
        return True
    elif Type == 'Normal':
        TexNode = createNormalMap(fileName)
        cmds.setAttr(TexNode+'.tex0',TexturePath,type = 'string')
        cmds.connectAttr(TexNode+'.outDisplacementVector',material+'.bump_input')
        return True
    elif Type == 'Anisotropy':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.connectAttr(TexNode+'.outAlpha',material+'.refl_aniso')
        return True
    elif Type == 'Mask':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.connectAttr(TexNode+'.outColor',material+'.opacity_color')
        return True
    elif Type == 'Opacity':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.connectAttr(TexNode+'.outAlpha',material+'.refr_weight')
        return True
    elif Type == 'Emissive':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.connectAttr(TexNode+'.outColor',material+'.emission_color')
        return True
    elif Type == 'Occlusion':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.connectAttr(TexNode+'.outColor',material+'.coat_color')
        return True
    elif Type == 'Roughness':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.connectAttr(TexNode+'.outAlpha',material+'.refl_roughness')
        return True
    elif Type == 'Cavity':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.connectAttr(TexNode+'.outAlpha',material+'.coat_weight')
        return True
    elif Type == 'Metallic':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.connectAttr(TexNode+'.outAlpha',material+'.refl_metalness')
        return True
    elif Type == 'Specular':
        TexNode = createFileTexture(fileName+'_File',fileName+'_Place2D')
        cmds.setAttr(TexNode+'.uvTilingMode',UDIMMode)
        cmds.setAttr(TexNode+'.fileTextureName',TexturePath,type = 'string')
        cmds.connectAttr(TexNode+'.outColor',material+'.refl_color')
        return True
    else:
        return False
def deleteUnusedNode():
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')


def fileDialog(title,Mode,des=None):
    res = cmds.fileDialog2(dialogStyle=1,caption=title,fileMode=Mode)
    if res != None:
        res = PL.normailizePath(res[0])
    else:
        res = ''
    if des != None:
        cmds.textField(des,text=res,e=1)
    return res



def progressWidow(title,currentamout = 0):
    PW = cmds.progressWindow(title = title,progress = currentamout,status = u'处理中...')
    return PW
def updateProgress(currentamout,max):
    cmds.progressWindow(edit=True, progress=int(currentamout/float(max)*100))
    if cmds.progressWindow(query=True, progress=True ) >= 100 :
        cmds.progressWindow(endProgress=1)
        return True


def exportABC(object,sFrame,eFrane,path):
    cmds.loadPlugin( 'AbcExport.mll' )
    cmds.loadPlugin( 'AbcImport.mll' )
    command = "-frameRange " + str(sFrame) + " " + str(eFrane) +" -stripNamespaces -uvWrite -writeColorSets -writeFaceSets -dataFormat ogawa -root " + object + " -file " + path
    cmds.AbcExport ( j = command )

def exportABC_gromm(objects,sFrame,eFrane,path):
    cmds.loadPlugin( 'AbcExport.mll' )
    cmds.loadPlugin( 'AbcImport.mll' )
    command = "-frameRange " + str(sFrame) + " " + str(eFrane) +" -attr groom_group_id -uvWrite -writeFaceSets -dataFormat ogawa -root " + objects + " -file " + path
    cmds.AbcExport ( j = command )

def exportxgenABC(filepath,nodes=None,start_frame=1, end_frame=1):
    command = ( ' -file '+ filepath+
                ' -df "ogawa" -fr '+ str(start_frame)+
                ' '+ str(end_frame)+ ' -step 1  -wfw'
    )
    nodecommand = ''
    for node in nodes:
        nodecommand = nodecommand + " -obj " + node
    command = nodecommand + command
    cmds.xgmSplineCache(export=True, j=command)
def exportOBJ(object,path):
    cmds.loadPlugin( 'objExport.mll' )
    cmds.select(object)
    cmds.file(path,pr=1,typ="OBJexport",es=1, force=True ,op="groups=0; ptgroups=0; materials=0; smoothing=0; normals=0")
    cmds.select( clear=True )
def importobjfile(filepath):
    newnodes = cmds.file(filepath, i=True,rnn=True)
    for newnode in newnodes:
        if cmds.nodeType(newnode) == 'transform' and len(cmds.listRelatives(newnode,shapes=True))!=0:
            return(newnode)
def importgroomabc(filepath):
    newnodes = cmds.file(filepath, i=True,rnn=True)
    return newnodes
def createNewUvset(obj,name):
    newvset = cmds.polyUVSet(obj,create=True)[0]
    cmds.polyUVSet(obj,rename=True,uvSet=newvset,newUVSet='vat1')
    return True

def exportFBXStatic(object,path):
    cmds.select( clear=True )
    cmds.select(object)
    keyword = ['Fbx','FBX export']
    # NOTE 防止maya出现fbx导出名称不一致的问题
    for key in keyword:
        try:
            cmds.file( path, force=1, type=key, op='groups=1', pr=1, es=1)
            break
        except:
            pass
    cmds.select( clear=True )

def export_fbx_without_dialog(object,path):
    pm.mel.FBXExport(object,f=path,s=1)
    
def import_fbx_without_dialog(fbxfile):
    beforeImportNodes = pm.ls(long=1)
    mel.eval('FBXImport -f "{0}"'.format(fbxfile))
    afterImportNodes = pm.ls(long=1)
    newNodes = [node for node in afterImportNodes if node not in beforeImportNodes]
    return(newNodes)


def getAllRepeatNodes():
    templist = []
    repeatNode = {}
    for node in cmds.ls(l=True):
        sname = node.split('|')[-1]
        if sname not in templist:
            templist.append(sname)
        else:
            repeatNode[sname] = node
    return repeatNode

def renameDuplicates():
    #Find all objects that have the same shortname as another
    #We can indentify them because they have | in the name
    duplicates = [f for f in cmds.ls() if '|' in f]
    #Sort them by hierarchy so that we don't rename a parent before a child.
    duplicates.sort(key=lambda obj: obj.count('|'), reverse=True)
     
    #if we have duplicates, rename them
    if duplicates:
        for name in duplicates:
            # extract the base name
            m = re.compile("[^|]*$").search(name) 
            shortname = m.group(0)
 
            # extract the numeric suffix
            m2 = re.compile(".*[^0-9]").match(shortname) 
            if m2:
                stripSuffix = m2.group(0)
            else:
                stripSuffix = shortname
             
            #rename, adding '#' as the suffix, which tells maya to find the next available number
            newname = cmds.rename(name, (stripSuffix + "#")) 
            print("renamed %s to %s" % (name, newname))
             
        return "重命名%s个对象" % len(duplicates)
    else:
        return u'未发现命名重复物体'

def DialogBoxCheck(title,Text):
    resoult = cmds.confirmDialog( title = title, 
                        message=Text, 
                        button=[u'是',u'否'], 
                        defaultButton=u'是', 
                        cancelButton=u'否', 
                        dismissString=u'否' )
    if resoult == u'是':
        return True
    else:
        return False
def AssignMaterialToTransformNode(Object,Material):
    cmds.select(Object)
    cmds.hyperShade(assign=Material)
    cmds.select( clear=True )


def aoLayerOverlay(arg=1):
    currentLayer = cmds.editRenderLayerGlobals(q=1,crl=1)
    layerObjects = cmds.editRenderLayerMembers(currentLayer,q=1)
    if DialogBoxCheck(u'警告',u'是否要把层{}的材质覆盖为AO材质'.format(currentLayer)):
        RsAONode = cmds.createNode('RedshiftAmbientOcclusion',n='RSAONODE_')
        cmds.setAttr(RsAONode+'.numSamples',256)
        RsISNode = cmds.createNode('RedshiftIncandescent',n='RSISNODE_')
        RsISSGNode = cmds.createNode('shadingEngine',n=RsISNode+'_SG')
        MaterialInfoNode = cmds.createNode('materialInfo',n=RsISNode+'_materialInfo')
        cmds.connectAttr(RsAONode+'.outColor',RsISNode+'.color')
        cmds.connectAttr(RsISNode+'.outColor',RsISSGNode+'.surfaceShader')
        cmds.connectAttr(RsISSGNode+'.message',currentLayer+'.shadingGroupOverride')
        cmds.connectAttr(RsISSGNode+'.message',MaterialInfoNode+'.shadingGroup')
        # assigne Material to shape
        for Object in layerObjects:
            AssignMaterialToTransformNode(Object,RsISNode)
    else:
        cmds.warning(u'操作被取消')

def getNodesRelativesByType(Nodes,type):
    returnNodes = []
    for node in Nodes:
        returnNodes = returnNodes + cmds.listRelatives(node,type=type)
    return returnNodes

def getKeyFrameRange(Node):
    keyFrames = cmds.keyframe(Node, q=True)
    if keyFrames != None:
        maxframe = math.ceil(max(keyFrames))
        minframe = math.floor(min(keyFrames))
        return(minframe,maxframe)
    else:
        return(0,0)


def setFrameRange(s,e):
    cmds.playbackOptions(min = s,ast=s)
    cmds.playbackOptions(max = e,aet=e)


def scaleFrameValue(attr,times):
    if cmds.keyframe(attr, q=True) == None:
        currentvalue = cmds.getAttr(attr)
        cmds.setAttr(attr,currentvalue*times)
    else:
        for i in cmds.keyframe(attr, q=True):
            currentvalue = cmds.keyframe(attr,t = (i,i),valueChange=1,q=1)[0]
            cmds.setKeyframe(attr,t = (i,i),v =currentvalue*times)


def recursionGroup(templist,group):
    ChildrenNodes = cmds.listRelatives(group,c=1)
    if ChildrenNodes == None:
        return templist
    for Children in ChildrenNodes:
        if cmds.listRelatives(Children,s=1) == None:
            recursionGroup(templist,Children)
        else:
            templist.append(Children)
    return templist

def exportGpuCache(obj,ExportPath):
    import os
    file_dir, file_name = os.path.split(ExportPath)
    file_name = file_name.replace('.abc','')
    pm.gpuCache(obj,directory=file_dir,fileName=file_name,dataFormat='ogawa',startTime=1,endTime=1,optimizationThreshold=40000,optimize=1,useBaseTessellation=False,writeMaterials=1,)
    


def GetAllTextureNodes():
    textureNodes = []
    fileNodes = pm.ls(type="file")
    normalNodes = pm.ls(type="RedshiftNormalMap")
    SpriteNodes = pm.ls(type="RedshiftSprite")
    allTextureNodes = fileNodes + normalNodes + SpriteNodes
    for node in allTextureNodes:
        myTextureNode = TextureNode()
        myTextureNode.nodeName = node.name()
        myTextureNode.nodeType = pm.nodeType(node)
        if myTextureNode.nodeType == 'file':
            attrName = "fileTextureName"
        else:
            attrName = "tex0"
        myTextureNode.TextureValue = node.getAttr(attrName)
        myTextureNode.TextureDir = os.path.normpath(os.path.split(myTextureNode.TextureValue)[0])
        TextureList = PL.getUDIMTextures(myTextureNode.TextureValue )
        for texture in TextureList:
            myTextureNode.TextureList.append(dict(path = texture,exist=os.path.exists(texture)))
        textureNodes.append(myTextureNode)
    return textureNodes

def GetMeshBaseFileNode(filenode):
    materials = []
    for nodeName in materialNodeNames:
        materials += pm.listConnections(filenode,c=False,t=nodeName)
    transfroms = []
    for m in materials:
        for sg in pm.listConnections(m,c=False,type="shadingEngine"):
            transfroms += [node for node in sg.inputs() if pm.nodeType(node) == "transform"]
    return transfroms


if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
    
    GetMeshBaseFileNode(pm.ls(selection=1)[0])
