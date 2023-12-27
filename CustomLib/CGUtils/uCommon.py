#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################
import functools
import os
import sys

from Qt import QtCore, QtWidgets
import time

#template worker
class MWorker(QtCore.QThread):
    def __init__(self,parent=None):
        super(MWorker,self).__init__(parent)
    def run(self,*args,**kwargs):
        import time
        time.sleep(4)


# 定义一些装饰器
def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"调用函数: {func.__name__} 使用参数: {args}, {kwargs},返回值为{result}")
        return result
    return wrapper


# some function
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
@log_function_call
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

