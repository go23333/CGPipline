# -*-coding:utf-8 -*-
import pymel.core as pm

def install(menu_id):
    pm.setParent(menu_id,menu=True)
    pm.menuItem(label=u'自由IK',command=freeik)
    pm.menuItem(label=u'adPose',command=adpose)
    pm.menuItem(label=u'bezierWeight',command=bezierWeight)
    pm.menuItem(label=u'批量权重导入导出', command=batchWeightIO)
    pm.menuItem(label=u'权重导入导出', command=weightsIO)
    pm.menuItem(label=u'选择有两个根骨骼的模型', command=selectTowJointModel)
    pm.menuItem(label=u'导入ADV面板', command=adv_panel)
    pm.menuItem(label=u'传递材质', command=transfer_material)
    pm.menuItem(label=u'自动保存SK', command=auto_save_sk)

transfer_material = """
from mayaTools.rig.transfer_material.gui import show;show()
"""

freeik = """
from mayaTools.rig.freefk.gui import showUI
showUI()
"""

adpose = """
from  mayaTools.rig.adPose.ui import  show_in_maya
show_in_maya()
"""
bezierWeight = """
from mayaTools.rig.bezierWeight.ui import show
show()
"""

batchWeightIO = """
from  mayaTools.rig.batchWeightsIO.JJweights import UI_JJweights
UI_JJweights()
"""

weightsIO = """
from mayaTools.rig.weightsIO.skinClusterWeight import win
win()"""

selectTowJointModel = """
from  mayaTools.core.mayaLibrary import select_model_inf_by_two_joint
select_model_inf_by_two_joint()
"""

adv_panel = """
from mayaTools.rig.MHBridgeToADV.gui import show
show()
"""

auto_save_sk = """
from mayaTools.rig.autoSaveSk import gui
gui.main()
"""

if __name__ == "__main__":
    from mayaTools import reloadModule,MODELPATH
    reloadModule()
    print(MODELPATH)