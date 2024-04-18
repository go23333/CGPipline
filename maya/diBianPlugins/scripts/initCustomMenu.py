#coding=utf-8
#Init maya menu

import os
import sys

# 添加包目录
vendroPath = os.path.dirname(__file__).replace('scripts','vendor')
sys.path.insert(0,vendroPath)



import pymel.core as pm

main_window = pm.language.melGlobals['gMainWindow']  #获取主窗口

menu_obj = 'MayaTools'
menu_label = 'MayaTools'
#删除重复的menu
if pm.menu(menu_obj,label=menu_label,exists=True,parent=main_window):
    pm.deleteUI(pm.menu(menu_obj,e=True,deleteAllItems=True))
    
mayaToolsUI = pm.menu(menu_obj,label=menu_label,parent=main_window,tearOff=True)

pm.menuItem(label=u'地编工具',subMenu=True,tearOff=True)
pm.menuItem(label=u'代理工具',command="mayaTools.mayaProxyTool.UIMain()")
pm.menuItem(label=u'自动UV',command="mayaTools.autouv.autouvMain()")
pm.menuItem(label=u'减面工具',command="mayaTools.reduceface.reducefaceMain()")
pm.menuItem(label=u'Unfold工具',command="mayaTools.rizomUVBridge.UI()")
pm.menuItem(label=u'gpuCache工具',command="mayaTools.gpuCacheTool.gpuCacheToolMain()")
pm.menuItem(label=u'NitroPoly建模工具包',command="mayaTools.thirdpart.nitroPoly.main()")

pm.menuItem(label=u'检查模型重复',command="mayaTools.others.checkRepeat()")
pm.menuItem(label=u'检查物体隐藏显示',command="mayaTools.others.checkHidden()")
pm.menuItem(label=u'随机选择面',command="mayaTools.others.randomSelectFaces()")
pm.menuItem(label=u'贴图自动刷新开关',command="mayaTools.others.distableRefreshTextures()")
 


pm.setParent('..',menu=True)
pm.menuItem(label=u'UE流程工具',subMenu=True,tearOff=True)
pm.menuItem(label=u'abc导出工具',command="mayaTools.abcExporter.abcExportToolMain()")
pm.menuItem(label=u'贴图连接',command="mayaTools.connectTexture.ConnectTextureMain()")
pm.menuItem(label=u'相机导出',command="mayaTools.cameraExporter.CameraExporterMain()")
pm.menuItem(label=u'静态网格体导出',command="import module.unreal.collection_textures_combine as ctc;ctc.MayaToUnrealPackUtil()")
pm.menuItem(label=u'毛发导出',command="mayaTools.xgenexporter.xgentoolsMain()")
pm.menuItem(label=u'地编流程工具',command="mayaTools.editPiplineTools.editPiplineToolsMain()")


pm.setParent('..',menu=True)
pm.menuItem(label=u'灯光工具',subMenu=True,tearOff=True)
pm.menuItem(label=u'AO层覆盖',command="mayaTools.mayaProxyTool.aoLayerOverlay()")
pm.setParent('..',menu=True)




otherTools = pm.menu('otherTools',label=u'其他工具',parent=main_window,tearOff=True)
pm.menuItem(label=u'腾讯导出工具',command="import pages\nglobal txExportPage\ntxExportPage = pages.exportPipline()\ntxExportPage.show(dockable=True)")

