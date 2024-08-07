#coding=utf-8
import mayaTools
import pymel.core as pm



def install():
    pm.setParent(mayaTools.menu_id,menu=True)
    pm.menuItem("Pipline",label=u'流程工具',subMenu=True,tearOff=True)

    pm.menuItem(label=u'贴图整理工具',command=TextureArrange)

TextureArrange = """
from mayaTools.pipline.TextureArrange import gui
gui.showUI()
"""