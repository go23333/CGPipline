from Qt.QtWidgets import QFrame,QWidget,QHBoxLayout,QLabel,QLineEdit


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



if __name__ == '__main__':
    line = QLine.HLine()
    print(line)