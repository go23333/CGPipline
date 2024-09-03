#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
import sys


def log(message):
    message = str(message)
    message = getInfos(1) + "\n" + message
    import unreal
    unreal.log(message)
class FakeException(Exception):
    pass
def getInfos(level:int):
    try:
        raise FakeException("this is fake")
    except Exception:
        f = sys.exc_info()[2].tb_frame
    while level >= 0:
        f = f.f_back
        level = level - 1
    infos = ""
    moduleName = f.f_globals["__name__"]
    if moduleName != "__ax_main__":
        infos += moduleName + " | "
    obj = f.f_locals.get("self", None)
    if obj:
        infos += obj.__class__.__name__ + "::"
    functionName = f.f_code.co_name
    if functionName != "<module>":
        infos += functionName + "()"
    # Line Number
    lineNumber = str(f.f_lineno)
    infos += " line " + lineNumber + ""

    if infos:
        infos = "[" + infos + "]"
    return infos


if __name__ == "__main__":
    pass