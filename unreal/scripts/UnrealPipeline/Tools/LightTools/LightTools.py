#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 20240828
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
from Qt import QtWidgets
from Qt import QtCore
from dayu_widgets.push_button import MPushButton
from dayu_widgets.qt import application
from dayu_widgets import dayu_theme
import unreal

from UnrealPipeline.core.CommonWidget import CommonMenuBar,SpinBoxWithLabel
import UnrealPipeline.core.UnrealHelper as UH
from songshunjie import lt_level,CameraHide

#灯光常用工具
class LightTools(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("灯光工具")
        self.resize(300,400)
        self.__init_ui()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()   #定义主布局
        menubar = CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        # 添加一些按钮
        pbAutoID = MPushButton("自动ID(包括植物)")
        pbAutoID.clicked.connect(UH.autoID())
        pbPoolSize = MPushButton("无限纹理流送池")
        pbPoolSize.clicked.connect(UH.poolSize)
        pbPopEmmissive = MPushButton("弹出自发光材质")
        pbPopEmmissive.clicked.connect(UH.popEmmissive)
        pbOpenImportCameraUI = MPushButton("打开相机导入窗口")
        pbOpenImportCameraUI.clicked.connect(self.openImportCameraUI)
        pbLightImportAndExport = MPushButton("灯光场景导入导出工具")
        pbLightImportAndExport.clicked.connect(self.LightImportAndExport)
        pbACtorVisible = MPushButton("使选中对象对镜头隐藏和显示")
        pbACtorVisible.clicked.connect(self.ACtorVisible)
        self.wNearClip = SpinBoxWithLabel("近裁剪面:",0,1,6,1000.0,0.00001,0.00001,0.00001)
        self.wNearClip.setOnValueChanged(self.nearClip)
        layMain.addWidget(pbAutoID)
        layMain.addWidget(pbPoolSize)
        layMain.addWidget(pbPopEmmissive)
        layMain.addWidget(pbOpenImportCameraUI)
        layMain.addWidget(pbLightImportAndExport)
        layMain.addWidget(pbACtorVisible)
        layMain.addWidget(self.wNearClip,alignment=QtCore.Qt.AlignTop)
        self.setLayout(layMain)
    def openImportCameraUI(self):
        UH.openImportCameraUI()
        pass
    def nearClip(self):
        value = self.wNearClip.getValue()
        UH.nearClip(value)
        #songshunjie插件
    def LightImportAndExport(self):
        lt_level.start()
        pass
    def ACtorVisible(self):
        CameraHide.start()
        pass


def Start():
    with application() as app:
        global w
        w = LightTools()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()



    