import maya.api.OpenMaya as om2




def maya_useNewAPI():

    pass



def initializePlugin(plugin):
    vendor = "ZCX"
    version = "1.0.0"
    plugin_fn = om2.MFnPlugin(plugin,vendor,version)



def uninitializePlugin(plugin):
    plugin_fn = om2.MFnPlugin(plugin)


