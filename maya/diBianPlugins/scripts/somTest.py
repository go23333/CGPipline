
import os
from PIL import Image



def GeneratePureColorImage(size,color,path):
    image = Image.new('RGB',size,color)
    image.save(path)

def InvertImage(path):
    image = Image.open(path)
    imvertImage = Image.eval(image,lambda x: 255 -x )
    imvertImage.save(path)
    
def BlendImagesByImage(imageAPath,imageBPath,alphaImagePath,NewPath):
    imageA = Image.open(imageAPath)
    imageB = Image.open(imageBPath)
    alphaImage = Image.open(alphaImagePath)   
    imageA = imageA.resize(alphaImage.size())
    imageB = imageB.resize(alphaImage.size())
    a,_,_,_ = alphaImage.split()
    Image.composite(imageA,imageB,a).save(NewPath)


BlendImagesByImage("E:\Downloads\HuaWei\AnQi_LiuChangYu_Pro_Shade\Texture\JWW_A001_ANQI_Color.1001.png",)