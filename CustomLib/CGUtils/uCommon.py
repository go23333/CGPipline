#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################
import functools
import os
import sys
import time
from enum import Enum, auto

from Qt import QtCore, QtWidgets


#定义一些结构
class FilmBackPreset():
    Film = "16:9 Film"
    DigitalFilm = "16:9 Digital Film"
    DSLR = "16:9 DSLR"
    Super8mm = "Super 8mm"
    Super16mm = "Super 16mm"


#template worker
class MWorker(QtCore.QThread):
    def __init__(self,parent=None):
        super(MWorker,self).__init__(parent)
    def run(self,*args,**kwargs):
        import time
        time.sleep(4)



# some function
def applyMacro(parten,parseresult):
    for key in parseresult:
        parten = parten.replace(f"${key}",parseresult[key])
    return parten

def parseCameraName(name):
    parseResult = {}
    nameSlpitList = name.split("_")
    if len(nameSlpitList) < 5:
        return False # 如果名称不合法返回假
    parseResult["ep"] = name.split("_")[0]
    parseResult["sc"] = name.split("_")[1]
    parseResult["number"] = name.split("_")[2]
    parseResult["frameStart"] = name.split("_")[3]
    parseResult["frameEnd"] = name.split("_")[4]
    parseResult["fullName"] = name.split(".")[0]
    return parseResult

CameraPathMacros = [
    "$ep",
    "$sc",
    "$number",
    "$frameStart",
    "$frameEnd",
    "$fullName",
]

def getApplication()->QtWidgets.QApplication:
    Application = QtWidgets.QApplication.instance()
    if not Application:
        Application = QtWidgets.QApplication(sys.argv)
    return Application

def isPathValid(path):
    if not os.path.isdir(path):
        return False
    if not os.path.exists(path):
        return False
    return True
def calcMD5(text):
    import hashlib
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return(m.hexdigest())

def getfilesFromPath(path,extension=None):
    filePaths = []
    for root,folder,files in os.walk(path):
        if extension:
            extension = extension.lower()
            files = [file for file in files if file.casefold().endswith(extension)]
        for file in files:
            filePaths.append(os.path.join(root,file))
    return filePaths
def getSizeStr(size):
    unittype = ["KB","MB","GB"]
    reslut = ""
    for unit in unittype:
        size = size/1024
        if size < 1024:
            reslut =f"{round(size,2)} {unit}"
            return reslut

def getFilesDataFrompath(path,extension=None):
    files = getfilesFromPath(path,extension)
    Datas = []
    for file in files:
        modifyTime = str(time.asctime(time.localtime(os.path.getmtime(file))))
        size = os.path.getsize(file)
        path = file
        name = os.path.splitext(os.path.basename(file))[0]
        md5 = calcMD5(name + modifyTime + path)
        dicData = {}
        dicData["name"] = name
        dicData["modifyTime"] = modifyTime
        dicData["size"] = getSizeStr(size)
        dicData["path"] = path
        dicData["MD5"] = md5
        dicData["imported"] = False
        Datas.append(dicData)
    return Datas

def normalizePath(path):
    return(os.path.normpath(path))


if __name__ == "__main__":
    files = getfilesFromPath(r"D:\UnrealPiplineTemp","fbx")
    cameraDatas = []
    for file in files:
        size = os.path.getsize(file)
        modifyTime = os.path.getmtime(file)
        path = file
        name = os.path.splitext(os.path.basename(file))[0]
        dicCameraData = {}
        dicCameraData["name"] = name
        dicCameraData["modifyTime"] = modifyTime
        dicCameraData["size"] = size
        dicCameraData["path"] = path
        cameraDatas.append(dicCameraData)
    print (cameraDatas)

