#coding=utf-8
import json
import os
import re
import webbrowser
import tempfile
import shutil
from mayaTools.core.log import log

def GetTempPath():
    return (tempfile.gettempdir())
def getWorkDir():
    workDir = r"d:\\Documents\\CGPipline\\maya\\"
    if not os.path.exists(workDir):
        os.makedirs(workDir)
    return workDir

def ListAllTexFromFolder(FolderPath):
    files = os.listdir(FolderPath)
    res = []
    for file in files:
        if len(file.split('.')) > 1:
            res.append(FolderPath+file)
    return(res)
def normailizePath(path):
    path = path.replace('\\','/')
    if path[-1] != '/' and '.' not in path:
        path = path + '/'
    return path

def keyFilter(PathList,key):
    '''base input key filter input list'''
    outputList = []
    for path in PathList:
        if key.lower() in path.lower():
            outputList.append(path)
    return(outputList)
def getFilesByKeyWords(rootPath,keyWord):
    files = ListAllTexFromFolder(rootPath)
    return(keyFilter(files,keyWord))

def IsUDIMFormate(TexturePath):
    fileName = TexturePath.split('/')[-1]
    pattern = re.compile(r'\.\<\w{4}\>\.')
    res = pattern.search(fileName)
    if res != None:
        return(res.group())
        
    pattern = re.compile(r'\.\d{4}\.')
    res = pattern.search(fileName)
    if res != None:
        return(res.group())

    return False
        
def calUDIMCount(TexturePath):
    UDIMKeyWord = IsUDIMFormate(TexturePath)
    if not UDIMKeyWord:
        return 1
    i = 1
    while True:
        tile = '.' + str(1000 + i) + '.'
        path = TexturePath.replace(UDIMKeyWord,tile)
        if not os.path.exists(path):
            return i-1
        i = i+1

def getUDIMTextures(TexturePath):
    UDIMKeyWord = IsUDIMFormate(TexturePath)
    textures = []
    if not UDIMKeyWord:
        return [TexturePath]
    i = 1
    while True:
        tile = '.' + str(1000 + i) + '.'
        path = TexturePath.replace(UDIMKeyWord,tile)
        if not os.path.exists(path):
            if textures == []:
                return [TexturePath]
            else:
                return textures
        textures.append(path)
        i = i+1


def getOtherChannelTexture(filePath,attr):
    keys = ['ARMS','Normal','Anisotropy','Mask','Opacity','Emissive','Occlusion','Roughness','Cavity','Metallic','Specular']
    info = {}
    for key in keys:
        subPath = filePath.replace(attr,key)
        if os.path.exists(subPath) and subPath != filePath:
            info[key] = subPath
        else:
            info[key] = ''
    return info
def sortByAscll(strlist):
    for j in range(0,len(strlist)-1):
        for i in range(0,len(strlist)-1):
            if strlist[i] > strlist[i+1]:
                tmp = strlist[i]
                strlist[i] = strlist[i+1]
                strlist[i+1] = tmp
    return strlist
def writejson(data,path):
    jsondata = json.dumps(data)
    file = open(path,'w+')
    file.write(jsondata)
    file.close()

def getRootPath():
    import mayaTools
    return (mayaTools.__path__[0])


def openWeb(webPath,*args):
	webbrowser.open(webPath, new=0, autoraise=True)


def CopyFileToDir(filePath,dir):
    fileName = os.path.basename(filePath)
    newFilePath = os.path.join(dir,fileName)
    try:
        shutil.copyfile(filePath,newFilePath)
    except:
        log("file {0} copy failed,please check".format(filePath))
    return filePath

def CopyFilesToDir(files,dir):
    for file in files:
        CopyFileToDir(file,dir)