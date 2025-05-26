#coding=utf-8
import pymel.core as pm


def install(menu_id):
    pm.setParent(menu_id,menu=True)
    pm.menuItem("LightTool",label=u'灯光工具',subMenu=True,tearOff=True)

    pm.menuItem(label=u'添加AO层',command=commandAoLayer)
    pm.menuItem(label=u'添加Rim层 ',command=commandRimLayer)




commandAoLayer = 'from mayaTools.core.uMaya import addCutomAOV;addCutomAOV("RedshiftAmbientOcclusion","custom_AO")'
commandRimLayer = 'from mayaTools.core.uMaya import addCutomAOV;addCutomAOV("RedshiftFresnel","custom_Rim")'