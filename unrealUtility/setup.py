#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################


from distutils.core import setup
from Cython.Build import cythonize

files = ["uUnreal.py","uGlobalConfig.py","uCommon.py","ShowWindow.py","Pages.py","initMenu.py"]

for file in files:
    setup(
        name='UC_',
        ext_modules=cythonize(file),
    )
