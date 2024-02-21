#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
# version: 2.7.18
##################################################################
from imp import reload

import Pages
reload(Pages)

extrenalWindow = []

def test():
    page = Pages.exportPipline()
    extrenalWindow.append(page)
    page.show(dockable=True)
    

def exportPiplineTool():
    page = Pages.exportPipline()
    extrenalWindow.append(page)
    page.show(dockable=True)