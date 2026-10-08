from qfluentwidgets import (Dialog,PushButton,IndeterminateProgressRing,SubtitleLabel)
from qfluentwidgets import (PushButton,ComboBox,LineEdit,IndeterminateProgressRing,Dialog,ToolButton)
from qfluentwidgets import FluentIcon as FIF

from PyQt5.QtWidgets import (QApplication,QWidget,
                             QHBoxLayout,QVBoxLayout,
                             QLabel,QTabWidget,QLineEdit,QToolButton,QFileDialog)

from PyQt5.QtWidgets import (QApplication,QWidget,
                             QFrame,QHBoxLayout,QVBoxLayout,)
from PyQt5.QtGui import (QMouseEvent, QPaintEvent,QPainter,QPixmap,QColor)
from PyQt5.QtCore import QObject, QRect,Qt,pyqtSignal,QThread,QPropertyAnimation

def showDialog(title,content,parent):
    w = Dialog(title,content,parent)
    w.setTitleBarVisible(False)
    w.setContentCopyable(True)
    return(w.exec())



class TabWidget(QTabWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("tableWidget")
        self.tabBar().close()


class FadeToolButton(ToolButton):
    def __init__(self, icon,parent):
        super().__init__(parent)
        self.setIcon(icon)
        self.close()
    def fadeAnimation(self,disappear:bool):
        
        startValue = 0.0
        endValue = 1.0
        if disappear:
            self.close()
            startValue = 1.0
            endValue = 0.0
        else:
            self.show()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1000)  # 动画持续时间 1000 毫秒.
        self.animation.setStartValue(startValue)  # 起始透明度为 1.0（完全不透明）
        self.animation.setEndValue(endValue)    # 结束透明度为 0.0（完全透明）
        self.animation.start()


class TabBarButton(QWidget):
    clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    def __init__(self, parent,text:str,index:int):
        super().__init__(parent)
        self.rootLayout = QHBoxLayout(self)
        self.selectedFlageWidth = 5
        self.setFixedSize(200, 25)
        self.label = QLabel(self,text=text)
        self.isSelected = False
        self.button_delete = FadeToolButton(FIF.DELETE,self)
        self.index = index

        self.__initWidget()
        self.__initConnection()
    def __initWidget(self):

        self.rootLayout.addWidget(self.label,alignment=Qt.AlignmentFlag.AlignLeft)
        self.rootLayout.addWidget(self.button_delete,alignment=Qt.AlignmentFlag.AlignRight)
        self.rootLayout.setContentsMargins(self.selectedFlageWidth+10,0,10,0)


        self.button_delete.setFixedSize(self.height()-2,self.height()-2)
        pass
    def __initConnection(self):
        self.button_delete.clicked.connect(lambda :self.delete_clicked.emit(self.index))
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        super().paintEvent(a0) 
        if not self.isSelected:
            return
        painter = QPainter(self)
        rect = QRect(0,0,self.selectedFlageWidth,self.height())
        painter.fillRect(rect,QColor(139,194,74,255))
        painter.end()
    def setSelected(self,isSelected:bool,force=False):
        if isSelected == self.isSelected and not force:
            return
        self.isSelected = isSelected
        self.setProperty("isSelected",self.isSelected)
        self.setStyle(QApplication.style())
    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        if self.isSelected:
            return
        self.clicked.emit(self.index)
    def setText(self,text:str):
        if len(text) > 10:
            text = text[:10] + "..."
        self.label.setText(text)
    def enterEvent(self, a0) -> None:
        self.button_delete.fadeAnimation(False)
    def leaveEvent(self, a0) -> None:
        self.button_delete.fadeAnimation(True)

def LoadPixmapSafely(path):
    pixmap = QPixmap(path)
    return(pixmap)

class QLine(QFrame):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setFrameShadow(QFrame.Shadow.Sunken)
    def SetHorizontal(self):
        self.setFrameShape(QFrame.Shape.HLine)
    def SetVertical(self):
        self.setFrameShape(QFrame.Shape.VLine)
    @classmethod
    def HLine(cls,parent):
        line = QLine(parent)
        line.SetHorizontal()
        return line
    @classmethod
    def VLine(cls,parent):
        line = QLine(parent)
        line.SetVertical()
        return line


def load_and_fix_image(image_uri):
    pass
    # assert not will_trigger_warning(image_uri),image_uri
    # return QPixmap(image_uri)

def scaleMap(width:int,height:int,mapPath:str)-> QPixmap:
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


def scalePixelMap(width:int,height:int,original_pixelmap:QPixmap)-> QPixmap:
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

def showDialog(title,content):
    w = Dialog(title,content)
    w.setTitleBarVisible(False)
    w.setContentCopyable(True)
    return(w.exec())

class StringButton(PushButton):
    onClicked = pyqtSignal(str)
    def __init__(self,text,icon=FIF.TAG,parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setIcon(icon)
        self.clicked.connect(lambda:self.onClicked.emit(self.text()))

class CommonWorker(QThread):
    fun = None
    overed = pyqtSignal()
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
    def run(self) -> None:
        if self.fun:
            self.fun()
        self.overed.emit()


class TitleProgressRing(QWidget):
    def __init__(self, parent=None, start=True,text=""):
        super().__init__(parent)
        self.progressRing = IndeterminateProgressRing(self,start)
        self.title = SubtitleLabel(text= text,parent=self)
        self.__initUI()
    def __initUI(self):
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.progressRing)
        self.mainLayout.addWidget(self.title,alignment=Qt.AlignmentFlag.AlignTop)


        self.mainLayout.setSpacing(10)
        self.setContentsMargins(0,0,0,0)


        self.setLayout(self.mainLayout)
        self.setFixedSize(200,200)
        pass


class LineEidtGroup(QWidget):
    returnPressed = pyqtSignal(str)
    def __init__(self, parent,text:str,textMaxWidth:int = 50):
        super().__init__(parent)
        self.textMaxWidth = textMaxWidth

        self.rootLayout = QHBoxLayout(self)
        self.labelText =QLabel(self,text=text)
        self.lineEdit = LineEdit(self)
        self.lineEdit.returnPressed.connect(self.returnPress)
        self.__initWidget()
        self.__initConnections()
    def __initWidget(self):
        self.rootLayout.addWidget(self.labelText)
        self.rootLayout.addWidget(self.lineEdit)
        self.rootLayout.setContentsMargins(0,0,0,0)
        self.labelText.setFixedWidth(self.textMaxWidth)
    def setText(self,text:str):
        self.lineEdit.setText(text)
    def clear(self):
        self.lineEdit.clear()
    def text(self):
        return self.lineEdit.text()
    def returnPress(self):
        self.returnPressed.emit(self.lineEdit.text())
        self.clear()
    def __initConnections(self):
        pass


class FileSelectGroup(QWidget):
    onSelectPath = pyqtSignal(str)
    def __init__(self, text:str,selectText:str,selectType:str,parent=None,textMaxWidth:int=50):
        super().__init__(parent)
        self.__init_UI(text,selectText,selectType,textMaxWidth)
    def __init_UI(self,text:str,selectText:str,selectType,textMaxidth):
        lyMain = QHBoxLayout(self)
        lyMain.setContentsMargins(0,0,0,0)
        self.setLayout(lyMain)

        label = QLabel(text,self)
        label.setFixedWidth(textMaxidth)
        lyMain.addWidget(label)

        self.le_path = QLineEdit(self)
        lyMain.addWidget(self.le_path)


        pb_select = QToolButton(self)
        lyMain.addWidget(pb_select)
        pb_select.clicked.connect(lambda :self.selectPath(selectText,selectType))

        self.setLayout(lyMain)
    def text(self):
        return self.le_path.text()
    def setText(self,text:str):
        self.le_path.setText(text)
    def selectPath(self,selectText,selectType):
        path, _ = QFileDialog.getOpenFileName(
            self,
            selectText,
            "",
            selectType
        )
        if path != "":
            self.le_path.setText(path)
        self.onSelectPath.emit(path)


class ComboxGroup(QWidget):
    currentTextChanged = pyqtSignal(str)
    def __init__(self, parent,text:str,textMaxWidth:int = 50):
        super().__init__(parent)
        self.textMaxWidth = textMaxWidth
        self.rootLayout = QHBoxLayout(self)
        self.labelText =QLabel(self,text=text)
        self.combox = ComboBox(self)
        self.combox.currentTextChanged.connect(self.currentTextChange)
        self.__initWidget()
    def __initWidget(self):
        self.rootLayout.addWidget(self.labelText)
        self.rootLayout.addWidget(self.combox)
        self.rootLayout.setContentsMargins(0,0,0,0)
        self.labelText.setFixedWidth(self.textMaxWidth)
    def addItems(self,items:list[str]):
        self.combox.addItems(items)
    def setCurrentText(self,text:str):
        self.combox.setCurrentText(text)
    def setCurrentIndex(self,index:int):
        self.combox.setCurrentIndex(index)
    def currentText(self):
        return self.combox.currentText()
    def currentIndex(self):
        return self.combox.currentIndex()
    def currentTextChange(self,str):
        self.currentTextChanged.emit(str)
    def clear(self):
        self.combox.clear()

