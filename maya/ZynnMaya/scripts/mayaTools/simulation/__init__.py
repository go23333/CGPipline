# -*-coding:utf-8 -*-
import mayaTools
import pymel.core as pm

def install(menu_id):
    pm.setParent(menu_id,menu=True)
    pm.menuItem(label=u'毛发解算属性批量编辑',command=hair_batch_edit)




hair_batch_edit = """
from mayaTools.simulation.batch_edit.gui import show;show()
"""
if __name__ == "__main__":
    from mayaTools import reloadModule,MODELPATH
    reloadModule()
    print(MODELPATH)