import unreal
import os



from Qt import QtCore
from Qt import QtWidgets

import uUnreal as UU
import uCommon as UC
import uGlobalConfig as UG
import Pages

from dayu_widgets.push_button import MPushButton
from dayu_widgets.push_button import MPushButton
from dayu_widgets.combo_box import MComboBox

import functools
from importlib import reload
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

print('ScenesFolder')


class ScenesMeshImporter(QtWidgets.QWidget):
    fbx_name=''
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("场景模型导入")
        self.resize(600,400)
        self.__init_ui()
    def __init_ui(self):

        layMain = QtWidgets.QVBoxLayout()   #定义主布局

        self.folderSelectGroup = Pages.folderSelectGroup("网格体文件路径:") #定义路径选择组

        self.wCamera = Pages.DateTableView(UC.CameraHeader)  #定义相机数据表格

        context_menu = self.wCamera.MakeContexMenu()   # 获取相机表格的上下文菜单并自定义
        maImportSelectedItems = context_menu.addAction("导入选中项目")
        maImportSelectedItems.triggered.connect(
            functools.partial(self.importCameras,True)
            )
        self.folderSelectGroup.setOnTextChanged(self.wCamera.fetchCamera)        # 文字框改变时刷新

        layImport = QtWidgets.QHBoxLayout()  #用于防止导入按钮的布局
        btnImport = MPushButton("场景模型导入并创建对应文件夹")
        btnImport.clicked.connect(
            functools.partial(self.importCameras,False)
            )
        cbSceneName = MComboBox()
        cbSceneName.setDisabled(True)

        layImport.addWidget(cbSceneName,alignment=QtCore.Qt.AlignLeft)
        layImport.addWidget(btnImport,alignment=QtCore.Qt.AlignRight)
        # 依次添加布局
        layMain.addLayout(self.folderSelectGroup)
        layMain.addWidget(self.wCamera)
        layMain.addLayout(layImport)
        self.setLayout(layMain)
    def closeEvent(self, event):
        return super().closeEvent(event)
    def showEvent(self, event):
        return super().showEvent(event)
    def importCameras(self,selected):
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
        self.importStaticmeshs(waitImportedQueue,self.fbx_name)

    def scenesCreate(self):
        sub_level_names=['_Shade','_Shade_Light','_Shade_VFX']
        basefloder_names=['/Map/Level','/Common','/Material','/Mesh','/Other','/BP','/VFX','/Texture']
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')
        #获取FBX路径
        fbx_path=self.folderSelectGroup.getFolderPath()
        #获取FBX名称
        fbx=os.listdir(fbx_path)[0]
        
        self.fbx_name=fbx.rsplit('_BG',1)[0]
        fbx_create_path='/Game/Assets/Scenes/'+self.fbx_name+'/Mesh'

        #创建基础文件夹
        for basefloder_name in basefloder_names:
            unreal.EditorAssetLibrary.make_directory('/Game/Assets/Scenes/'+self.fbx_name+basefloder_name)
        #创建主关卡
        if not unreal.EditorAssetSubsystem().does_asset_exist('/Game/Assets/Scenes/'+self.fbx_name+'/Map/'+self.fbx_name+'_Main'):
            unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=self.fbx_name+'_Main',package_path='/Game/Assets/Scenes/'+self.fbx_name+'/Map',asset_class=unreal.World,factory=unreal.WorldFactory())
        #创建子关卡
        for sub_level_name in sub_level_names:
            if not unreal.EditorAssetSubsystem().does_asset_exist('/Game/Assets/Scenes/'+self.fbx_name+'/Map/Level/'+self.fbx_name+sub_level_name):
                unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=self.fbx_name+sub_level_name,package_path='/Game/Assets/Scenes/'+self.fbx_name+'/Map/Level',asset_class=unreal.World,factory=unreal.WorldFactory())
        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')



    def importStaticmeshs(self,datas:list,fbx_name,sceneName=None):

        self.StaticMeshImportPathPatten ="/Game/Assets/Scenes/%s/Mesh/"%fbx_name
        # paramater Texture Import
        self.TextureImportPathPatten = "/Game/Assets/Scenes/%s/Texture/"%fbx_name
        # paramater Material Create
        self.MaterialInstancePath = "/Game/Assets/Scenes/%s/Material/"%fbx_name
        self.LocalSceneDefaultMaterial = "/Game/Assets/Scenes/%s/Common/Material/M_BG_ARM"%fbx_name
        self.SceneDefaultMaterial = "/ZynnPlugin/Assets/Material/M_BG_ARM"
        

        UU.saveAll()          # 保存所有资产,防止导入过程中崩溃
        UU.duplicate_asset(self.SceneDefaultMaterial,self.LocalSceneDefaultMaterial)
        wrapMaterial = UU.WrapMaterial(unreal.load_asset(self.LocalSceneDefaultMaterial))
        for data in datas: # 遍历所有传入的资产数据
            name = data["name"]
            path = data["path"]
            parseReslut = UC.parseStaticMeshName(name,sceneName)
            destinationPath = UC.applyMacro(self.StaticMeshImportPathPatten,parseReslut)
            wrapSM = UU.WrapStaticMesh.importFromFbx(path,destinationPath,1) #导入静态网格体
            JsonPath = path.replace('.fbx','.json')
            Json_file = UC.ReadJsonFile(JsonPath)
            MaterialInfoList = UC.analyseJson(Json_file)
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

                if TexturePath['refl_roughness'] == None:
                    ARMSPath = TexturePath['refl_metalness']
                else:
                    ARMSPath = TexturePath['refl_roughness']
                WrapARMS = self.textureImport(ARMSPath)
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
        wrapTex = UU.WrapTexture.importTexture( texturePaths[0],self.TextureImportPathPatten)
        if len(texturePaths) == 1:
            return wrapTex
        if not (wrapTex.setVTEnable(UG.globalConfig.get().TextureEnableVT) and UG.globalConfig.get().TextureEnableVT):
            UC.ConvertTexture.resizerTextures(texturePaths)
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