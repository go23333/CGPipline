#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################

import configparser
import CGUtils.uCommon as UC

class GlobalConfig():
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.configFilePaht = ""
        # paramater Camera Import
        self.CameraImportPathPatten = "/Game/Shots/Sequence/$ep/$sc/$ep_$sc_$number"
        self.CameraimportUniformScale = 1
        self.CameraimportAspectRatio = 1.777778
    def loadConfigFromFile(self):
        pass
    def saveConfigFIle(self):
        pass

global globalConfig
globalConfig = GlobalConfig()


if __name__ == "__main__":
    import configparser

    # 创建一个配置对象
    config = configparser.ConfigParser()

    # 写入配置到文件
    config['Section1'] = {'key1': 'value1', 'key2': 'value2'}
    config['Section2'] = {'key3': 'value3', 'key4': 'value4'}

    with open('example.ini', 'w') as configfile:
        config.write(configfile)

    # 从文件读取配置
    config.read('example.ini')

    # 获取配置值
    value1 = config.get('Section1', 'key1')
    value3 = config.get('Section2', 'key3')

    print(f"Value1: {value1}")
    print(f"Value3: {value3}")
    
    pass