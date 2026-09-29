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
    name="nuke转视频",
    version="1.2",
    description="nuke批处理(外包)",
    options=options,
    executables=[Executable("nuke_bathc_render_ui.py")]
)


#python setup_wf.py build