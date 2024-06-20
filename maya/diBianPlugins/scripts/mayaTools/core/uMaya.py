#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
##################################################################
import pymel.core as pm

import json

import os
from collections import OrderedDict

from maya.api.OpenMaya import MImage
from PIL import Image

class materialTemplate(object):
    def __init__(self):
        self.materialName = None
        self.fUDIM = False
        self.normalPaths = []
    def getDataDict(self):
        data = OrderedDict();
        data["materialName"] = self.materialName
        data["fUDIM"] = self.fUDIM
        data["normalPaths"] = self.normalPaths
        return data

class PBRMaterialTemplate(materialTemplate):
    def __init__(self):
        super(PBRMaterialTemplate,self).__init__()
        self.type = "PBR"
        self.baseColorPaths = []
        self.TextureTiling = (1,1)
        self.roughnessPaths = []
        self.metallicPaths = []


    def getDataDict(self):
        data = super(PBRMaterialTemplate,self).getDataDict()
        data["type"] = self.type
        data["baseColorPaths"] = self.baseColorPaths
        data["TextureTiling"] = self.TextureTiling
        
        data["roughnessPaths"] = self.roughnessPaths
        data["metallicPaths"] = self.metallicPaths
        return(data)

#递归一个节点返回他的所有字节点
def recurveNode(node):
    descendants = []
    # 获取当前节点的直接子节点
    children = node.getChildren()
    for child in children:
        # 将子节点添加到后代列表中
        descendants.append(child)
        # 递归获取子节点的所有后代
        descendants.extend(recurveNode(child))
    return descendants

#过滤节点列表
def filterNode(nodes,type):
    result = []
    for node in nodes:
        if node.nodeType() == type:
            result.append(node)
    return result

#获取一个mesh节点上所有的材质节点
def getMaterialsOfMesh(mesh):
    materials = []
    # 获取mesh节点的着色引擎
    shading_engines = mesh.outputs(type='shadingEngine')
    # 遍历所有着色引擎
    for se in shading_engines:
        # 获取连接到着色引擎的材质球
        mats = pm.ls(se.inputs(), materials=True)
        materials.extend(mats)
    return materials


def recurveInputs(node):
    inputNodes = [node]
    for subNode in node.inputs():
        inputNodes.append(subNode)
        inputNodes.extend(recurveInputs(subNode))
    return list(set(inputNodes))


#获取一个材质节点对应属性上的贴图,UDIM和重复度
def getMaterialAttr(material,attrName):
    rootNodes =  material.attr(attrName).inputs()#获取材质对应属性名称下的第一个节点
    if rootNodes == []:
        values = material.attr(attrName).get()
        print(type(values))
        if (type(values) == float):
            values = (values,values,values)
        if (attrName == "bump_input"):
            values = (0.5,0.5,1.0)
        return (values,False,1)#如果该属性下未连接节点返回
    rootNode = rootNodes[0]
    if rootNode.nodeType() == "RedshiftNormalMap":  #如果根节点为法线节点:
        texturePath =  rootNode.attr("tex0").get()
        
        if ".<UDIM>." in texturePath:
            udim = True
            texturePath = texturePath.replace(".<UDIM>.",".1001.")
        else:
            udim = False
        tilingNode = rootNode.attr("uvCoord").inputs()
        if tilingNode == []:
            tiling = (1,1)
        else:
            tiling = (tilingNode[0].attr("repeatU").get(),tilingNode[0].attr("repeatV").get())
    else:                                                                     #如果根节点为其他节点
        fileNodes = filterNode(recurveInputs(rootNode),"file")             #遍历根节点下所有的节点
        if fileNodes == []:
            return (None,False,1)                                             #如果该属性下未连接节点返回
        if len(fileNodes) > 1:
            return False                                                      #如果含有多个文件节点则返回假                                   
        fileNode = fileNodes[0]
        texturePath = fileNode.attr("fileTextureName").get()
        if fileNode.attr("uvTilingMode").get() == 0:
            udim = False
        else:
            udim = True
        tilingNode = fileNode.attr("uvCoord").inputs()
        if tilingNode == []:
            tiling = (1,1)
        else:
            tiling = (tilingNode[0].attr("repeatU").get(),tilingNode[0].attr("repeatV").get())
    return (texturePath,udim,tiling)
def CopyFileAndGetNewPath(sPath,dFolder):
    if not os.path.exists(dFolder):
        os.makedirs(dFolder)
    import shutil
    _,fileName = os.path.split(sPath)
    dPath = os.path.join(dFolder,fileName)
    try:
        shutil.copy(sPath,dPath)
    except:
        pass
    return dPath

def GeneratePureColorImage(size,color,path):
    image = Image.new('RGB',size,color)
    image.save(path)

def InvertImage(path):
    image = Image.open(path)
    imvertImage = Image.eval(image,lambda x: 255 -x )
    imvertImage.save(path)

def getUDIMPath(texurePath):
    import re
    pattern = re.compile(ur'\.\d\d\d\d\.')
    key = pattern.findall(texurePath)[0]
    for i in range(1000,2000):
        yield texurePath.replace(key,".{}.".format(i))

def ConvertToLocalPath(path,rootPath):
    return(path.replace(rootPath,''))



def TexturePipline(textureSloat,material,rootpath,genTexture):
    # NOTE 获取临时路径
    import tempfile
    tempPath= tempfile.gettempdir()
    textureRootPath = os.path.join(rootpath,"Texture")
    baseColorPath,fUDIM,TextureTiling = getMaterialAttr(material,textureSloat)
    texturePaths = [] 
    #如果是属性, 生成一张贴图
    if (type(baseColorPath) == tuple and genTexture):
        tempPath  = os.path.join(tempPath,"{}_{}_.jpg".format(material.name(),textureSloat))
        GeneratePureColorImage(64,baseColorPath,tempPath)
        baseColorPath = tempPath
    elif(type(baseColorPath) == tuple):
        # NOTE 当不生成贴图,且需要生成贴图时直接返回空列表,表示当前插槽没有连接贴图
        return(texturePaths,fUDIM,TextureTiling)
    else:
        pass
    # NOTE 拷贝贴图到新文件夹,并统计路径
    if (fUDIM):
        # NOTE 当UDIM时需要批量复制贴图文件
        for baseColorPathUDIM in getUDIMPath(baseColorPath):
            if not os.path.exists(baseColorPathUDIM):
                # NOTE 如果文件不存在
                continue
            texturePaths.append(ConvertToLocalPath(CopyFileAndGetNewPath(baseColorPathUDIM,textureRootPath),rootpath))
    else:
        # NOTE 非UDIM情况下复制一张就可以
        texturePaths.append(ConvertToLocalPath(CopyFileAndGetNewPath(baseColorPath,textureRootPath),rootpath))
    return texturePaths,fUDIM,TextureTiling

def exportPipline(fullName):
    #
    fbxFilePath = fullName + ".fbx"
    rootpath,_ = os.path.split(fbxFilePath)


    slObjects = pm.ls(selection = True)
    if slObjects == []:
        return(False,u"当前未选择任何物体")
    meshs = []
    # NOTE 遍历所有选择的物体,并将找到其中所有的mesh节点
    for obj in slObjects:
        meshs.extend(filterNode(recurveNode(obj),'mesh'))
    # NOTE 遍历所有找到的mesh并将找到其上的材质
    materials = []
    for mesh in meshs:
        materials.extend(getMaterialsOfMesh(mesh))
    # NOTE 将找到的材质去重
    materials = list(set(materials))
    materialDatas = []
    for material in materials:
        realMaterialName = material.name()
        # NOTE　考虑混合材质的情况,找到连接贴图最多的那个材质球作为最终输出的材质球
        if material.nodeType() == "RedshiftMaterialBlender":
            subMaterials = []
            subMaterials.extend(material.inputs(type="RedshiftMaterial"))
            subMaterials.extend(material.inputs(type = "RedshiftArchitectural"))
            maxTextureNodeCount = 0
            for subMaterial in subMaterials:
                if len(subMaterial.inputs(type = "file")) > maxTextureNodeCount:
                    maxTextureNodeCount = len(subMaterial.inputs(type = "file"))
                    material = subMaterial
        if material.nodeType() == "RedshiftMaterial":
            wrapMaterial = PBRMaterialTemplate()
            wrapMaterial.materialName = realMaterialName

            # NOTE BaseColor
            wrapMaterial.baseColorPaths,wrapMaterial.fUDIM,wrapMaterial.TextureTiling = TexturePipline("diffuse_color",material,rootpath,True)
            wrapMaterial.normalPaths,_,_ = TexturePipline("bump_input",material,rootpath,True)
            # NOTE 判断使用那种贴图流程
            f0Paths,_,_ = TexturePipline("refl_reflectivity",material,rootpath,False)
            if f0Paths == []:
                # NOTE 标准金属度流程
                wrapMaterial.roughnessPaths,_,_ = TexturePipline("refl_roughness",material,rootpath,True)
                wrapMaterial.metallicPaths,_,_ = TexturePipline("refl_metalness",material,rootpath,True)
            else:
                # NOTE f0流程
                wrapMaterial.metallicPaths = f0Paths
                reflectionColorPaths,_,_ = TexturePipline("refl_color",material,rootpath,True)
                diffusePaths = wrapMaterial.baseColorPaths
                
                



        elif material.nodeType() == "RedshiftArchitectural":
            pass
            # wrapMaterial = legacyMaterialTemplate()
            # wrapMaterial.materialName = realMaterialName

            # attrs = getMaterialAttr(material,"brdf_0_degree_refl")
            # if not attrs :
            #      return (False,"材质{0}不符合标准,请检查".format(material.name()))
            # wrapMaterial.fUDIM = attrs[1]   
            # wrapMaterial.f0Path = attrs[0]
            # wrapMaterial.f0Tiling = attrs[2]


            # attrs = getMaterialAttr(material,"diffuse")
            # if not attrs :
            #      return (False,"材质{0}不符合标准,请检查".format(material.name()))
            # wrapMaterial.diffusePath = attrs[0]
            # wrapMaterial.diffuseTiling = attrs[2]


            # attrs = getMaterialAttr(material,"bump_input")
            # if not attrs :
            #      return (False,"材质{0}不符合标准,请检查".format(material.name()))
            # wrapMaterial.normalPath = attrs[0]
            
            # attrs = getMaterialAttr(material,"refl_color")
            # if not attrs :
            #      return (False,"材质{0}不符合标准,请检查".format(material.name()))
            # wrapMaterial.reflectColorPath = attrs[0]
            # wrapMaterial.reflectColorTiling = attrs[2]

            # attrs = getMaterialAttr(material,"refl_gloss")
            # if not attrs :
            #      return (False,"材质{0}不符合标准,请检查".format(material.name()))
            # wrapMaterial.glossinessPath = attrs[0]
            # wrapMaterial.glossinessTiling = attrs[2]
        materialDatas.append(wrapMaterial.getDataDict())
    # NOTE 导出FBX

    pm.mel.FBXExport(f=fullName + ".fbx",s=1)
    print(materialDatas)
    with open(fullName + ".json",'w+') as f:
        f.write(json.dumps(materialDatas))
    return (True,u"导出成功")

def getFileName():
    current_file_path = pm.system.sceneName()
    return(os.path.basename(current_file_path).split(".")[0])
def getRootPath():
    current_file_path = pm.system.sceneName()
    return(os.path.dirname(current_file_path))