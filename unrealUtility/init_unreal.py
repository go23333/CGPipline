#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
import getpass
import sys

user_name = getpass.getuser()
if user_name == 'zhaocunxi':
    paths = [r"d:\Documents\ZCXCode\CGPipline\unreal",r"C:\ProgramData\anaconda3\envs\unreal53\Lib\site-packages"]
else:
    paths = [r"O:\ZynnPlugins\CGPipline\unreal",r"O:\ZynnPlugins\site-packages\Unreal"]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import initMenu