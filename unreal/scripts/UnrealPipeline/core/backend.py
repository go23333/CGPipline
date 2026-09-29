import requests
from UnrealPipeline.core.Config import globalConfig as Config


class Backend():
    instance = None
    def __init__(self):
        self.backendAddress = "http://192.168.3.20:5050"
        #self.backendAddress = "http://127.0.0.1:5050"
        pass
    def isBackendAvailable(self) -> bool:
        try:
            response = requests.get(self.backendAddress)
            return True
        except:
            return False
    def getCategories(self):
        response = requests.get(self.backendAddress +"/config/category")
        return response.json()
    def getAssetRootPath(self):
        response = requests.get(self.backendAddress +"/config/assetsLibraryPath")
        return response.json()["uri"]
    def getAssetsCount(self):
        response = requests.get(self.backendAddress +"/assets/count")
        return response.json()
    def addAssetToDB(self,asset:dict):
        response = requests.post(self.backendAddress +"/assets/add",json=asset)
        return response.text
    def getAsset(self,assetID:str):
        response = requests.get(self.backendAddress +f"/assets/{assetID}")
        if response.text != "false":
            return response.json()
        else:
            return False
    @classmethod
    def Get(cls):
        if cls.instance is None:
            cls.instance = Backend()
        return cls.instance
    