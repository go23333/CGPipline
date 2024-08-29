from pygltflib import GLTF2, Scene,ImageFormat
import os
from PIL import Image
import shutil


class WrapGLB():
    def __init__(self,filePath:str) -> None:
        self.filePath = filePath
        self.glbFileName = os.path.splitext(os.path.basename(self.filePath))[0]
        self.gltf = GLTF2().load(self.filePath)
        self.rootPath = os.path.dirname(self.filePath)
    def ExportAndGetMaterialData(self):
        self.__convertTextures()
        result = []
        TextureRootPath = os.path.join(self.rootPath,"Textures")
        if not os.path.exists(TextureRootPath):
            os.makedirs(TextureRootPath)
        for material in  self.gltf.materials:
            materialName = material.name
            if materialName.endswith(self.glbFileName):
                materialName = materialName.removesuffix("_" + self.glbFileName)
            baseColorTex = material.pbrMetallicRoughness.baseColorTexture
            normalTex = material.normalTexture
            MRTex = material.pbrMetallicRoughness.metallicRoughnessTexture


            baseColorPath = os.path.join(TextureRootPath,f"{materialName}_BaseColor.png")

            if baseColorTex != None:
                oldBaseColorPath = os.path.join(self.rootPath,f"{baseColorTex.index}.png")
                if not os.path.exists(oldBaseColorPath):
                    return False
                shutil.copy(oldBaseColorPath,baseColorPath)
            else:
                color = material.pbrMetallicRoughness.baseColorFactor
                Tex = Image.new("RGB",(64,64),(int(color[0]*255),int(color[1]*255),int(color[2]*255)))
                Tex.save(baseColorPath,"PNG")

            normalPath = os.path.join(TextureRootPath,f"{materialName}_Normal.png")

            if normalTex != None:
                oldNormalPath = os.path.join(self.rootPath,f"{normalTex.index}.png")
                if not os.path.exists(oldNormalPath):
                    return False
                shutil.copy(oldNormalPath,normalPath)
            else:
                Tex = Image.new("RGB",(64,64),(128,128,255))
                Tex.save(normalPath,"PNG")


            RoughnessPath = os.path.join(TextureRootPath,f"{materialName}_Roughness.png")
            MetallicPath = os.path.join(TextureRootPath,f"{materialName}_Metallic.png")

            if MRTex != None:
                oldMRPath = os.path.join(self.rootPath,f"{MRTex.index}.png")
                CompositeImage = Image.open(oldMRPath)
                channels = CompositeImage.split()
                MetallicImage = channels[1]
                RoughnessImage = channels[2]
                RoughnessImage.save(RoughnessPath,"PNG")
                MetallicImage.save(MetallicPath,"PNG")
                CompositeImage.close()
                os.remove(oldMRPath)
            else:
                image = Image.new('L',(64,64),color = 0)
                image.save(MetallicPath,'png')
                image = Image.new('L',(64,64),color = 128)
                image.save(RoughnessPath,'png')

            materialInfo = dict(
                    materialName = materialName,
                    fUDIM = False,
                    type = "PBR",
                    baseColorPaths=[baseColorPath.replace(self.rootPath,"")],
                    roughnessPaths = [RoughnessPath.replace(self.rootPath,"")],
                    metallicPaths = [MetallicPath.replace(self.rootPath,"")],
                    normalPaths = [normalPath.replace(self.rootPath,"")],
                    TextureTiling = (1.0,1.0)
                )
            result.append(materialInfo)
        return result
    def __convertTextures(self):
        self.gltf.convert_images(ImageFormat.FILE,override=True)
        self.gltf.save(self.filePath)
        self.gltf = GLTF2().load(self.filePath)
    def DeleteUseless(self):
        for tex in self.gltf.textures:
            path = os.path.join(self.rootPath,f"{tex.source}.png")
            if os.path.exists(path):
                os.remove(path)
        os.remove(self.filePath)
        
    
            
