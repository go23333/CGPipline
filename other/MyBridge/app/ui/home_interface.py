from qfluentwidgets import (FlowLayout,PushButton,
                            SmoothScrollArea,SearchLineEdit,
                            ComboBox,Dialog,InfoBar,InfoBarPosition,
                            ToolButton
                            )
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import (QApplication,QWidget,
                             QFrame,QHBoxLayout,QVBoxLayout,QMenu,
                             QLabel,QSizePolicy,QStyledItemDelegate,
                             QStyleOptionViewItem,QStyle,QListView,
                             QAbstractItemView,QOpenGLWidget,QMessageBox)
from PyQt5.QtGui import (QPaintEvent,
                         QBrush,QPainter,QColor,
                         QResizeEvent,QPen,
                         QPainterPath)
from PyQt5.QtCore import (QRect,Qt,
                          pyqtSignal,QThread,QAbstractListModel,
                          QModelIndex,QSize,QRectF,QPoint,QPropertyAnimation,QEasingCurve)
import pyperclip

import os
import typing

import  math

from app.core.style_sheet import StyleSheet
from app.core.common_widgets import scalePixelMap,scaleMap,StringButton,LoadPixmapSafely
import app.core.utility as ut
from app.core.config import Config
from app.core.translator import Translator
from ..core.backend import Backend
from .import_interface import AssetsEditInterface
from ..core.utility import AssetFormatN
from ..core.Log import Log
from ..core.thread import ThreadPool
import app.resource.resource_rc




logger = Log.get().getLogger("HomePage")
logger.setLevel(Log.Level.debug)


class AssetItem():
    def __init__(self):
        self.name = None
        self.favorite = None
        self.type = None
        self.AssetID  = None
        self.jsonUri = None
        self.asset   = None
        self.category = None
        self.subcategory = None
        self.tags        = None
        self.type        =None
        self.previewFile =None
        self.rootFolder  =None
        self.lods        =None
        self.SearchWords = None
        self.image = None
        self.Format = None
        self.SoftwareVersion = None
    def load_image(self,width:int=512,height:int=512):
        worker = ThreadPool.get().get_one_thread()
        worker.fun = lambda:self.load_image_thread(width,height)
        worker.start()
    def load_image_thread(self,width,height):
        if os.path.exists((self.previewFile)):
            self.image = scaleMap(width,height,self.previewFile)
    @classmethod
    def load_from_dict(cls,data:dict,rootpath:str)->"AssetItem":
        item = cls()
        item.name        = data["name"]
        item.AssetID     = data["AssetID"]
        item.asset       = data["asset"]
        item.category    = data["category"]
        item.subcategory = data["subcategory"]
        item.tags        = data["tags"]
        item.type        = data["type"]
        item.previewFile = os.path.join(rootpath,data["rootFolder"],data["previewFile"])
        item.rootFolder  = os.path.join(rootpath,data["rootFolder"])
        item.lods        = data["lods"]
        item.SearchWords = data["SearchWords"]
        item.jsonUri     = os.path.join(rootpath,data["rootFolder"],data["jsonUri"])
        item.Format      = ut.AssetFormatN._member_map_[data["Format"]]
        item.SoftwareVersion = data["SoftwareVersion"]
        return item

class DynamicListModel(QAbstractListModel):
    class SortOrder(int):
        AscendingOrder = ... # type: Qt.SortOrder
        DescendingOrder = ... # type: Qt.SortOrder
    class DataType(int):
        name = ...
    item_update = pyqtSignal(QModelIndex)
    def __init__(self,parent):
        super().__init__(parent)
        self.__loaded_datas:list[AssetItem] = []
        self.__all_datas:list[AssetItem] = []
        self.is_loaded = False
        self.filtered_datas:list[AssetItem] = []
        self.current_loaded_count = 0
        self.per_times_loaded_count = 36
        self.load_from_server()
        self.items_filter()
    def load_from_server(self):
        if ut.checkisBackendRunning(self.parent()):
            remoteAssetLibrary = Backend.Get().getAssetRootPath()
            datas = Backend.Get().getAssetsList()
        else:
            datas = []
            remoteAssetLibrary = ""
        self.__all_datas = []
        for data in datas:
            self.__all_datas.append(AssetItem.load_from_dict(data,remoteAssetLibrary))
    def items_filter(self,type_index:int=0,formatIndex:int=0,category_index:int=0,subcategory_index:int=0,search_key_word:str=""):
        self.clear_datas()
        self.filtered_datas = []
        for data in self.__all_datas:
            if type_index >= 1:
                type = list(ut.AssetType.__members__.values())[type_index-1]
                if type.value != data.type:
                    continue
            if formatIndex >= 1:
                format = ut.AssetFormatN._value2member_map_[formatIndex]
                if data.Format != format:
                    continue
            if category_index >= 1:
                category = ut.GetCategorys(0)[category_index-1]
                if category != data.category:
                    continue
            if subcategory_index >=1:
                subcategory = ut.GetSubCategorys(category_index-1)[subcategory_index-1]
                if subcategory != data.subcategory:
                    continue
            if search_key_word != "" and search_key_word.lower() not in data.SearchWords.lower():
                continue
            self.filtered_datas.append(data)
        logger.info(f"资产过滤完成,符合条件的资产数量为:{len(self.filtered_datas)}")
        self.load_more_data()
    def clear_datas(self):
        self.beginResetModel()
        self.__loaded_datas = []
        self.endResetModel()
        self.current_loaded_count = 0
    def data(self, index, role = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.__loaded_datas[index.row()].name
        elif role == Qt.ItemDataRole.CheckStateRole:
            return self.__loaded_datas[index.row()].Format
        elif role == Qt.ItemDataRole.DecorationRole:
            return self.__loaded_datas[index.row()].image
        elif role == Qt.ItemDataRole.UserRole + 1:
            return  self.__loaded_datas[index.row()]
        return None
    def setData(self, index, value, role = ...):
        if role == Qt.ItemDataRole.UserRole + 1:
            self.__all_datas[index.row()] = value
            self.__loaded_datas[index.row()] = value
            self.dataChanged.emit(index,index,[role])
            self.item_update.emit(index)
    def rowCount(self, parent = QModelIndex()):
        return len(self.__loaded_datas)
    def removeRow(self, row, parent = ...):
        self.beginRemoveRows(parent,row,row+1)
        self.__all_datas.remove(self.__loaded_datas[row])
        self.__loaded_datas.remove(self.__loaded_datas[row])
        self.endRemoveRows()
    def append_row(self,item:dict):
        self.beginRemoveRows(QModelIndex(),len(self.__all_datas),len(self.__all_datas)+1)
        remoteAssetLibrary = Backend.Get().getAssetRootPath()
        item = AssetItem.load_from_dict(item,remoteAssetLibrary)
        self.__all_datas.append(item)
        self.endRemoveRows()
    def load_more_data(self):
        if self.is_loaded:
            return
        self.is_loaded = True
        worker = ThreadPool.get().get_one_thread()
        worker.fun = self.__load_more_data_thread
        worker.finished.connect(self.__on_data_loaded)
        worker.start()
    def parent(self)->"AssetCardView":
        return super().parent()
    def __load_more_data_thread(self):
        self.new_datas = []
        for i in range(self.current_loaded_count,self.current_loaded_count + self.per_times_loaded_count):
            if i >= len(self.filtered_datas):
                return
            itme = self.filtered_datas[i]
            itme.load_image(256,256)
            self.new_datas.append(itme)
            self.current_loaded_count += 1
    def __on_data_loaded(self):
        self.beginInsertRows(QModelIndex(),len(self.__loaded_datas),len(self.__loaded_datas) + len(self.new_datas)-1)
        self.__loaded_datas.extend(self.new_datas)
        self.endInsertRows()
        self.is_loaded = False





class AssetDelegate(QStyledItemDelegate):
    def __init__(self,parent,radius:float):
        super().__init__(parent)
        self.radius = radius
        self.border_width = 2
        self.text_offset = 4
        self.max_display_name_length = 10
        self.favorite_icon_offset = 4
        self.pen = QPen()
        self.pen.setWidth(self.border_width)
        self.format_icon_size = 30
        self.unrealIcon = scaleMap(self.format_icon_size,self.format_icon_size,r":/MyBridge/icons/Unreal_flag.png")
        self.fbxIcon = scaleMap(self.format_icon_size,self.format_icon_size,r":/MyBridge/icons/fbx_flag.png")
        self.mayaIcon = scaleMap(self.format_icon_size,self.format_icon_size,r":/MyBridge/icons/maya_flag.png")
        self.spIcon = scaleMap(self.format_icon_size,self.format_icon_size,r":/MyBridge/icons/SP_flag.png")

    def sizeHint(self, option, index):
        width = self.parent().gridSize().width()
        height = self.parent().gridSize().width()
        return QSize(width,height)

    def parent(self)->"AssetCardView":
        return super().parent()

    def paint(self, painter: typing.Optional[QPainter], option: QStyleOptionViewItem, index: QModelIndex):
        name = index.data(Qt.ItemDataRole.DisplayRole)
        image = index.data(Qt.ItemDataRole.DecorationRole)
        format = index.data(Qt.ItemDataRole.CheckStateRole)

        format_icon = self.fbxIcon
        if format == AssetFormatN.UnrealEngine:
            format_icon = self.unrealIcon
        elif format == AssetFormatN.Maya:
            format_icon = self.mayaIcon
        elif format == AssetFormatN.SubstancePainter:
            format_icon = self.spIcon

        width = self.parent().gridSize().width()
        height = self.parent().gridSize().width()
        spacing = self.parent().spacing()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing,True)

        rect = QRect(
            int(option.rect.center().x()-width/2+spacing/2),
            int(option.rect.center().y()-height/2+spacing/2),
            width-spacing,
            height-spacing
        )

        selected = option.state & QStyle.State_Selected
        hovered = option.state & QStyle.State_MouseOver

        #绘制边框
        border_color = None
        if selected:
            border_color = QColor(0, 174, 255)
        elif hovered:
            border_color = QColor(112, 112, 112)
        if border_color:
            self.pen.setColor(border_color)
            painter.setPen(self.pen)
            painter.drawRoundedRect(rect, self.radius, self.radius,Qt.SizeMode.RelativeSize)

        #绘制内容
        content_rect = rect.adjusted(
            self.border_width,
            self.border_width,
            -self.border_width,
            -self.border_width
        )
        #设置一个遮罩
        path = QPainterPath()
        path.addRoundedRect(QRectF(content_rect),self.radius,self.radius)
        painter.setClipPath(path)

        #绘制背景
        painter.fillRect(content_rect, QColor(0,0,0))
        #绘制图像
        if image:
            image_rect_src = QRect(0,0,image.width(),image.height())
            painter.drawPixmap(content_rect,image,image_rect_src)


        #复原笔刷效果
        painter.restore()
        #绘制文本
        name = name
        if len(name) > self.max_display_name_length:
            name = name[0:self.max_display_name_length] + "..."
        if hovered:
            self.pen.setColor(QColor(255,255,255))
            painter.drawText(content_rect.bottomLeft() + QPoint(self.text_offset,-self.text_offset),name)
            #绘制格式图标
            image_rect_src = QRect(0, 0, self.format_icon_size, self.format_icon_size)
            des_rec = content_rect.adjusted(
                content_rect.width()-self.format_icon_size-10,
                content_rect.height()-self.format_icon_size-10,
                -(content_rect.width()-self.format_icon_size),
                -(content_rect.height()-self.format_icon_size)
            )
            painter.drawPixmap(des_rec,format_icon,image_rect_src)

class AssetCardView(QListView):
    item_selected = pyqtSignal(QModelIndex)
    def __init__(self, parent = ...):
        super().__init__(parent)
        #初始化一些变量
        self.card_size = 200
        self.radius = 5
        self.__init_widget_properties()
        self.__init_widget_connections()
        self.enalbe_opengl()
        # 第一次加载数据
        self.model().load_more_data()
    def __init_widget_properties(self):
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setGridSize(QSize(self.card_size,self.card_size))
        self.setSpacing(5)                  # 设置项目间距
        self.setMovement(QListView.Static)   # 禁止拖动项目
        self.setResizeMode(QListView.ResizeMode.Fixed) # 自动调整布局
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setUniformItemSizes(True)#所有项目大小相同,提醒性能
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)#设置右键菜单策略
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setContentsMargins(0,0,0,0)

        #优化滚动效果
        self.animation = QPropertyAnimation(self.verticalScrollBar(), b"value")
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.animation.setDuration(300)  # 动画持续时间(毫秒)

        #初始化数据模型
        self.setModel(DynamicListModel(self))
        #初始化渲染效果
        self.setItemDelegate(AssetDelegate(self,self.radius))

    def enalbe_opengl(self):
        if QApplication.testAttribute(Qt.ApplicationAttribute.AA_UseOpenGLES):
            viewport = QOpenGLWidget()
            self.setViewport(viewport)

    def __init_widget_connections(self):
        self.verticalScrollBar().valueChanged.connect(self.vertical_scall_changed)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def model(self)->DynamicListModel:
        return super().model()

    def show_context_menu(self,pos):
        index = self.indexAt(pos)
        # 创建菜单
        menu = QMenu(self)
        if index.isValid():  # 如果点击在有效项目上
            # 添加项目相关操作
            action = menu.addAction("复制资产ID")
            action.triggered.connect(lambda :pyperclip.copy(index.data(Qt.ItemDataRole.UserRole+1).AssetID))
            action = menu.addAction("打开文件夹")
            action.triggered.connect(lambda:self.go_to_file(index))
            action = menu.addAction("删除资产")
            action.triggered.connect(lambda :self.delete_asset(index))
            action = menu.addAction("编辑资产")
            action.triggered.connect(lambda:self.edit_item(index))
        menu.exec_(self.viewport().mapToGlobal(pos))

    def go_to_file(self,index:QModelIndex):
        path = os.path.normpath(index.data(Qt.ItemDataRole.UserRole+1).rootFolder)
        if os.path.exists(path):
            os.startfile(path)
        else:
            QMessageBox.warning(self,"错误","该资产路径不存在,请检查或删除该资产")

    def delete_asset(self,index:QModelIndex):
        data:AssetItem = index.data(Qt.ItemDataRole.UserRole+1)
        w = Dialog("提示",f"是否删除资产{data.name}?")
        w.setTitleBarVisible(False)
        w.setContentCopyable(True)
        if w.exec() and Backend.Get().isBackendAvailable():
            ut.removeFolder(data.rootFolder)#删除资产目录
            Backend.Get().deleteAssetFromDB(data.AssetID)#从数据库中删除
            self.model().removeRow(index.row(),QModelIndex())#从当前显示的列表中删除

    def edit_item(self,index:QModelIndex):
        editInterface = AssetsEditInterface(self.parentWidget().parentWidget().parentWidget().parentWidget().parentWidget())
        editInterface.loadDataFromModelindex(index)
        editInterface.show()

    def vertical_scall_changed(self,value):
        max_vale = self.verticalScrollBar().maximum()
        rate = value/(max_vale+0.000001)
        if rate>0.99:
            self.model().load_more_data()
# ------------------  重写一些事件 ------------------
    def resizeEvent(self, e):
        itemsPerRow = 3
        width = self.width()-2
        if width <= self.card_size:
            width = 685
        if width < 412:
            itemsPerRow = 2
        elif width > 685 and width < 1200:
            itemsPerRow = 4
        elif width > 1200:
            itemsPerRow = 5
        cardSize = round(width/itemsPerRow - 2 * self.spacing() )
        self.setGridSize(QSize(cardSize,cardSize))
        return super().resizeEvent(e)

    def selectionChanged(self, selected, deselected):
        if selected.isEmpty():
            return
        self.selectedChang = True
        index = selected.indexes()[0]
        logger.info(f"设置当前选中的索引为{index.row()}")
        self.item_selected.emit(index)
        return super().selectionChanged(selected, deselected)

    def wheelEvent(self, event):
        # 停止当前动画
        self.animation.stop()

        # 计算目标位置
        current = self.verticalScrollBar().value()
        delta = event.angleDelta().y()
        target = current - delta * 4  # 减小滚动步长

        # 设置动画参数
        self.animation.setStartValue(current)
        self.animation.setEndValue(target)

        # 启动动画
        self.animation.start()

        event.accept()  # 阻止默认滚动行为




class InfoPanelImagePreivew(QFrame):
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.backGroundImageUri = ""
        self.backGroundImage = None
        self.backGroundColor = QColor(15,15,15,255)
        self.setFixedHeight(300)
    def __reloadImage(self):
        self.backGroundImage = scaleMap(self.width(),self.height(),self.backGroundImageUri)
        self.update()
    def setImgae(self,imagePath:str):
        self.backGroundImageUri = imagePath
        self.__reloadImage()
    def paintEvent(self, e: QPaintEvent | None) -> None:
        painter = QPainter(self)
        painter.fillRect(0,0,self.width(),self.height(),self.backGroundColor)
        brush = QBrush()
        brush.setTexture(self.backGroundImage)
        rect  = QRect(0,0,painter.device().width(),painter.device().height())
        painter.fillRect(rect,brush)
        painter.end()
    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        self.__reloadImage()
        return super().resizeEvent(a0)

class InfoPanel(QFrame,Translator):
    onExportClicked = pyqtSignal()
    onTagClicked = pyqtSignal(str)
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.setFixedWidth(400)
        self.shadowWidth = 20
        self.maxAssetTitleLength = 15

        self.rootLayout = QVBoxLayout(self)

        self.scrollArea = SmoothScrollArea(self)
        self.scrollWidget = QWidget(self.scrollArea)
        self.scrollWidgetLayout = QVBoxLayout(self.scrollWidget)

        self.titleImage = InfoPanelImagePreivew(self)

        self.titelWidget = QWidget(self)
        self.titelWidgetLayout = QVBoxLayout(self.titelWidget)

        self.titleLabel = QLabel(self.titelWidget,text="titleLabel")
        self.typeLabel = QLabel(self.titelWidget,text="typeLabel")


        self.CategoryLabel = QLabel(self.titelWidget,text="CategoryLabel")

        self.formatLabel = QLabel(self.titelWidget,text="资产格式:FBX")
        self.versionLabel = QLabel(self.titelWidget,text="软件版本:None")

        self.tagsWidget = QWidget(self.titelWidget)
        self.tagsFlowLayout = FlowLayout(self.tagsWidget,False)
        self.tagsFlowLayout .setContentsMargins(10,10,10,10)
        self.tagsFlowLayout .setVerticalSpacing(20)
        self.tagsFlowLayout .setHorizontalSpacing(10)

        self.exportWidget = QWidget(self)
        self.exportWidgetLayout = QHBoxLayout(self.exportWidget)

        self.button_export = PushButton(self.tra("Export"),self.exportWidget)

        self.combox_res = ComboBox(parent=self.exportWidget)
        self.combox_res.addItems([item.value for item in list(ut.TextureSize.__members__.values())])
        self.combox_res.currentIndexChanged.connect(self.__saveConfig)


        self.combox_lod = ComboBox(parent=self.exportWidget)

        #self.combox_lod.currentIndexChanged.connect(self.__saveConfig)

        self.__initWidget()
        self.__loadConfig()
    def __initWidget(self):
        self.rootLayout.addWidget(self.scrollArea)
        self.rootLayout.addWidget(self.exportWidget)
        self.rootLayout.setContentsMargins(0,0,0,0)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setContentsMargins(0,0,0,0)

        self.scrollWidgetLayout.addWidget(self.titleImage)
        self.scrollWidgetLayout.addWidget(self.titelWidget)


        self.scrollWidgetLayout.setContentsMargins(0,0,0,0)
        self.scrollWidgetLayout.setSpacing(0)
        self.scrollWidgetLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollWidgetLayout.addWidget(self.tagsWidget)
        self.exportWidgetLayout.addWidget(self.combox_res)
        self.exportWidgetLayout.addWidget(self.combox_lod)
        self.exportWidgetLayout.addWidget(self.button_export)
        self.exportWidgetLayout.setContentsMargins(0,10,0,10)

        self.titelWidget.setObjectName("InfoPanelTitleWidget")
        self.titelWidgetLayout.addWidget(self.titleLabel)
        self.titelWidgetLayout.addWidget(self.typeLabel)
        self.titelWidgetLayout.addWidget(self.CategoryLabel)
        self.titelWidgetLayout.addWidget(self.formatLabel)
        self.titelWidgetLayout.addWidget(self.versionLabel)

        self.button_export.clicked.connect(lambda:self.onExportClicked.emit())

        self.titleLabel.setObjectName("titleLabel")
        self.typeLabel.setObjectName("typeLabel")
        self.CategoryLabel.setObjectName("typeLabel")
        self.versionLabel.setObjectName("format")
        self.formatLabel.setObjectName("format")


        self.tagsWidget.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        self.tagsWidget.setObjectName("TagWidget")
    def setPanelInfo(self,imagePath:str,name:str,type:str,tags:list[str],category,subcategory,lods:list[int]=[],format:AssetFormatN=AssetFormatN.FBX,version:str="None"):
        self.titleImage.setImgae(imagePath)
        #裁切名称长度
        if len(name) > self.maxAssetTitleLength:
            name = name[0:self.maxAssetTitleLength] + "..."
        self.titleLabel.setText(name)
        self.typeLabel.setText(type)

        self.CategoryLabel.setText(f"{category}|{subcategory}")

        self.formatLabel.setText(f"资产格式:{format.name}")
        self.versionLabel.setText(f"软件版本:{version}")

        for i in range(self.tagsFlowLayout.count()):
            button = self.tagsFlowLayout.itemAt(i).widget()
            #释放内存
            button.deleteLater()
            button = None

        self.tagsFlowLayout.removeAllWidgets()
        for tag in tags:
            button = StringButton(tag)
            button.onClicked.connect(self.tagClicked)
            self.tagsFlowLayout.addWidget(button)

        self.combox_lod.clear()
        self.combox_lod.addItem(f"original")

        for lod in lods:
            self.combox_lod.addItem(f"Lod{lod}")
        index = math.ceil(len(self.combox_lod.items) * 0.3)-1 or 0
        self.combox_lod.setCurrentIndex(index)

    def tagClicked(self,text):
        self.onTagClicked.emit(text)
    def __loadConfig(self):
        self.combox_res.setCurrentIndex(Config.Get().exportTextureSizeIndex)
        try:
            self.combox_lod.setCurrentIndex(Config.Get().exportLodIndex)
        except:
            pass
    def __saveConfig(self,index):
        Config.Get().exportTextureSizeIndex = self.combox_res.currentIndex()
        Config.Get().exportLodIndex = self.combox_lod.currentIndex()

class ItemHeader(QFrame,Translator):
    searchSignal = pyqtSignal(str)
    clearSignal = pyqtSignal()
    def __init__(self,parent):
        super().__init__(parent=parent)
        self.rootLayout = QVBoxLayout(self)
        self.rootLayout.setContentsMargins(0,0,0,0)

        self.headerWidget = QWidget(self)
        self.headerWidgetLayout = QVBoxLayout(self.headerWidget)

        self.searchBar = SearchLineEdit(self.headerWidget)

        self.widget_refresh_combox = QWidget(self.headerWidget)
        self.layout_refresh_combox = QHBoxLayout(self.widget_refresh_combox)
        self.layout_refresh_combox.setContentsMargins(0,0,0,0)

        self.comboxWidget = QWidget(self.widget_refresh_combox)
        self.comboxWidgetLayout = QHBoxLayout(self.comboxWidget)


        self.combox_type = ComboBox(self)
        self.combox_type.addItem("请选择资产类型")
        self.combox_type.addItems([self.tra(item.value) for item in list(ut.AssetType.__members__.values())])
        self.combox_type.setFixedWidth(200)



        self.combox_format = ComboBox(self)
        self.combox_format.addItem("请选择资产格式")
        self.combox_format.addItems(ut.AssetFormatN._member_names_)
        self.combox_format.setFixedWidth(200)

        self.combox_category = ComboBox(self)
        self.combox_category.addItem("请选择资产主分类")
        self.combox_category.addItems(ut.GetCategorys(0))
        self.combox_category.setFixedWidth(200)



        self.combox_subcategory = ComboBox(self)
        self.combox_subcategory.addItem("请选择资产次级分类")
        self.combox_subcategory.setFixedWidth(200)



        self.widget_refresh = QWidget(self.widget_refresh_combox)
        self.layout_refresh = QVBoxLayout(self.widget_refresh)
        self.layout_refresh.setContentsMargins(0,0,0,0)

        self.refresh_button = ToolButton(FIF.SYNC)
        self.refresh_button.setToolTip("刷新资产库")
        self.layout_refresh.addWidget(self.refresh_button,alignment=Qt.AlignmentFlag.AlignRight)


        self.layout_refresh_combox.addWidget(self.comboxWidget)
        self.layout_refresh_combox.addWidget(self.widget_refresh)

        self.__initWidget()

    def __initWidget(self):
        self.rootLayout.addWidget(self.headerWidget)
        self.rootLayout.setContentsMargins(15,15,15,15)
        self.headerWidgetLayout.addWidget(self.searchBar)
        self.headerWidgetLayout.addWidget(self.widget_refresh_combox)
        self.headerWidgetLayout.setContentsMargins(0,0,0,0)


        self.comboxWidgetLayout.setContentsMargins(0,0,0,0)
        self.comboxWidgetLayout.addWidget(self.combox_type)
        self.comboxWidgetLayout.addWidget(self.combox_format)
        self.comboxWidgetLayout.addWidget(self.combox_category)
        self.comboxWidgetLayout.addWidget(self.combox_subcategory)
        self.comboxWidgetLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)


        self.searchBar.searchSignal.connect(self.__search)
        self.searchBar.clearSignal.connect(self.__clear)
        self.searchBar.returnPressed.connect(lambda:self.__search(self.searchBar.text()))
    def __search(self,text:str):
        """ emit search signal """
        text = text.strip()
        if text:
            self.searchSignal.emit(text)
        else:
            self.clearSignal.emit()
    def __clear(self):
        self.clearSignal.emit()


class HomeInterface(QWidget,Translator):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.content_padding = 20

        self.__initWidget()
        self.__initConnection()
        self.__setQss()
        self.setObjectName("home_interface")

    def __initWidget(self):
        self.rootLayout = QVBoxLayout(self)
        self.rootLayout.setContentsMargins(0,0,0,0)
        self.rootLayout.setSpacing(0)

        widget_header = QWidget(self)
        layout_header = QVBoxLayout(widget_header)
        self.rootLayout.addWidget(widget_header)

        self.item_header = ItemHeader(self)
        layout_header.addWidget(self.item_header)



        widget_content = QWidget(self)
        layout_content = QHBoxLayout(widget_content)
        layout_content.setContentsMargins(self.content_padding,0,10,0)
        layout_content.setSpacing(0)
        self.rootLayout.addWidget(widget_content)


        self.asset_card_view = AssetCardView(self)
        self.info_panel = InfoPanel(self)
        self.info_panel.close()
        layout_content.addWidget(self.asset_card_view)
        layout_content.addWidget(self.info_panel)
    def exportToUnreal(self):
        selected_items = self.asset_card_view.selectedIndexes()
        for item in selected_items:
            if ut.sendAssetToUE(
                item.data(Qt.ItemDataRole.UserRole+1),
                Config.Get().getSendSocketAddress(),
                self.info_panel.combox_res.currentIndex(),
                self.info_panel.combox_lod.currentText()):
                InfoBar.success(
                    title=self.tra('Notice:'),
                    content=self.tra("Export successful"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
            else:
                InfoBar.error(
                    title=self.tra('Error:'),
                    content=self.tra("Export failed"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP,
                    duration=2000,
                    parent=self
                )
                break
    def __initConnection(self):
        self.item_header.searchSignal.connect(self.FilterCardsPerLevel)
        self.item_header.clearSignal.connect(self.FilterCardsPerLevel)
        self.item_header.combox_type.currentIndexChanged.connect(self.FilterCardsPerLevel)
        self.item_header.combox_format.currentIndexChanged.connect(self.FilterCardsPerLevel)
        self.item_header.combox_category.currentIndexChanged.connect(self.changeSubcategoryComboxBaseOnCategory)
        self.item_header.combox_subcategory.currentIndexChanged.connect(self.FilterCardsPerLevel)
        self.item_header.refresh_button.clicked.connect(self.update_asset_from_server)
        self.asset_card_view.item_selected.connect(self.update_info_panel)
        self.asset_card_view.model().item_update.connect(self.update_info_panel)
        self.info_panel.onTagClicked.connect(self.setSearchText)
        self.info_panel.onExportClicked.connect(self.exportToUnreal)
    def update_info_panel(self,index:QModelIndex):
        data:AssetItem = index.data(Qt.ItemDataRole.UserRole + 1)
        self.info_panel.setPanelInfo(
            data.previewFile,
            data.name,
            data.type,
            data.tags,
            data.category,
            data.subcategory,
            data.lods,
            data.Format,
            data.SoftwareVersion
        )
        if not self.info_panel.isVisible():
            self.info_panel.show()
    def setSearchText(self,text):
        self.item_header.searchBar.setText(text)
        self.FilterCardsPerLevel()
    def FilterCardsPerLevel(self,*arg):
        type_index = self.item_header.combox_type.currentIndex()
        category_index = self.item_header.combox_category.currentIndex()
        subcategory_index = self.item_header.combox_subcategory.currentIndex()
        search_key_word = self.item_header.searchBar.text()
        format_index = self.item_header.combox_format.currentIndex()
        self.asset_card_view.model().items_filter(type_index,format_index,category_index,subcategory_index,search_key_word)
    def update_asset_from_server(self):
        self.asset_card_view.model().load_from_server()
        self.FilterCardsPerLevel()
        logger.info("从资产库更新资产")
    #根据主分类改变次级分类
    def changeSubcategoryComboxBaseOnCategory(self,index):
        index = index - 1
        if index >= 0:
            self.item_header.combox_subcategory.clear()
            self.item_header.combox_subcategory.addItem("请选择资产次级分类")
            self.item_header.combox_subcategory.addItems(ut.GetSubCategorys(index))
        else:
            self.item_header.combox_subcategory.clear()
            self.item_header.combox_subcategory.addItem("请选择资产次级分类")
    def append_new_item(self,item:dict):
        self.asset_card_view.model().append_row(item)
    def __setQss(self):
        StyleSheet.HOME_INTERFACE.apply(self)




