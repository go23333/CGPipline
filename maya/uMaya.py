#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
# version: 2.7.18
##################################################################


import pymel.core as pm

import json

import os

class PBRMaterialTemplate():
    def __init__(self):
        self.materialName = None
        self.fUDIM = False

        self.baseColorPath = None
        self.baseColorTiling = (1,1)
        
        self.roughnessPath = None
        self.roughnessTiling = (1,1)

        self.metallicPath = None
        self.metallicTiling = (1,1)

        self.normalPath = None
        self.normalTiling = (1,1)
    def getDataDict(self):
        data = {}

        data["materialName"] = self.materialName
        data["fUDIM"] = self.fUDIM

        data["baseColorPath"] = self.baseColorPath
        data["baseColorTiling"] = self.baseColorTiling
        
        data["roughnessPath"] = self.roughnessPath
        data["roughnessTiling"] = self.roughnessTiling

        data["metallicPath"] = self.metallicPath
        data["metallicTiling"] = self.metallicTiling

        data["normalPath"] = self.normalPath
        data["normalTiling"] = self.normalTiling
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
        return (None,False,1)#如果该属性下未连接节点返回
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


def exportPipline(fullName):
    slObjects = pm.ls(selection = True)
    if slObjects == []:
        return(False,"当前未选择任何物体")
    meshs = []
    for obj in slObjects:
        meshs.extend(filterNode(recurveNode(obj),'mesh'))
    materials = []
    for mesh in meshs:
        materials.extend(getMaterialsOfMesh(mesh))
    materials = list(set(materials))
    materialDatas = []

    for material in materials:
        if material.nodeType() == "RedshiftMaterial":
            wrapMaterial = PBRMaterialTemplate()
            wrapMaterial.materialName = material.name()

            attrs = getMaterialAttr(material,"diffuse_color")
            if not attrs :
                 return (False,"材质{0}不符合标准,请检查".format(material.name()))
            wrapMaterial.fUDIM = attrs[1]   
            wrapMaterial.baseColorPath = attrs[0]
            wrapMaterial.baseColorTiling = attrs[2]
            
            attrs = getMaterialAttr(material,"bump_input")
            print(attrs)
            if not attrs :
                 return (False,"材质{0}不符合标准,请检查".format(material.name()))
            wrapMaterial.normalPath = attrs[0]
            wrapMaterial.normalTiling = attrs[2]

            attrs = getMaterialAttr(material,"refl_roughness")
            if not attrs :
                 return (False,"材质{0}不符合标准,请检查".format(material.name()))
            wrapMaterial.roughnessPath = attrs[0]
            wrapMaterial.roughnessTiling = attrs[2]

            attrs = getMaterialAttr(material,"refl_metalness")
            if not attrs :
                 return (False,"材质{0}不符合标准,请检查".format(material.name()))
            wrapMaterial.metallicPath = attrs[0]
            wrapMaterial.metallicTiling = attrs[2]
            materialDatas.append(wrapMaterial.getDataDict())
    print(materialDatas)
    pm.mel.FBXExport(f=fullName + ".fbx",s=1)
    with open(fullName + ".json",'w+') as f:
        f.write(json.dumps(materialDatas))
    return (True,u"导出成功")



def getFileName():
    current_file_path = pm.system.sceneName()
    return(os.path.basename(current_file_path).split(".")[0])