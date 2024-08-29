import fbx

def CreateManager():
    manager= fbx.FbxManager.Create()
    ios = fbx.FbxIOSettings.Create(manager, fbx.IOSROOT)
    manager.SetIOSettings(ios)
    return manager

def apply_material_to_node(node, material):
    node_attribute = node.GetNodeAttribute()
    if node_attribute and node_attribute.GetAttributeType() == fbx.FbxNodeAttribute.eMesh:
        node.RemoveAllMaterials()
        pMesh = node.GetMesh()
        pMesh.InitMaterialIndices(fbx.FbxLayerElement.eAllSame)
        node.AddMaterial(material)
    # 遍历子节点
    for i in range(node.GetChildCount()):
        apply_material_to_node(node.GetChild(i), material)
def CreateMaterial(manager,name):
    material = fbx.FbxSurfacePhong.Create(manager, name)
    material.Diffuse.Set(fbx.FbxDouble3(1.0, 0.0, 0.0))  # 设置漫反射颜色为红色
    material.Specular.Set(fbx.FbxDouble3(1.0, 1.0, 1.0))  # 设置高光颜色为白色
    material.Shininess.Set(50.0)  # 设置光泽度
    return material
class FbxSceneLoader():
    def __init__(self,manager,SceneName = "MyScene") -> None:
        self.manager = manager
        self.scene = fbx.FbxScene.Create(self.manager,SceneName)
    def importFormFile(self,path:str):
        importer = fbx.FbxImporter.Create(self.manager, "")
        if not importer.Initialize(path, -1, self.manager.GetIOSettings()):
            print("Error: Unable to import file.")
            exit()
        if not importer.Import(self.scene):
            print("Error: Unable to import scene.")
            exit()
        importer.Destroy()
    def SetMaterial(self,material):
        root_node = self.scene.GetRootNode()
        if root_node:
            for i in range(root_node.GetChildCount()):
                apply_material_to_node(root_node.GetChild(i), material)
    def SaveScene(self,path):
        exporter = fbx.FbxExporter.Create(self.manager, "")
        if not exporter.Initialize(path, -1,self.manager.GetIOSettings()):
            print("Error: Unable to export file.")
            exit()
        if not exporter.Export(self.scene):
            print("Error: Unable to export scene.")
            exit()
        exporter.Destroy()



if __name__ == "__main__":
    manager = CreateManager()
    Scene = FbxSceneLoader(manager,"Test")
    Scene.importFormFile("d:\Desktop\SM_BLD_balcony_v02_01.FBX")
    m = CreateMaterial(manager,"Test")
    Scene.SetMaterial(m)
    Scene.SaveScene("d:\Desktop\SM_BLD_balcony_v02_01_out.FBX")

    manager.Destroy()



