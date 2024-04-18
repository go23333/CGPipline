#coding=utf-8
import subprocess


def callPolygonCruncher(pnormal,puv,path,percentage):
    cmd_str = "PolygonCruncher.exe -input-files \"{}\" -level1 {}".format(path,percentage)
    if pnormal:
        cmd_str = cmd_str + ' -normal-protect'
    if puv:
        cmd_str = cmd_str + ' -uv-protect'
    from mayaToolsold.lib import pluginsRootPath
    dirname = pluginsRootPath + '/thirdpart/Polygon Cruncher'
    print(subprocess.call(cmd_str, cwd=dirname, shell=True))


def callUnWrap(infilepath,outfilepath,cmddictnormal):
        cmd_str = "UnWrapConsole3.exe {} {} ".format(infilepath,outfilepath)
        for key in cmddictnormal.keys():
            cmd_str = cmd_str + key + cmddictnormal[key] + ' '
        from mayaToolsold.lib import pluginsRootPath
        dirname = pluginsRootPath + 'thirdpart'
        subprocess.call(cmd_str, cwd=dirname, shell=True)
