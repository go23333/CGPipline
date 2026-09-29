#coding=utf-8
from __future__ import division,print_function
import shutil
import stat
from tempfile import gettempdir
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omi
import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import os
import json


from PySide2.QtWidgets import *
from PySide2.QtCore import Qt,QRect,Signal
from PySide2.QtGui import QPixmap,QColor,QPainter

from mayaTools.core.backend import Backend
import mayaTools.core. mayaLibrary as ml



if Backend.Get().isBackendAvailable():
    category = Backend.Get().getCategories()
else:
    category = {}

def GetCategorys(level):
    if level == 0:
        return list(category.keys())
    elif level == 1:
        return [ele for value in category.values() for ele in value.keys() ]
    elif level == 2:
        return [c for value in category.values() for ele in value.keys() for c in value[ele]]
    else:
        raise
def GetSubCategorys(parentIndex):
    return [ele for ele in category[GetCategorys(0)[parentIndex]].keys()]

def grap_current_3d_view_to_image(path):
    view = omi.M3dView.active3dView()
    view.setObjectDisplay(omi.M3dView.kDisplayEverything ^ omi.M3dView.kDisplayGrid)
    view.refresh()
    image = om.MImage()
    image.create(view.portWidth(),view.portHeight(),4,om.MImage.kFloat)
    view.readColorBuffer(image,True)
    view.setObjectDisplay(omi.M3dView.kDisplayEverything)
    _,ext = os.path.splitext(path)
    image.writeToFile(path,ext[1:])
def recursion_get_textureNode(node):
    TextureNodes = []
    sNodes = cmds.listConnections(node,d=0,scn=1)
    if not sNodes:
        return TextureNodes
    for node in sNodes:
        if cmds.nodeType(node) == "file":
            TextureNodes.append(node)
        elif cmds.nodeType(node) in ["RedshiftNormalMap","RedshiftSprite"]:
            TextureNodes.append(node)
        else:
            TextureNodes.extend(recursion_get_textureNode(node))  
    return TextureNodes

def get_all_udim_tiles(texturePath):
    textures = []
    udimFlag = "1001"
    if "<UDIM>" in texturePath:
        udimFlag = "<UDIM>"
    elif "<udim>" in texturePath:
        udimFlag = "<udim>"
    for i in range(1001,2000):
        path = texturePath.replace(udimFlag,str(i))
        if os.path.exists(path):
            textures.append(path)
        else:
            return textures
    return textures

def scaleMap(width,height,mapPath):
    original_pixelmap = QPixmap(mapPath)

    scaled_pixmap = QPixmap(width,height)
    scaled_pixmap.fill(QColor(80,80,80,0))


    painter = QPainter(scaled_pixmap)
    
    try:
        scaled_factor = min(width / float(original_pixelmap.width()+0.1), height / float(original_pixelmap.height()+0.1))
    except ZeroDivisionError:
        scaled_factor = 0.3
        pass

    scaled_size = original_pixelmap.size() * scaled_factor

    x = (width - scaled_size.width()) / 2
    y = (height - scaled_size.height()) / 2
    
    painter.drawPixmap(QRect(int(x), int(y), scaled_size.width(), scaled_size.height()), original_pixelmap)

    painter.end()

    return scaled_pixmap

class LayoutWidget(QWidget):
    class LayoutType:
        VBOX = 1
        HBOX = 2
    def __init__(self,layoutType,parent=None):
        super(LayoutWidget,self).__init__(parent)
        parent.layout().addWidget(self)
        if layoutType == self.LayoutType.VBOX:
            self.layout_main = QVBoxLayout(self)
        elif layoutType == self.LayoutType.HBOX:
            self.layout_main = QHBoxLayout(self)
        self.layout_main.setContentsMargins(0,0,0,0)
        self.layout_main.setSpacing(0)
        self.setLayout(self.layout_main)
    def setContentsMargins(self,l,t,r,b):
        self.layout_main.setContentsMargins(l,t,r,b)
    def setSpacing(self,value):
        self.layout_main.setSpacing(value)
    def addWidget(self,widget):
        self.layout_main.addWidget(widget)
    def setAlign(self,Align):
        self.layout_main.setAlignment(Align)

        

class ImageCaptureView(QWidget):
    def __init__(self,parent=None,size=128):
        super(ImageCaptureView,self).__init__(parent)
        self._currentImagePath  = None
        self.image_size = size
        self.__initUI()
    def __initUI(self):
        layout_main = QVBoxLayout()
        layout_main.setContentsMargins(0,0,0,0)
        layout_main.setSpacing(10)
        layout_main.setAlignment(Qt.AlignTop)
        self.setLayout(layout_main)


        self.image_viewer = QLabel(parent=self)
        self.image_viewer.setFixedSize(self.image_size,self.image_size)
        self.image_viewer.setStyleSheet("background-color: rgb(35, 35, 35);")
        layout_main.addWidget(self.image_viewer)



        area_bottom = LayoutWidget(LayoutWidget.LayoutType.HBOX,self)
        self.buttonCapture = QPushButton(parent=self)
        self.buttonCapture.setFixedSize(16,16)
        self.buttonCapture.clicked.connect(self.captureViewport)
        area_bottom.addWidget(self.buttonCapture)
        area_bottom.setSpacing(5)
        area_bottom.setAlign(Qt.AlignLeft)
        self.buttonSelectImage = QPushButton(parent=self)
        self.buttonSelectImage.setFixedSize(16,16)
        self.buttonSelectImage.clicked.connect(self.select_Image)
        area_bottom.addWidget(self.buttonSelectImage)
    def setImage(self,imagePath):
        self._currentImagePath = imagePath
        self.image_viewer.setPixmap(scaleMap(self.image_size,self.image_size,imagePath))
    def getCurrentImagePath(self):
        return self._currentImagePath
    def captureViewport(self):
        tempImagePath = os.path.join(gettempdir(),"view_port_temp_iamge.png")
        grap_current_3d_view_to_image(tempImagePath)
        self.setImage(tempImagePath)
    def select_Image(self):
        file = QFileDialog.getOpenFileName(parent=self,caption="选择要作为预览图的文件",filter="Images (*.png *.jpg)")[0]
        if not file:
            return
        self.setImage(file)
    def get_current_Image(self):
        return self._currentImagePath



class ComboxGroup(QWidget):
    currentTextChanged = Signal(str)
    def __init__(self,text,parent=None,lebelWidth=80):
        super(ComboxGroup,self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self.label = QLabel(parent=self,text=text)
        self.label.setFixedWidth(50)
        layout.addWidget(self.label)
        self.combox = QComboBox(parent=self)
        self.combox.currentTextChanged.connect(self.__currentTextChange)
        layout.addWidget(self.combox)
    def addItem(self,item):
        self.combox.addItem(item)
    def addItems(self,items):
        self.combox.addItems(items)
    def clear(self):
        self.combox.clear()
    def currentText(self):
        return(self.combox.currentText())
    def __currentTextChange(self,text):
        self.currentTextChanged.emit(text)

class LineEditGroup(QWidget):
    def __init__(self,text,parent=None,lebelWidth=80):
        super(LineEditGroup,self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        self.label = QLabel(parent=self,text=text)
        self.label.setFixedWidth(50)
        layout.addWidget(self.label)
        self.lineEdit = QLineEdit(parent=self)
        layout.addWidget(self.lineEdit)
    def set_text(self,text):
        self.lineEdit.setText(text)
    def text(self):
        return self.lineEdit.text()


class ExportToLibraryUI(MayaQWidgetDockableMixin,QWidget):
    def __init__(self,parent=None):
        super(ExportToLibraryUI,self).__init__(parent)
        self.setWindowTitle("资产入库工具")
        self.resize(500,250)
        self.__initUI()
    def __initUI(self):
        layout_main = QVBoxLayout()
        layout_main.setContentsMargins(10,10,10,10)
        layout_main.setSpacing(0)
        layout_main.setAlignment(Qt.AlignTop)
        self.setLayout(layout_main)

        area_info = LayoutWidget(LayoutWidget.LayoutType.HBOX,self)
        area_info.setSpacing(15)

        area_info_left = LayoutWidget(LayoutWidget.LayoutType.VBOX,area_info)
        self.imageCaptureView = ImageCaptureView(self,size=200)
        area_info_left.addWidget(self.imageCaptureView)

        area_info_right = LayoutWidget(LayoutWidget.LayoutType.VBOX,area_info)
        area_info_right.setAlign(Qt.AlignTop)
        area_info_right.setContentsMargins(0,0,0,0)
        area_info_right.setSpacing(20)
        self.line_name = LineEditGroup("名称:",self)
        area_info_right.addWidget(self.line_name)

        self.line_tag = LineEditGroup("标签:",self)
        area_info_right.addWidget(self.line_tag)

        self.combox_type = ComboxGroup("类型:",self)
        area_info_right.addWidget(self.combox_type)
        self.combox_type.addItem("3D Assets")


        self.combox_category = ComboxGroup("主分类:",self)
        self.combox_category.addItems(GetCategorys(0))
        
        area_info_right.addWidget(self.combox_category)

        self.combox_sub_category = ComboxGroup("子分类:",self)
        self.__setSubCategory(self.combox_category.currentText())
        self.combox_category.currentTextChanged.connect(self.__setSubCategory)



        area_info_right.addWidget(self.combox_sub_category)

        areaInput = LayoutWidget(LayoutWidget.LayoutType.HBOX,self)
        areaInput.setAlign(Qt.AlignRight)
        self.buttonAddToLibrary = QPushButton(parent=self,text="添加到库中")
        self.buttonAddToLibrary.clicked.connect(self.add_to_library)
        self.buttonAddToLibrary.setFixedWidth(100)
        areaInput.addWidget(self.buttonAddToLibrary)
    def __setSubCategory(self,text):
        self.combox_sub_category.clear()
        self.combox_sub_category.addItems([item for item in category[text].keys()])       
    def add_to_library(self):
        #获取选择的对象
        selected_objs = cmds.ls(sl=1)
        if not selected_objs:
            QMessageBox.warning(self,"错误","没有选择任何物体")
            return
        #获取名称
        name = self.line_name.text()
        if not name:
            QMessageBox.warning(self,"错误","名称不能为空")
            return
        #获取标签
        tag = self.line_tag.text()
        if not tag:
            result = QMessageBox.question(self,"提示","未输入标签,是否继续?",QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
            if result == QMessageBox.No:
                return
        tag = tag.replace(u"，",",")
        tags = [t for t in tag.split(",") if t!=""]
        #获取预览图片
        previewImagePath = self.imageCaptureView.get_current_Image()
        if not previewImagePath:
            QMessageBox.warning(self,"错误","未设置预览图片")
            return
        #获取分类和子分类
        category = self.combox_category.currentText()
        subCategory = self.combox_sub_category.currentText()
        #获取资产ID
        assetID = Backend().Get().getAssetID()
        #获取类型
        assetType = self.combox_type.currentText()
        #获取maya版本
        mayaVersion = cmds.about(version=1)
        if assetType == "3D Assets":
            #获取并创建根目录
            rootpath = "{}/{}".format(Backend.Get().getAssetRootPath(),assetID)
            textureRootPath = rootpath + "/Textures"
            if not os.path.exists(textureRootPath):
                os.makedirs(textureRootPath)
            #拼接MB文件路径
            mbFilePath = os.path.join(rootpath,"{}.mb".format(assetID))
            #将选中对象关联的贴图移动到新的路径
            texFileList = []
            textureNodes = []
            for obj in selected_objs:
                #获取所有的shape
                shapes = cmds.listRelatives(obj,ad=1,c=1,ni=1,type='shape')
                if not shapes: #跳过不含shape的对象
                    continue
                for shape in shapes:
                    if cmds.getAttr(shape+".intermediateObject"):#跳过中间对象
                        continue
                    ses = cmds.listConnections(shape,type='shadingEngine')
                    if not ses:
                        continue #跳过没有材质引擎的对象
                    se = ses[0]
                    materials = cmds.listConnections(se,d=0,scn=1,type='RedshiftMaterial') or []
                    for material in materials:
                        textureNodes.extend(recursion_get_textureNode(material))
            oldTexturePath = []

            textureNodes = set(textureNodes)#贴图节点去重

            for texNode in textureNodes:
                UDIM = False
                if cmds.nodeType(texNode) in ["RedshiftNormalMap","RedshiftSprite"]:
                    attrName = "tex0"
                elif cmds.nodeType(texNode) == "file":
                    attrName = "fileTextureName"
                    if cmds.getAttr(texNode + ".uvTilingMode") != 0:
                        UDIM = True
                filePath = cmds.getAttr(texNode + "." + attrName)
                oldTexturePath.append(filePath)
                if "<UDIM>" in filePath or "<udim>" in filePath:
                    UDIM = True
                if not UDIM:
                    texFileList.append(filePath)
                else:
                    texFileList.extend(get_all_udim_tiles(filePath))
                # #设置新的贴图路径
                baseName = os.path.basename(filePath)
                cmds.setAttr(texNode + "." + attrName,os.path.join(textureRootPath,baseName),type= "string")

            cmds.file(mbFilePath, exportSelected=True, type='mayaBinary', force=True)#导出mb文件

            #还原贴图节点的路径
            textureNodes = list(textureNodes)
            for i in range(len(textureNodes)):
                if cmds.nodeType(textureNodes[i]) in ["RedshiftNormalMap","RedshiftSprite"]:
                    attrName = "tex0"
                elif cmds.nodeType(textureNodes[i]) == "file":
                    attrName = "fileTextureName"
                cmds.setAttr(textureNodes[i] + "." + attrName,oldTexturePath[i],type= "string")
            
            #复制收集到的贴图
            texFileList = set(texFileList)#去重
            
            #检查贴图源文件是否存在
            for texFile in texFileList:
                if not os.path.exists(texFile):
                    QMessageBox.warning(self,u"错误",u"贴图{}文件不存在请保证所有贴图文件存在后再入库".format(texFile))
                    shutil.rmtree(rootpath)
                    return

            for texFile in texFileList:
                baseName = os.path.basename(texFile)
                newPath = os.path.normpath(os.path.join(textureRootPath,baseName))
                assert not os.path.exists(newPath),u"error,file {} exists".format(newPath)
                shutil.copy(texFile,newPath)
                try:
                    current_permissions = os.stat(newPath).st_mode
                    os.chmod(newPath,current_permissions | stat.S_IWRITE)
                except:
                    print(u"无法移除文件:{}的只读属性".format(newPath))

            #复制预览图到新目录
            _,ext = os.path.splitext(previewImagePath)
            previewImageNewPath = os.path.join(rootpath,"{}_preview_1{}".format(assetID,ext))
            previewImagePath = shutil.copy(previewImagePath,previewImageNewPath)

            asset = dict(
                name           = name,
                ZbrushFile     = "",
                AssetID        = assetID,
                rootFolder     = assetID,
                JsonUri        = "{}.json".format(assetID),

                tags           = tags,
                previewFile    = [os.path.basename(previewImageNewPath)],
                Lods           = [],
                assetMaterials = [],
                MeshVars       = [],

                type           = "3D Assets",
                category       = category,
                subcategory    = subCategory,
                surfaceSize    = "1 Meter",
                assetFormat    = "FBX",

                OriginMesh     = dict(
                    uri = os.path.basename(mbFilePath),
                    name = os.path.basename(mbFilePath),
                    extension = ".mb"
                ),

                TilesV         = "false",
                TilesH         = "false",

                AssetIndex     = Backend.Get().getAssetsCount(),
                OldJson        = "",
            )
            # 提取放在数据库中的数据
            assetToLibraryData = dict(
                name        = asset["name"],
                AssetID     = asset["AssetID"],
                jsonUri     = asset["JsonUri"],
                TilesH      = asset["TilesH"],
                Tilesv      = asset["TilesV"],
                asset       = asset["assetFormat"],
                category    = asset["category"],
                subcategory = asset["subcategory"],
                surfaceSize = asset["surfaceSize"],
                tags        = asset['tags'],
                type        = asset['type'],
                previewFile = asset["previewFile"][0],
                rootFolder  = asset["rootFolder"],
                lods        = [],
                SearchWords = u"{} {} {} {}".format(asset['name'],asset['AssetID'],asset['category'],asset['subcategory']) + u" ".join(asset['tags']),
                Format         = "Maya",
                SoftwareVersion = mayaVersion
                )
            # 保存json文件
            with open(os.path.join(rootpath,asset["JsonUri"]),"w+") as file:
                file.write(json.dumps(asset))
            r = Backend.Get().addAssetToDB(assetToLibraryData)
            print(assetToLibraryData)
            QMessageBox.information(self,u"提示",u"资产入库完成")
            self.close()

def showUI():
    if not Backend.Get().isBackendAvailable():
        QMessageBox.warning(None,"错误","当前后台服务器不可用,无法添加资产到库中")
        return
    global exportToLibraryUI
    exportToLibraryUI = ExportToLibraryUI()
    exportToLibraryUI.show(dockable=True)


if __name__ == "__main__":
    #from mayaTools import reloadModule
    #reloadModule()
    showUI()








            



        


