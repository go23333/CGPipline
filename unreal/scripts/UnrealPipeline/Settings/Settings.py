#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################

import unreal

from Qt import QtWidgets,QtCore


from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.label import MLabel
from dayu_widgets.spin_box import MDoubleSpinBox,MSpinBox
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.push_button import MPushButton
from dayu_widgets.qt import application
from dayu_widgets import dayu_theme




import UnrealPipeline.core.Config as UC
import UnrealPipeline.core.utilis as UU
import os

class Settings(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("全局设置")
        self.resize(500,400)
        self.move(800,600)
        self.__init_ui()
        self.__loadConfig()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()


        # 相机设置
        layCameraImportSettings = QtWidgets.QVBoxLayout()  #定义Q主布局
        layCameraImportSettings.setSpacing(5)
        # input
        layMacroInput = QtWidgets.QHBoxLayout()
        self.leCameraInputMacro = MLineEdit()
        self.leCameraInputMacro.textChanged.connect(self.applyMacroCamera)

        layMacroInput.addWidget(MLabel("宏输入:"))
        layMacroInput.addWidget(self.leCameraInputMacro)
        CurrentMacro = ""
        for macro in UU.CameraPathMacros:
            CurrentMacro = CurrentMacro + " | " + macro
        # NOTE output
        layMacroOutput = QtWidgets.QHBoxLayout()
        self.leMacroOutput = MLineEdit()
        self.leMacroOutput.setEnabled(False)
        layMacroOutput.addWidget(MLabel("宏输出:"))
        layMacroOutput.addWidget(self.leMacroOutput)

        
        
        self.sbCameraRatio = MDoubleSpinBox()
        self.sbCameraRatio.setDecimals(6)


        layCameraAspectRatio = QtWidgets.QHBoxLayout()
        layCameraAspectRatio.addWidget(MLabel("相机纵横比:"))
        layCameraAspectRatio.addWidget(self.sbCameraRatio)

        # 相机剪切前后滚帧设置
        self.cameraImportPreRollFrame = MSpinBox()
        self.cameraImportPostRollFrame = MSpinBox()



        layCameraRollFrame = QtWidgets.QHBoxLayout()
        layCameraRollFrame.addWidget(MLabel("相机导入前滚帧"))
        layCameraRollFrame.addWidget(self.cameraImportPreRollFrame)
        layCameraRollFrame.addWidget(MLabel("相机导入后滚帧"))
        layCameraRollFrame.addWidget(self.cameraImportPostRollFrame)



        # NOTE add to main layout
        layCameraImportSettings.addWidget(MLabel("相机导入路径宏设置:").h4(),alignment=QtCore.Qt.AlignTop)
        layCameraImportSettings.addWidget(MLabel("示例相机名称:Ep000_sc003_001_001_131_cam"),alignment=QtCore.Qt.AlignTop)
        layCameraImportSettings.addLayout(layMacroInput)
        layCameraImportSettings.addWidget(MLabel(f"当前可以使用的宏有:{CurrentMacro}"))
        layCameraImportSettings.addLayout(layMacroOutput)
        layCameraImportSettings.addLayout(layCameraAspectRatio)
        layCameraImportSettings.addLayout(layCameraRollFrame)
        # 静态网格体设置
        layMeshImportSettings = QtWidgets.QVBoxLayout()  #定义Q主布局
        layMeshImportSettings.setSpacing(5)
        # input
        layMeshMacroInput = QtWidgets.QHBoxLayout()
        self.leMeshMacroInput = MLineEdit()
        #self.leMeshMacroInput.textChanged.connect(self.applyMacro)

        layMeshMacroInput.addWidget(MLabel("宏输入:"))
        layMeshMacroInput.addWidget(self.leMeshMacroInput)
        CurrentMeshMacroTip = ""

        # NOTE output
        layMeshMacroOutput = QtWidgets.QHBoxLayout()
        self.leMeshMacroOutput = MLineEdit()
        self.leMeshMacroOutput.setEnabled(False)
        layMeshMacroOutput.addWidget(MLabel("宏输出:"))
        layMeshMacroOutput.addWidget(self.leMeshMacroOutput)

        # 是否使用场景名称
        self.useSceneName = MCheckBox("使用场景名称")
        # NOTE add to main layout
        layMeshImportSettings.addWidget(MLabel("静态网格体路径设置:").h4(),alignment=QtCore.Qt.AlignTop)
        layMeshImportSettings.addWidget(MLabel("示例模型名称:TestMesh,示例场景名称:TestScene"),alignment=QtCore.Qt.AlignTop)
        layMeshImportSettings.addLayout(layMeshMacroInput)
        layMeshImportSettings.addWidget(MLabel(f"当前可以使用的宏有:{CurrentMeshMacroTip}"))
        layMeshImportSettings.addLayout(layMeshMacroOutput)
        layMeshImportSettings.addWidget(self.useSceneName,alignment=QtCore.Qt.AlignRight)

        layoutbuttons = QtWidgets.QHBoxLayout()
        pbSaveConfig = MPushButton("保存设置")
        pbSaveConfig.clicked.connect(self.saveConfig)
        layoutbuttons.addWidget(pbSaveConfig,alignment=QtCore.Qt.AlignRight)


        layMain.addLayout(layCameraImportSettings)
        layMain.addLayout(layMeshImportSettings)
        layMain.addSpacerItem(QtWidgets.QSpacerItem(20,20,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding))
        layMain.addLayout(layoutbuttons)

        self.setLayout(layMain)
    def __loadConfig(self):
        self.leCameraInputMacro.setText(UC.globalConfig.get().CameraImportPathPatten)
        self.sbCameraRatio.setValue(UC.globalConfig.get().CameraimportAspectRatio)
        self.cameraImportPreRollFrame.setValue(UC.globalConfig.get().cameraImportPreRollFrame)
        self.cameraImportPostRollFrame.setValue(UC.globalConfig.get().cameraImportPostRollFrame)
    def saveConfig(self):
        UC.globalConfig.get().CameraImportPathPatten = self.leCameraInputMacro.text()
        UC.globalConfig.get().CameraimportAspectRatio = self.sbCameraRatio.value()
        UC.globalConfig.get().cameraImportPreRollFrame = self.cameraImportPreRollFrame.value()
        UC.globalConfig.get().cameraImportPostRollFrame = self.cameraImportPostRollFrame.value()
        UC.globalConfig.get().saveConfig()
        pass
    def applyMacroCamera(self):
        parseResult = UU.parseCameraName("Ep000_sc003_001_001_131_cam")
        if parseResult:
            result = UU.applyMacro(self.leCameraInputMacro.text(),parseResult)
            self.leMacroOutput.setText(os.path.normpath(result))


def Start():
    with application() as app:
        global w
        w = Settings()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()
