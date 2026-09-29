from cx_Freeze import setup, Executable
import os
import shutil

build_dir_name = 'MayaBlackBox_v3'


def copy_after_build(target_dir,source_dir):
    
    if os.path.exists(source_dir) and os.path.isdir(source_dir):
        # 如果目标已存在，先删除再复制，避免冲突
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)
    else:
        print(f"Source directory {source_dir} not found, skipping...")

packages = [

    'subprocess',
    'os',
    'openpyxl',
    'json',
    'tempfile',
    'PyQt5.QtCore',
    'PyQt5.QtWidgets',
    'win32api',
    'win32con',
    'dayu_widgets'  
]
 
options = {
    'build_exe': {
        
        'packages': packages,
        'build_exe': build_dir_name,
        # "compressed": True
        # 'zip_include_packages': ['PyQt5'],
        # 'zip_exclude_packages': []
    }
}

setup(
    name="mayapy运行程序",
    version="3.0.0",
    description="maya批处理",
    options=options,
    executables=[Executable("MayaBlackBox.py")]
)



# target_dir = os.path.dirname(os.path.abspath(__file__)) + '/MayaBlackBox_v3'
# source_dir = 
# copy_after_build(target_dir,)


#conda activate py37
#python setup.py build