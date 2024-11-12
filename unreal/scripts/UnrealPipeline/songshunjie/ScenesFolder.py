import unreal
import os

from Qt import QtCore
from Qt import QtWidgets

import UnrealPipeline.core.UnrealHelper as UU
import UnrealPipeline.core.utilis as util
import UnrealPipeline.core.Config as UC
from UnrealPipeline.core.CommonWidget import folderSelectGroup,DateTableView

from dayu_widgets.push_button import MPushButton
from dayu_widgets.push_button import MPushButton
from dayu_widgets.label import MLabel
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.line_tab_widget import MLineTabWidget
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

import functools
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

print('ScenesFolder1.1')


class ScenesMeshImporter(QtWidgets.QWidget):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("场景模型导入")
        self.resize(600,400)
        self.__init_ui()
    def __init_ui(self):

        layMain = QtWidgets.QVBoxLayout()   #定义主布局

        self.folderSelectGroup = folderSelectGroup("网格体文件路径:") #定义路径选择组
        self.wCamera = DateTableView(util.CameraHeader)  #定义相机数据表格

        self.folderSelectGroup.setOnTextChanged(self.wCamera.fetchCamera)        # 文字框改变时刷新
        self.folderSelectGroup.setOnTextChanged(self.importName)  

        layImport = QtWidgets.QVBoxLayout() 

        lay_scene = QtWidgets.QVBoxLayout()
        lay_pro = QtWidgets.QVBoxLayout()
        #创建抽屉
        btn_tab=MLineTabWidget(alignment=QtCore.Qt.AlignLeft)
        #创建放到抽屉的盒子
        box_scene=QtWidgets.QGroupBox()
        box_scene.setStyleSheet('QGroupBox{color:white;border:0px ;}')
        box_pro=QtWidgets.QGroupBox()
        box_pro.setStyleSheet('QGroupBox{color:white;border:0px ;}')

        #场景box
        self.scene_name_text=MLineEdit().medium()
        self.scene_name_text.setPlaceholderText(self.tr("输入资产名称"))

        scene_btn = MPushButton("场景模型导入并创建对应文件夹")
        scene_btn.clicked.connect(
            functools.partial(self.importScenes,False)
            )
        self.error_lable=MLabel('')
        self.error_lable.setStyleSheet("color: red")
        lay_scene.addWidget(self.scene_name_text)
        lay_scene.addWidget(self.error_lable)
        lay_scene.addWidget(scene_btn,alignment=QtCore.Qt.AlignRight)

        box_scene.setLayout(lay_scene)

        #道具box
        lay_pro_edit = QtWidgets.QHBoxLayout()
        self.pro_name_text=MLineEdit().medium()
        self.pro_name_text.setPlaceholderText(self.tr("输入资产名称"))

        self.ep_text=MLineEdit().medium()
        self.ep_text.setPlaceholderText(self.tr("输入集数"))

        lay_pro_edit.addWidget(self.ep_text)
        lay_pro_edit.addWidget(self.pro_name_text)

        

        pro_btn = MPushButton("道具模型导入并创建对应文件夹")
        pro_btn.clicked.connect(
            functools.partial(self.importPro,False)
            )
        
        lay_pro.addLayout(lay_pro_edit)
        lay_pro.addWidget(self.error_lable)
        lay_pro.addWidget(pro_btn,alignment=QtCore.Qt.AlignRight)

        box_pro.setLayout(lay_pro)
        #创建抽屉名称
        btn_tab.add_tab(box_scene,{"text": "场景"})
        btn_tab.add_tab(box_pro,{"text": "道具"})

        layImport.addWidget(btn_tab)

        # 依次添加布局
        layMain.addLayout(self.folderSelectGroup)
        layMain.addWidget(self.wCamera)

        layMain.addLayout(layImport)

        self.setLayout(layMain)
    def closeEvent(self, event):
        return super().closeEvent(event)
    def showEvent(self, event):
        return super().showEvent(event)
    def importScenes(self,selected):
        
            waitImportedQueue = []
            if selected:
                for name in self.wCamera.getSelectNames():
                    for data in self.wCamera.datas:
                        if data["name"] == name:
                            waitImportedQueue.append(data)
            else:
                for data in self.wCamera.datas:
                    if not data["imported"]:
                        waitImportedQueue.append(data)
            self.scenesCreate()
            self.importStaticmeshs(waitImportedQueue)
        

    def importPro(self,selected):
        
            waitImportedQueue = []
            if selected:
                for name in self.wCamera.getSelectNames():
                    for data in self.wCamera.datas:
                        if data["name"] == name:
                            waitImportedQueue.append(data)
            else:
                for data in self.wCamera.datas:
                    if not data["imported"]:
                        waitImportedQueue.append(data)
            self.proCreate()
            self.importStaticmeshs(waitImportedQueue)

        

    def importName(self):
        
        #获取文件名称
        fbx_path=self.folderSelectGroup.getFolderPath()
        fbx=os.listdir(fbx_path)[0]
        #判断规则
        if '_BG' in fbx:
            fbx_name=fbx.rsplit('_BG',1)[0]   
            self.scene_name_text.setText(fbx_name)
        else:  
            fbx_name=fbx.rsplit('.',1)[0] 
            self.pro_name_text.setText(fbx_name)
        
        



    def scenesCreate(self):
        sub_level_names=['_Shade','_Shade_Light','_Shade_VFX']
        basefloder_names=['/Map/Level','/Common','/Material','/Mesh','/Other','/BP','/VFX','/Texture']
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')

        scene_name= self.scene_name_text.text()

        #创建基础文件夹
        for basefloder_name in basefloder_names:
            unreal.EditorAssetLibrary.make_directory('/Game/Assets/Scenes/'+scene_name+basefloder_name)
        #创建主关卡
        if not unreal.EditorAssetSubsystem().does_asset_exist('/Game/Assets/Scenes/'+scene_name+'/Map/'+scene_name+'_Main'):
            main_level=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=scene_name+'_Main',package_path='/Game/Assets/Scenes/'+scene_name+'/Map',asset_class=unreal.World,factory=unreal.WorldFactory())
        #创建子关卡
        for sub_level_name in sub_level_names:
            if not unreal.EditorAssetSubsystem().does_asset_exist('/Game/Assets/Scenes/'+scene_name+'/Map/Level/'+scene_name+sub_level_name):
                sub_level=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=scene_name+sub_level_name,package_path='/Game/Assets/Scenes/'+scene_name+'/Map/Level',asset_class=unreal.World,factory=unreal.WorldFactory())
                unreal.EditorLevelUtils().add_level_to_world(main_level,level_package_name=sub_level.get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')
        #生成路径
        self.StaticMeshImportPathPatten ="/Game/Assets/Scenes/%s/Mesh/"%scene_name
        # paramater Texture Import
        self.TextureImportPathPatten = "/Game/Assets/Scenes/%s/Texture/"%scene_name
        # paramater Material Create
        self.MaterialInstancePath = "/Game/Assets/Scenes/%s/Material/"%scene_name
        self.LocalSceneDefaultMaterial = "/Game/Assets/Scenes/%s/Common/Material/M_ARM_VT"%scene_name
        self.SceneDefaultMaterial = "/ZYNNPlugins/Assets/Material/M_ARM_VT"
        self.error_lable.setText('') 



    def proCreate(self):
        #获取FBX名称
        pro_name=self.pro_name_text.text()
        #获取ep名称
        ep=self.ep_text.text()
        #设置名称列表
        basefloder_names=['/Material','/Mesh','/Texture']
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')

        #创建基础文件夹
        for basefloder_name in basefloder_names:
            unreal.EditorAssetLibrary.make_directory('/Game/Assets/Pro/'+ep+'/'+pro_name+basefloder_name)
        

        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')
        #生成路径
        self.StaticMeshImportPathPatten ='/Game/Assets/Pro/'+ep+'/'+pro_name+'/Mesh/'
        # paramater Texture Import
        self.TextureImportPathPatten = '/Game/Assets/Pro/'+ep+'/'+pro_name+'/Texture/'
        # paramater Material Create
        self.MaterialInstancePath = '/Game/Assets/Pro/'+ep+'/'+pro_name+'/Material/'
        self.LocalSceneDefaultMaterial ='/Game/Assets/Pro/'+ep+'/'+pro_name+'/Common/Material/M_ARM_VT'
        self.SceneDefaultMaterial = "/ZYNNPlugins/Assets/Material/M_ARM_VT"
        self.error_lable.setText('') 

        

    def parseStaticMeshName(self,name,sceneName):
        parseResult = {}
        parseResult["name"] = name
        if sceneName:
            parseResult["scenename"] = sceneName
        return parseResult

    def importStaticmeshs(self,datas:list,sceneName=None):

        UU.saveAll()          # 保存所有资产,防止导入过程中崩溃
        # UU.duplicate_asset(self.SceneDefaultMaterial,self.LocalSceneDefaultMaterial)
        wrapMaterial = UU.WrapMaterial(unreal.load_asset(self.SceneDefaultMaterial))
        for data in datas: # 遍历所有传入的资产数据
            name = data["name"]
            path = data["path"]
            parseReslut = util.parseStaticMeshName(name,sceneName)
            # parseReslut = self.parseStaticMeshName(name,sceneName)
            destinationPath = util.applyMacro(self.StaticMeshImportPathPatten,parseReslut)
            wrapSM = UU.WrapStaticMesh.importFromFbx(path,destinationPath,1) #导入静态网格体
            JsonPath = path.replace('.fbx','.json')
            Json_file = util.ReadJsonFile(JsonPath)
            MaterialInfoList = util.analyseJson(Json_file)
            for MaterialInfo in MaterialInfoList:
                # 判断是否创建材质
                if not MaterialInfo['CreateMaterial']:
                    continue
                wrapMaterialIns = UU.WrapMaterialInstance.create(self.MaterialInstancePath + MaterialInfo["Materialname"])
                wrapMaterialIns.setParent(wrapMaterial.asset)
                TexturePath = MaterialInfo['TexturePath']
                if TexturePath['diffuse_color'] != None:
                    wrapBaseColor = self.textureImport(TexturePath['diffuse_color'])
                    wrapBaseColor.setAsColor()
                    wrapBaseColor.setVTEnable(True)
                    wrapBaseColor.saveAsset()
                    wrapMaterialIns.setTextureParameter("BaseColor_Map",wrapBaseColor.asset)
                    print("BaseColor_Map")

                if TexturePath['refl_roughness'] == None:
                    ARMSPath = TexturePath['refl_metalness']
                else:
                    ARMSPath = TexturePath['refl_roughness']
                WrapARMS = self.textureImport(ARMSPath)
                UU.saveAll()
                WrapARMS.setAsLinerColor()
                WrapARMS.setVTEnable(True)
                WrapARMS.saveAsset()
                wrapMaterialIns.setTextureParameter("ARMS_Map",WrapARMS.asset)
                
                
                if TexturePath['bump_input'] != None:
                    wrapNormal = self.textureImport(TexturePath['bump_input'])
                    wrapNormal.setAsNormal()
                    wrapNormal.setVTEnable(True)
                    wrapNormal.saveAsset()
                    wrapMaterialIns.setTextureParameter("Normal_Map",wrapNormal.asset)

                if TexturePath['emission_color'] != None:
                    WrapEmissive = self.textureImport(TexturePath['emission_color'])
                    WrapEmissive.setAsColor()
                    WrapEmissive.setVTEnable(True)
                    WrapEmissive.saveAsset()
                    wrapMaterialIns.setTextureParameter("Emmissive_Map",wrapNormal.asset)
                    wrapMaterialIns.setScalarParameter("自发光强度",1.0)
                wrapMaterialIns.saveAsset()
                wrapSM.setMaterialBySloatName(MaterialInfo["Materialname"],wrapMaterialIns.asset)
            wrapSM.saveAsset()

    def textureImport(self,texturePaths:list):
        UU.saveAll()          # 保存所有资产,防止导入过程中崩溃
        wrapTex = UU.WrapTexture.importTexture( texturePaths[0],self.TextureImportPathPatten)
        if len(texturePaths) == 1:
            return wrapTex
        if not (wrapTex.setVTEnable(UC.globalConfig.get().TextureEnableVT) and UC.globalConfig.get().TextureEnableVT):
            util.ConvertTexture.resizerTextures(texturePaths)
            wrapTex = UU.WrapTexture.importTexture(texturePaths[0],self.TextureImportPathPatten)
        return wrapTex




def start():
    with application() as app:
        global test
        test = ScenesMeshImporter()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   with application() as app:
        global test
        test = ScenesMeshImporter()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))