#coding=utf-8
import maya.api.OpenMaya as om2
import maya.api.OpenMayaUI as om2ui
import maya.api.OpenMayaRender as om2r

def maya_useNewAPI():
    pass


class HelloWorldNode(om2ui.MPxLocatorNode):
    TYPE_NAME = "helloworld"
    TYPE_ID = om2.MTypeId(0x0007f7f7)
    DRAW_CLASSIFICATION = "drawdb/geometry/helloworld"
    DRAW_REGISTRANT_ID = "HelloWorldNode"
    def __init__(self):
        super(HelloWorldNode,self).__init__()
    
    @classmethod
    def creator(cls):
        return HelloWorldNode()
    @classmethod
    def initialize(cls):
        pass


class HelloWorldDrawOverride(om2r.MPxDrawOverride):
    NAME = "HelloWorldDrawOverride"
    def __init__(self,obj):
        super(HelloWorldDrawOverride,self).__init__(obj,None,False)
    def prepareForDraw(self,obj_path,camera_path,frame_context,old_data):
        pass
    def supportedDrawAPIs(self):
        return om2r.MRenderer.kAllDevices
    def hasUIDrawables(self):
        return True
    def addUIDrawables(self,obj_path,draw_manager,frame_context,data):
        #draw_manager:om2r.MUIDrawManager
        draw_manager.beginDrawable()
        draw_manager.text2d(om2.MPoint(100,100),"Hello World")
        draw_manager.endDrawable()
    @classmethod
    def creator(cls,obj):
        return HelloWorldDrawOverride(obj)



def initializePlugin(plugin):
    vendor = "ZCX"
    version = "1.0.0"
    plugin_fn = om2.MFnPlugin(plugin,vendor,version)
    try:
        plugin_fn.registerNode(
                                HelloWorldNode.TYPE_NAME,
                                HelloWorldNode.TYPE_ID,
                                HelloWorldNode.creator,
                                HelloWorldNode.initialize,
                                om2.MPxNode.kLocatorNode,
                                HelloWorldNode.DRAW_CLASSIFICATION
                                )
    except:
        om2.MGlobal.displayError("Faied to register node :{0}".format(HelloWorldNode.TYPE_NAME))
    
    try:
        om2r.MDrawRegistry.registerDrawOverrideCreator(HelloWorldNode.DRAW_CLASSIFICATION,
                                                        HelloWorldNode.DRAW_REGISTRANT_ID,
                                                        HelloWorldDrawOverride.creator)
    except:
        om2.MGlobal.displayError("Faied to register draw override :{0}".format(HelloWorldDrawOverride.NAME))


def uninitializePlugin(plugin):
    plugin_fn = om2.MFnPlugin(plugin)

    try:
        om2r.MDrawRegistry.deregisterDrawOverrideCreator(HelloWorldNode.DRAW_CLASSIFICATION,HelloWorldNode.DRAW_REGISTRANT_ID)
    except:
        om2.MGlobal.displayError("Faied to deregister draw override :{0}".format(HelloWorldDrawOverride.NAME))
    try:
        plugin_fn.deregisterNode(HelloWorldNode.TYPE_ID)
    except:
        om2.MGlobal.displayError("Faied to deregister node :{0}".format(HelloWorldNode.TYPE_NAME))

    

