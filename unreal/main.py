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
import uUnreal as UU
reload(UU)
import CGUtils.uCommon as UC
reload(UC)
import Pages
reload(Pages)



def test():
    UU.autoID()
    global urnealApp
    urnealApp = UC.getApplication()
    
    global mywindow
    mywindow = Pages.StaticMeshImporter()
    dayu_theme.apply(mywindow)
    mywindow.show()
    UU.appendWindowToUnreal(int(mywindow.winId()))
    
   

        