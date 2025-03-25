#coding=utf-8
import pymel.core as pm
import maya.cmds as cmds


#确保需要的插件已经打开
pm.loadPlugin( 'fbxmaya.mll' )



def export_fbx(obj,path,op=""):
    current_select = cmds.ls(sl=1)
    cmds.select(cl=1)
    cmds.select(obj)
    pm.mel.FBXExport(f=path,pr=1,op=op,s=1)
    cmds.select(cl=1)
    cmds.select(current_select)

def import_fbx(path,rpr):
    pm.mel.FBXImport(f=path,ignoreVersion=1,mergeNamespacesOnClash=0,rpr=rpr, pr=1)



if __name__ == '__main__':
    from mayaTools import reloadModule
    reloadModule()
    export_fbx("pCube2","d:/test.fbx")

    


