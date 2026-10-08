import os
import random
import string
import shutil
import copy
import re
import json
from PIL import Image,ImageFile

import socket
import sys
from win32com.client import Dispatch
from .backend import Backend
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from enum import Enum,auto
from dataclasses import dataclass,field
from app.core.Log import Log
import socket


from app.core.SPHandler import RemotePainter
from app.core.Log import Log
logger = Log.get().getLogger("Utility")
logger.setLevel(Log.Level.debug)

TextureExtensions = [".png",'.exr','.jpg']
ModelExtensions = [".fbx",".ztl"]

class MyBridgetGlobalEnum(Enum):
    def __format__(self, format_spec: str) -> str:
        return super().__format__(format_spec)

    
class ComparableEnum(MyBridgetGlobalEnum):
    def GetValue(self,var):
        #子类需要对这个函数进行实现
        raise
    def __lt__(self,other):
        return self.GetValue(self) < self.GetValue(other)
    def __gt__(self,other):
        return self.GetValue(self) > self.GetValue(other)
    def __eq__(self,other):
        return self.GetValue(self) == self.GetValue(other)
    def __ge__(self,other):
        return self.GetValue(self) >= self.GetValue(other)
    def __le__(self,other):
        return self.GetValue(self) <= self.GetValue(other)
    def __int__(self):
        return self.GetValue(self)

class TextureSize(ComparableEnum):
    _2k = "2K"
    _4k = "4K"
    _8K = "8K"
    def GetValue(self,var):
         return eval(var.value[0])
    
class AssetType(MyBridgetGlobalEnum):
    Assets3D = "3D Assets"
    Surface = "Surface"
    Decal   = "Decal"
    Plant   = "Plant"
    Brush   = "brush"
    VFX     = "VFX"
    SmartMaterial="SmartMaterial"
    Texture = "Texture"


class AssetSize(MyBridgetGlobalEnum):
    Meter1  = "1 Meter"
    Meters2 = "2 Meters"
    Meters3 = "3 Meters"
    Meters4 = "4 Meters"

class AssetFormat(MyBridgetGlobalEnum):
    UnrealEngine = "Unreal Engine"
    FBX          = "FBX"
    SubstancePainter = "SubstancePainter"


class AssetFormatN(MyBridgetGlobalEnum):
    UnrealEngine = auto()
    FBX          = auto()
    Maya         = auto()
    SubstancePainter = auto()


class AssetMapType(MyBridgetGlobalEnum):
    Albedo = "Albedo"
    AO = "AO"
    Brush = "Brush"
    Bump = "Bump"
    Cavity = "Cavity"
    Diffuse = "Diffuse"
    Displacement = "Displacement"
    Fuzz = "Fuzz"
    Gloss = "Gloss"
    Mask = "Mask"
    Metalness = "Metalness"
    Normal = "Normal"
    Opacity = "Opacity"
    Roughness = "Roughness"
    Specular = "Specular"
    Translucency = "Translucency"
    Curvature = "curvature"
    Transmission = "transmission"
    Thickness    = "thickness"


if Backend.Get().isBackendAvailable():
    category = Backend.Get().getCategories()
else:
    category = {}


def GetParentsCategory(name):
    for p in category.keys():
        for c in category[p].keys():
            for cc in category[p][c]:
                if name == cc:
                    return p,c,cc
    return False

def GetCategorys(level:int):
    if level == 0:
        return list(category.keys())
    elif level == 1:
        return [ele for value in category.values() for ele in value.keys() ]
    elif level == 2:
        return [c for value in category.values() for ele in value.keys() for c in value[ele]]
    else:
        raise
def GetSubCategorys(parentIndex:int):
    return [ele for ele in category[GetCategorys(0)[parentIndex]].keys()]

@dataclass(repr=False)
class SerializeBase:
    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        for key in data.keys():
            if isinstance(data[key],MyBridgetGlobalEnum):
                data[key] = data[key].value
            elif isinstance(data[key],SerializeBase):
                data[key] = data[key].to_dict()
            elif isinstance(data[key],list):
                for i in range(len(data[key])):
                    try:
                        data[key][i] = data[key][i].to_dict()
                    except:
                        pass
        return data
    def __repr__(self) -> str:
        return(str(self.to_dict()))
    @classmethod
    def from_dict(cls,data):
        asset = cls()
        for key in data.keys():
            obj = asset.__getattribute__(key)
            if isinstance(obj,MyBridgetGlobalEnum):
                asset.__setattr__(key,copy.deepcopy(obj.__class__._value2member_map_[data[key]]))
            elif isinstance(obj,SerializeBase):
                asset.__setattr__(key,obj.__class__.from_dict(data[key]))
            elif isinstance(obj,list):
                itemClass = cls.__annotations__[key].__args__[0]
                if isinstance(itemClass(),SerializeBase):
                    for item in data[key]:
                        asset.__getattribute__(key).append(itemClass.from_dict(item))
                else:
                    asset.__setattr__(key,data[key])
            else:
                asset.__setattr__(key,data[key])
        return asset

@dataclass(repr=False)
class AssetMap(SerializeBase):
    uri         : str          = field(default_factory=str)
    extension   : str          = field(default_factory=str)
    name        : str          = field(default_factory=str)
    type        : AssetMapType = field(default=AssetMapType.Albedo)
    subMapCount : int          = field(default_factory=int) 
    UDIM        : bool         = field(default_factory=bool)
    size        : TextureSize  = field(default=TextureSize._2k)
@dataclass(repr=False)
class AssetMesh(SerializeBase):
    uri         : str          = field(default_factory=str)
    name         : str          = field(default_factory=str)
    extension   : str          = field(default_factory=str)
@dataclass(repr=False)
class LOD(SerializeBase):
    mesh         : AssetMesh          = field(default_factory=AssetMesh)
    normalMap    : AssetMap           = field(default_factory=AssetMap)
    level        : int                = field(default_factory=int)
    def findLodNormal(self):
        lodMeshUri = self.mesh.uri
        lodMeshFolder = os.path.dirname(lodMeshUri)
        normalFileName = ""
        for file in os.listdir(lodMeshFolder):
            if "normal" in file.lower() and "lod" in file.lower():
                if str(self.level) in file:
                    normalFileName = file
                    break
        if normalFileName != "":
            self.normalMap.uri = os.path.join(lodMeshFolder,normalFileName)
            self.normalMap.name,self.normalMap.extension = os.path.splitext(normalFileName)
            self.normalMap.type = AssetMapType.Normal
            self.normalMap.subMapCount = 1
            self.normalMap.UDIM = False
@dataclass(repr=False)
class Material(SerializeBase):
    name         : str               = field(default_factory=str)
    maps         : list[AssetMap]    = field(default_factory=list[AssetMap])
@dataclass(repr=False)
class MeshVar(SerializeBase):
    OriginMesh     : AssetMesh         = field(default_factory=AssetMesh)
    Lods           : list[LOD]         = field(default_factory=list[LOD])
    VarIndex       : int               = field(default_factory=int)
@dataclass(repr=False)
class Asset(SerializeBase):
    name           : str               = field(default_factory=str)
    ZbrushFile     : str               = field(default_factory=str)
    AssetID        : str               = field(default_factory=str)
    rootFolder     : str               = field(default_factory=str)
    JsonUri        : str               = field(default_factory=str)

    tags           : list[str]         = field(default_factory=list[str])
    previewFile    : list[str]         = field(default_factory=list[str])
    Lods           : list[LOD]         = field(default_factory=list[LOD])
    assetMaterials : list[Material]    = field(default_factory=list[Material])
    MeshVars       : list[MeshVar]     = field(default_factory=list[MeshVar])

    type           : AssetType         = field(default=AssetType.Assets3D)
    category       : str               = field(default_factory=str)
    subcategory    : str               = field(default_factory=str)
    surfaceSize    : AssetSize         = field(default=AssetSize.Meter1)
    assetFormat    : AssetFormat       = field(default=AssetFormat.FBX)

    OriginMesh     : AssetMesh         = field(default_factory=AssetMesh)


    TilesV         : bool              = field(default_factory=bool)
    TilesH         : bool              = field(default_factory=bool)

    AssetIndex     : int               = field(default_factory=int)
    OldJson        : str               = field(default_factory=str)



def ClassifyFilesFormFolder(folder:str):
    models = []
    images = []
    assetName = ''
    files = os.listdir(folder)
    for file in files:
        basename,ext = os.path.splitext(file)
        ext = ext.lower()
        filePath = os.path.join(folder,file)
        if not os.path.isfile(filePath):
            continue #跳过目录
        # 根据拓展名分类文件类型
        if ext.lower() in TextureExtensions:
            images.append(filePath)
            pass
        elif ext.lower() in ModelExtensions:
            models.append(filePath)
            pass
        if ext == ".jpg":
            assetName = basename
    return dict(assetName = assetName,images = images,models=models)





def readImage(filePath)->ImageFile:
    logger.info(f"读取图片{filePath}")
    _,ext = os.path.splitext(filePath)
    if ext.lower() == '.exr':
        # image = exr_to_srgb(filePath)
        # if not image:
        #     return False
        return False
    else:
        try:
            image = Image.open(filePath)
        except:
            return False
    return image


def GetTextureSize(uri:str,udim:bool=False):
    if udim:
        uri = uri.replace("udim","1001")
    image = readImage(uri)
    if not image:
        return False
    size = image.size
    maxSize = max(size[0],size[1])
    if maxSize >= 8192:
        return TextureSize._8K
    elif maxSize >= 4096:
        return TextureSize._4k
    else:
        return TextureSize._2k
def removeFolder(path):
    if os.path.exists(path):
        shutil.rmtree(path)

#进入此函数的所有路径需要保证完成规格化
def MakeAssetByData(datas:dict)->Asset:
    asset = Asset()
    asset.name = datas["name"]
    asset.tags = datas["tags"]

    asset.type = copy.deepcopy(AssetType._value2member_map_[datas["type"]])
    asset.category = datas["category"]
    asset.subcategory = datas["subCategory"]

    material = Material()
    for mapType in datas["mapData"].keys():
        mapPath = datas["mapData"][mapType]
        # 跳过不存在的贴图
        if mapPath == "":
            continue
        assetMap = AssetMap()
        assetMap.type = copy.deepcopy(AssetMapType._value2member_map_[mapType])
        assetMap.name,assetMap.extension = os.path.splitext(os.path.basename(mapPath))
        assetMap.uri = mapPath
        assetMap.subMapCount = 1
        assetMap.UDIM = False
        assetMap.size = GetTextureSize(assetMap.uri)
        material.maps.append(assetMap)
        material.name = asset.name
    asset.assetMaterials.append(material)
    if asset.type == AssetType.Assets3D or asset.type == AssetType.Plant:
        asset.OriginMesh = AssetMesh()
        asset.OriginMesh.uri = datas["orginMesh"]
        asset.OriginMesh.name,asset.OriginMesh.extension = os.path.splitext(os.path.basename(datas["orginMesh"]))
        for i in range(len(datas["lods"])):
            lod = LOD()
            lod.mesh = AssetMesh()
            lod.mesh.uri = datas["lods"][i]
            lod.mesh.name,lod.mesh.extension = os.path.splitext(os.path.basename(lod.mesh.uri))
            lod.level = i
            lod.findLodNormal()
            asset.Lods.append(lod)
        zbrushFileUri = asset.OriginMesh.uri.replace("fbx","ZTL")
        if os.path.exists(zbrushFileUri):
            asset.ZbrushFile = zbrushFileUri
    elif asset.type == AssetType.Surface or asset.type == AssetType.Decal:
        asset.surfaceSize = copy.deepcopy(AssetSize._value2member_map_[datas["surfaceSize"]])
        asset.TilesV =  datas["TilesVertically"]
        asset.TilesH = datas["TillesHorizontically"]
    else:
        pass
    asset.previewFile.append(datas["previewImage"])
    asset.assetFormat = AssetFormat.FBX
    return asset


def update_asset(asset:Asset,assetLibFolder:str):
    #更新json文件
    rootFolder = os.path.join(assetLibFolder,asset.rootFolder)
    JsonUri_abs = os.path.join(rootFolder,asset.JsonUri)
    with open(JsonUri_abs,'w+',encoding='utf-8') as f:
        f.write(json.dumps(asset.to_dict()))
    #更新数据库
    Backend.Get().changeAsset(asset.AssetID,"name",asset.name)
    Backend.Get().changeAsset(asset.AssetID,"tags",asset.tags)
    Backend.Get().changeAsset(asset.AssetID,"type",asset.type.value)
    Backend.Get().changeAsset(asset.AssetID,"category",asset.category)
    Backend.Get().changeAsset(asset.AssetID,"subcategory",asset.subcategory)
    Backend.Get().changeAsset(asset.AssetID,"subcategory",asset.subcategory)
    SearchWords = f"{asset.name} {asset.AssetID} {asset.category} {asset.subcategory}"+" ".join(asset.tags)
    Backend.Get().changeAsset(asset.AssetID,"SearchWords",SearchWords)

def isMapUriValid(url:str,udim:bool)->bool:
    if url.strip() == "":
        # 如果url为空 返回假
        return False
    elif not os.path.exists(url) and not udim:
        # 如果非UDIM的情况下 url文件不存在返回空
        return False
    elif udim and not os.path.exists(url.replace("udim","1001")):
        # 如果UDIM情况下,1001文件不存在返回空
        return False
    else:
        return True
def CopyAndRenameAsset(asset:Asset,assetLibFolder:str):
    logger.info(f"Start to move asset {asset.name}")
    # 计算资产ID
    asset.AssetID = generate_unique_string(7)
    logger.info(f"Asset ID is :{asset.AssetID}")
    # 创建资产根目录
    rootFolder = os.path.join(assetLibFolder,f"{asset.AssetID}")
    logger.info(f"Asset root folder is :{rootFolder}")
    asset.rootFolder = f"{asset.AssetID}"
    if not os.path.exists(rootFolder):
        os.makedirs(rootFolder)
    # 获取资产编号
    asset.AssetIndex = Backend.Get().getAssetsCount()

    #复制Bridge中原有的Json文件
    if asset.OldJson != "":
        asset.OldJson = CopyFileToFolderSingle(asset.OldJson,rootFolder,f"{asset.AssetID}_old.json")

    if asset.type == AssetType.Assets3D or asset.type == AssetType.Plant:
        for i in range(len(asset.Lods)):
            asset.Lods[i].mesh.name = f"{asset.AssetID}_LOD{asset.Lods[i].level}{asset.Lods[i].mesh.extension}"
            asset.Lods[i].mesh.uri = CopyFileToFolderSingle(asset.Lods[i].mesh.uri,rootFolder,asset.Lods[i].mesh.name)
            asset.Lods[i].normalMap.name = f"{asset.AssetID}_Normal_LOD{asset.Lods[i].level}{asset.Lods[i].normalMap.extension}"
            asset.Lods[i].normalMap.uri = CopyFileToFolderSingle(asset.Lods[i].normalMap.uri,rootFolder,asset.Lods[i].normalMap.name)
        for i in range(len(asset.MeshVars)):
            var_sub_folder = os.path.join(rootFolder,f"Var{asset.MeshVars[i].VarIndex}")
            if not os.path.exists(var_sub_folder):
                os.makedirs(var_sub_folder)
            asset.MeshVars[i].OriginMesh.name = f"{asset.AssetID}_Var{asset.MeshVars[i].VarIndex}{asset.MeshVars[i].OriginMesh.extension}"
            asset.MeshVars[i].OriginMesh.uri = CopyFileToFolderSingle(asset.MeshVars[i].OriginMesh.uri,var_sub_folder,asset.MeshVars[i].OriginMesh.name)
            for j in range(len(asset.MeshVars[i].Lods)):
                asset.MeshVars[i].Lods[j].mesh.name = f"{asset.AssetID}_Var{asset.MeshVars[i].VarIndex}_LOD{asset.MeshVars[i].Lods[j].level}{asset.MeshVars[i].OriginMesh.extension}"
                asset.MeshVars[i].Lods[j].mesh.uri = CopyFileToFolderSingle(asset.MeshVars[i].Lods[j].mesh.uri,var_sub_folder,asset.MeshVars[i].Lods[j].mesh.name)
        asset.OriginMesh.name = asset.AssetID + asset.OriginMesh.extension
        asset.OriginMesh.uri = CopyFileToFolderSingle(asset.OriginMesh.uri,rootFolder,asset.OriginMesh.name)
        asset.ZbrushFile = CopyFileToFolderSingle(asset.ZbrushFile,rootFolder,f"{asset.AssetID}.ZTL")
    else:
        pass
    for i in range(len(asset.assetMaterials)):
        for j in range(len(asset.assetMaterials[i].maps)):
            if asset.assetMaterials[i].maps[j].UDIM:
                asset.assetMaterials[i].maps[j].name = f"{asset.AssetID}_{asset.assetMaterials[i].maps[j].type.value}.{'udim'}{asset.assetMaterials[i].maps[j].extension}"
            else:
                asset.assetMaterials[i].maps[j].name = f"{asset.AssetID}_{asset.assetMaterials[i].maps[j].type.value}{asset.assetMaterials[i].maps[j].extension}"
            asset.assetMaterials[i].maps[j].size = GetTextureSize(asset.assetMaterials[i].maps[j].uri,asset.assetMaterials[i].maps[j].UDIM)
            asset.assetMaterials[i].maps[j].uri = CopyFileToFolderUDIM(asset.assetMaterials[i].maps[j].uri,rootFolder,asset.assetMaterials[i].maps[j].name,False,asset.assetMaterials[i].maps[j].UDIM,asset.assetMaterials[i].maps[j].subMapCount)
    for i in range(len(asset.previewFile)):
        _,ext = os.path.splitext(asset.previewFile[i])
        asset.previewFile[i] = scaleImage(asset.previewFile[i])
        asset.previewFile[i] = CopyFileToFolderSingle(asset.previewFile[i],rootFolder,f"{asset.AssetID}_Preview_{i}{ext}",True)
    JsonUri_abs = os.path.join(rootFolder,f"{asset.AssetID}.json")
    asset.JsonUri = os.path.basename(JsonUri_abs)
    with open(JsonUri_abs,'w+',encoding='utf-8') as f:
        f.write(json.dumps(asset.to_dict()))
    return asset

def generate_random_string(length=10):
    # 定义生成随机字符串的字符集
    characters = string.ascii_letters + string.digits
    # 使用 random.choices 从字符集中随机选择字符，形成指定长度的字符串
    random_string = ''.join(random.choices(characters, k=length))
    return random_string
def generate_unique_string(length=10):
    while(1):
        random_string = generate_random_string(length)
        if Backend.Get().getAsset(random_string) == False:
            return random_string



def CopyFileToFolderSingle(filePath:str,folder:str,newName:str = None,move:bool=False):
    logger.info(f"将文件{filePath},复制到目录{folder}中")
    if not os.path.exists(filePath):
        assert f"文件{filePath}不存在"
        return ""
    newFileName = os.path.basename(filePath)
    if newName:
        newFileName = newName
    newFilePath = os.path.join(folder,newFileName)
    if move:
        shutil.move(filePath,newFilePath)
    else:
        shutil.copyfile(filePath,newFilePath)
    return os.path.basename(newFilePath)


def CopyFileToFolderUDIM(filePath:str,folder:str,newName:str = None,move:bool=False,udim=False,udimCount:int=1):
    if udim:
        udimMaps = []
        for i in range(udimCount):
            udimFlag = "1{:03d}".format(i+1)
            udim_new_name = newName.replace("udim",udimFlag)
            udim_old_path = filePath.replace("udim",udimFlag)
            udimMaps.append(CopyFileToFolderSingle(udim_old_path,folder,udim_new_name,move))
        return udimMaps[0].replace("1001","udim")
    else:
        return CopyFileToFolderSingle(filePath,folder,newName,move)

def scaleImage(imagePath:str):
    baseName = os.path.basename(imagePath)
    name,ext = os.path.splitext(baseName)
    dirName = os.path.dirname(imagePath)

    image = readImage(imagePath)
    w,h = image.size
    image.thumbnail((512,int(512/w *h)))
    newpath = os.path.join(dirName,f"{name}_thumb{ext}")
    image.save(newpath)
    return newpath


def sendStringToUE(string:str,address:tuple[str,int]):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(address)
        client_socket.sendall(string.encode())
        return True
    except:
        return False
    
def copyMapToFolder(map:AssetMap,folder:str)->AssetMap:
    newUri = os.path.join(folder,map.name)
    shutil.copy(map.uri,newUri)
    map.uri = newUri
    return map

def GenRoughnessMapUDIM(glossinessUri,assetID:str,dirName:str,extension:str,udim:bool = False):
    if udim:
        uris = GetUDIMTextures(glossinessUri)
    else:
        uris = [glossinessUri]
    new_uris = []
    for i,uri in enumerate(uris): 
        if udim:
            udimFlag = ".1{:03d}".format(i+1)
        else:
            udimFlag = ""
        new_uris.append(GenRoughnessMap(uri,assetID,dirName,extension,udim,udimFlag))
def GenRoughnessMap(glossinessUri,assetID:str,dirName:str,extension:str,udimflag:str=""):
    roughness_uri = os.path.join(dirName,f"{assetID}_roughness{udimflag}{extension}")
    if os.path.exists(roughness_uri):
        return roughness_uri
    img_gloss = readImage(glossinessUri).convert("L")
    img_roughness =Image.eval(img_gloss,lambda c: 255 - c)
    img_roughness.save(roughness_uri)
    return roughness_uri

def GenARMMapUDIM(ao:str,roughness:str,metallic:str,assetID:str,opacity:str,Translucency:str,extension:str,type:AssetType,dirName:str,udim:bool=False):
    arms_uris = []
    if udim:
        roughness_uris = GetUDIMTextures(roughness)
        length = len(roughness_uris)
        if ao:
            ao_uris = GetUDIMTextures(ao)
        else:
            ao_uris = [None] * length

        if metallic:
            metallic_uris = GetUDIMTextures(metallic)
        else:
            metallic_uris = [None] * length

        if opacity:
            opacity_uris = GetUDIMTextures(opacity)
        else:
            opacity_uris = [None] * length

        if Translucency:
            Translucency_uris = GetUDIMTextures(Translucency)
        else:
            Translucency_uris = [None] * length
    else:
        roughness_uris = [roughness]
        if ao:
            ao_uris = [ao]
        else:
            ao_uris = [None]

        if metallic:
            metallic_uris = [metallic]
        else:
            metallic_uris = [None]

        if opacity:
            opacity_uris = [opacity]
        else:
            opacity_uris = [None]

        if Translucency:
            Translucency_uris =[Translucency]
        else:
            Translucency_uris = [None] 
    for i,uri in enumerate(roughness_uris): 
        if udim:
            udimFlag = ".1{:03d}".format(i+1)
        else:
            udimFlag = ""
        arms_uris.append(GenARMMap(ao_uris[i],roughness_uris[i],metallic_uris[i],assetID,opacity_uris[i],Translucency_uris[i],extension,type,dirName,udimFlag))
    return arms_uris

def GenARMMap(ao:str,roughness:str,metallic:str,assetID:str,opacity:str,Translucency:str,extension:str,type:AssetType,dirName:str,udimflag:str="")->str:
    armUri = os.path.join(dirName,f"{assetID}_ARM{udimflag}{extension}")
    if os.path.exists(armUri):
        return armUri
    
    if roughness:
        rouImage = readImage(roughness).convert("L")
    if opacity:
        opacityImage = readImage(opacity).convert("L")
    if Translucency:
        translucencyImage = readImage(Translucency).convert("L")

    if ao:
        aoImage = readImage(ao).convert("L")
    else:
        aoImage = Image.new("L",rouImage.size,255)
    if metallic:
        metaImage = readImage(metallic).convert("L")
    else:
        metaImage = Image.new("L",rouImage.size,0)

    if type == AssetType.Assets3D or type == AssetType.Surface:
        r,g,b = aoImage.split()[0],rouImage.split()[0],metaImage.split()[0]
        armImage = Image.merge("RGB",(r,g,b))
        armImage.save(armUri)
        return armUri
    elif type == AssetType.Decal:
        r,g,b,a = aoImage.split()[0],rouImage.split()[0],metaImage.split()[0],opacityImage.split()[0]
        armImage = Image.merge("RGBA",(r,g,b,a))
        armImage.save(armUri)
        pass
    elif type == AssetType.Plant:
        r,g,b,a = aoImage.split()[0],rouImage.split()[0],translucencyImage.split()[0],opacityImage.split()[0]
        armImage = Image.merge("RGBA",(r,g,b,a))
        armImage.save(armUri)
        pass
    else:
        pass
    return armUri
def ResizeTextureByStringUDIM(uri:str,rootDir:str,size:str,UDIM:bool=False):
    if UDIM:
        uris = GetUDIMTextures(uri)
    else:
        uris = [uri]
    new_uris = []
    for uri in uris:
        new_uris.append(ResizeTextureByString(uri,rootDir,size))
    return new_uris

def ResizeTextureByString(uri:str,rootDir:str,size:str):
    logger.info(f"尝试缩放贴图:{uri}")
    if not os.path.exists(rootDir):
        logger.info(f"尝试创建目录:{rootDir}")
        os.makedirs(rootDir)
    fileName = os.path.basename(uri)
    logger.info(f"贴图文件名为:{fileName}")
    newFileuri = os.path.join(rootDir,fileName)
    logger.info(f"缩放后贴图路径为:{newFileuri}")
    # _,ext = os.path.splitext(fileName)
    # if ext == ".exr":
    #     newFileuri = newFileuri.replace(ext,".png")
    if os.path.exists(newFileuri):
        logger.info(f"目录下已经存在缩放过的贴图,跳过")
        return newFileuri
    image = readImage(uri)
    if not image:
        return False
    if size == "2K":
        logger.info(f"将贴图缩放为2K")
        scalfactor = 2048
    elif size == "4K":
        logger.info(f"将贴图缩放为2K")
        scalfactor = 4096
    else:
        logger.info(f"将贴图缩放为8K")
        scalfactor = 8192
    image = image.resize((scalfactor,scalfactor))
    image.save(newFileuri)
    logger.info(f"贴图缩放成功")
    return newFileuri
def fixNormalMiss(rootPath:str,asset:Asset,jsonuri:str):
    files = os.listdir(rootPath)
    files = [file for file in files if "normal" in file.lower()]
    for normal in files:
        if "lod" in normal.lower():
            index = eval(normal.lower().split("lod")[-1].split(".")[0])
            logger.info(f"发现存在LOD{index}的法线贴图,可以替代")
            if asset.Lods[index].normalMap.uri == "":
                asset.Lods[index].normalMap.uri = os.path.basename(normal)
                asset.Lods[index].normalMap.name,asset.Lods[index].normalMap.extension = os.path.splitext(asset.Lods[index].normalMap.uri)
        else:
            pass
    with open(jsonuri,"w",encoding='utf-8') as f:
        f.write(json.dumps(asset.to_dict()))
    return asset


def SendCommandToSP(command:str):
    logger.info(f"将以下消息发送到SP中:\n{command}")
    Remote = RemotePainter()
    try:
        Remote.checkConnection()
        Remote.execScript(command)
    except ConnectionRefusedError as e:
        logger.error(f"链接到SP出现错误,检查sp后重试")
        return False

def sendAssetToUE(assetImte,address:tuple[str,int],sizeIndex:int,lod_level:str):
    with open(assetImte.jsonUri,'r',encoding="utf-8") as f:
            asset = Asset.from_dict(json.loads(f.read()))
    rootFolder = os.path.join(Backend.Get().getAssetRootPath(),asset.rootFolder)
    
    logger.info(f"当前资产根目录为:{rootFolder}")
    logger.info(f"当前资产格式为:{assetImte.Format.name}")

    if assetImte.Format == AssetFormatN.FBX:
        Ao = None
        Roughness = None
        BaseColor = None
        Normal = None
        Metallic = None
        Translucency = None
        Opacity = None
        Glossiness = None
        meshUri = None
        armUri = None
        udim = False
        #获取所有需要的贴图
        size = list(TextureSize.__members__.values())[sizeIndex].value
        extension = ".png"
        for map in asset.assetMaterials[0].maps:
            if map.uri == "":
                continue
            mapUri = os.path.join(rootFolder,map.uri)
            if map.UDIM:
                mapUri = mapUri.replace("udim","1001")
                udim = True
            if map.size.value != size:
                # 这里如果贴图是UDIM会把关键词udim替换为1001
                mapUri = ResizeTextureByStringUDIM(mapUri,os.path.join(rootFolder,f"Thumbs/{size}"),size,map.UDIM)[0]
                if not mapUri:
                    continue
            if map.type== AssetMapType.Albedo:
                BaseColor = mapUri
            elif map.type == AssetMapType.AO:
                Ao = mapUri
            elif map.type == AssetMapType.Metalness:
                Metallic = mapUri
            elif map.type == AssetMapType.Normal:
                Normal = mapUri
            elif map.type == AssetMapType.Roughness:
                Roughness = mapUri
            elif map.type == AssetMapType.Opacity:
                Opacity = mapUri
            elif map.type == AssetMapType.Translucency:
                Translucency = mapUri
            elif map.type == AssetMapType.Gloss:
                Glossiness = mapUri
            else:
                pass
        #尝试修复法线贴图路径
        if not Normal:
            logger.info(f"法线贴图未找到,尝试寻找")
            asset = fixNormalMiss(rootFolder,asset,assetImte.jsonUri)
        #获取对应的mesh
        if lod_level == "original":
            meshUri = os.path.join(rootFolder,asset.OriginMesh.uri)
        else:
            lod_index = GetLodLevelByName(lod_level)
            meshUri = os.path.join(rootFolder,asset.Lods[lod_index].mesh.uri)
            if asset.Lods[lod_index].normalMap.uri != "":
                Normal = os.path.join(rootFolder,asset.Lods[lod_index].normalMap.uri)
        logger.info(f"当前导出的模型的地址为{meshUri}")
        #尝试寻找其他法线贴图路径
        if not Normal:
            logger.info(f"法线贴图仍然未找到,尝试使用其他lod的法线贴图代替")
            for lod in asset.Lods:
                Normal = os.path.join(rootFolder,lod.normalMap.uri)
                if os.path.exists(Normal):
                    break
                else:
                    Normal = None
                    logger.info(f"不存在其他法线贴图")

        if not Roughness and Glossiness:
            Roughness = GenRoughnessMapUDIM(Glossiness,asset.AssetID,os.path.dirname(BaseColor),extension,udim)[0]
        if not (Roughness and BaseColor and Normal):
            return False
        elif asset.type == AssetType.Decal and not Opacity:
            return False
        elif asset.type == AssetType.Plant and not(Opacity and Translucency):
            return False
        armUri = GenARMMapUDIM(Ao,Roughness,Metallic,asset.AssetID,Opacity,Translucency,extension,asset.type,os.path.dirname(BaseColor),udim)[0]
        if not armUri:
            return False
        message = dict(
            name = asset.name.replace(" ","_"),#去除资产名称中的空格
            AssetID = asset.AssetID,
            assetFormat = asset.assetFormat.value,
            assetType = asset.type.value,
            baseColor = BaseColor,
            normal = Normal,
            arm = armUri,
            mesh = meshUri,
            udim = str(udim)
        )
        logger.info(f"将以下消息发送到UE中:\n{message}")
        flag = sendStringToUE(json.dumps(message), address)
        if flag:
            logger.info(f"消息发送成功,消息队列长度为{flag}")
            return True
        else:
            logger.info("消息发送失败")
            return False
    elif  assetImte.Format == AssetFormatN.UnrealEngine:
        meshUri = os.path.join(Backend.Get().getAssetRootPath(),asset.AssetID,asset.AssetID)
        message = dict(
            name = asset.name.replace(" ","_"),#去除资产名称中的空格
            AssetID = asset.AssetID,
            assetFormat = assetImte.Format.name,
            assetType = asset.type.value,
            baseColor = "",
            normal = "",
            arm = "",
            mesh = meshUri,
            udim = str(False)
        )
        logger.info(f"将以下消息发送到UE中:\n{message}")
        flag = sendStringToUE(json.dumps(message), address)
        if flag:
            logger.info(f"消息发送成功,消息队列长度为{flag}")
            return True
        else:
            logger.info("消息发送失败")
            return False
    elif assetImte.Format == AssetFormatN.SubstancePainter:
        command = ("import substance_painter.resource as res;res.import_project_resource('{}',res.Usage.SMART_MATERIAL,name='{}')"
                   .format(
                    os.path.join(rootFolder,asset.OriginMesh.uri).replace("\\","/")
                        ,asset.name))
        return SendCommandToSP(command)
    else:
        logger.info(f"目前仅支持导出FBX和虚幻引擎资产")
        return False

def refixDB():
    path = r'\\192.168.3.126\AssetLibrary'
    dataCachePath = os.path.join(path,"AssetDataCache.json")
    assetPath = os.path.join(path,"Assets")
    db = TinyDB(dataCachePath)
    User = Query()
    for data in db.all():
        db.update({"jsonUri":os.path.basename(data["jsonUri"])},User.AssetID == data["AssetID"])
        db.update({"previewFile":os.path.basename(data["previewFile"])},User.AssetID == data["AssetID"])
        db.update({"rootFolder":data["rootFolder"].removeprefix("O:/AssetLibrary\\Assets\\")},User.AssetID == data["AssetID"])
def GetLodLevelByName(name:str)->int:
    name = name.lower()
    if "lod" not in name:
        return False
    base_name,_ = os.path.splitext(name)
    lod_level = eval(base_name.split('lod')[-1])
    return lod_level

def fixAssetData():
    path = r'\\192.168.3.126\AssetLibrary'
    dataCachePath = os.path.join(path,"AssetDataCache.json")
    assetPath = os.path.join(path,"Assets")
    db = TinyDB(dataCachePath)
    for i in range(len(db.all())):
        data = db.all()[i]
        data["rootFolder"] = os.path.join(assetPath,data["rootFolder"])
        data["previewFile"] = os.path.join(assetPath,data["rootFolder"],data["previewFile"])
        data["jsonUri"] =os.path.join(assetPath,data["rootFolder"],data["jsonUri"])
        with open(data["jsonUri"],'r',encoding="utf-8") as f:
            assetData = json.loads(f.read())
        assetData["AssetIndex"] = i
        asset = Asset.from_dict(assetData)
        asset.JsonUri = os.path.basename(asset.JsonUri)
        for i in range(len(asset.Lods)):
            asset.Lods[i].mesh.uri = os.path.basename(asset.Lods[i].mesh.uri)
            asset.Lods[i].normalMap.uri = os.path.basename(asset.Lods[i].normalMap.uri)
        asset.OriginMesh.uri = os.path.basename(asset.OriginMesh.uri)
        asset.ZbrushFile = os.path.basename(asset.ZbrushFile)
        for i in range(len(asset.assetMaterials[0].maps)):
            asset.assetMaterials[0].maps[i].uri = os.path.basename(asset.assetMaterials[0].maps[i].uri)
        asset.previewFile[0] = os.path.basename(asset.previewFile[0])
        asset.rootFolder = asset.rootFolder.split("\\")[-1]
        assetData = asset.to_dict()
        try:
            shutil.copy(data["jsonUri"],data["jsonUri"] + ".bak")
        except:
            pass
        with open(data["jsonUri"],'w+',encoding="utf-8") as f:
            f.write(json.dumps(assetData))


def checkReadAccess(path):
    return(os.access(path,os.R_OK))
def checkWriteAccess(path):
    return(os.access(path,os.W_OK) and os.access(path,os.X_OK) )

def getExeVersion(path):
    information_parser = Dispatch("Scripting.FileSystemObject")
    version = information_parser.GetFileVersion(path)
    return(version)

def compareVersion(old:str,new:str):
    oSplit = old.split(".")
    nSplit = new.split(".")
    for i in range(len(oSplit)):
        if eval(oSplit[i]) < eval(nSplit[i]):
            return True
    return False

def get_pid(pname):
    import psutil
    pids = []
    for proc in psutil.process_iter():
        if proc.name() == pname:
            pids.append(proc.pid)
    if len(pids) <= 1:
        return False
    else:
        return True

def GetExePath():
    exePath = sys.executable if getattr(sys, 'frozen', False) else __file__
    if '.exe' not in exePath:
        return False
    return exePath


def checkisBackendRunning(parent=None):
    if Backend.Get().isBackendAvailable():
        return True
    else:
        QMessageBox.warning(parent,"提示","服务器地址不可用,请检查设置")
        return False


def AddAssetDataToDataBase(asset:Asset):
        #将资产添加到资产数据库中
        assetToLibraryData = dict(
            name        = asset.name,
            AssetID     = asset.AssetID,
            jsonUri     = asset.JsonUri,
            TilesH      = asset.TilesH,
            Tilesv      = asset.TilesV,
            asset       = asset.assetFormat.value,
            category    = asset.category,
            subcategory = asset.subcategory,
            surfaceSize = asset.surfaceSize.value,
            tags        = asset.tags,
            type        = asset.type.value,
            previewFile = asset.previewFile[0],
            rootFolder  = asset.rootFolder,
            lods        = [lod.level for lod in asset.Lods],
            SearchWords = f"{asset.name} {asset.AssetID} {asset.category} {asset.subcategory}"+" ".join(asset.tags),
            #目前从软件本身入库的资产的格式都是FBX
            Format      = "FBX",
            SoftwareVersion = "None"
            )
        logger.info(f"将如下资产添加到服务器中:\n{assetToLibraryData}")
        Backend.Get().addAssetToDB(assetToLibraryData)
        return assetToLibraryData


class CustomWorker(QThread):
    onFinished = pyqtSignal()
    def __init__(self, fun,parent=None) -> None:
        super().__init__(parent)
        self.fun = fun
    def run(self) -> None:
        self.fun()
        self.onFinished.emit()

class SocketThread(QThread):
    isrunning = True
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.host = "127.0.0.1"
        self.port = 45450
        self.__isListening = True
    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定地址和端口
        self.socket.bind((self.host, self.port))
        # 开始监听，参数5表示等待连接的最大数量
        self.socket.listen()
        print(f"Server is listening on {self.host}:{self.port}")
        # 无限循环来接受客户端连接
        while self.__isListening:
            try:
                # 接受客户端连接，这个调用会阻塞，直到接收到连接
                conn, addr = self.socket.accept()
            except OSError as e:
                print(f"An error occurred: {e}")
                break
            with conn:
                print(f"Connected by {addr}")
                # 持续接收数据
                while True:
                    try:
                        # 接收数据，1024是接收缓冲区的大小
                        data = conn.recv(1024)
                        if not data:
                            # 没有数据，客户端可能关闭了连接
                            break
                        # 打印接收到的数据
                        message = data.decode()
                        print(f"Received: {message}")
                        # 可以选择回显数据给客户端
                        # conn.sendall(data)
                    except Exception as e:
                        # 捕获异常，可能是连接中断
                        print(f"An error occurred: {e}")
                        break
        print("listening stoped")
    def stop(self):
        self.__isListening = False
        self.socket.close()
    @classmethod
    def StartListening(cls,parent=None):
        thread = SocketThread(parent)
        thread.start()
        return thread

def get_current_vesrion():
    version = ""
    exePath = GetExePath()
    if exePath:
        version = getExeVersion(exePath)
    return version

def ConvertAssetPathsToAbs(asset:Asset,assetLibrarypath:str):
    assetRootPath = os.path.join(assetLibrarypath,asset.rootFolder)
    
    asset.rootFolder = assetRootPath

    asset.JsonUri = os.path.join(assetRootPath,asset.JsonUri)

    for i,lod in enumerate(asset.Lods):
        asset.Lods[i].mesh.uri = os.path.join(assetRootPath,asset.Lods[i].mesh.uri)
        if asset.Lods[i].normalMap.uri != "":
            asset.Lods[i].normalMap.uri = os.path.join(assetRootPath,asset.Lods[i].normalMap.uri)
    
    for i,meshVar in enumerate(asset.MeshVars):
        asset.MeshVars[i].OriginMesh.uri = os.path.join(assetRootPath,asset.MeshVars[i].OriginMesh.uri)
        for i,lod in enumerate(asset.MeshVars[i].Lods):
            asset.MeshVars[i].Lods[i].mesh.uri = os.path.join(assetRootPath,asset.MeshVars[i].Lods[i].mesh.uri)
            if asset.MeshVars[i].Lods[i].normalMap.uri != "":
                asset.MeshVars[i].Lods[i].normalMap.uri = os.path.join(assetRootPath,asset.MeshVars[i].Lods[i].normalMap.uri)

    if asset.OldJson != "":
        asset.OldJson = os.path.join(assetRootPath,asset.OldJson)

    if asset.OriginMesh.uri != "":
        asset.OriginMesh.uri = os.path.join(assetRootPath,asset.OriginMesh.uri)

    if asset.ZbrushFile != "":
        asset.ZbrushFile = os.path.join(assetRootPath,asset.ZbrushFile)
    
    for i,material in enumerate(asset.assetMaterials):
        for j,map in enumerate(asset.assetMaterials[i].maps):
            asset.assetMaterials[i].maps[j].uri = os.path.join(assetRootPath,asset.assetMaterials[i].maps[j].uri)

    for i,previewImage in enumerate(asset.previewFile):
        asset.previewFile[i] = os.path.join(assetRootPath,asset.previewFile[i])
    
    return asset



def checkTextureUDIM(uri:str):
    match = re.search(r'\.(\d{4})\.', uri)
    if match:
        return match.group(1)
    else:
        return False

def GetUDIMTextures(uri:str):
    if "udim" in uri:
        flag = 'udim'
    elif '1001' in uri:
        flag = '1001'
    textures = []
    for i in range(1,10000):
        udimFlag = "1{:03d}".format(i)
        textureUri = uri.replace(flag,udimFlag)
        if os.path.exists(textureUri):
            textures.append(textureUri)
        else:
            break
    return textures

def fix_error_image(image_uri:str):
    max_size = 1024
    image = Image.open(image_uri, "r")

    width, height = image.size
    maxLength = max(width, height)
    if maxLength <= max_size:
        return
    if width > height:
        new_width = max_size
        new_height = int(height * (max_size / width))
    else:
        new_height = max_size
        new_width = int(width * (max_size / height))
    resized_image = image.resize((new_width, new_height))
    resized_image.save(image_uri, quality=85, optimize=True)


if __name__ == "__main__":
    exePath = "D:\Documents\ZCXCode\MyBridge\dist\MyBridge\MyBridge.exe"
    getExeVersion(exePath)



    

    





    
