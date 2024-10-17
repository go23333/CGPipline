#coding=utf-8
import pymel.core as pm



def install(menu_id):
    pm.setParent(menu_id,menu=True)
    pm.menuItem("Pipline",label=u'流程工具',subMenu=True,tearOff=True)
    pm.menuItem(label=u'贴图整理工具',command=TextureArrange)
    pm.menuItem(label=u'贴图连接工具',command=connectTexture)
    pm.menuItem(label=u'地编用工具',command=edittools)


TextureArrange = """
from mayaTools.pipline.TextureArrange import gui
gui.showUI()
"""

connectTexture = """
from mayaTools.pipline.connectTexture import gui
gui.showUI()
"""

edittools = """
from mayaTools.pipline.editPiplineTools import gui
gui.showUI()
"""