import os.path
import shutil
import json
import logging

from PySide6.QtWidgets import (QWidget,QDockWidget,QStackedWidget
                                ,QFrame,QSplitter,QListView
                                ,QBoxLayout,QMenu,QLabel
                               ,QHBoxLayout,QVBoxLayout,QPushButton
                               ,QLineEdit,QMessageBox,QComboBox
                               ,QGridLayout)
from PySide6.QtGui import  QAction,QContextMenuEvent,QIcon,QPixmap
from  PySide6.QtCore import  QModelIndex,Qt,QObject,QPoint,QFile,QIODeviceBase
from PySide6.QtUiTools import QUiLoader
import substance_painter.ui as ui
import substance_painter.resource as res
import substance_painter.application as app

import uis.sp_utilis as ut



def FindWidgetByName(parent:QWidget,name:str):
    for obj in parent.children():
        if obj.objectName() == name:
            return obj
    return  None






class WindowExportToLibrary(QWidget):
    customObjectname = "AssetLibraryWindow"
    def __init__(self, parent=None):
        super().__init__(parent)
        self.category = None
        self.resource = None
        self.resize(500,500)
        self.setWindowTitle("AssetLibrary")
        self.setObjectName(self.customObjectname)
        self.uiLoader = QUiLoader()
        self.tempImageURL = ""
        self.types = ["SmartMaterial","Texture"]
        self.__setup_ui()

    def __setup_ui(self):
        layoutMain = QHBoxLayout(self)
        self.setLayout(layoutMain)
        layoutMain.setContentsMargins(0,0,0,0)
        uiFilePath = os.path.join(os.path.dirname(__file__),"uifiles","AssetLibrary.ui")
        ui_file = QFile(uiFilePath)
        if not ui_file.open(QIODeviceBase.OpenModeFlag.ReadOnly):
            logging.error(f"无法读取UI文件:{ui_file.errorString()}")
            return
        self.ui = self.uiLoader.load(ui_file)
        ui_file.close()
        if not self.ui:
            logging.error("加载UI文件失败")
            return
        layoutMain.addWidget(self.ui)

        #获取可交互控件
        btn_setCurrentAsset = self.ui.findChild(QPushButton,"setCurrentAsset")
        btn_setCurrentAsset.clicked.connect(self.getCurrentAssetData)

        btn_Export = self.ui.findChild(QPushButton,"btn_export")
        btn_Export.clicked.connect(self.ExportToLibrary)

    def ExportToLibrary(self):
        #获取名称
        leName:QLineEdit = self.findChild(QLineEdit,"leAssetName")
        name = leName.text()
        #获取标签
        leTags:QLineEdit = self.findChild(QLineEdit,"lb_tags")
        tags = leTags.text().strip()
        tags.replace("，",",")
        tags = [tag.strip() for tag in tags.split(",") if tag]
        #获取资产类型
        lbType:QLabel = self.findChild(QLabel,"lb_type")
        assetType = lbType.text()
        #获取资产主分类
        cbCategory:QComboBox = self.findChild(QComboBox,"cb_categoryMain")
        category = cbCategory.currentText()
        #获取副分类
        cbSubCategory:QComboBox = self.findChild(QComboBox,"cb_subCategory")
        subCategory = cbSubCategory.currentText()
        #获取资产ID
        assetId = ut.Backend.get().GetAssetID()
        if not assetId:
            QMessageBox.about(self,"错误","获取资产ID失败,检查设置")
            return False
        #获取软件版本
        version = app.version()
        #获取根目录
        rootPath = ut.Backend.get().GetRootPath()
        if not rootPath:
            QMessageBox.about(self,"错误","获取资产根目录失败,检查设置")
            return False
        rootPath = "{}/{}".format(rootPath,assetId)

        #拼接新文件名
        newFilePath = os.path.join(rootPath,f"{assetId}{self.resource.getExtension()}")
        #拼接预览图新路径
        newPreviewPath = os.path.join(rootPath, "{}_preview_1.{}".format(assetId, self.resource.GetPreviewImageExtension()))

        assetCount = ut.Backend.get().GetAssetCount()


        asset = dict(
            name=name,
            ZbrushFile="",
            AssetID=assetId,
            rootFolder=assetId,
            JsonUri="{}.json".format(assetId),

            tags=tags,
            previewFile=[os.path.basename(newPreviewPath)],
            Lods=[],
            assetMaterials=[],
            MeshVars=[],

            type=assetType,
            category=category,
            subcategory=subCategory,
            surfaceSize="1 Meter",
            assetFormat="SubstancePainter",

            OriginMesh=dict(
                uri=os.path.basename(newFilePath),
                name=os.path.basename(newFilePath),
                extension=self.resource.getExtension()
            ),

            TilesV="false",
            TilesH="false",

            AssetIndex=assetCount,
            OldJson="",
        )

        # 提取放在数据库中的数据
        assetToLibraryData = dict(
            name=asset["name"],
            AssetID=asset["AssetID"],
            jsonUri=asset["JsonUri"],
            TilesH=asset["TilesH"],
            Tilesv=asset["TilesV"],
            asset=asset["assetFormat"],
            category=asset["category"],
            subcategory=asset["subcategory"],
            surfaceSize=asset["surfaceSize"],
            tags=asset['tags'],
            type=asset['type'],
            previewFile=asset["previewFile"][0],
            rootFolder=asset["rootFolder"],
            lods=[],
            SearchWords=u"{} {} {} {}".format(asset['name'], asset['AssetID'], asset['category'],
                                              asset['subcategory']) + u" ".join(asset['tags']),
            Format="SubstancePainter",
            SoftwareVersion=version
        )
        #统一执行创建文件复制文件的操作
        if not os.path.exists(rootPath):
            os.makedirs(rootPath)#创建文件夹

        #复制对应文件
        shutil.copy(self.resource.url, newFilePath)
        shutil.copy(self.tempImageURL, newPreviewPath)

        #保存json文件
        with open(os.path.join(rootPath, asset["JsonUri"]), "w+") as file:
            file.write(json.dumps(asset))

        r = ut.Backend.get().AddAssetToDB(assetToLibraryData)
        print(assetToLibraryData)
        QMessageBox.information(self,"提示",f"资产{name}入库完成")
        self.parent().close()
        return True
    def getCurrentAssetData(self):
        self.resource:ut.SPResource = ut.GetSelectedResource()
        if not self.resource:
            return

        typeStr = None
        if self.resource.GetType() == res.Type.SMART_MATERIAL:
            typeStr = "SmartMaterial"
        elif self.resource.GetType() == res.Type.IMAGE:
            typeStr = "Texture"
        else:
            QMessageBox.about(self,"提示","目前资产库只支持贴图和智能材质球入库")
            return

        le_name:QLineEdit = self.findChild(QLineEdit,"leAssetName")
        le_name.setText(self.resource.name)

        self.tempImageURL = self.resource.SavePreviewImage("D://","sp_temp")
        if not self.tempImageURL:
            return

        lbType:QLabel = self.findChild(QLabel,"lb_type")
        lbType.setText(typeStr)



        lbImage:QLabel = self.findChild(QLabel,"lb_image")
        lbImage.setPixmap(QPixmap(self.tempImageURL))

    def showEvent(self, event):
        self.category:dict = ut.Backend.get().GetCategory()
        cbCategory:QComboBox = self.findChild(QComboBox,"cb_categoryMain")


        cbCategory.clear()
        cbCategory.currentTextChanged.connect(self.CategoryChangeEvent)
        cbCategory.addItems(list(self.category.keys()))
        cbCategory.setCurrentIndex(0)


        return super().showEvent(event)
    def CategoryChangeEvent(self,newText:str):
        cbSubCategory:QComboBox = self.findChild(QComboBox,"cb_subCategory")
        cbSubCategory.clear()
        if newText in self.category.keys():
            cbSubCategory.addItems(list(self.category[newText].keys()))


def show():
    mainWindow = ui.get_main_window()
    window = FindWidgetByName(mainWindow,WindowExportToLibrary.customObjectname)
    if window:
        window.close()
        window.deleteLater()
    window = WindowExportToLibrary(mainWindow)
    ui.add_dock_widget(window)
    # window.parent().show()

