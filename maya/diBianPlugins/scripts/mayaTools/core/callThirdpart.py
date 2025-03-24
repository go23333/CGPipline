#coding=utf-8
import subprocess
import mayaTools.core.pathLibrary as pt
import os
import pymel.core as pm



def WriteLoader(ObjectDir,LoaderDir):
    folder = os.path.dirname(LoaderDir)
    if os.path.exists(folder) == False:
        os.makedirs(folder)
    U3dLuaScript = ('U3dLoad({File={Path="' + ObjectDir + '", ImportGroups=true, XYZUVW=true, UVWProps=true}})')
    with open(LoaderDir, 'wt') as f:
        f.write(U3dLuaScript)
        print ('Write Unfold3d Loader Complete!')

def call_unfold_export(ObjectDir,LoaderDir):
    WriteLoader(ObjectDir,LoaderDir)
    RizomUVDir = pt.getRootPath().split("\\scripts\\")[0] + "\\thirdpart\\Unfold3D VS 2018.0\\unfold3d.exe"
    subprocess.Popen('"' + RizomUVDir + '"' + ' -cfi ' + LoaderDir)


def callPolygonCruncher(pnormal,puv,path,percentage):
    cmd_str = "PolygonCruncher.exe -input-files \"{0}\" -level1 {1}".format(path,percentage)
    if pnormal:
        cmd_str += ' -normal-protect'
    if puv:
        cmd_str += ' -uv-protect'
    cmd_str += "-output-files \"test.fbx\" "
    dirname = pt.getRootPath().split("\\scripts\\")[0] + "\\thirdpart\\Polygon Cruncher\\"
    print(subprocess.call(cmd_str, cwd=dirname, shell=True))


def callUnWrap(infilepath,outfilepath,cmddictnormal):
        cmd_str = "UnWrapConsole3.exe {} {} ".format(infilepath,outfilepath)
        for key in cmddictnormal.keys():
            cmd_str = cmd_str + key + cmddictnormal[key] + ' '
        dirname = pt.getRootPath().split("\\scripts\\")[0] + "\\thirdpart"
        subprocess.call(cmd_str, cwd=dirname, shell=True)


def export():
    
    
    pass

if __name__ == '__main__':
    from mayaTools import reloadModule
    reloadModule()
    obj = pm.ls(sl=True)
    pm.mel.FBXExport(filename="D:/test.fbx",s=True)