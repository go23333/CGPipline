#encoding=utf-8

import maya.mel as mm
import pymel.core as pm
import random


def checkRepeat():
    mm.eval("source \"mel/AriSamePositionSelector.mel\";")


def checkHidden():
    mm.eval("source \"mel/jiancha.mel\";")


def distableRefreshTextures():
    mm.eval("source \"mel/setRenderThumbnailUpdate.mel\";")

def randomSelectFaces():
    sel = pm.ls(sl=1)
    pm.select(random.sample(sel[0].f,len(sel[0].f)/5*3),r=1) 