from qfluentwidgets import (PrimaryPushSettingCard,TitleLabel,SettingCardGroup,SettingCard,
                            LineEdit,InfoBar,InfoBarPosition)
from qfluentwidgets import FluentIcon as FIF

from PyQt5.QtWidgets import (QWidget,QFileDialog,QVBoxLayout)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import Qt,pyqtSignal
from qfluentwidgets.common.icon import FluentIconBase


from app.core.Log import Log
from app.core.config import Config
from app.core.translator import Translator
import app.core.utility as ut

class LineEditSettingCard(SettingCard):
    editingFinished = pyqtSignal(str)
    def __init__(self, icon: str | QIcon | FluentIconBase, title, text=None, parent=None):
        super().__init__(icon, title, None, parent)
        self.text = text
        self.__initWindow()
    def __initWindow(self):
        self.lineEdit = LineEdit(self)
        self.lineEdit.setMinimumWidth(200)
        self.lineEdit.setText(self.text)
        self.hBoxLayout.addWidget(self.lineEdit)
        self.hBoxLayout.addSpacing(16)
        self.lineEdit.editingFinished.connect(self.__editingFinished)
    def setText(self,text:str):
        self.text = text
        self.lineEdit.setText(text)
    def __editingFinished(self):
        text = self.lineEdit.text()
        self.editingFinished.emit(text)


class SettingInterface(QWidget,Translator):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.__initWindow()
        self.__setQss()
    def __initWindow(self):
        rootLayout = QVBoxLayout(self)

        label_Settings = TitleLabel(self.tra("Settings"),self)


        version = ut.get_current_vesrion()


        self.aboutGroup = SettingCardGroup("关于", self)
        self.aboutCard = PrimaryPushSettingCard(
            self.tr(''),
            FIF.INFO,
            self.tr('About'),
            '© ' + self.tr('Copyright') + f"  2025,zynn. " +
            self.tr('Version') + " " + version,
            self.aboutGroup
        )
        self.aboutCard.button.setHidden(True)
        self.aboutGroup.addSettingCard(self.aboutCard)

        


        group_connect_settings = SettingCardGroup(self.tra("Connect Settings"),self)

        card_connect_address = LineEditSettingCard(
            FIF.CONNECT,
            self.tra("Connect address"),
            text = Config.Get().socketAddress,
            parent = group_connect_settings
        )
        card_connect_address.editingFinished.connect(self.__setAddress)
        card_connect_port = LineEditSettingCard(
            FIF.CONNECT,
            self.tra("Connect port"),
            text = str(Config.Get().socketSendPort),
            parent = group_connect_settings
        )
        card_connect_port.editingFinished.connect(self.__setPort)
        group_connect_settings.addSettingCard(card_connect_address)
        group_connect_settings.addSettingCard(card_connect_port)




        rootLayout.addWidget(label_Settings)
        rootLayout.addWidget(group_connect_settings)
        rootLayout.addWidget(self.aboutGroup)
        rootLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        

        rootLayout.setContentsMargins(50,30,50,30)
        rootLayout.setSpacing(0)
        self.setObjectName("setting_interface")

    def __SeletLibraryFolder(self):
        folder = QFileDialog.getExistingDirectory(
            self, self.tra("Choose folder"), "./")
        if not folder or Config.Get().remoteAssetLibraryFolder == folder:
            return
        Config.Get().remoteAssetLibraryFolder = folder
        self.card_server_address.setContent(folder)
        Config.Get().saveConfig()
        self.showInfoConfigSaved()
    def __setAddress(self,text:str):
        Config.Get().socketAddress = text
        Config.Get().saveConfig()
        self.showInfoConfigSaved()
    def __setBackendAddress(self,text:str):
        Config.Get().backendAddress = text.strip()
        Config.Get().saveConfig()
        self.showInfoConfigSaved()
    def __setPort(self,text:str):
        Config.Get().socketSendPort = eval(text)
        Config.Get().saveConfig()
        self.showInfoConfigSaved()
    def showInfoConfigSaved(self):
        InfoBar.success(
            title=self.tra('notice:'),
            content=self.tra("The current Settings have been saved and will take effect after the restart"),
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    def __setQss(self):
        pass
