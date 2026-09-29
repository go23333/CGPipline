import logging

import base64
import os.path
import substance_painter.logging as log
import substance_painter.ui as ui
import substance_painter.resource as res
import substance_painter.js as js


from PySide6.QtWidgets import QListView
from PySide6.QtGui import  QAction
from  PySide6.QtCore import  Qt

import  http.client
import  json


class Backend:
    instance = None
    def __init__(self):
        self.host = "192.168.3.20:5050"
    def GetCategory(self) -> dict:
        conn = http.client.HTTPConnection(self.host,timeout=4)
        try:
            conn.request("GET", "/config/category")
            response = conn.getresponse()
            data = response.read().decode('utf-8')
            return json.loads(data)
        except TimeoutError as e:
            logging.error(f"HTTP 链接错误{e}")
            return {}
    def GetAssetID(self):
        conn = http.client.HTTPConnection(self.host,timeout=4)
        try:
            conn.request("GET","/assets/assetsID")
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            return json.loads(data)["assetID"]
        except TimeoutError as e:
            logging.error(f"HTTP 链接错误{e}")
            return False
        except ConnectionAbortedError as e:
            logging.error(f"HTTP 链接错误{e}")
            return False
    def GetRootPath(self):
        conn = http.client.HTTPConnection(self.host,timeout=4)
        try:
            conn.request("GET","/config/assetsLibraryPath")
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            return str(json.loads(data)["uri"])
        except TimeoutError as e:
            logging.error(f"HTTP 链接错误{e}")
            return False
    def GetAssetCount(self):
        conn = http.client.HTTPConnection(self.host,timeout=4)
        try:
            conn.request("GET","/assets/count")
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            return json.loads(data)
        except TimeoutError as e:
            logging.error(f"HTTP 链接错误{e}")
            return False
    def AddAssetToDB(self,asset):
        conn = http.client.HTTPConnection(self.host,timeout=4)
        try:
            conn.request("POST","/assets/add",body=json.dumps(asset))
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            return json.loads(data)
        except TimeoutError as e:
            logging.error(f"HTTP 链接错误{e}")
            return False
    @classmethod
    def get(cls):
        if not cls.instance:
            cls.instance = Backend()
        return  cls.instance



class SPResource:
    name:str = ""
    imageBase64:str = ""
    shelfName:str = "###############"
    __realResource:res.Resource = None
    datas = {}
    def __init__(self,datas:dict,resource:res.Resource):
        self.name = datas[0]
        self.imageBase64 = GetImageFromHTML(datas[3])
        self.__realResource = resource

        url = self.__realResource.identifier().url()
        self.shelfName = url[11:url.find("/",11)]

        self.datas = js.evaluate(f'alg.resources.getResourceInfo("{self.__realResource.identifier().url()}")')


    def SavePreviewImage(self,output_dir:str,fileName:str):
        if not self.imageBase64:
            return False
        return SaveBase64Image(self.imageBase64,output_dir,fileName)
    @property
    def url(self):
        return self.datas["filePath"]
    def GetPreviewImageExtension(self):
        return detect_image_format(self.imageBase64)
    def GetShelfName(self):
        return self.shelfName
    def GetType(self):
        return  self.__realResource.type()
    def getExtension(self):
        _,ext = os.path.splitext(self.datas["filePath"])
        return ext




def GetSelectedResource():
    mainWindow = ui.get_main_window()
    listView:QListView = mainWindow.findChild(QListView,name="resources" ,options=Qt.FindChildOption.FindChildrenRecursively)
    index = listView.currentIndex()

    currentItemData = listView.model().itemData(index)
    if index.row() == -1:
        return  False

    actionMaterial:QAction = mainWindow.findChild(QAction,name="materials_action" ,options=Qt.FindChildOption.FindChildrenRecursively)
    actionSmartMaterial:QAction = mainWindow.findChild(QAction,name="smart_materials_action" ,options=Qt.FindChildOption.FindChildrenRecursively)
    actionSmartMasks:QAction = mainWindow.findChild(QAction,name="smart_masks_action" ,options=Qt.FindChildOption.FindChildrenRecursively)
    actionFilters:QAction = mainWindow.findChild(QAction,name="filters_action" ,options=Qt.FindChildOption.FindChildrenRecursively)
    actionBrushes:QAction = mainWindow.findChild(QAction,name="brushes_action" ,options=Qt.FindChildOption.FindChildrenRecursively)
    actionAlphas:QAction = mainWindow.findChild(QAction,name="alphas_action" ,options=Qt.FindChildOption.FindChildrenRecursively)
    actionTextures:QAction = mainWindow.findChild(QAction,name="textures_action" ,options=Qt.FindChildOption.FindChildrenRecursively)
    actionEnv:QAction = mainWindow.findChild(QAction,name="environments_action" ,options=Qt.FindChildOption.FindChildrenRecursively)
    actionFont:QAction = mainWindow.findChild(QAction,name="fonts_action" ,options=Qt.FindChildOption.FindChildrenRecursively)


    actions = {
        actionMaterial:"basematerial",
        actionSmartMaterial:"smartmaterial",
        actionSmartMasks : 'smartmask',
        actionFilters : 'filter',
        actionBrushes : "brush",
        actionAlphas : "alpha",
        actionTextures : "texture",
        actionEnv : "environment",
        actionFont : "font"
    }
    currentType = ""
    for f in actions.keys():
        if f.isChecked():
            currentType = actions[f]
            break
    resources:res.Resource = res.search(f"u:{currentType} "
                           f"n:{currentItemData[0]}")[0]



    return SPResource(currentItemData,resources)


def GetImageFromHTML(htmlstr:str)->str:
    indexStart = htmlstr.find('base64,')
    indexEnd = htmlstr.find('"', indexStart)
    return htmlstr[indexStart + 7:indexEnd]



def detect_image_format(base64_str):
    if base64_str.startswith('/9j/'):
        return 'jpg'
    elif base64_str.startswith('iVBORw0KGgo'):
        return 'png'
    elif base64_str.startswith('R0lGODlh'):
        return 'gif'
    else:
        return 'png'  # 默认使用png


def SaveBase64Image(base64_str,output_dir:str,fileName:str,overwrite:bool=True):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        imageFormat = detect_image_format(base64_str)
        fileName = f"{fileName}.{imageFormat}"
        output_path = os.path.join(output_dir,fileName)

        if os.path.exists(output_path):
            if not overwrite:
                return True
            else:
                os.remove(output_path)

        image_data = base64.b64decode(base64_str)
        with open(output_path,"wb") as f:
            f.write(image_data)
        log.info(f"图片已经保存到:{output_path}")
        return output_path
    except Exception as e:
        log.info(f"保存图片失败:{e}")
        return False
