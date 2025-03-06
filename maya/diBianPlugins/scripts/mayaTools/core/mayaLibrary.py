#coding=utf-8
import math
import re

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import maya.api.OpenMaya as om

import xgenm as xg
import xgenm.xgGlobal as xgg


import mayaTools.core.pathLibrary as PL
from mayaTools.core.log import log
import os

GROOM_GROUP_ID_NAME = 'groom_group_id'
GROOM_GUIDE_NAME = 'groom_guide'

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
    if ".<UDIM>." in TexturePath:
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
    command = "-frameRange " + str(sFrame) + " " + str(eFrane) +" -attr groom_group_id -attr groom_guide -uvWrite -writeFaceSets -dataFormat ogawa -root " + objects + " -file " + path
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
    pm.select(clear=1)
    pm.select(object)
    pm.mel.FBXExport(object,f=path,s=1)
    pm.select(clear=1)
    
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





def sortHairStrandsGroup(groupName):
    index = groupName.find("_Hair")

    return int(groupName[index+5:index+7])

def regroupHair():
    id_attr_name = 'groom_group_id'
    # 获取选择的节点
    selections = cmds.ls(sl=1)

    xgGroom = None
    hairStrands = []
    # 分离xgGroom和毛发条
    for selection in selections:
        if selection == "xgGroom":
            xgGroom = selection
        else:
            hairStrands.append(selection)
    # 如果没有找到xgGroom节点则返回
    if not xgGroom:
        return
    # 按照组名排序毛发条
    hairStrands = sorted(hairStrands,key=sortHairStrandsGroup)

    # 创建用于存放新毛发的组
    Hair_Strands_Groups = cmds.createNode('transform', name='Strands_Export_Groups')
    Hair_Guide_Groups = cmds.createNode('transform', name='Hair_Guide_Groups')

    # 获取xgGroom下的所有transform节点
    guide_groups = cmds.listRelatives(xgGroom,type='transform')

    # 遍历每个guide组
    for guide_group in guide_groups:
        # 跳过非xgCurvesFromGuides节点
        if not "xgCurvesFromGuides" in guide_group:
            continue
        # 获取guide组的ID
        try:
            guide_id_index = cmds.getAttr(guide_group +".{}".format('groom_group_id'))
        except:
            guide_id_index = 0
    
        # 将毛发曲线按照ID分组
        guide_idx = eval(guide_group.replace("xgCurvesFromGuides",""))
        hairStrand = hairStrands[guide_idx-1]

        #将毛发的变换重命名,赋予ID,并附加到毛发组中
        strands_group = cmds.listRelatives(hairStrand,type='transform',f=1)[0]
        cmds.addAttr(strands_group, longName=id_attr_name, attributeType='short', defaultValue=guide_id_index, keyable=True)
        cmds.addAttr(strands_group, longName='{}_AbcGeomScope'.format(id_attr_name), dataType='string', keyable=True)
        cmds.setAttr('{}.{}_AbcGeomScope'.format(strands_group, id_attr_name), 'con', type='string')
        strands_group = cmds.rename(strands_group,"Strands_Group_{}".format(guide_idx))
        cmds.parent(strands_group,Hair_Strands_Groups)
        


        guides_name = "guides_group_{}".format(guide_id_index)
        if not cmds.objExists(guides_name):
            guides_group = cmds.createNode('transform', name=guides_name,p=Hair_Guide_Groups)
            cmds.addAttr(guides_group, longName=id_attr_name, attributeType='short', defaultValue=guide_id_index, keyable=True)
            cmds.addAttr(guides_group, longName='{}_AbcGeomScope'.format(id_attr_name), dataType='string', keyable=True)
            cmds.setAttr('{}.{}_AbcGeomScope'.format(guides_group, id_attr_name), 'con', type='string')
        else:
            guides_group = guides_name

        guide_group_new_name = "Hair_Guide_{}".format(guide_idx)
        cmds.rename(guide_group,guide_group_new_name)
        cmds.parent(guide_group_new_name,guides_group)
        cmds.delete(hairStrand)
    
    # 删除原始的xgGroom节点
    cmds.delete(xgGroom)


def exportHair():
    guide_attr_name = 'groom_guide'
    id_attr_name = 'groom_group_id'

    guide_group = cmds.ls(sl=1)[0]
    guide_export_group = cmds.createNode('transform', name="Guide_Export_Group")
    guide_groups = cmds.listRelatives(guide_group,type="transform",f=1)
    for guide_group in guide_groups:
        group_id_index = cmds.getAttr(guide_group+".{}".format(id_attr_name))
        for sub_guide_group in cmds.listRelatives(guide_group,typ="transform",f=1):
            new_guides_group = cmds.createNode('transform', name= sub_guide_group + "Guide_E",p=guide_export_group)
            cmds.addAttr(new_guides_group, longName=guide_attr_name, attributeType='short', defaultValue=1, keyable=True)
            cmds.addAttr(new_guides_group, longName='riCurves', attributeType='bool', defaultValue=1, keyable=True)
            cmds.addAttr(new_guides_group, longName='{}_AbcGeomScope'.format(guide_attr_name), dataType='string', keyable=True)
            cmds.setAttr('{}.{}_AbcGeomScope'.format(new_guides_group, guide_attr_name), 'con', type='string')
            cmds.addAttr(new_guides_group, longName=id_attr_name, attributeType='short', defaultValue=group_id_index, keyable=True)
            cmds.addAttr(new_guides_group, longName='{}_AbcGeomScope'.format(id_attr_name), dataType='string', keyable=True)
            cmds.setAttr('{}.{}_AbcGeomScope'.format(new_guides_group, id_attr_name), 'con', type='string')

            curves_shape = []
            curves_no_sim_shape = []
            guide_or_follicle_group = cmds.listRelatives(sub_guide_group,typ="transform")
            for guide_or_follicle in guide_or_follicle_group:
                if "follicle" in guide_or_follicle:
                    curve_transforom = cmds.listConnections(guide_or_follicle+".outCurve")
                    curves_shape += cmds.listRelatives(curve_transforom, ad=True, type='nurbsCurve',f=1)
                else:
                    curves_no_sim_shape += cmds.listRelatives(guide_or_follicle, ad=True, type='nurbsCurve',f=1)
            for curve in curves_shape:
                cmds.parent(curve, new_guides_group, shape=True, relative=True)
            if curves_no_sim_shape != []:
                new_guides_group_no_sim = cmds.createNode('transform', name= sub_guide_group + "Guide_E_nosim",p=guide_export_group)
                cmds.addAttr(new_guides_group_no_sim, longName=guide_attr_name, attributeType='short', defaultValue=1, keyable=True)
                cmds.addAttr(new_guides_group_no_sim, longName='riCurves', attributeType='bool', defaultValue=1, keyable=True)
                cmds.addAttr(new_guides_group_no_sim, longName='{}_AbcGeomScope'.format(guide_attr_name), dataType='string', keyable=True)
                cmds.setAttr('{}.{}_AbcGeomScope'.format(new_guides_group_no_sim, guide_attr_name), 'con', type='string')
                cmds.addAttr(new_guides_group_no_sim, longName=id_attr_name, attributeType='short', defaultValue=group_id_index, keyable=True)
                cmds.addAttr(new_guides_group_no_sim, longName='{}_AbcGeomScope'.format(id_attr_name), dataType='string', keyable=True)
                cmds.setAttr('{}.{}_AbcGeomScope'.format(new_guides_group_no_sim, id_attr_name), 'con', type='string')
            for curve in curves_no_sim_shape:
                cmds.parent(curve, new_guides_group_no_sim, shape=True, relative=True)




def convert_xgen_guides_to_curves(description_name):
    cmds.select(description_name,r=1)
    curve_group_name = description_name+"_guide_curves"
    mel.eval('xgmCreateCurvesFromGuidesOption(0, 0, "{}")'.format(curve_group_name))
    return curve_group_name


def get_attr(node,attrName,defaultValue):
    try:
        return cmds.getAttr(node+".{}".format(attrName))
    except:
        return defaultValue

def add_groom_id_attr(node,value):
    cmds.addAttr(node, longName=GROOM_GROUP_ID_NAME, attributeType='short', defaultValue=value, keyable=True)
    cmds.addAttr(node, longName='{}_AbcGeomScope'.format(GROOM_GROUP_ID_NAME), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(node, GROOM_GROUP_ID_NAME), 'con', type='string')

def add_guide_attr(node):
    cmds.addAttr(node, longName=GROOM_GUIDE_NAME, attributeType='short', defaultValue=1, keyable=True)
    cmds.addAttr(node, longName='riCurves', attributeType='bool', defaultValue=1, keyable=True)
    cmds.addAttr(node, longName='{}_AbcGeomScope'.format(GROOM_GUIDE_NAME), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(node, GROOM_GUIDE_NAME), 'con', type='string')



def make_guide(origin_guide_group,parent,copy=False):
    guide_groups = cmds.listRelatives(origin_guide_group,type='transform')
    #遍历每个包含曲线的组
    for guide_group in guide_groups:
        #为每个包含曲线的组在用于导出的组内创建一个,曲线父组
        new_guide_group = cmds.createNode('transform',name="{}_Export".format(guide_group),p=parent)

        #为这个新组赋予属性
        groom_group_id = get_attr(guide_group,GROOM_GROUP_ID_NAME,0)
        add_groom_id_attr(new_guide_group,groom_group_id)
        add_guide_attr(new_guide_group)

        curves_shape = []
        curves_no_sim_shape = []
        guide_or_follicle_group = cmds.listRelatives(guide_group,typ="transform")
        for guide_or_follicle in guide_or_follicle_group:
            if "follicle" in guide_or_follicle:
                curve_transforom = cmds.listConnections(guide_or_follicle+".outCurve")
                curves_shape += cmds.listRelatives(curve_transforom, ad=True, type='nurbsCurve',f=1)
            else:
                if copy:
                    guide_or_follicle = cmds.duplicate(guide_or_follicle)
                curves_no_sim_shape += cmds.listRelatives(guide_or_follicle, ad=True, type='nurbsCurve',f=1)
        for curve in curves_shape:
            cmds.parent(curve, new_guide_group, shape=True, relative=True)

        if curves_shape == []:
            cmds.delete(new_guide_group)

        if curves_no_sim_shape != []:
            new_guide_group = cmds.createNode('transform',name="{}_nosim_Export".format(guide_group),p=parent)
            add_groom_id_attr(new_guide_group,groom_group_id)
            add_guide_attr(new_guide_group)
            original_parents = []
            for curve in curves_no_sim_shape:
                original_parents.append(cmds.listRelatives(curve,ap=1,type='transform')[0])
                cmds.parent(curve, new_guide_group, shape=True, relative=True)
            #如果新的曲线是复制出来的,那么删除复制出来的transform节点
            if copy:
                for p in original_parents:
                    cmds.delete(p)

def prepare_export_groom(tempABC = r"d:\temp.abc"):
    
    descriptions = xg.descriptions()#获取所有xgen描述
    #将毛发描述转换为交互式,并转换为曲线
    interactives = []
    for description in descriptions:
        interactive_shape = cmds.xgmGroomConvert(description)
        interactives.append(cmds.listRelatives(interactive_shape,ap=1,type='transform')[0])
    exportxgenABC(tempABC,interactives,0,0) #直接导出交互式毛发
    #删除交互式
    for interactive in interactives:
        cmds.delete(interactive)

    newnodes = importgroomabc(tempABC)
    curveNodes = []
    for node in newnodes:
        if cmds.nodeType(node) == 'transform' and cmds.listRelatives(node,type = 'nurbsCurve'):
            curveNodes.append(node)
    print(curveNodes)
    for_export_group = cmds.createNode('transform', name="For_Export_Group")

    parents = []
    for i,curveNode in enumerate(curveNodes):
        parent = cmds.listRelatives(curveNode,ap=1,type="transform")[0]
        if parent not in parents:
            parents.append(parent)
        description_name = parent.replace("temp_","").replace("_splineDescription","")
        groom_group_id = get_attr(description_name,GROOM_GROUP_ID_NAME,0)
        add_groom_id_attr(curveNode,groom_group_id)
        curveNode = cmds.rename(curveNode,"Hair_Strands_{}".format(i))
        cmds.parent(curveNode,for_export_group)

    for parent in parents:
        try:
            cmds.delete(parent)
        except:
            parent

            
    #将毛发描述的导线转换为曲线
    Guide_Curves = cmds.createNode('transform', name="Guide_Curves") #创建一个组用来保存导线组
    for description in descriptions:
        curves = convert_xgen_guides_to_curves(description)
        groom_group_id = get_attr(description,GROOM_GROUP_ID_NAME,0)
        add_groom_id_attr(curves,groom_group_id)
        cmds.parent(curves,Guide_Curves)
    try:
        cmds.delete("xgGroom")
    except:
        pass

    make_guide(Guide_Curves,for_export_group,True)
    #return for_export_group
    #exportABC_gromm(for_export_group,0,0,export_path)

def export_groom_guide_cache(guides,export_path,sFrame,eFrame):
    for_export_group = cmds.createNode('transform', name="For_Export_Group")
    make_guide(guides,for_export_group)
    exportABC_gromm(for_export_group,sFrame,eFrame,export_path)

if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
    prepare_export_groom()


