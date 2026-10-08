# coding: utf-8
import os.path
import sys
from .core.Log import Log
logger = Log.get().getLogger("app")
logger.setLevel(Log.Level.debug)



ISPACKED = getattr(sys,'frozen',False)
def update_rc_file():
    logger.info("当前环境:开发,编译qrc文件为py文件")
    import os
    qrc_file = r'app\resource\resource.qrc'
    output_file = r'app\resource\resource_rc.py'
    cmd = f'pyrcc5 {qrc_file} -o {output_file}'
    os.system(cmd)


if not ISPACKED:
    update_rc_file()
    ROOT_PATH = os.path.dirname(__file__).removesuffix("\\app")
else:
    ROOT_PATH = os.path.dirname(__file__).removesuffix("\\_internal\\app")
