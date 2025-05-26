#coding=utf-8
import pymel.core as pm

from mayaTools.core.iconManage import IconManage





def install(menu_id):
    pm.setParent(menu_id,menu=True)
    pm.menuItem("EditTools",label=u'地编常用工具',subMenu=True,tearOff=True)

    pm.menuItem(label=u'Unfold',command=unfoldTool,image=IconManage.Unfold())





unfoldTool = """
from mayaTools.editTools.unfold import gui
gui.showUI()
"""