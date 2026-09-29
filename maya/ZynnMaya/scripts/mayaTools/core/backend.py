#coding=utf-8
import requests
import os
import json

from mayaTools.core.config import Config

class Backend:
    instance = None
    def __init__(self):
        self.backendAddress = Config.get().backendAddress
        self.localAssetLibraryFolder = os.path.join(os.environ['USERPROFILE'], 'Documents',"MyBridge")
        self.localConfigSavePath = os.path.join(self.localAssetLibraryFolder,"config.json")
    def isBackendAvailable(self):
        try:
            response = requests.get(self.backendAddress)
            return True
        except:
            return False
    def getCategories(self):
        response = requests.get(self.backendAddress+"/config/category")
        return response.json()
    def getAssetRootPath(self):
        response = requests.get(self.backendAddress+"/config/assetsLibraryPath")
        return str(response.json()["uri"])
    def addAssetToDB(self,asset):
        response = requests.post(self.backendAddress+"/assets/add",json=asset)
        return response.text
    def getAssetID(self):
        response = requests.get(self.backendAddress+"/assets/assetsID")
        return response.json()["assetID"]
    def getAssetsCount(self):
        response = requests.get(self.backendAddress+"/assets/count")
        return response.json()
    @classmethod
    def Get(cls):
        if cls.instance is None:
            cls.instance = Backend()
        return cls.instance


if __name__ == "__main__":
    # from mayaTools import reloadModule
    # reloadModule()
    print(Backend().Get().backendAddress)