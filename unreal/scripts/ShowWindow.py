#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################

from dayu_widgets import dayu_theme
import Pages
import uUnreal as UU


from Qt import QtWidgets



global externalWindow
externalWindow = []

def showCameraImporter():
    mywindow = Pages.CameraImporter()
    dayu_theme.apply(mywindow)
    mywindow.show()
    externalWindow.append(mywindow)
    UU.appendWindowToUnreal(int(mywindow.winId()))

def showStaticMeshImporter():
    mywindow = Pages.StaticMeshImporter()
    dayu_theme.apply(mywindow)
    mywindow.show()
    externalWindow.append(mywindow)
    UU.appendWindowToUnreal(int(mywindow.winId()))


def showLevelDesignTool():
    mywindow = Pages.LevelDesignTool()
    dayu_theme.apply(mywindow)
    mywindow.show()
    externalWindow.append(mywindow)
    UU.appendWindowToUnreal(int(mywindow.winId()))


def showLightTools():
    mywindow = Pages.LightTools()
    dayu_theme.apply(mywindow)
    mywindow.show()
    externalWindow.append(mywindow)
    UU.appendWindowToUnreal(int(mywindow.winId()))


def showSettings():
    mywindow = Pages.Settings()
    dayu_theme.apply(mywindow)
    mywindow.show()
    externalWindow.append(mywindow)
    UU.appendWindowToUnreal(int(mywindow.winId()))


def showNormalizeExporter():
    mywindow = Pages.NormalizeExporter()
    dayu_theme.apply(mywindow)
    mywindow.show()
    externalWindow.append(mywindow)
    UU.appendWindowToUnreal(int(mywindow.winId()))