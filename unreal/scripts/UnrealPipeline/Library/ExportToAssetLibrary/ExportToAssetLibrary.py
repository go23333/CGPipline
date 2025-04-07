#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2025.1
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################

import unreal


from Qt.QtWidgets import QMainWindow,QApplication,QWidget,QComboBox
from Qt import QtWidgets
from Qt.QtCore import Qt,Signal




import os
import json

from dayu_widgets import dayu_theme


from dayu_widgets.qt import application,MIcon
from dayu_widgets.label import MLabel
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.combo_box import MComboBox

import UnrealPipeline.core.CommonWidget as cw
from UnrealPipeline.core.Config import globalConfig
import UnrealPipeline.core.utilis as ut

from UnrealPipeline.core.layout.flow_layout import FlowLayout

from UnrealPipeline.core.backend import Backend
import UnrealPipeline.core.UnrealHelper as uh



class LabelLineEdit(QWidget):
    enterfun = None
    def __init__(self,label:str,parent = None):
        super().__init__(parent)
        self.__initUI()
        self.label.setText(label)
    def SetLabelFixedWidth(self,width:int):
        self.label.setFixedWidth(width)
    def SetLineEditText(self,text:str):
        self.lineEdit.setText(text)
    def __initUI(self):
        layout = QtWidgets.QHBoxLayout()
        self.label = MLabel("Label")
        self.lineEdit = MLineEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)
    def keyPressEvent(self, event):
        if self.lineEdit.text() != "" and (self.enterfun and event.key() == 16777220 or event.key() == 16777221):
            self.enterfun(self.lineEdit.text())
            self.lineEdit.clear()
        return super().keyPressEvent(event)
    def text(self):
        return self.lineEdit.text()
        
class ComboxLineEdit(QWidget):
    currentTextChanged = Signal(str)
    def __init__(self,label:str,parent = None):
        super().__init__(parent)
        self.__initUI()
        self.label.setText(label)
    def SetLabelFixedWidth(self,width:int):
        self.label.setFixedWidth(width)
    def addItems(self,items:list):
        self.combox.addItems(items)
    def __initUI(self):
        layout = QtWidgets.QHBoxLayout()
        self.label = MLabel("Label")
        self.combox = MComboBox()
        self.combox.currentTextChanged.connect(self.currentTextChange)
        layout.addWidget(self.label)
        layout.addWidget(self.combox)
        self.setLayout(layout)
    def currentTextChange(self,text:str):
        self.currentTextChanged.emit(text)
    def CurrentText(self):
        return self.combox.currentText()
    def clear(self):
        self.combox.clear()
    def setCurrentText(self,text:str):
        try:
            self.combox.setCurrentText(text)
        except:
            pass
class TagButton(MPushButton):
    deleteClicked = None
    def __init__(self, text="",parent=None):
        super().__init__(text, MIcon("trash_line.svg", "#ddd"), parent)
        self.__initConnection()
    def __initConnection(self):
        self.clicked.connect(self.DeleteClicked)
    def DeleteClicked(self):
        if self.deleteClicked != None:
            self.deleteClicked(self.objectName())



class TagArea(QWidget):
    tags = []
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__initUI()
    def __initUI(self):
        self.main_layout = FlowLayout(self)
    def addTag(self,text:str):
        button = TagButton(text=text,parent=self)
        button.setObjectName(text)
        self.tags.append(text)
        button.deleteClicked = self.deleteTag
        self.main_layout.addWidget(button)
    def deleteTag(self,objectName:str):
        button = self.findChild(TagButton,objectName)
        self.main_layout.removeWidget(button)
        self.tags.remove(objectName)
        button.close()
        
class ExportToAssetLibrary(cw.CommonMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(600,250)
        self.MoveToCenter()
        self.setWindowTitle("导出到资源库")
        self.thumbnail_path = os.path.join(globalConfig.get().tempFolder,"asset_thumbnail.png")
        self.asset_path = None
        self.__initUI()
        self.__initConnect()
        self.current_category_text = ""
    def __initUI(self):
        Widget_main = QWidget(self)
        Layout_main = QtWidgets.QVBoxLayout(Widget_main)
        Layout_main.setAlignment(Qt.AlignTop)
        self.setCentralWidget(Widget_main)


        Widget_asset = QWidget(Widget_main)
        laytout_asset = QtWidgets.QHBoxLayout(Widget_asset)


        self.assetImage = MLabel(parent=Widget_asset)
        self.assetImage.setFixedHeight(256)
        self.assetImage.setFixedWidth(256)



        Widget_info = QWidget(Widget_asset)
        layout_info = QtWidgets.QVBoxLayout(Widget_info)

        self.lbe_name = LabelLineEdit(label="资产名称:",parent=Widget_asset)
        self.lbe_name.SetLabelFixedWidth(80)

        self.tags_area = TagArea(parent=Widget_asset)
        self.tags_area.setFixedHeight(200)

        self.lbe_tags = LabelLineEdit(label="标签:    ",parent=Widget_asset)

        self.lbe_tags.SetLabelFixedWidth(80)


        self.cb_type = ComboxLineEdit(label="类型  ")
        self.cb_type.addItems(["3D Assets"])




        self.cb_category = ComboxLineEdit(label="主分类")
        self.cb_category.addItems(ut.GetCategorys(0))
        self.cb_category.currentTextChanged.connect(self.__setSubCategory)

        self.cb_subcategory = ComboxLineEdit(label="子分类")
        self.__setSubCategory(self.cb_category.CurrentText())


        layout_info.addWidget(self.lbe_name)   
        layout_info.addWidget(self.tags_area)   
        layout_info.addWidget(self.lbe_tags)
        layout_info.addWidget(self.cb_type)   
        layout_info.addWidget(self.cb_category)
        layout_info.addWidget(self.cb_subcategory)
        layout_info.setAlignment(Qt.AlignTop)
        layout_info.setContentsMargins(0,0,0,0)

        laytout_asset.addWidget(self.assetImage)
        laytout_asset.addWidget(Widget_info)



        widget_buttons = QWidget(Widget_main)
        layout_buttons = QtWidgets.QHBoxLayout(widget_buttons)



        self.pb_export = MPushButton("导出")
        self.pb_export.setFixedWidth(100)

        self.pb_refresh_thumbnail = MPushButton("刷新缩略图")
        self.pb_refresh_thumbnail.setFixedWidth(100)
        
        layout_buttons.addWidget(self.pb_refresh_thumbnail,alignment=Qt.AlignLeft)
        layout_buttons.addWidget(self.pb_export,alignment=Qt.AlignRight)



        Layout_main.addWidget(Widget_asset)
        Layout_main.addWidget(widget_buttons)
    def __initConnect(self):
        self.pb_refresh_thumbnail.clicked.connect(self.RefreshThumbnail)
        self.lbe_tags.enterfun = self.tags_area.addTag
        self.pb_export.clicked.connect(self.ExportToLibrary)
    def __setSubCategory(self,text:str):
        self.cb_subcategory.clear()
        self.cb_subcategory.addItems(ut.category[text])
    def ExportToLibrary(self):
        name = self.lbe_name.text()
        tags = [tag.rstrip() for tag in self.tags_area.tags]
        tags.append("虚幻引擎")
        previewImagePath = self.thumbnail_path
        category = self.cb_category.CurrentText()
        subcategory = self.cb_subcategory.CurrentText()
        AssetID = ut.generate_unique_string(7)
        if type(self.asset) == unreal.StaticMesh:
            tempPath = globalConfig.get().MyBridgeTargetPathBuildin + "/3D_Assets" + AssetID + "/"
            #复制网格体和依赖项到新目录
            self.asset = uh.MoveStaticMeshAndDependenceToFolder(self.asset,tempPath)
            #设置枢轴位置
            unreal.PythonExtensionBPLibrary.bake_mesh_pivot(self.asset,unreal.PivotPreset.BOUNDING_BOX_CENTER_BOTTOM)
            # 复制并保存预览图片
            rootpath = Backend.Get().getAssetRootPath() +f"/{AssetID}"
            _,ext = os.path.splitext(previewImagePath)

            system_path = uh.convert_unreal_path_to_system_path(tempPath)
            des_path = rootpath + f"/{AssetID}"
            # 复制资产到对应资产库目录
            ut.copy_folder(system_path,des_path)

            # 复制预览图到对应目录
            previewImagePath = ut.CopyFileToFolder(previewImagePath,rootpath,f"{AssetID}_preview_1{ext}",False)


            asset = dict(
                name           = name,
                ZbrushFile     = "",
                AssetID        = AssetID,
                rootFolder     = AssetID,
                JsonUri        = f"{AssetID}.json",

                tags           = tags,
                previewFile    = [previewImagePath],
                Lods           = [],
                assetMaterials = [],
                MeshVars       = [],

                type           = "3D Assets",
                category       = category,
                subcategory    = subcategory,
                surfaceSize    = "1 Meter",
                assetFormat    = "Unreal Engine",

                OriginMesh     = dict(
                    uri = "",
                    name = "",
                    extension = ""
                ),

                TilesV         = "false",
                TilesH         = "false",

                AssetIndex     = Backend.Get().getAssetsCount(),
                OldJson        = ""
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
                SearchWords = f"{asset['name']} {asset['AssetID']} {asset['category']} {asset['subcategory']}" + " ".join(asset['tags'])
                )
            # 保存json文件
            with open(os.path.join(rootpath,asset["JsonUri"]),"w+",encoding='utf-8') as file:
                file.write(json.dumps(asset))
        
            Backend.Get().addAssetToDB(assetToLibraryData)
            #清理文件
            unreal.EditorAssetLibrary.delete_directory(tempPath)
            self.close()
        else:
            pass
    def RefreshThumbnail(self):
        if self.asset_path:
            unreal.PythonExtensionBPLibrary.save_thumbnail_to_file(self.asset_path ,self.thumbnail_path)
            self.assetImage.setPixmap(cw.scaleMap(256,256,self.thumbnail_path))
    def LoadAssetData(self,asset:unreal.Object):
        self.asset_path = asset.get_path_name()
        self.asset = asset
        unreal.PythonExtensionBPLibrary.save_thumbnail_to_file(self.asset_path,self.thumbnail_path)
        self.lbe_name.SetLineEditText(asset.get_name())
        self.assetImage.setPixmap(cw.scaleMap(256,256,self.thumbnail_path))


def Start():
    with application() as app:
        global w
        w = ExportToAssetLibrary()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))
        w.LoadAssetData(unreal.EditorUtilityLibrary.get_selected_assets()[0])
        

if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()
