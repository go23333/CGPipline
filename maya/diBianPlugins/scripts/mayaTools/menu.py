#coding=utf-8

import pymel.core as pm

menuID = "mayaTools"

def create(menuID=menuID):
    #确保不重复创建
    if pm.menu(menuID, exists=True):
        pm.deleteUI(menuID)
    menuID = pm.menu(menuID,
            parent="MayaWindow",
            tearOff=True,
            allowOptionBoxes=True,
            label=menuID)
    return menuID