#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################

import sys
from importlib import reload

paths = [r"D:\Documents\ZCXCode\CGPipline\CustomLib",r"d:\Documents\ZCXCode\CGPipline\unreal",r"C:\ProgramData\anaconda3\envs\unreal53\Lib\site-packages"]

for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import main
reload(main)
main.test()
