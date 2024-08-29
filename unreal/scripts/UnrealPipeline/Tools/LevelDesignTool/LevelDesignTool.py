#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.08
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
from Qt import QtWidgets,QtCore

from dayu_widgets.push_button import MPushButton
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.divider import MDivider
from dayu_widgets.qt import application
from dayu_widgets import dayu_theme
import unreal

from UnrealPipeline.core.CommonWidget import CommonMenuBar
import UnrealPipeline.core.UnrealHelper as UH

class LevelDesignTool(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("地编工具")
        self.resize(300,400)
        self.move(800,600)
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()   #定义主布局

        # 添加一些按钮
        pbOpenSelectedFoliage = MPushButton(text="打开选中植物窗口")
        pbOpenSelectedFoliage.clicked.connect(self.openSelectedFoliage)
        pbConvertFoliageToStaticMesh = MPushButton(text="转换植物为静态网格体")
        pbConvertFoliageToStaticMesh.clicked.connect(self.convertFoliageToStaticMesh)
        pbEnalbeFullPercisionUV = MPushButton(text="开启全精度UV")
        pbEnalbeFullPercisionUV.clicked.connect(self.enableFullPercisionUV)
        pbSimpleLight = MPushButton(text="简单光照")
        pbSimpleLight.clicked.connect(self.simpleLight)
        pbSelectSimilarActor = MPushButton(text="选择相似Actor")
        pbSelectSimilarActor.clicked.connect(self.selectSimilarActor)

        layBreakBlueprint = QtWidgets.QHBoxLayout()
        self.cboxDeleteOriginalBlueprint = MCheckBox(text="删除原来蓝图")
        pbBreakBlueprint = MPushButton(text="执行蓝图拆分")
        pbBreakBlueprint.clicked.connect(self.breakBlueprint)
        layBreakBlueprint.addWidget(self.cboxDeleteOriginalBlueprint)
        layBreakBlueprint.addWidget(pbBreakBlueprint)

        menubar = CommonMenuBar()  #定义菜单栏
        layMain.menuBar = menubar
        layMain.setMenuBar(menubar)
        layMain.addWidget(pbOpenSelectedFoliage)
        layMain.addWidget(pbConvertFoliageToStaticMesh)
        layMain.addWidget(pbEnalbeFullPercisionUV)
        layMain.addWidget(pbSimpleLight)
        layMain.addWidget(pbSelectSimilarActor)
        layMain.addWidget(MDivider("蓝图拆分工具"),alignment=QtCore.Qt.AlignTop)
        layMain.addLayout(layBreakBlueprint)
        self.setLayout(layMain)
    def openSelectedFoliage(self):
        UH.openSelectedFoliage()
    def convertFoliageToStaticMesh(self):
        UH.FoliageToSMActor()
    def enableFullPercisionUV(self):
        UH.enableFullPercisionUV()
    def simpleLight(self):
        UH.simpleLight()
    def selectSimilarActor(self):
        UH.selectSimilarActor()
    def breakBlueprint(self):
        UH.breakBlueprint(self.cboxDeleteOriginalBlueprint.isChecked())

def Start():
    with application() as app:
        global w
        w = LevelDesignTool()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()
