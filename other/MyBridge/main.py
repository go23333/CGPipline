# coding: utf-8


from qfluentwidgets import NavigationItemPosition,FluentWindow,toggleTheme,SplashScreen
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize,Qt
from PyQt5.QtWidgets import QMessageBox
import sys
import subprocess

import app.resource.resource_rc
from app.ui.home_interface import HomeInterface
from app.ui.setting_interface import SettingInterface
from app.core.translator import Translator
import app.core.utility as ut
from app.core.backend import Backend
from app.ui.import_interface import AssetsImportInterface
from app.ui.batchrender_interface import BatchRenderInterface
from app import ISPACKED
from app.core.config import  Config
from app.ui.f2v_interface import F2vInterface
from app.ui.v_inf_interface import VINFInterface
from app.ui.abc_batch_import import AbcBatchImport

from app.core.Log import Log
logger = Log.get().getLogger("Main")
logger.setLevel(Log.Level.debug)

class MainWindow(FluentWindow,Translator):
    def __init__(self):
        super().__init__()
        self.__initWindow()
        self.__createSubInterface()

        self.splashScreen.finish()
    def __createSubInterface(self):
        #create sub window
        self.homeInterface = HomeInterface(self)
        self.SettingInterface = SettingInterface(self)
        self.assetImportInterface = AssetsImportInterface(self)
        self.assetImportInterface.imported.connect(self.homeInterface.append_new_item)
        self.f2vInterface =F2vInterface(self)
        self.vinfoInterface = VINFInterface(self)
        self.batchRenderInterface = BatchRenderInterface(self)
        self.abc_batch_import = AbcBatchImport(self)
        

        #add sub interface
        nvaigration = self.addSubInterface(self.homeInterface,FIF.HOME,self.tra("Home"))
        nvaigration = self.addSubInterface(self.assetImportInterface,FIF.DOWNLOAD,self.tra("Import"))
        nvaigration = self.addSubInterface(self.f2vInterface,FIF.IMAGE_EXPORT,"合成视频")
        nvaigration = self.addSubInterface(self.vinfoInterface,FIF.VIDEO,"检查帧数")
        nvaigration = self.addSubInterface(self.batchRenderInterface,FIF.IMAGE_EXPORT,"UE批量渲染")
        nvaigration = self.addSubInterface(self.abc_batch_import,FIF.IMAGE_EXPORT,"缓存批量导入")



        nvaigration = self.addSubInterface(self.SettingInterface,FIF.SETTING,self.tra("Settings"),NavigationItemPosition.BOTTOM)


    def __initWindow(self):
        self.setWindowTitle("中影年年资产库")
        self.setWindowIcon(QIcon(r":/MyBridge/image/icon.png"))
        self.navigationInterface.setExpandWidth(200)
        self.setMinimumSize(1200,400)
        self.resize(1200,800)

        # create splash screen
        self.splashScreen = SplashScreen(QIcon(r":/MyBridge/image/logo_large.png"), self)
        self.splashScreen.setIconSize(QSize(400, 400))
        self.splashScreen.raise_()

        # move to center
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.show()
        # 立即处理当前事件循环中所有待处理的事件,保持程序响应性.
        # 避免界面冻结,实时更新UI
        QApplication.processEvents()
    def closeEvent(self, e):
        Config.Get().saveConfig()
        logger.info("主窗口已经关闭")
        return super().closeEvent(e)
    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

if __name__ == "__main__":
    # 检查是否存在实例
    if ut.get_pid("MyBridge.exe"):
        logger.info("已经存在运行的实例,本实例退出")
        sys.exit(0)
    #创建并设置app
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    logger.info("app创建成功")

    #检查更新
    newest_version = None
    current_version = ut.get_current_vesrion()
    if ISPACKED:
        newest_version = Backend.Get().check_update(current_version)
    else:
        logger.info("当前程序未打包,跳过更新")
    if newest_version:
        reply = QMessageBox.question(None,"确认","发现新版本,是否更新?")
        if reply == 16384:
            newest_version_path = Backend.Get().download_version(newest_version)
            subprocess.Popen([newest_version_path])
            logger.info("下载完成,开始更新")
            sys.exit(0)
        else:
            pass

    # 启动窗口
    toggleTheme()
    window = MainWindow()
    window.show()
    logger.info("程序启动完成")
    sys.exit(app.exec_())




