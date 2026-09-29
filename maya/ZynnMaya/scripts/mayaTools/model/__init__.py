# -*-coding:utf-8 -*-
import pymel.core as pm


def install(menu_id):
    pm.setParent(menu_id,menu=True)
    pm.menuItem(label=u'nitropoly',command=nitropoly)

nitropoly = """
from mayaTools.model.nitroPoly.nitroPoly import main
main()
"""