#coding=utf-8
from pkgutil import extend_path
import sys

from core.log import log
import menu
# 确保之后导入mayaTools模块时使用__path__作为路径
__path__ = extend_path(__path__, __name__)

self = sys.modules[__name__]
self.menu_id = None

def install():
    self.menu_id = menu.create()


def reloadModule(name="mayaTools",*args):
    for mod in sys.modules.copy():
        if mod.startswith(name):
            log("delete model:{0}".format(mod))
            del sys.modules[mod]

if __name__ == "__main__":
    reloadModule()
