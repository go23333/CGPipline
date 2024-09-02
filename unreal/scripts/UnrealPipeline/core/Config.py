#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
class globalConfig():
    _instance = None
    def __init__(self) -> None:
        # paths
        self.LogFilePath = r'D:\Documents\CGPipline\log\unreal.log'
        self.configFilePath = r"d:\Documents\CGPipline\save\config.config"
        # paramater Camera Import
        self.CameraImportPathPatten = "/Game/Shots/Sequence/$ep/$sc/$ep_$sc_$number"
        self.CameraimportUniformScale = 1
        self.CameraimportAspectRatio = 1.777778
        self.cameraImportPreRollFrame = 10
        self.cameraImportPostRollFrame = 10
        self.cameraPlaybackStartOffset = 0
        self.cameraPlaybackEndOffset = 0
        # paramater Mesh Import
        self.StaticMeshImportPathPatten = "/Game/Assets/Scene/Mesh/"
        # paramater Texture Import
        self.TextureImportPathPatten = "/Game/Assets/Scene/Texture/"
        self.TextureEnableVT = 1 #0:关闭,1:启用,2:自动
        # paramater Material Create
        self.MaterialInstancePath = "/Game/Assets/Scene/Material/"
        self.LocalSceneDefaultMaterial = "/Game/Assets/Scene/Common/Material/M_BG_ARM"
        self.SceneDefaultMaterial = "/ZynnPlugin/Assets/Material/M_BG_ARM"
        self.loadConfig()
    def saveConfig(self):
        import json
        import os 
        dir,_ = os.path.split(self.configFilePath)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(self.configFilePath,"w+",encoding="utf-8") as f:
            f.write(json.dumps(self.__asDict()))
    def loadConfig(self):
        import json
        import os 
        if not os.path.exists(self.configFilePath):
            return False
        with open(self.configFilePath,"r",encoding="utf-8") as file:
            data = json.loads(file.read())
        if data:
            self.__loadFromDict(data)
    def __asDict(self) -> dict:
        attrs = [attr for attr in dir(self)  if not attr.startswith("_") and not callable(self.__getattribute__(attr))]
        values = [self.__getattribute__(attr) for attr in attrs]
        return dict(zip(attrs,values))
    def __loadFromDict(self,data:dict):
        for attr in data.keys():
            self.__setattr__(attr,data[attr])
    @classmethod
    def get(cls):
        if cls._instance == None:
            cls._instance = globalConfig()
        return cls._instance
    
if __name__ == "__main__":
    print(globalConfig.get().configFilePath)
    
    pass