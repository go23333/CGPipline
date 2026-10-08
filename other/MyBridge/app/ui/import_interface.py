# coding: utf-8
from qfluentwidgets import (PushButton,SmoothScrollArea,
                            TitleLabel,CheckBox,LineEdit,
                            LineEditButton,FlowLayout,
                            ToolButton,IndeterminateProgressRing)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import (QWidget,QHBoxLayout,QVBoxLayout,QLabel,
                             QFileDialog,QToolButton)
from PyQt5.QtCore import QSize,pyqtSignal,QModelIndex
from PyQt5.QtCore import Qt,QPoint
import copy
import os
import json


from app.core.translator import Translator
from app.core.style_sheet import StyleSheet
from ..core.common_widgets import scaleMap
import app.core.common_widgets as common
from app.core.utility import category,GetCategorys,AssetType,ClassifyFilesFormFolder,Asset
from ..core import utility as utility
from ..core.backend import Backend
from app import ISPACKED
ROOT_PATH = "."

class SelectFileLineEdit(LineEdit):
    selectedFile = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.openBrowserButton = LineEditButton(FIF.FOLDER, self)
        self.openBrowserButton.setIconSize(QSize(self.openBrowserButton.width()-4,self.openBrowserButton.width()-4))
        self.hBoxLayout.addWidget(self.openBrowserButton, 0, Qt.AlignRight)
        self.setClearButtonEnabled(True)
        self.setTextMargins(0, 0, 59, 0)
        self.title = "select a file"
        self.filter = "All Files(*)"
        self.__initConnection()
    def __initConnection(self):
        self.openBrowserButton.clicked.connect(self.selectFile)
    def selectFile(self):
        global ROOT_PATH
        options = QFileDialog.Options()
        fileUrl,_ = QFileDialog.getOpenFileName(self,self.title,filter=self.filter,options=options,directory=ROOT_PATH)
        if fileUrl != "":
            self.setText(fileUrl)
            self.selectedFile.emit()
            ROOT_PATH = os.path.dirname(fileUrl)
            return True
        return False
    def setTitle(self,title:str):
        self.title = title
    def setFilter(self,filter:str):
        self.filter = filter

class DirectiorySelectGroup(QWidget):
    textChanged = pyqtSignal(str)
    def __init__(self, parent,text:str,textMaxWidth:int = 50,title:str="选择一个文件",filter:str = "All Files(*)",UDIM:bool=True):
        super().__init__(parent)
        self.texMaxWidth = textMaxWidth
        self.rootLayout = QHBoxLayout(self)
        self.label = QLabel(self,text=text)
        self.setObjectName(text)
        #self.checkbox = CheckBox(self)
        self.lineEdit = SelectFileLineEdit(self)
        self.lineEdit.textChanged.connect(self.checkUDIM)
        self.lineEdit.setTitle(title)
        self.lineEdit.setFilter(filter)
        self.udim = UDIM
        self.__initWidget()
        self.__initConnections()
        self.GroupLabel = text
    def __initWidget(self):
        self.rootLayout.setContentsMargins(0,0,0,0)
        #self.rootLayout.addWidget(self.checkbox)
        self.rootLayout.addWidget(self.label)
        self.rootLayout.addWidget(self.lineEdit)
        if self.udim:
            self.cb_UDIM = CheckBox(self)
            self.rootLayout.addWidget(QLabel(self,text="UDIM"))
            self.rootLayout.addWidget(self.cb_UDIM)
        self.label.setFixedWidth(self.texMaxWidth-15)
        #self.checkbox.setFixedWidth(15)
    def __initConnections(self):
        #self.lineEdit.selectedFile.connect(lambda: self.checkbox.setChecked(True))
        self.lineEdit.textChanged.connect(lambda: self.textChanged.emit(self.lineEdit.text()))
        #self.checkbox.stateChanged.connect(self.selectFile)
        pass
    def setText(self,text:str):
        self.lineEdit.setText(text)
    def checkUDIM(self):
        if not self.udim:
            return
        uri = self.lineEdit.text()
        udim = utility.checkTextureUDIM(uri)
        if udim:
            self.cb_UDIM.setChecked(True)
            uri = uri.replace(udim,f"udim")
            self.lineEdit.setText(uri)
    def text(self):
        return self.lineEdit.text()


class FrameLessFloatingWindow(QWidget):
    def __init__(self, title:str="None" ,parentScaleFactor:str=0.9, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.parentScaleFactor = parentScaleFactor
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowTitleHint|Qt.FramelessWindowHint)
    def showEvent(self, a0):
        self.moveEvent(None)
        self.resizeEvent(None)
        #self.parent().setDisabled(True)
        return super().showEvent(a0)
    def moveEvent(self, a0):
        p:QWidget = self.parent()
        self.move(p.pos()+QPoint(int(p.width()/2),int(p.height()/2))-QPoint(int(self.width()/2),int(self.height()/2)))
    def resizeEvent(self, a0):
        p:QWidget = self.parent()
        self.resize(int(p.width()*self.parentScaleFactor),int(p.height()*self.parentScaleFactor))
    def closeEvent(self, a0):
        p:QWidget = self.parent()
        #p.setDisabled(False)
        return super().closeEvent(a0)


class TextureGroups(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.maxTextWidth = 150
        self.texFilter = "图像(*.jpg *.png *.exr)"
        self.lods:list[DirectiorySelectGroup] = []
        self.__initUI()
    def __initUI(self):
        layout_main = QVBoxLayout(self)
        self.setLayout(layout_main)
        layout_main.setContentsMargins(0,0,0,0)
        layout_main.setSpacing(5)

        self.group_texAlbedo = DirectiorySelectGroup(self,"Albedo",self.maxTextWidth,filter=self.texFilter)
        self.group_texbrush = DirectiorySelectGroup(self,"Brush",self.maxTextWidth,filter=self.texFilter)
        self.group_texAO = DirectiorySelectGroup(self,"AO",self.maxTextWidth,filter=self.texFilter)
        self.group_texBump = DirectiorySelectGroup(self,"Bump",self.maxTextWidth,filter=self.texFilter)
        self.group_texCavity= DirectiorySelectGroup(self,"Cavity",self.maxTextWidth,filter=self.texFilter)
        self.group_texDiffuse = DirectiorySelectGroup(self,"Diffuse",self.maxTextWidth,filter=self.texFilter)
        self.group_texDisplacement = DirectiorySelectGroup(self,"Displacement",self.maxTextWidth,filter=self.texFilter)
        self.group_texFuzz = DirectiorySelectGroup(self,"Fuzz",self.maxTextWidth,filter=self.texFilter)
        self.group_texGloss = DirectiorySelectGroup(self,"Gloss",self.maxTextWidth,filter=self.texFilter)
        self.group_texMask = DirectiorySelectGroup(self,"Mask",self.maxTextWidth,filter=self.texFilter)
        self.group_texMetalness = DirectiorySelectGroup(self,"Metalness",self.maxTextWidth,filter=self.texFilter)
        self.group_texNormal = DirectiorySelectGroup(self,"Normal",self.maxTextWidth,filter=self.texFilter)
        self.group_texOpacity = DirectiorySelectGroup(self,"Opacity",self.maxTextWidth,filter=self.texFilter)
        self.group_texRoughness = DirectiorySelectGroup(self,"Roughness",self.maxTextWidth,filter=self.texFilter)
        self.group_texSpecular = DirectiorySelectGroup(self,"Specular",self.maxTextWidth,filter=self.texFilter)
        self.group_texTranslucency = DirectiorySelectGroup(self,"Translucency",self.maxTextWidth,filter=self.texFilter)
        self.textureGroups = [
                        self.group_texAlbedo,
                        self.group_texbrush,
                        self.group_texAO,
                        self.group_texBump,
                        self.group_texCavity,
                        self.group_texDiffuse,
                        self.group_texDisplacement ,
                        self.group_texFuzz,
                        self.group_texGloss,
                        self.group_texMask,
                        self.group_texMetalness,
                        self.group_texNormal ,
                        self.group_texOpacity ,
                        self.group_texRoughness,
                        self.group_texSpecular ,
                        self.group_texTranslucency ]
        for i in self.textureGroups:
            layout_main.addWidget(i)


class TextureCollapsibleBox(QWidget):
    deleteClicked = pyqtSignal(int)
    def __init__(self,title="", text="",index:int=0,parent = None):
        super().__init__(parent)
        self.title = title
        self.initText = text
        self.index = index

        self.__initUI()
    def __initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0,0,0,0)

        widget_buttons = QWidget(self)
        layout_buttons = QHBoxLayout(widget_buttons)
        layout_buttons.setContentsMargins(0,0,0,0)


        #创建折叠按钮
        self.toggle_button = QToolButton(text=self.title,checkable=True,checked=False)
        self.toggle_button.setStyleSheet("QToolButton{ border:none;}")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.clicked.connect(self.toggle)
        layout_buttons.addWidget(self.toggle_button)

        self.lineEdit = LineEdit()
        self.lineEdit.setText(self.initText)
        layout_buttons.addWidget(self.lineEdit)

        pb_delete = ToolButton(FIF.DELETE,parent=self)
        pb_delete.clicked.connect(self.deleteMaterial)


        layout_buttons.addWidget(pb_delete)

        #创建可折叠区域
        self.content_area = QWidget()
        self.content_area.setLayout(QVBoxLayout())
        self.content_area.setVisible(False)
        self.content_area.layout().setContentsMargins(0,20,0,220)
        self.content_area.layout().setSpacing(0)

        self.textureGroups = TextureGroups(self)

        self.content_area.layout().addWidget(self.textureGroups)

        mainLayout.addWidget(widget_buttons)
        mainLayout.addWidget(self.content_area)

    def toggle(self):
        if self.toggle_button.isChecked():
            self.content_area.setVisible(True)
            self.toggle_button.setArrowType(Qt.DownArrow)
        else:
            self.content_area.setVisible(False)
            self.toggle_button.setArrowType(Qt.RightArrow)
        pass
    def deleteMaterial(self):
        self.deleteClicked.emit(self.index)
    def text(self):
        return self.lineEdit.text()


class TagButton(PushButton):
    index = 0
    deletClicked = pyqtSignal(int)
    def __init__(self,text,icon,parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setIcon(icon)
        self.clicked.connect(lambda:self.deletClicked.emit(self.index))
        
class AssetsImportData(QWidget,Translator):
    assetNameChanged = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.infoTextWidth = 100
        self.maxTextWidth = 200
  

        #some indices  
        self.materialIndices = 0
        self.tagIndices = 0
        self.lodsIndics = 0
        self.MeshVarIndics = 0


        self.__initUI()
        self.__loadCombox()
    def __initUI(self):
        layoutMain = QVBoxLayout(self)
        layoutMain.setContentsMargins(0,10,0,10)
        self.setLayout(layoutMain)
        scrollWidget = QWidget(self)
        scrollWidget.setObjectName("scrollWidget")
        self.scrollWidgetLayout = QVBoxLayout(scrollWidget)
        self.scrollWidgetLayout.setContentsMargins(20,20,20,20)
        self.scrollWidgetLayout.setSpacing(20)
        self.scrollWidgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        
        scrollArea = SmoothScrollArea(self)
        scrollArea.setWidget(scrollWidget)
        scrollArea.setWidgetResizable(True)
        scrollArea.setContentsMargins(0,0,0,0)
        scrollArea.setObjectName("scrollArea")
        layoutMain.addWidget(scrollArea)




        assetWidget = QWidget(scrollWidget)
        assetLayout = QHBoxLayout(assetWidget)
        assetLayout.setContentsMargins(0,0,0,0)
        assetLayout.setSpacing(20)
        self.scrollWidgetLayout.addWidget(assetWidget)

        previewImageWidget = QWidget(assetWidget)
        previewImageLayout = QVBoxLayout(previewImageWidget)
        previewImageLayout.setContentsMargins(0,0,0,0)
        assetLayout.addWidget(previewImageWidget)

        assetLayout.addWidget(common.QLine.VLine(self))

        self.previewImage = QLabel(previewImageWidget)
        self.previewImage.setFixedSize(256,256)
           

        previewImageLayout.addWidget(self.previewImage)


        assetInfoWidget = QWidget(assetWidget)
        assetInfoLayout = QVBoxLayout(assetInfoWidget)
        assetInfoLayout.setContentsMargins(0,0,0,0)
        assetLayout.addWidget(assetInfoWidget)

        self.leg_name = common.LineEidtGroup(self,"名称",self.infoTextWidth)
        self.leg_name.lineEdit.__textChanged.connect(self.assetNameChange)
        assetInfoLayout.addWidget(self.leg_name)




        tags_widegt = QWidget(self)
        tags_widegt.setMinimumHeight(50)
        assetInfoLayout.addWidget(tags_widegt)

        self.layout_tags = FlowLayout(tags_widegt,False)

        self.layout_tags .setContentsMargins(10,10,10,10)
        self.layout_tags .setVerticalSpacing(20)
        self.layout_tags .setHorizontalSpacing(10)
        leg_tags = common.LineEidtGroup(self,"标签",self.infoTextWidth)
        leg_tags.returnPressed.connect(self.addTag)
    
        assetInfoLayout.addWidget(leg_tags)

        self.combox_type = common.ComboxGroup(self,"类型",self.infoTextWidth)
        assetInfoLayout.addWidget(self.combox_type)


        
        widgetCategorys = QWidget(self)
        assetInfoLayout.addWidget(widgetCategorys)
        widgetCategorysLayout = QHBoxLayout(widgetCategorys)
        widgetCategorysLayout.setContentsMargins(0,0,0,0)

        self.combox_category = common.ComboxGroup(widgetCategorys,"分类",self.infoTextWidth)
        self.combox_category.currentTextChanged.connect(self.__setSubCategory)
        widgetCategorysLayout.addWidget(self.combox_category)
        self.combox_subcategory = common.ComboxGroup(widgetCategorys,"子分类",self.infoTextWidth)
        widgetCategorysLayout.addWidget(self.combox_subcategory)

        # self.combox_SurfaceSize = common.ComboxGroup(assetInfoWidget,"表面面积",self.infoTextWidth)
        #assetInfoLayout.addWidget(self.combox_SurfaceSize)



        # widgetTile = QWidget(self)
        #assetInfoLayout.addWidget(widgetTile)
        # widgetTileLayout = QHBoxLayout(widgetTile)
        # widgetTileLayout.setContentsMargins(0,0,0,0)



        # self.checkbox_TilesVertically = CheckBox("垂直平铺",widgetTile)
        # self.checkbox_TilesVertically.setChecked(True)
        # self.checkobx_TillesHorizontically = CheckBox("水平平铺",widgetTile)
        # self.checkobx_TillesHorizontically.setChecked(True)


        # widgetTileLayout.addWidget(self.checkbox_TilesVertically)
        # widgetTileLayout.addWidget(self.checkobx_TillesHorizontically)

        self.group_previewImage = DirectiorySelectGroup(self,"预览图片",self.infoTextWidth,filter="all files(*)",UDIM=False)
        self.group_previewImage.textChanged.connect(self.setPreviewImage)
        assetInfoLayout.addWidget(self.group_previewImage)



        self.scrollWidgetLayout.addWidget(common.QLine.HLine(self))


        widget_add_material = QWidget(self)
        layout_add_material = QHBoxLayout(widget_add_material)
        layout_add_material.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_add_material.setContentsMargins(0,0,0,0)
        

        pb_add_material = PushButton(icon=FIF.ADD,text="添加材质",parent = self)
        pb_add_material.clicked.connect(lambda:self.addMaterial())
        layout_add_material.addWidget(pb_add_material)

        self.scrollWidgetLayout.addWidget(widget_add_material)



        widget_materials = QWidget(self)
        self.layout_materials = QVBoxLayout(widget_materials)
        self.layout_materials.setContentsMargins(0,0,0,0)
        self.layout_materials.setSpacing(10)

        self.scrollWidgetLayout.addWidget(widget_materials)


        self.scrollWidgetLayout.addWidget(common.QLine.HLine(self))


        self.OriginMesh =  DirectiorySelectGroup(self,"网格",self.maxTextWidth,title="选择一个模型",filter="fbx file(*.fbx)",UDIM=False)
        self.zbrushFile =  DirectiorySelectGroup(self,"ZBrush",self.maxTextWidth,title="选择一个ZBrush文件",filter="zbrush tool file(*.ZTL)",UDIM=False)
        
        
        self.scrollWidgetLayout.addWidget(self.OriginMesh)  
        self.scrollWidgetLayout.addWidget(self.zbrushFile)

        widget_add_lod_button = QWidget(self)
        layout_add_lod_button = QHBoxLayout(widget_add_lod_button)
        layout_add_lod_button.setContentsMargins(0,0,0,0)
        layout_add_lod_button.setAlignment(Qt.AlignmentFlag.AlignRight)


        pb_add_lod = PushButton(icon=FIF.ADD,text="添加LOD",parent=self)
        pb_add_lod.clicked.connect(lambda x:self.addLod())

        layout_add_lod_button.addWidget(pb_add_lod)

        self.scrollWidgetLayout.addWidget(widget_add_lod_button)


        self.widget_lods = QWidget(self)
        self.layout_lods = QVBoxLayout(self.widget_lods)
        self.layout_lods.setContentsMargins(0,0,0,0)

        self.scrollWidgetLayout.addWidget(self.widget_lods)

    def __loadCombox(self):
        self.combox_type.addItems([self.tra(item.value) for item in list(AssetType.__members__.values())])
        self.combox_category.addItems(GetCategorys(0))
    def __setSubCategory(self,c:str):
        self.combox_subcategory.clear()
        self.combox_subcategory.addItems(category[c])
    def addLod(self,lodPath:str="",normalPath:str = "")->DirectiorySelectGroup:
        lod_group = DirectiorySelectGroup(self.widget_lods,f"LOD {self.lodsIndics}",self.maxTextWidth,title="选择一个模型",filter="fbx file(*.fbx)",UDIM=False)
        texture_group = DirectiorySelectGroup(self.widget_lods,f"LOD {self.lodsIndics} Normal",self.maxTextWidth,title="选择一张法线贴图",filter="图像(*.jpg *.png *.exr)",UDIM=False)
        lod_group.setText(lodPath)
        texture_group.setText(normalPath)
        self.layout_lods.addWidget(lod_group)
        self.layout_lods.addWidget(texture_group)
        self.layout_lods.setSpacing(10)
        self.lodsIndics += 1
    def addTag(self,text:str):
        button = TagButton(text=text,icon=FIF.DELETE,parent=self)
        button.deletClicked.connect(self.deleteTag)
        button.index = self.tagIndices
        button.setObjectName(f"TagButton_{self.tagIndices}")
        self.layout_tags.addWidget(button)
        self.tagIndices += 1
    def deleteTag(self,index:int):
        name = f"TagButton_{index}"
        object = self.findChild(TagButton,name)
        self.layout_tags.removeWidget(object)
        object.close()
        object.deleteLater()
        object = None
    def addMaterial(self,materialName=""):
        material_area = TextureCollapsibleBox(title="材质名称:",text=materialName,index=self.materialIndices,parent=self)
        material_area.setObjectName(f"TextureCollapsibleBox_{material_area.index}")
        self.materialIndices += 1
        material_area.deleteClicked.connect(self.deleteMaterial)
        self.layout_materials.addWidget(material_area)
        return material_area
    def deleteMaterial(self,index:int):
        name = f"TextureCollapsibleBox_{index}"
        object = self.findChild(TextureCollapsibleBox,name)
        self.layout_materials.removeWidget(object)
        object.close()
        object.deleteLater()
        object = None
    def setPreviewImage(self,path:str):
        self.previewImage.setPixmap(scaleMap(self.previewImage.width(),self.previewImage.height(),path))     
    def loadDataFromAsset(self,asset:Asset):
        #将资产路径转换为绝对路径
        asset = utility.ConvertAssetPathsToAbs(asset,Backend.Get().getAssetRootPath())
        self.leg_name.setText(asset.name)
        for tag in asset.tags:
            self.addTag(tag)

        self.combox_type.setCurrentIndex(AssetType._member_names_.index(asset.type.name))

        self.combox_category.setCurrentText(asset.category)
        self.combox_subcategory.setCurrentText(asset.subcategory)

        self.group_previewImage.setText(asset.previewFile[0])
        self.setPreviewImage(asset.previewFile[0])

        for material in asset.assetMaterials:
            material_area = self.addMaterial(material.name)
            for map in material.maps:
                if map.type == utility.AssetMapType.Albedo:
                    material_area.textureGroups.group_texAlbedo.setText(map.uri)
                elif map.type == utility.AssetMapType.Brush:
                    material_area.textureGroups.group_texbrush.setText(map.uri)
                elif map.type == utility.AssetMapType.AO:
                    material_area.textureGroups.group_texAO.setText(map.uri)
                elif map.type == utility.AssetMapType.Bump:
                    material_area.textureGroups.group_texBump.setText(map.uri)
                elif map.type == utility.AssetMapType.Cavity:
                    material_area.textureGroups.group_texCavity.setText(map.uri)
                elif map.type == utility.AssetMapType.Diffuse:
                    material_area.textureGroups.group_texDiffuse.setText(map.uri)
                elif map.type == utility.AssetMapType.Displacement:
                    material_area.textureGroups.group_texDisplacement.setText(map.uri)
                elif map.type == utility.AssetMapType.Fuzz:
                    material_area.textureGroups.group_texFuzz.setText(map.uri)
                elif map.type == utility.AssetMapType.Gloss:
                    material_area.textureGroups.group_texGloss.setText(map.uri)
                elif map.type == utility.AssetMapType.Mask:
                    material_area.textureGroups.group_texMask.setText(map.uri)
                elif map.type == utility.AssetMapType.Metalness:
                    material_area.textureGroups.group_texMetalness.setText(map.uri)
                elif map.type == utility.AssetMapType.Normal:
                    material_area.textureGroups.group_texNormal.setText(map.uri)
                elif map.type == utility.AssetMapType.Opacity:
                    material_area.textureGroups.group_texOpacity.setText(map.uri)
                elif map.type == utility.AssetMapType.Roughness:
                    material_area.textureGroups.group_texRoughness.setText(map.uri)
                elif map.type == utility.AssetMapType.Specular:
                    material_area.textureGroups.group_texSpecular.setText(map.uri)
                elif map.type == utility.AssetMapType.Translucency:
                    material_area.textureGroups.group_texTranslucency.setText(map.uri)
        
        self.OriginMesh.setText(asset.OriginMesh.uri)
        self.zbrushFile.setText(asset.ZbrushFile)

        for lod in asset.Lods:
            self.addLod(lodPath=lod.mesh.uri,normalPath=lod.normalMap.uri)
    def loadDataFromFolder(self,files:dict):
        #获取资产名称
        self.leg_name.setText(files["assetName"])

        #处理图片
        hasOpacity = False
        lod_normals = []
        materialGroup = self.addMaterial(f"{files['assetName']}_mat")
        for image in files["images"]:
            #使用文件名识别防止目录中出现和关键词相同的情况
            fileName = os.path.basename(image)
            if "lod" in fileName.lower():
                lod_normals.append(image)
                continue
            for group in materialGroup.textureGroups.textureGroups:
                if group.GroupLabel.lower() in fileName.lower():
                    group.lineEdit.setText(image)
                    if group.GroupLabel == "opacity":
                        hasOpacity = True
                        continue
            name,ext = os.path.splitext(image)
            if name == files["assetName"] or ext == ".jpg":
                self.group_previewImage.setText(image)
                continue
        
        if files["models"] == []:
            if hasOpacity:
                self.combox_type.setCurrentIndex(AssetType._member_names_.index(AssetType.Decal.value))
            else:
                self.combox_type.setCurrentIndex(AssetType._member_names_.index(AssetType.Surface.value))
        lodIndexs = {}
        for meshUri in files["models"]:
            if ".fbx" in meshUri.lower() and "lod" not in meshUri.lower():
                self.OriginMesh.setText(meshUri)
            elif "lod" in meshUri.lower():
                t = meshUri.lower().find("lod") + 3
                level = meshUri[t:t+1]
                lodIndexs[level] = meshUri
            elif ".ztl" in meshUri.lower():
                self.zbrushFile.setText(meshUri)

        for i in lodIndexs.keys():
            # 遍历获取到的法线贴图
            for normal in lod_normals:
                if f"lod{i}" in normal.lower():
                    self.addLod(lodPath=lodIndexs[str(i)], normalPath=normal)



    def assetNameChange(self):
        self.assetNameChanged.emit(self.leg_name.text())
    def getAssetForImport(self):
        asset = Asset()
        asset.name = self.leg_name.text()
        if asset.name == "":
            common.showDialog("错误","资产名称不能为空","错误")
            return
        tags = []
        for tagbutton in self.findChildren(TagButton):
            tag = tagbutton.text().strip()  
            if tag != "":
                tags.append(tag)
        asset.tags = tags
        asset.type = copy.deepcopy(utility.AssetType._member_map_[utility.AssetType._member_names_[self.combox_type.currentIndex()]])
        asset.category = self.combox_category.currentText()
        asset.subcategory = self.combox_subcategory.currentText()

        asset.previewFile = [self.group_previewImage.text()]
        if asset.previewFile[0] == "":
            common.showDialog("错误","预览图片不能为空","错误")
            return
        for materialGroup in self.findChildren(TextureCollapsibleBox):
            material = utility.Material()
            material.name = materialGroup.text()
            for group in materialGroup.textureGroups.textureGroups:
                udim = group.cb_UDIM.isChecked()
                mapUri = group.lineEdit.text()
                #跳过路径不合法的贴图
                if not utility.isMapUriValid(mapUri,udim):
                    continue
                map = utility.AssetMap()
                map.uri = mapUri
                map.name = os.path.basename(mapUri)
                map.extension = os.path.splitext(mapUri)[1]
                if udim:
                    map.subMapCount = len(utility.GetUDIMTextures(mapUri))
                    map.UDIM = True
                    map.size = utility.GetTextureSize(mapUri.replace("udim","1001"))
                else:
                    map.UDIM = False
                    map.subMapCount = 1
                    map.size = utility.GetTextureSize(mapUri)
                map.type = copy.deepcopy(utility.AssetMapType._value2member_map_[group.GroupLabel])
                material.maps.append(map)
            asset.assetMaterials.append(material)
        if asset.type == utility.AssetType.Assets3D or asset.type == utility.AssetType.Plant:
            asset.OriginMesh.uri = self.OriginMesh.text()
            if asset.OriginMesh.uri == "":
                common.showDialog("错误","网格不能为空")
                return
            asset.OriginMesh.name = os.path.basename(asset.OriginMesh.uri)
            asset.OriginMesh.extension = os.path.splitext(asset.OriginMesh.uri)[1]
            if self.zbrushFile.text() != "":
                asset.ZbrushFile = self.zbrushFile.text()
            lod_normal_groups = self.widget_lods.findChildren(DirectiorySelectGroup)
            lod_groups = []
            normal_groups = []
            for group in lod_normal_groups:
                if "normal" in group.objectName().lower():
                    normal_groups.append(group)
                else:
                    lod_groups.append(group)
            for i,lod_group in enumerate(lod_groups):
                lod = utility.LOD()
                lod.level = int(lod_group.objectName().split(" ")[-1])
                lod_group.objectName()
                lod.mesh.uri = lod_group.text()
                lod.mesh.name = os.path.basename(lod.mesh.uri)
                _,lod.mesh.extension = os.path.splitext(lod.mesh.name)
                lod.normalMap.uri = normal_groups[i].text()
                lod.normalMap.name = os.path.basename(lod.normalMap.uri)
                lod.normalMap.type = utility.AssetMapType.Normal
                _,lod.normalMap.extension = os.path.splitext(lod.normalMap.name)
                lod.normalMap.size = utility.GetTextureSize(lod.normalMap.uri)
                asset.Lods.append(copy.deepcopy(lod))
        elif asset.type == AssetType.Surface or asset.type == AssetType.Decal:
            pass
        else:
            pass
        asset.assetFormat = utility.AssetFormat.FBX
        return asset
    def getAssetForEdit(self):
        asset = Asset()
        asset.name = self.leg_name.text()
        if asset.name == "":
            common.showDialog("错误","资产名称不能为空","错误")
            return
        tags = []
        for tagbutton in self.findChildren(TagButton):
            tag = tagbutton.text().strip()  
            if tag != "":
                tags.append(tag)
        asset.tags = tags
        utility.AssetType._member_map_
        asset.type = copy.deepcopy(utility.AssetType._member_map_[utility.AssetType._member_names_[self.combox_type.currentIndex()]])
        asset.category = self.combox_category.currentText()
        asset.subcategory = self.combox_subcategory.currentText()
        return asset

class AssetsEditInterface(FrameLessFloatingWindow):
    def __init__(self,parent=None):
        super().__init__("资产编辑",0.9,parent)
        self.__initUI()
        self.__setQss()
        self.setObjectName("assets_import_interface")
    def loadDataFromModelindex(self,index:QModelIndex):
        self.index = index
        data = self.index.data(Qt.ItemDataRole.UserRole+1)
        jsonFilePath =  os.path.join(Backend.Get().getAssetRootPath(),data.rootFolder,data.jsonUri) 
        with open(jsonFilePath,mode='r',encoding='utf-8') as f:
            data = json.loads(f.read())
        self.currentOriginalAsset = Asset.from_dict(data)
        self.assetsImportData.loadDataFromAsset(copy.deepcopy(self.currentOriginalAsset))
    def __initUI(self):
        layoutMain = QVBoxLayout(self)
        layoutMain.setContentsMargins(10,10,10,10)
        self.setLayout(layoutMain)

        layoutMain.addWidget(TitleLabel("编辑资产",self))


        self.assetsImportData = AssetsImportData(parent=self)

        layoutMain.addWidget(self.assetsImportData)

       
        widgetButtons = QWidget(self)
        layoutMain.addWidget(widgetButtons,alignment=Qt.AlignmentFlag.AlignBottom)
        layoutButtons = QHBoxLayout(widgetButtons)
        layoutButtons.setAlignment(Qt.AlignmentFlag.AlignRight)
        pb_save = PushButton(FIF.SAVE,"保存",widgetButtons)
        pb_save.clicked.connect(self.save_asset)
        layoutButtons.addWidget(pb_save)

        pb_close = PushButton(FIF.SAVE,"关闭",widgetButtons)
        pb_close.clicked.connect(self.close)
        layoutButtons.addWidget(pb_close)
    
    def save_asset(self):
        asset = self.assetsImportData.getAssetForEdit()
        if not asset:
            return
        self.currentOriginalAsset.name = asset.name
        self.currentOriginalAsset.tags = asset.tags
        self.currentOriginalAsset.type = asset.type
        self.currentOriginalAsset.category = asset.category
        self.currentOriginalAsset.subcategory = asset.subcategory
        utility.update_asset(self.currentOriginalAsset,Backend.Get().getAssetRootPath())
        
        data = self.index.data(Qt.ItemDataRole.UserRole+1)
        data.name = asset.name
        data.tags = asset.tags
        data.type = asset.type.value
        data.category = asset.category
        data.subcategory = asset.subcategory
        data.SearchWords = f"{data.name} {data.AssetID} {data.category} {data.subcategory}"+" ".join(data.tags)
        self.index.model().setData(self.index,data,Qt.ItemDataRole.UserRole+1)
        self.close()
        self.deleteLater()

        
    def __setQss(self):
        StyleSheet.apply_other("assets_import_interface",self)


class AssetsImportInterface(QWidget):
    imported = pyqtSignal(dict)
    def __init__(self,parent=None):
        super().__init__(parent)

        self.tab_bar_button_indices = 0
        self.current_tab_index = -1

        self.__initUI()
        self.__setQss()
        self.setObjectName("assets_import_interface")
    def __initUI(self):
        layout_main = QHBoxLayout(self)
        layout_main.setContentsMargins(0,0,0,0)
        layout_main.setSpacing(0)


        widget_tab_bar = QWidget(self)
        widget_tab_bar.setObjectName("widget_tab_bar")
        widget_tab_bar.setFixedWidth(300)
        layout_main.addWidget(widget_tab_bar)
        layout_tab_bar = QVBoxLayout(widget_tab_bar)
        layout_tab_bar.setContentsMargins(0,0,0,0)
        layout_tab_bar.setAlignment(Qt.AlignmentFlag.AlignTop)




        widget_tab_bar_close = QWidget(widget_tab_bar)
        layout_tab_bar.addWidget(widget_tab_bar_close)
        layout_tab_bar_close = QHBoxLayout(widget_tab_bar_close)
        layout_tab_bar_close.setContentsMargins(10,10,10,10)
        layout_tab_bar_close.setAlignment(Qt.AlignmentFlag.AlignLeft)



        widget_tab_bar_header = QWidget(widget_tab_bar)
        layout_tab_bar.addWidget(widget_tab_bar_header)
        layout_tab_bar_header = QHBoxLayout(widget_tab_bar_header)
        layout_tab_bar_header.setContentsMargins(0,0,0,0)



        label_title = QLabel("资产导入",widget_tab_bar_header)
        label_title.setObjectName("label_title")
        layout_tab_bar_header.addWidget(label_title,alignment=Qt.AlignmentFlag.AlignLeft)
        layout_tab_bar_header.setContentsMargins(10,30,10,30)
        button_add_asset = ToolButton(FIF.ADD,widget_tab_bar_header)
        button_add_asset.clicked.connect(self.addTab)
        layout_tab_bar_header.addWidget(button_add_asset,alignment=Qt.AlignmentFlag.AlignRight)


        widget_tab_bar_buttons = QWidget(widget_tab_bar)
        layout_tab_bar.addWidget(widget_tab_bar_buttons)
        self.layout_tab_bar_buttons = QVBoxLayout(widget_tab_bar_buttons)
        self.layout_tab_bar_buttons.setSpacing(15)



        widget_tab_content = QWidget(self)
        layout_main.addWidget(widget_tab_content)
        layout_tab_content = QVBoxLayout(widget_tab_content)
        layout_tab_content.setContentsMargins(0,0,0,0)

        self.switchWidget = common.TabWidget(self)
        layout_tab_content.addWidget(self.switchWidget)



        widget_import_button = QWidget(self)
        widget_import_button.setObjectName("widget_import_button")
        layout_tab_content.addWidget(widget_import_button)
        layout_import_button = QHBoxLayout(widget_import_button)
        layout_import_button.setContentsMargins(20,5,20,20)
        layout_import_button.setAlignment(Qt.AlignmentFlag.AlignRight)
        pb_import = PushButton(FIF.DOWNLOAD,"导入",widget_import_button)
        pb_import.clicked.connect(self.importAssetToLibrary)
        layout_import_button.addWidget(pb_import)

        self.progressRing = IndeterminateProgressRing(self)
        self.progressRing.close()


    def addTab(self):
        # 通过对话框选取目录,如果路径为空,则跳过
        folder = QFileDialog.getExistingDirectory(self,"选择资产目录")
        if folder == "":
            return
        # 按照文件类型获取目录下的文件
        global ROOT_PATH
        ROOT_PATH = folder
        files = ClassifyFilesFormFolder(folder)

        tab_bar_button = common.TabBarButton(self,"资产导入",self.tab_bar_button_indices)
        tab_bar_button.setObjectName(f"tab_bar_button_{self.tab_bar_button_indices}")
        tab_bar_button.clicked.connect(self.switchTab)
        tab_bar_button.delete_clicked.connect(self.removeTab)
        asset_data_interface = AssetsImportData(self)
        asset_data_interface.setObjectName(f"asset_data_interface_{self.tab_bar_button_indices}")
        asset_data_interface.assetNameChanged.connect(tab_bar_button.setText)
        asset_data_interface.loadDataFromFolder(files)
        self.switchWidget.addTab(asset_data_interface,f"资产导入{self.tab_bar_button_indices}")
        self.layout_tab_bar_buttons.addWidget(tab_bar_button,alignment=Qt.AlignmentFlag.AlignLeft)
        self.switchTab(self.tab_bar_button_indices)

        self.tab_bar_button_indices += 1
    def removeTab(self,index:int):
        #如果当前选中的tab是将要删除的tab，则将当前选中的tab切换到下一个tab
        if index == self.current_tab_index:
            button = None
            #首先向下查找
            for i in range(index+1,self.tab_bar_button_indices):
                button = self.findChild(common.TabBarButton,f"tab_bar_button_{i}")
                if button:
                    self.switchTab(i)
                    break
            #如果向下查找没有找到，则向上查找
            if not button:
                for i in range(index-1,0,-1):
                    button = self.findChild(common.TabBarButton,f"tab_bar_button_{i}")
                    if button:
                        self.switchTab(i)
                        break

        button = self.findChild(common.TabBarButton,f"tab_bar_button_{index}")
        button.close()
        button.deleteLater()
        button = None

        widget =self.switchWidget.findChild(AssetsImportData,f"asset_data_interface_{index}")
        widget.close()
        widget.deleteLater()
        widget = None

    def switchTab(self,index:int):
        #如果当前选中的tab和要切换的tab相同，则不进行切换
        if index == self.current_tab_index:
            return
        #如果当前选中的tab不是-1，则将当前选中的tab的按钮设置为未选中
        if self.current_tab_index != -1:
            button = self.findChild(common.TabBarButton,f"tab_bar_button_{self.current_tab_index}")
            if button:
                button.setSelected(False,force=True)
        #将当前选中的tab的按钮设置为选中
        button = self.findChild(common.TabBarButton,f"tab_bar_button_{index}")
        button.setSelected(True,force=True)

        #切换到对应的tab
        widget =self.switchWidget.findChild(AssetsImportData,f"asset_data_interface_{index}")
        self.switchWidget.setCurrentWidget(widget)

        #更新当前选中的tab的索引
        self.current_tab_index = index
    def __setQss(self):
        StyleSheet.apply_other("assets_import_interface",self)
    def closeWindow(self):
        self.close()
        self.deleteLater()
    def importAssetToLibrary(self):
        widget =self.switchWidget.findChild(AssetsImportData,f"asset_data_interface_{self.current_tab_index}")
        if not widget:
            return
        asset = widget.getAssetForImport()
        if not asset:
            return
        if ISPACKED:
            worker = common.CommonWorker(self)
            worker.fun = lambda : self.importAssetToLibraryThread(asset)
            worker.overed.connect(self.import_over)
            worker.start()
            self.setDisabled(True)
            self.progressRing.move(int(self.width()/2),int(self.height()/2))
            self.progressRing.show()
        else:
            self.importAssetToLibraryThread(asset)
            self.import_over()
    def importAssetToLibraryThread(self,asset:Asset):
        asset = utility.CopyAndRenameAsset(asset,Backend.Get().getAssetRootPath())
        self.library_data = utility.AddAssetDataToDataBase(asset)
    def import_over(self):
        self.removeTab(self.current_tab_index)
        self.setDisabled(False)
        self.progressRing.close()
        self.imported.emit(self.library_data)






        






