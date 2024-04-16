#coding=utf-8
import maya.api.OpenMaya as om2

def maya_useNewAPI():
    pass

class HelloWorldCmd(om2.MPxCommand):
    COMMAND_NAME ="HelloWorld"
    def __init__(self):
        super(HelloWorldCmd,self).__init__()#sper()可以接收两个参数一个是子类的类名,一个是子类的实例
    def doIt(self,args):
        print(args.asInt(0))
        print("Hello World")


    @classmethod
    def creator(cls):
        return HelloWorldCmd()

    
def initializePlugin(plugin):
    vendor = "ZCX"
    version = "1.0.0"
    plugin_fn = om2.MFnPlugin(plugin,vendor,version)
    try:
        plugin_fn.registerCommand(HelloWorldCmd.COMMAND_NAME,HelloWorldCmd.creator)
    except:
        om2.MGlobal.displayError("Faied to register command :{0}".format(HelloWorldCmd.COMMAND_NAME))
    



def uninitializePlugin(plugin):
    plugin_fn = om2.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterCommand(HelloWorldCmd.COMMAND_NAME)
    except:
        om2.MGlobal.displayError("Faied to deregister command :{0}".format(HelloWorldCmd.COMMAND_NAME))
    

