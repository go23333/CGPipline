#coding=utf-8
import pymel.core as pm



def install(menu_id):
    pm.setParent(menu_id,menu=True)
    pm.menuItem("Pipline",label=u'流程工具',subMenu=True,tearOff=True)
    pm.menuItem(label=u'贴图整理工具',command=TextureArrange)
    pm.menuItem(label=u'贴图连接工具',command=connectTexture)
    pm.menuItem(label=u'地编用工具',command=edittools)
    pm.menuItem(label=u'UDIM拆分工具',command=udimSplit)
    pm.menuItem(label=u'布料解算BS烘焙工具',command=blendShapeBake)
    pm.menuItem(label=u'BS连接骨骼工具',command=bsToJoin)


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



udimSplit = """
from mayaTools.pipline.udimSplit import gui
gui.showUI()
"""

blendShapeBake = """
from mayaTools.pipline.blendShapeBake import gui
gui.showUI()
"""

bsToJoin = """
from mayaTools.pipline.bsToJoin import gui
gui.showUI()
"""