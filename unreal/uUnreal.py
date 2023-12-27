#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################
import unreal
from CGUtils.uCommon import log_function_call
import time

# 函数
    
def unrealLog(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log(logstring)

def unrealLogWarning(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log_warning(logstring)

def unrealLogError(category:str,text:str):
    logstring = f"[{category}] {time.asctime(time.localtime(time.time()))}:{text}"
    unreal.log_error(logstring)


@log_function_call
def appendWindowToUnreal(winID:int):
    unrealLog("ZynnPipline",f"窗口{winID}已经注册到引擎中")
    unreal.parent_external_window_to_slate(winID)



