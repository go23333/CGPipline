from cx_Freeze import setup, Executable

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
        # "compressed": True
        # 'zip_include_packages': ['PyQt5'],
        # 'zip_exclude_packages': []
    }
}
 
setup(
    name="mayapy运行程序(外包)",
    version="1.2",
    description="maya批处理(外包)",
    options=options,
    executables=[Executable("MayaBlackBox_WF.py")]
)


#python setup_wf.py build