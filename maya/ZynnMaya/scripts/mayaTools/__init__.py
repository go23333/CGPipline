#coding=utf-8
from pkgutil import extend_path
import sys
import os
import functools
import time
from mayaTools.core.log import log
import pymel.core as pm


#判断当前的python版本
PYTHONVERSION = sys.version_info.major
# 确保之后导入mayaTools模块时使用__path__作为路径
__path__ = extend_path(__path__, __name__)
MODELPATH = os.path.dirname(__file__)

def timer_decorator(func):
    """装饰器：记录函数的运行时间"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 记录开始时间
        start_time = time.time()
        
        # 执行被装饰的函数
        result = func(*args, **kwargs)
        
        # 记录结束时间
        end_time = time.time()
        
        # 计算并打印运行时间
        run_time = end_time - start_time
        print(u"函数 {0} 运行时间: {1} 秒".format(func.__name__,run_time))
        
        return result
    
    return wrapper



def install_mayaTools():
    menuID="mayaTools"
    #确保不重复创建
    try:
        pm.deleteUI(menuID)
    except RuntimeError:
        pass
    menuID = pm.menu(menuID,
            parent="MayaWindow",
            tearOff=True,
            allowOptionBoxes=True,
            label=menuID)
    import mayaTools.pipline as pipline
    pipline.install(menuID)
    import mayaTools.lightTools as lightTools
    lightTools.install(menuID)
    import mayaTools.export as export
    export.install(menuID)
    import mayaTools.optimize as optimize
    optimize.install(menuID)
    import mayaTools.editTools as edit
    edit.install(menuID)

def install_rigTools():
    menuID=u"绑定工具"
    #确保不重复创建
    try:
        pm.deleteUI(menuID)
    except RuntimeError:
        pass
    menuID = pm.menu(menuID,
            parent="MayaWindow",
            tearOff=True,
            allowOptionBoxes=True,
            label=menuID)
    import mayaTools.rig as rig
    rig.install(menuID)


def install_modelTools():
    menuID=u"模型工具"
    #确保不重复创建
    try:
        pm.deleteUI(menuID)
    except RuntimeError:
        pass
    menuID = pm.menu(menuID,
            parent="MayaWindow",
            tearOff=True,
            allowOptionBoxes=True,
            label=menuID)
    import mayaTools.model as model
    model.install(menuID)


def install_simTools():
    menuID=u"解算工具"
    #确保不重复创建
    try:
        pm.deleteUI(menuID)
    except RuntimeError:
        pass
    menuID = pm.menu(menuID,
            parent="MayaWindow",
            tearOff=True,
            allowOptionBoxes=True,
            label=menuID)
    import mayaTools.simulation as simulation
    simulation.install(menuID)



def install():
    install_mayaTools()
    install_rigTools()
    install_modelTools()
    install_simTools()
    

def reloadModule(name="mayaTools",*args):
    for mod in sys.modules.copy():
        if mod.startswith(name):
            #log("delete model:{0}".format(mod))
            del sys.modules[mod]

if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
