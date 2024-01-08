#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################

import configparser
import CGUtils.uCommon as UC

class unrealConfig():
    configFilePath = ""
    # paramater Camera Import
    CameraImportPathPatten = "/Game/Shots/Sequence/$ep/$sc/$ep_$sc_$number"
    CameraimportUniformScale = 1
    CameraimportAspectRatio = 1.777778
    # paramater Mesh Import
    StaticMeshImportPathPatten = "/Game/Assets/Scene/Mesh/"
    # paramater Texture Import
    TextureImportPathPatten = "/Game/Assets/Scene/Texture/"
    TextureEnableVT = 1 #0:关闭,1:启用,2:自动
    # paramater Material Create
    MaterialInstancePath = "/Game/Assets/Scene/Material/"
    LocalSceneDefaultMaterial = "/Game/Assets/Scene/Common/Material/M_BG_ARM"
    SceneDefaultMaterial = "/ZynnPlugin/Assets/Material/M_BG_ARM"






if __name__ == "__main__":



    # import configparser

    # # 创建一个配置对象
    # config = configparser.ConfigParser()

    # # 写入配置到文件
    # config['Section1'] = {'key1': 'value1', 'key2': 'value2'}
    # config['Section2'] = {'key3': 'value3', 'key4': 'value4'}

    # with open('example.ini', 'w') as configfile:
    #     config.write(configfile)

    # # 从文件读取配置
    # config.read('example.ini')

    # # 获取配置值
    # value1 = config.get('Section1', 'key1')
    # value3 = config.get('Section2', 'key3')

    # print(f"Value1: {value1}")
    # print(f"Value3: {value3}")
    
    pass