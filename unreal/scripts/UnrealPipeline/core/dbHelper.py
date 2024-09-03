#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
from tinydb import TinyDB,Query

class WrapDB():
    def __init__(self,path) -> None:
        self.db = TinyDB(path)

class HWProjectDB(WrapDB):
    instance = None
    def __init__(self) -> None:
        self.filePath = "S:\HuaWeiDB\db.json"
        super().__init__(self.filePath)
    def insert(self,data):
        self.db.insert({"fullName":data})
    def query(self,data):
        user = Query()
        return(self.db.search(user.fullName == data))
    def uniqueInsert(self,data):
        if self.query(data) == []:
            self.insert(data)
    @classmethod
    def Get(cls):
        if cls.instance == None:
            cls.instance = HWProjectDB()
        return cls.instance
    def Destory(self):
        self.instance.db.close()
        self.instance = None
    def close(self):
        self.instance.db.close()
    def __del__(self):
        self.Destory()
