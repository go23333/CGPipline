import os
import sys
import shutil

version_info_flage = "vsinfo"
version_info_file = "version_info.txt"
installer_file = "installer_pack.iss"
iscc_exe = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
installer_file_path = "dist/MyBridge.exe"
mybridge_build_path = "dist/MyBridge"
def get_version():
    readme = os.path.join(os.path.dirname(__file__),"Readme.md")
    with open(readme,'r',encoding='utf-8') as f:
        lines = f.readlines()
    version = ""
    for line in lines:
        if line.startswith('## v'):
            version = line.replace('## v',"")
    version = version.strip().split(".")
    return version

def clean():
    for folder in ["build"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    for file in [version_info_file,installer_file,"MyBridge.spec"]:
        if os.path.exists(file):
            os.remove(file)


def pack_mybridge_by_pyinstaller(debug=False):
    from PyInstaller.__main__ import run
    version = get_version()
    version_info_template = os.path.join(os.path.dirname(__file__),"other/version_info_template.txt")
    with open(version_info_template,'r',encoding='utf-8') as f:
        version_info_template = f.read()
    version_info = version_info_template.replace(version_info_flage,",".join(version))
    with open(version_info_file,'w+',encoding='utf-8') as f:
        f.write(version_info)
    opts = [
        'main.py',
        '--name=MyBridge',  # 指定生成的可执行文件的名称
        '--noconfirm',
        '--icon=app/resource/image/icon.png',  # 如果有图标的话
        '--clean',#清理打包过程的临时文件
        "--version-file=version_info.txt"
    ]
    #在Debug模式下添加控制台
    if not debug:
        opts.append('--windowed')# GUI应用，不显示控制台
    run(opts)

    #复制脚本文件夹到打包好的文件中
    shutil.copytree("scripts","dist/MyBridge/scripts")

    
def pack_installer():
    if not os.path.exists(mybridge_build_path):
        print("打包的程序文件不存在,安装包生成失败")
        return
    import subprocess
    version = get_version()
    installer_template = os.path.join(os.path.dirname(__file__),"other/installer_template.iss")
    with open(installer_template,'r',encoding='utf-8') as f:
        installer_template = f.read()
    installer_info = f'#define MyAppVersion "{".".join(version)}"\n' + installer_template
    with open(installer_file,'w+',encoding='utf-8') as f:
        f.write(installer_info)
    subprocess.call(f'"{iscc_exe}" installer_pack.iss',cwd=os.path.dirname(__file__))


def upload_installer():
    if not os.path.exists(installer_file_path):
        print("安装包文件不存在上传失败")
        return 
    import requests
    url = f"http://192.168.3.20:5050/update/upload/{'.'.join(get_version())}"
    with open(installer_file_path,'rb') as f:
        files = {'file':(installer_file_path,f)}
        r = requests.post(url,files=files)

if __name__ == '__main__':
    isdebug = False
    isinstaller = False
    isupload = False
    isbuild = False
    if "-build" in sys.argv:
        isbuild = True
    if "-debug" in sys.argv:
        isdebug = True
    if "-installer" in sys.argv:
        isinstaller = True
    if "-upload" in sys.argv:
        isupload = True
    #清理上次生成的内容
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    if isbuild:
        #打包软件
        pack_mybridge_by_pyinstaller(isdebug)
    #打包安装包
    if isinstaller:
        pack_installer()
    #上传安装包
    if isupload:
        upload_installer()


    #执行清理
    clean()
