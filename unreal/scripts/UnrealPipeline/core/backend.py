import requests
from UnrealPipeline.core.Config import globalConfig as Config
import json


class Backend():
    instance = None
    def __init__(self):
        pass
    def isBackendAvailable(self) -> bool:
        try:
            response = requests.get(Config.get().backendAddress)
            return True
        except:
            return False
    def getCategories(self):
        response = requests.get(Config.get().backendAddress+"/config/category")
        return response.json()
    def getAssetRootPath(self):
        response = requests.get(Config.get().backendAddress+"/config/assetsLibraryPath")
        return response.json()["uri"]
    def getAssetsCount(self):
        response = requests.get(Config.get().backendAddress+"/assets/count")
        return response.json()
    def addAssetToDB(self,asset:dict):
        response = requests.post(Config.get().backendAddress+"/assets/add",json=asset)
        return response.text
    def getAsset(self,assetID:str):
        response = requests.get(Config.get().backendAddress+f"/assets/{assetID}")
        if response.text != "false":
            return response.json()
        else:
            return False
    @classmethod
    def Get(cls):
        if cls.instance is None:
            cls.instance = Backend()
        return cls.instance
    