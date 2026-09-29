#-*- coding:utf-8 -*-
from __future__ import division,print_function
import math
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class QLine(QFrame):
    def __init__(self,parent=None):
        super(QLine,self).__init__(parent)
        self.setFrameShadow(QFrame.Sunken)
    def SetHorizontal(self):
        self.setFrameShape(QFrame.HLine)
    def SetVertical(self):
        self.setFrameShape(QFrame.VLine)
    @classmethod
    def HLine(cls,parent=None):
        line = QLine(parent)
        line.SetHorizontal()
        return line
    @classmethod
    def VLine(cls,parent=None):
        line = QLine(parent)
        line.SetVertical()
        return line
    
class LabelLineEditGroup(QWidget):
    def __init__(self,text,parent=None):
        super(LabelLineEditGroup,self).__init__(parent)
        self.labelText = text
        self.__initUI()
    def __initUI(self):
        layout_main = QHBoxLayout(self)
        layout_main.setContentsMargins(0,0,0,0)
        self.setLayout(layout_main)
        label = QLabel(parent=self,text=self.labelText)
        layout_main.addWidget(label)
        self.lineEdit = QLineEdit(parent=self)
        layout_main.addWidget(self.lineEdit)
    def setText(self,text):
        self.lineEdit.setText(text)
    def text(self):
        return self.lineEdit.text()
    

class LineEditGroup(QWidget):
    textChanged = Signal(str)
    def __init__(self,text,label_width=50,parent=None):
        super(LineEditGroup,self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        label = QLabel(text)
        label.setFixedWidth(label_width)
        layout.addWidget(label)
        self.lineEdit = QLineEdit(self)
        self.lineEdit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.lineEdit)
    def setText(self,text):
        self.lineEdit.setText(text)
    def clear(self):
        self.lineEdit.clear()
    @property
    def text(self):
        return self.lineEdit.text()
    def _on_text_changed(self,text):
        self.textChanged.emit(self.text)

class ComboxGroup(QWidget):
    textChanged = Signal(str)
    def __init__(self,text,label_width=50,parent=None):
        super(ComboxGroup,self).__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        label = QLabel(text)
        label.setFixedWidth(label_width)

        layout.addWidget(label)
        self.comBox = QComboBox(self)
        self.comBox.currentTextChanged.connect(self._on_text_changed)
        layout.addWidget(self.comBox)
        if isinstance(parent,WidgetGroup):
            parent.addWidget(self)
    def _on_text_changed(self,text):
        self.textChanged.emit(text)
    def add_items(self,items):
        self.comBox.addItems(items)
    def add_item(self,item):
        self.comBox.addItem(item)
    def clear(self):
        self.comBox.clear()
    def set_current_index(self,index):
        self.comBox.setCurrentIndex(index)
    def get_current_text(self):
        return self.comBox.currentText()

class Line(QFrame):
    def __init__(self,isHorizontal,width = 1,parent = None):
        super(Line,self).__init__(parent)
        direction = QFrame.VLine
        if isHorizontal:
            direction = QFrame.HLine
        self.setFrameShape(direction)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(width)
        self.setMidLineWidth(width)


class WidgetGroup(QWidget):
    def __init__(self,isHorizontal,parent = None):
        super(WidgetGroup,self).__init__(parent)

        if isinstance(parent,WidgetGroup):
            parent.addWidget(self)
        self.lMain = None
        if isHorizontal:
            self.lMain = QHBoxLayout(self)
            self.lMain.setAlignment(Qt.AlignLeft)
        else:
            self.lMain = QVBoxLayout(self)
            self.lMain.setAlignment(Qt.AlignTop)
        self.setContentsMargins(0,0,0,0)
    def addWidget(self,widget):
        self.lMain.addWidget(widget)
    def setContentsMargins(self,l,t,r,b):
        self.lMain.setContentsMargins(l,t,r,b)
    def setSpacing(self,spacing):
        self.lMain.setSpacing(spacing)
    def setAlignment(self,alignment):
        self.lMain.setAlignment(alignment)


class ValueInputGroupType:
    INT = 0
    FLOAT = 1

class ValueInputGroup(QWidget):
    onValueChanged = Signal(float)
    def __init__(self,parent=None,text="",valueMax = 100,valueMin=0,step=0.01,value_type=ValueInputGroupType.FLOAT):
        super(ValueInputGroup,self).__init__(parent)
        self.__text = text
        self.__max = valueMax
        self.__min = valueMin
        self.value_type = value_type
        self.step = step
        self.decimals = 1000

        self.initUI()
    def initUI(self):
        ly_main = QHBoxLayout(self)
        self.setLayout(ly_main)
        ly_main.setContentsMargins(0,0,0,0)
        self.__label = QLabel(self.__text)
        ly_main.addWidget(self.__label)

        if self.value_type == ValueInputGroupType.FLOAT:
            self.__spinBox = QDoubleSpinBox()
        else:
            self.__spinBox = QSpinBox()

        self.__spinBox.setMaximum(self.__max)
        self.__spinBox.setMinimum(self.__min)
        self.__spinBox.valueChanged.connect(self.__SpinBoxChanged)
        self.__spinBox.setButtonSymbols(QSpinBox.NoButtons)
        self.__spinBox.setSingleStep(self.step)
        ly_main.addWidget(self.__spinBox)
        self.__slider = QSlider()
        self.__slider.setMaximum(self.__max * self.decimals)
        self.__slider.setMinimum(self.__min * self.decimals)
        self.__slider.valueChanged.connect(self.__SliderChanged)
        self.__slider.setOrientation(Qt.Horizontal)
        self.__slider.setSingleStep(self.step * self.decimals)
        ly_main.addWidget(self.__slider)
    def __SpinBoxChanged(self,value):
        self.__slider.setValue(value*self.decimals)
        self.onValueChanged.emit(value)
    def __SliderChanged(self,value):
        self.__spinBox.setValue(float(value)/self.decimals)
    def value(self):
        return self.__spinBox.value()
    def setValue(self,value):
        self.__spinBox.setValue(value)

class PointType:
    NONE = 0
    LINEAR = 1
    SMOOTH = 2
    SPLINE = 3

class BezierPoint:
    __x = 0.0
    __y = 0.0
    type = PointType.LINEAR
    def __init__(self,x=0,y=0):
        self.__x = x
        self.__y = y
        pass
    def x(self):
        return self.__x
    def y(self):
        return self.__y
    def setX(self,value):
        self.__x = value
    def setY(self,value):
        self.__y = value

class Bezier(QWidget):
    onDataChange = Signal()
    def __init__(self,parent=None):
        super(Bezier,self).__init__(parent)
        self.y_axis_length = None
        self.x_axis_length = None
        self.zero_point = None
        self.points = [BezierPoint(0,1)]
        self.current_point_index = 0
        self.RLEdgeWidth = 10
        self.ButtomEdgeWidth = 20
        self.background_color = QColor(200,200,200)
        self.point_radius = 5

        self.btn_delete_length = 10
        self.move_point = False

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(200)
    def paintEvent(self, event):
        rect = self.rect()
        rect.adjust(self.RLEdgeWidth ,5,-self.RLEdgeWidth ,-self.ButtomEdgeWidth)
        #绘制之前更新基本信息
        self.x_axis_length = rect.width()
        self.y_axis_length = rect.height()
        #开始绘制
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #绘制背景
        painter.fillRect(rect,self.background_color)

        #绘制曲线
        point_start = BezierPoint(0,self.points[0].y())
        point_end = BezierPoint(1,self.points[-1].y())

        path = QPainterPath()
        path.moveTo(rect.bottomLeft())
        path.lineTo(*self.DeNormalizePos(point_start.x(),point_start.y()))

        for index,point in enumerate(self.points):
            if index >= len(self.points)-1:
                break
            if index == 0:
                path.lineTo(*self.DeNormalizePos(self.points[0].x(), self.points[0].y()))
            next_point = self.points[index+1]
            x1,y1 = self.DeNormalizePos(point.x(),point.y())
            x2,y2 = self.DeNormalizePos(next_point.x(),next_point.y())
            if point.type == PointType.NONE:
                path.lineTo(x2,y1)
                path.lineTo(x2,y2)
            elif point.type == PointType.LINEAR:
                path.lineTo(x2,y2)
            elif point.type == PointType.SMOOTH:
                mid_x = (x1 + x2)/2
                c1 = QPoint(
                    mid_x,
                    y1
                )
                c2 = QPoint(
                    mid_x,
                    y2
                )
                path.cubicTo(c1,c2,QPoint(x2,y2))
            elif point.type == PointType.SPLINE:
                mid_x = (x1 + x2)/2
                c1 = QPoint(
                    (mid_x+x1)/2,
                    y1
                )
                c2 = QPoint(
                    (mid_x+x2)/2,
                    y2
                )
                path.cubicTo(c1,c2,QPoint(x2,y2))
                pass
        path.lineTo(*self.DeNormalizePos(point_end.x(),point_end.y()))

        path.lineTo(rect.bottomRight())
        painter.fillPath(path,QColor(80,80,80))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawPath(path)

        #绘制点
        for i,point in enumerate(self.points):
            if i == self.current_point_index:
                point_color = QColor(255,255,255)
            else:
                point_color = QColor(0,0,0)
            painter.setPen(QPen(point_color))
            p_x,p_y = self.DeNormalizePos(point.x(),point.y())
            painter.drawEllipse(QPoint( p_x,p_y ),self.point_radius,self.point_radius)

            btn_x = p_x - self.btn_delete_length/2
            btn_y = rect.bottomLeft().y() + self.btn_delete_length/2
            btn_rect = QRect(btn_x,btn_y,self.btn_delete_length,self.btn_delete_length)


            painter.fillRect(btn_rect,point_color)

        painter.end()
        return super(Bezier,self).paintEvent(event)
    def mousePressEvent(self, event):
        m_posx = event.x()
        m_posy = event.y()
        rect = self.rect()
        rect.adjust(self.RLEdgeWidth ,5,-self.RLEdgeWidth ,-self.ButtomEdgeWidth)


        if not rect.contains(m_posx,m_posy):
            #检测是否需要删除顶点
            for i, point in enumerate(self.points):
                p_x, p_y = self.DeNormalizePos(point.x(), point.y())
                btn_x = p_x - self.btn_delete_length/2
                btn_y = rect.bottomLeft().y() + self.btn_delete_length/2
                btn_rect = QRect(btn_x,btn_y,self.btn_delete_length,self.btn_delete_length)
                if btn_rect.contains(m_posx,m_posy) and len(self.points) > 1:
                    self.points.pop(i)
                    self.current_point_index = 0
            self.update()
            self.onDataChange.emit()
            return super(Bezier,self).mousePressEvent(event)


        #检测是否可以移动点
        for index,point in enumerate(self.points):
            p_x,p_y = self.DeNormalizePos(point.x(),point.y())
            dis_x = p_x - m_posx
            dis_y = p_y - m_posy
            if math.sqrt(dis_x*dis_x + dis_y*dis_y) <= self.point_radius+3:
                self.current_point_index = index
                self.move_point = True
                self.update()
                self.onDataChange.emit()

                return super(Bezier,self).mousePressEvent(event)
        #添加新顶点
        new_point = BezierPoint(*self.NormalizePos(m_posx,m_posy))
        self.add_new_point(new_point)


        self.current_point_index = self.points.index(new_point)
        self.move_point = True
        self.update()
        self.onDataChange.emit()
        return super(Bezier,self).mousePressEvent(event)
    def add_new_point(self,pint):
        self.points.append(pint)
        self.points.sort(key=lambda p:p.x())
        self.update()
    def mouseReleaseEvent(self, event):
        self.move_point = False
        return super(Bezier,self).mouseReleaseEvent(event)
    def mouseMoveEvent(self, event):
        if self.move_point:
            new_x,new_y = self.NormalizePos(event.x(),event.y())
            self.points[self.current_point_index].setX(new_x)
            self.points[self.current_point_index].setY(new_y)
            self.update()
        self.onDataChange.emit()
        return super(Bezier,self).mouseMoveEvent(event)
    def NormalizePos(self,x,y,clamp = True):
        x_pos = (x - self.RLEdgeWidth)/self.x_axis_length
        y_pos = (self.height() - y - self.ButtomEdgeWidth)/self.y_axis_length

        if clamp:
            if x_pos < 0:x_pos = 0
            if x_pos > 1:x_pos = 1
            if y_pos < 0:y_pos = 0
            if y_pos > 1:y_pos = 1
        return x_pos,y_pos
    def DeNormalizePos(self,x,y):
        x_pos = x*self.x_axis_length + self.RLEdgeWidth
        y_pos  =self.height()- y*self.y_axis_length - self.ButtomEdgeWidth
        return x_pos,y_pos

class BezierWidget(QWidget):
    def __init__(self,parent=None):
        super(BezierWidget,self).__init__(parent)
        self.resize(600,400)
        self.__initUI()
        self.__updateData()
    def __initUI(self):
        lay_main = QVBoxLayout(self)
        self.setLayout(lay_main)

        self.bezier = Bezier(self)
        self.bezier.onDataChange.connect(self.__updateData)
        lay_main.addWidget(self.bezier)

        w_input = WidgetGroup(True,self)
        w_input.setMaximumHeight(20)
        lay_main.addWidget(w_input)

        w_input.addWidget(QLabel("Interploation"))
        self.cb_inter = QComboBox()
        self.cb_inter.addItems(["None","Linear","Smooth","Spline"])
        self.cb_inter.setCurrentIndex(1)
        self.cb_inter.currentIndexChanged.connect(self.__setBezierData)
        w_input.addWidget(self.cb_inter)

        w_input.addWidget((QLabel("Selected value:")))

        self.sb_value = QDoubleSpinBox()
        self.sb_value.setButtonSymbols(QSpinBox.NoButtons)
        self.sb_value.setMaximum(1.0)
        self.sb_value.setMinimum(0.0)
        self.sb_value.setMinimumWidth(80)
        self.sb_value.setValue(1)
        self.sb_value.valueChanged.connect(self.__setBezierData)
        w_input.addWidget(self.sb_value)


        w_input.addWidget((QLabel("Selected position:")))
        self.sb_pos = QDoubleSpinBox()
        self.sb_pos.setButtonSymbols(QSpinBox.NoButtons)
        self.sb_pos.setMaximum(1.0)
        self.sb_pos.setMinimum(0.0)
        self.sb_pos.setMinimumWidth(80)
        self.sb_pos.setValue(0)
        self.sb_pos.valueChanged.connect(self.__setBezierData)

        w_input.addWidget(self.sb_pos)
    def __updateData(self):
        point = self.bezier.points[self.bezier.current_point_index]

        self.sb_pos.blockSignals(True)
        self.sb_pos.setValue(point.x())
        self.sb_pos.blockSignals(False)

        self.sb_value.blockSignals(True)
        self.sb_value.setValue(point.y())
        self.sb_value.blockSignals(False)

        self.cb_inter.blockSignals(True)
        self.cb_inter.setCurrentIndex(point.type)
        self.cb_inter.blockSignals(False)

    def __setBezierData(self,*args):
        self.bezier.points[self.bezier.current_point_index].type = self.cb_inter.currentIndex()
        self.bezier.points[self.bezier.current_point_index].setY(self.sb_value.value())
        self.bezier.points[self.bezier.current_point_index].setX(self.sb_pos.value())
        self.bezier.update()


if __name__ == '__main__':
    w = BezierWidget()
    w.show()