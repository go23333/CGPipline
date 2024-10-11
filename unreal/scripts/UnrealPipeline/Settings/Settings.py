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
from Qt.QtWidgets import QScrollArea
import os



import UnrealPipeline.core.Config as UC
import UnrealPipeline.core.utilis as UU


class Settings(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("全局设置")
        self.move(600,300)
        self.__init_ui()
        self.__loadConfig()
    def __init_ui(self):
        layMain = QtWidgets.QVBoxLayout()






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
        layCameraAspectRatio.setContentsMargins(0,0,0,0)

        # 相机剪切前后滚帧设置
        self.cameraImportPreRollFrame = MSpinBox()
        self.cameraImportPostRollFrame = MSpinBox()



        layCameraRollFrame = QtWidgets.QHBoxLayout()
        layCameraRollFrame.addWidget(MLabel("相机导入前滚帧"))
        layCameraRollFrame.addWidget(self.cameraImportPreRollFrame)
        layCameraRollFrame.addWidget(MLabel("相机导入后滚帧"))
        layCameraRollFrame.addWidget(self.cameraImportPostRollFrame)
        layCameraRollFrame.setContentsMargins(0,0,0,0)

        # 相机导入playback Range 设置

        self.cameraImportPlayBackRangeStart = MSpinBox()
        self.cameraImportPlayBackRangeEnd = MSpinBox()

        layCameraPlayBackRange = QtWidgets.QHBoxLayout()

        layCameraPlayBackRange.addWidget(MLabel("相机导入回放范围开始偏移值"))
        layCameraPlayBackRange.addWidget(self.cameraImportPlayBackRangeStart)
        layCameraPlayBackRange.addWidget(MLabel("相机导入回放范围结束偏移值"))
        layCameraPlayBackRange.addWidget(self.cameraImportPlayBackRangeEnd)


        
        widget_camera_settings = QtWidgets.QFrame(self)
        widget_camera_settings_layout = QtWidgets.QVBoxLayout(widget_camera_settings)

        widget_camera_settings_layout.addWidget(MLabel("相机导入路径宏设置:").h4(),alignment=QtCore.Qt.AlignTop)
        widget_camera_settings_layout.addWidget(MLabel("示例相机名称:Ep000_sc003_001_001_131_cam"),alignment=QtCore.Qt.AlignTop)
        widget_camera_settings_layout.addLayout(layMacroInput)
        widget_camera_settings_layout.addWidget(MLabel(f"当前可以使用的宏有:{CurrentMacro}"))
        widget_camera_settings_layout.addLayout(layMacroOutput)
        widget_camera_settings_layout.addLayout(layCameraAspectRatio)
        widget_camera_settings_layout.addLayout(layCameraRollFrame)
        widget_camera_settings_layout.addLayout(layCameraPlayBackRange)
        widget_camera_settings_layout.setContentsMargins(0,0,0,0)
        widget_camera_settings.setObjectName("widget_camera_settings")
        #widget_camera_settings.setStyleSheet("#widget_camera_settings{background-color: rgb(30, 30, 30);border-radius: 8px;}")


        # 静态网格体设置
        layMeshImportSettings = QtWidgets.QVBoxLayout()  #定义Q主布局
        layMeshImportSettings.setSpacing(5)
        # input
        layMeshMacroInput = QtWidgets.QHBoxLayout()
        self.leMeshMacroInput = MLineEdit()
        self.leMeshMacroInput.textChanged.connect(self.applyMarcoStaticmesh)

        layMeshMacroInput.addWidget(MLabel("宏输入:"))
        layMeshMacroInput.addWidget(self.leMeshMacroInput)
        CurrentMeshMacroTip = " | ".join(UU.StaticMeshMacros)
        # NOTE output
        layMeshMacroOutput = QtWidgets.QHBoxLayout()
        self.leMeshMacroOutput = MLineEdit()
        self.leMeshMacroOutput.setEnabled(False)
        layMeshMacroOutput.addWidget(MLabel("宏输出:"))
        layMeshMacroOutput.addWidget(self.leMeshMacroOutput)

        # NOTE add to main layout
        layMeshImportSettings.addWidget(MLabel("静态网格体路径设置:").h4(),alignment=QtCore.Qt.AlignTop)
        layMeshImportSettings.addWidget(MLabel("示例模型名称:TestMesh,示例场景名称:TestScene"),alignment=QtCore.Qt.AlignTop)
        layMeshImportSettings.addLayout(layMeshMacroInput)
        layMeshImportSettings.addWidget(MLabel(f"当前可以使用的宏有:{CurrentMeshMacroTip}"))
        layMeshImportSettings.addLayout(layMeshMacroOutput)
        layMeshImportSettings.setContentsMargins(0,0,0,0)


        layoutbuttons = QtWidgets.QHBoxLayout()
        pbSaveConfig = MPushButton("保存设置")
        pbSaveConfig.clicked.connect(self.__saveConfig)
        layoutbuttons.addWidget(pbSaveConfig,alignment=QtCore.Qt.AlignRight)




        # MyBridgeSettings
        mybridge_setttings_widget = QtWidgets.QWidget(self)
        mybridge_setttings_Layout = QtWidgets.QVBoxLayout(mybridge_setttings_widget)
        mybridge_setttings_Layout.setContentsMargins(0,0,0,0)

        mybridge_setttings_Layout.addWidget(MLabel("资产库导入设置:").h4(),alignment=QtCore.Qt.AlignTop)
        


        # lineEdit_connectHost = MLineEdit("连接地址(需重启):")
        # lineEdit_connectPort = MLineEdit("连接端口(需重启):")
        # mybridge_setttings_Layout.addWidget(lineEdit_connectHost)
        # mybridge_setttings_Layout.addWidget(lineEdit_connectPort)






        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scrollWidget = QtWidgets.QWidget(scroll)
        scroll.setWidget(scrollWidget)
        scrollWidgetLayout = QtWidgets.QVBoxLayout(scrollWidget)
        scrollWidgetLayout.setContentsMargins(20,30,20,0)


        scrollWidgetLayout.addWidget(widget_camera_settings)
        scrollWidgetLayout.addLayout(layMeshImportSettings)
        scrollWidgetLayout.addSpacerItem(QtWidgets.QSpacerItem(20,20,QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding))
        scrollWidgetLayout.addWidget(mybridge_setttings_widget)
        scrollWidgetLayout.addLayout(layoutbuttons)


        layMain.addWidget(scroll)

        layMain.setContentsMargins(0,0,0,0)
        self.setLayout(layMain)
    def __loadConfig(self):
        self.leCameraInputMacro.setText(UC.globalConfig.get().CameraImportPathPatten)
        self.sbCameraRatio.setValue(UC.globalConfig.get().CameraimportAspectRatio)
        self.cameraImportPreRollFrame.setValue(UC.globalConfig.get().cameraImportPreRollFrame)
        self.cameraImportPostRollFrame.setValue(UC.globalConfig.get().cameraImportPostRollFrame)

        self.cameraImportPlayBackRangeStart.setValue(UC.globalConfig.get().cameraPlaybackStartOffset)
        self.cameraImportPlayBackRangeEnd.setValue(UC.globalConfig.get().cameraPlaybackEndOffset)
        self.leMeshMacroInput.setText(UC.globalConfig.get().StaticMeshImportPathPatten)
    def __saveConfig(self):
        UC.globalConfig.get().CameraImportPathPatten = self.leCameraInputMacro.text()
        UC.globalConfig.get().CameraimportAspectRatio = self.sbCameraRatio.value()
        UC.globalConfig.get().cameraImportPreRollFrame = self.cameraImportPreRollFrame.value()
        UC.globalConfig.get().cameraImportPostRollFrame = self.cameraImportPostRollFrame.value()

        UC.globalConfig.get().cameraPlaybackStartOffset = self.cameraImportPlayBackRangeStart.value()
        UC.globalConfig.get().cameraPlaybackEndOffset = self.cameraImportPlayBackRangeEnd.value()
        UC.globalConfig.get().StaticMeshImportPathPatten = self.leMeshMacroInput.text()
        UC.globalConfig.get().saveConfig()
        pass
    def applyMacroCamera(self):
        parseResult = UU.parseCameraName("Ep000_sc003_001_001_131_cam")
        if parseResult:
            result = UU.applyMacro(self.leCameraInputMacro.text(),parseResult)
            self.leMacroOutput.setText(os.path.normpath(result))
    def applyMarcoStaticmesh(self):
        parseResult = UU.parseStaticMeshName("TestMesh","TestScene")
        if parseResult:
            result = UU.applyMacro(self.leMeshMacroInput.text(),parseResult)
            self.leMeshMacroOutput.setText(os.path.normpath(result))
        pass

def Start():
    with application() as app:
        global w
        w = Settings()
        w.resize(400,600)
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()
