#coding=utf-8
import mayaTools
import pymel.core as pm



def install():
    pm.setParent(mayaTools.menu_id,menu=True)
    pm.menuItem("thirdpart",label=u'其他脚本',subMenu=True,tearOff=True)

