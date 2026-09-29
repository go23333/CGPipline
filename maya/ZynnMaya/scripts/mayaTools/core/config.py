import os
import json



class Config:
    instance = None
    def __init__(self):
        self.localAssetLibraryFolder = os.path.join(os.environ['USERPROFILE'], 'Documents',"MyBridge")
        self.localTempFolder = os.path.join(self.localAssetLibraryFolder,"Temp")
        self.localConfigSavePath = os.path.join(self.localAssetLibraryFolder,"config.json")
        self.backendAddress = "http://192.168.3.20:5050"
    @classmethod
    def get(cls):
        if not cls.instance:
            cls.instance = cls()
        return cls.instance