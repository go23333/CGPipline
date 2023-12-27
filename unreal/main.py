#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
##################################################################




from Qt import QtWidgets
from dayu_widgets import dayu_theme

import sys
from importlib import reload

#import my modules
import uUnreal as UT
reload(UT)
import CGUtils.uCommon as UU
reload(UU)
import Pages as Pages
reload(Pages)




def test():
    global urnealApp
    urnealApp = UU.getApplication()
    
    global mywindow
    mywindow = Pages.LevelDesignTool()
    dayu_theme.apply(mywindow)
    mywindow.show()
    UT.appendWindowToUnreal(int(mywindow.winId()))
    
   

        