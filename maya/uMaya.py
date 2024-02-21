#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
# version: 2.7.18
##################################################################


import pymel.core as pm

import json


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
    def setBaseColor(self,path,tiling = (1,1)):
        self.baseColorPath = path
        self.baseColorTiling = tiling
    def setRoughness(self,path,tiling = (1,1)):
        self.roughnessPath = path
        self.roughnessTiling = tiling
    def setMetallic(self,path,tiling = (1,1)):
        self.metallicPath = path
        self.metallicTiling = tiling
    def setNormal(self,path,tiling = (1,1)):
        self.normalPath = path
        self.normalTiling = tiling
    def convertToJson(self):
        data = {}

        data["materialName"] = self.materialName
        data["fUDIM"] = self.fUDIM

        data["baseColorPath"] = self.baseColorPath
        data["baseColorTiling"] = self.baseColorTiling
        
        data["roughnessPath"] = self.roughnessPath
        data["roughnessTiling"] = self.roughnessTiling

        data["metallicPath"] = self.metallicPath
        data["metallicTiling"] = self.metallicTiling

        data["normalPath"] = self
        data["normalTiling"] = (1,1)
        return(json.dumps(data))




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

#获取一个材质节点对应属性上的贴图,UDIM和重复度
def getMaterialAttr(material,attrName):
    fileNode =  material.attr(attrName).inputs()
    if fileNode == []:
        return (None,False,1)
    fileNode = fileNode[0]
    if fileNode.nodeType() == "file":
        texturePath = fileNode.attr("fileTextureName").get()
        udim = fileNode.attr("uvTilingMode").get()
        tilingNode = fileNode.attr("uvCoord").inputs()
        if tilingNode == []:
            tiling = 1;
        else:
            tiling = tilingNode[0].attr("repeatU").get()
    else:
        texturePath = fileNode.attr("tex0").get()
        if ".<UDIM>." in texturePath:
            udim = True
            texturePath.replace(".<UDIM>.",".1001.")
        else:
            udim = False
        tilingNode = fileNode.attr("uvCoord").inputs()
        if tilingNode == []:
            tiling = 1;
        else:
            tiling = tilingNode[0].attr("repeatU").get()
    return (texturePath,udim,tiling)


def checkSelectMeshs(fullName):
    acceptAbleMaterialType = ["RedshiftMaterial","RedshiftArchitectural"]
    acceptAbleTexturelType = ["file","RedshiftNormalMap"]
    slObjects = pm.ls(selection = True)
    meshs = []
    for obj in slObjects:
        meshs.extend(filterNode(recurveNode(obj),'mesh'))
    materials = []
    for mesh in meshs:
        materials.extend(getMaterialsOfMesh(mesh))
    materials = list(set(materials))
    datas = []
    for material in materials:
        if material.nodeType() not in acceptAbleMaterialType:
            return(False,u"材质球{0}的类型不是可接受的类型,请检查".format(material.name()))
        for input in material.inputs():
            if input.nodeType() not in acceptAbleTexturelType:
                return(False,u"材质球{0}含有不可接受的贴图类型请检查".format(material.name()))
        data = {}
        if material.nodeType() == "RedshiftMaterial":
            data["materialName"] = material.name()
            data["type"] = "pbr"
            data["baseColor"],data["baseColorUDIM"],data["baseColorTiling"] = getMaterialAttr(material,"diffuse_color")
            data["roughness"],data["roughnessUDIM"],data["roughnessTiling"] = getMaterialAttr(material,"refl_roughness")
            data["normal"],data["normalUDIM"],data["normalTiling"] = getMaterialAttr(material,"bump_input")
            data["metallic"],data["metallicUDIM"],data["metallicTiling"] = getMaterialAttr(material,"refl_metalness")
        elif material.nodeType() == "RedshiftArchitectural":
            data["materialName"] = "None"
            data["type"] = "ssss"
            pass
        datas.append(data)
        del data
    print(datas)

    



    pm.mel.FBXExport(f=fullName + ".fbx",s=1)
    with open(fullName + ".json",'w+') as f:
        f.write(json.dumps(datas))
    return (True,u"成功")
