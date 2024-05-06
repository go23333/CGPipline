#coding=utf-8
import subprocess

def callPolygonCruncher(pnormal,puv,path,percentage):
    cmd_str = "PolygonCruncher.exe -input-files \"{0}\" -level1 {1}".format(path,percentage)
    if pnormal:
        cmd_str += ' -normal-protect'
    if puv:
        cmd_str += ' -uv-protect'
    cmd_str += "-output-files \"test.fbx\" "
    import mayaTools.core.pathLibrary as pt
    dirname = pt.getRootPath().split("\\scripts\\")[0] + "\\thirdpart\\Polygon Cruncher\\"
    print(subprocess.call(cmd_str, cwd=dirname, shell=True))


def callUnWrap(infilepath,outfilepath,cmddictnormal):
        cmd_str = "UnWrapConsole3.exe {} {} ".format(infilepath,outfilepath)
        for key in cmddictnormal.keys():
            cmd_str = cmd_str + key + cmddictnormal[key] + ' '
        import mayaTools.core.pathLibrary as pt
        dirname = pt.getRootPath().split("\\scripts\\")[0] + "\\thirdpart"
        subprocess.call(cmd_str, cwd=dirname, shell=True)


if __name__ == '__main__':
     callPolygonCruncher(True,True,"d:\\Documents\\CGPipline\\maya\\toReduceMesh.fbx",50)