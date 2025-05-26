#RizomUV Bridge for Maya
import os
import subprocess
from imp import reload

import maya.cmds as cmds

import mayaToolsold.lib.mayaLibrary as ml
from mayaToolsold.lib.pathLibrary import normailizePath

reload(ml)

#Dir
##########################################################################
from mayaToolsold.lib import pluginsRootPath
RizomUVDir = (pluginsRootPath + r'thirdpart\Unfold3D VS 2018.0\unfold3d.exe')
print(RizomUVDir)
ObjectType = (r'fbx')
##########################################################################


rootdir = normailizePath( os.getenv('TEMP')) 
if not os.path.exists(rootdir + 'data'):
    os.makedirs(rootdir + 'data')
ObjectDir = rootdir + ('data/RBMObject.') + ObjectType
LoaderDir = rootdir + ('data/Loader.lua')
ConfigDir = rootdir + ('data/config.json')

def WriteLoader(*args):
    ZomLuaScript = ('ZomLoad({File={Path="' + ObjectDir + '", ImportGroups=true, XYZUVW=true, UVWProps=true}})')
    U3dLuaScript = ('U3dLoad({File={Path="' + ObjectDir + '", ImportGroups=true, XYZUVW=true, UVWProps=true}})')
    if ('rizomuv.exe' in RizomUVDir) == True:
        with open(LoaderDir, 'wt') as f:
            f.write(ZomLuaScript)
            print ('Write RizomUV Loader Complete!')
    else:
        if ('unfold3d.exe' in RizomUVDir) == True:
            with open(LoaderDir, 'wt') as f:
                f.write(U3dLuaScript)
                print ('Write Unfold3d Loader Complete!')
        else:
            print ('Write Loader Error!')


def Export_OBJ(*args):
    WriteLoader()
    SelOBJ = cmds.ls( sl=True )
    if ('fbx' in ObjectType) == True:
        ml.export_fbx_without_dialog(SelOBJ,ObjectDir)
        cmds.select(SelOBJ)
        print ('Export FBX complete!')
    else:
        if ('obj' in ObjectType) == True:
            cmds.file( ObjectDir, force=1, type="OBJexport", options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", es=1)
            print ('Export OBJ complete!')
        else:
            print ('Export Object Type Error!')
    subprocess.Popen('"' + RizomUVDir + '"' + ' -cfi ' + LoaderDir)
    

def Import_OBJ(*args):
    if ('fbx' in ObjectType) == True:
        SelOBJ = cmds.ls( sl=True )
        for item in SelOBJ:
            cmds.delete()
        ml.import_fbx_without_dialog(ObjectDir)
        #cmds.file(ObjectDir, i=1, ignoreVersion=1, mergeNamespacesOnClash=0, rpr='RBMObject', type='FBX', pr=1)
        cmds.select(SelOBJ, r=True)
        print ('Import FBX complete!')
    else:
        if('obj' in ObjectType) == True:
            SelOBJ = cmds.ls( sl=True )
            cmds.file( ObjectDir, i=1, gn='RizomUVBridge', type="OBJ", gr=1)
            print ('Import OBJ complete!')
        else:
            print ('Import Object Type Error!')

#UI
def UI(*args):
    if cmds.window('BridgeUI', ex=1):
        cmds.deleteUI('BridgeUI', window=1)
    cmds.window ('BridgeUI', title="RizomUV Bridge", iconName='RizomUV Bridge', widthHeight=(210, 120) )
    cmds.columnLayout( rowSpacing=5, columnAttach=('both', 5), adjustableColumn=1)
    cmds.text ( h=20, l='RizomUV Bridge for Maya')
    cmds.text (l='v0.6 Update by ZCX')
    cmds.button ( h=30, l='Export', width=100, c=Export_OBJ)
    cmds.separator (style='in' )
    cmds.button ( h=30, l='Import', width=100, c=Import_OBJ)
    cmds.showWindow ('BridgeUI')
