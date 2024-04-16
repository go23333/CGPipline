import maya.cmds as cmds
import maya.mel as mel
import maya.utils as utils
import sys,os
import maya.OpenMaya as om
from deleteUserSetup import deluserSetup
from deletePTTQ import delPTTQ
from deleteAnimDXH import deleteAnimImportPathDXH
cbIds=[]
#deluserSetup()
deleteAnimImportPathDXH()
cbIds.append(om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeOpen, deluserSetup))
cbIds.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterOpen, delPTTQ))
cbIds.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterImport, delPTTQ))
cbIds.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterLoadReference, delPTTQ))

cbIds.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterCreateReference, delPTTQ))
cbIds.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterLoadReferenceAndRecordEdits, delPTTQ))
cbIds.append(om.MSceneMessage.addCallback(om.MSceneMessage.kAfterImportReference, delPTTQ))

target_disk = 'Z:'
if not os.path.exists(target_disk):
    os.system(r"net use Z: \\192.168.3.251\NnTools$")

def deleteMessage(*args, **kwargs):
    for id in cbIds:
        try:
            om.MMessage.removeCallback(id)
        except:
            pass
def delPlugins(*args, **kwargs):
    unknownPlugins = cmds.unknownPlugin(query=1,list=1)
    for Plugin in unknownPlugins:
        if Plugin!="Mayatomr":
            cmds.unknownPlugin(Plugin,remove=1)

om.MSceneMessage.addCallback(om.MSceneMessage.kBeforeSave, delPlugins)
om.MSceneMessage.addCallback(om.MSceneMessage.kAfterSave, deleteMessage)

import RS_Scripts_2016
reload(sys)

sys.setdefaultencoding('gb2312')

utils.executeDeferred("RS_Scripts_2016.RS_Scripts()")