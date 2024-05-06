#coding=utf-8
import mayaTools
import pymel.core as pm



def install():
    pm.setParent(mayaTools.menu_id,menu=True)
    pm.menuItem("optimize",label=u'优化工具',subMenu=True,tearOff=True)


    pm.menuItem(label=u'GPU缓存工具',command=commandGpuCache)
    pm.menuItem(label=u'减面工具 ',command=commandreduceface)
    pm.menuItem(label=u'代理工具 ',command=commandProxyTools)


commandGpuCache = """
from mayaTools.optimize.gpuCacheTool import gui
gui.showUI()
"""
commandreduceface = """
from mayaTools.optimize.reduceface import gui
gui.showUI()
"""
commandProxyTools = """
from mayaTools.optimize.mayaProxyTool import gui
gui.showUI()
"""