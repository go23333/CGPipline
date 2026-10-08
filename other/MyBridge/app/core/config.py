import os
import json
from app.core.Log import Log
from app import ISPACKED


logger = Log.get().getLogger("Config")
logger.setLevel(Log.Level.debug)

class Config():
    instance = None
    def __init__(self) -> None:
        self.localAssetLibraryFolder = os.path.join(os.environ['USERPROFILE'], 'Documents',"MyBridge")
        self.localTempFolder = os.path.join(self.localAssetLibraryFolder,"Temp")
        self.localConfigSavePath = os.path.join(self.localAssetLibraryFolder,"config.json")

        # can saved value
        self.socketAddress = "127.0.0.1"
        self.socketSendPort = 54321
        self.exportTextureSizeIndex = 0
        self.exportLodIndex = 0
        self.backendAddress = "http://192.168.3.20:5050"

        self.CurrentUnrealPath = r"F:/UE_5.7/Engine/Binaries/Win64/UnrealEditor.exe"
        self.CurrentUnrealProjectPath = r"E:/UnrealEngine57Project/RenderTest/RenderTest.uproject"
        self.CurrentRenderConfigPath = r"E:/UnrealEngine57Project/RenderTest/Content/Pending_MoviePipelinePrimaryConfig.uasset"

        self.loadConfig()
        self.__createFolders()
    def loadConfig(self):
        #如果项目未打包,则不从配置中读取
        if not ISPACKED:
            logger.info("项目未打包,跳过配置读取")
            return
        #如果配置文件不存在,跳过读取配置
        if not os.path.exists(self.localConfigSavePath):
            logger.info("配置文件不存在,跳过导入配置")
            return

        #服务器地址固定
        self.backendAddress = "http://192.168.3.20:5050"

        #打开配置文件
        with open(self.localConfigSavePath,'r',encoding="utf-8") as f:
            data = json.loads(f.read())

        self.socketAddress = data.get("sockeAddress", self.socketAddress)
        self.socketSendPort = data.get("socketSendPort", self.socketSendPort)
        self.exportTextureSizeIndex = data.get("exportTextureSizeIndex", self.exportTextureSizeIndex)
        self.exportLodIndex = data.get("exportLodIndex", self.exportLodIndex)
        self.CurrentUnrealPath = data.get("CurrentUnrealPath", self.CurrentUnrealPath)
        self.CurrentUnrealProjectPath = data.get("CurrentUnrealProjectPath", self.CurrentUnrealProjectPath)
        self.CurrentRenderConfigPath = data.get("CurrentRenderConfigPath", self.CurrentRenderConfigPath)

        logger.info("配置文件导入成功")
    def saveConfig(self):
        data = dict(
            sockeAddress = self.socketAddress,
            socketSendPort = self.socketSendPort,
            exportTextureSizeIndex = self.exportTextureSizeIndex,
            exportLodIndex = self.exportLodIndex,
            CurrentUnrealPath = self.CurrentUnrealPath,
            CurrentUnrealProjectPath = self.CurrentUnrealProjectPath,
            CurrentRenderConfigPath = self.CurrentRenderConfigPath,
        )
        with open(self.localConfigSavePath,'w+',encoding="utf-8") as f:
            f.write(json.dumps(data))
        logger.info("配置文件保存完成")
    def __createFolders(self):
        folders = [
            self.localAssetLibraryFolder,
            self.localTempFolder
        ]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
    def getSendSocketAddress(self)->tuple[str,int]:
        return (self.socketAddress, self.socketSendPort)
    @classmethod
    def Get(cls):
        if not cls.instance:
            logger.info("配置尚未创建,创建新的配置类单例")
            cls.instance = cls()
        return cls.instance