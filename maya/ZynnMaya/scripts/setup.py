"encoding=utf-8"
from setuptools import  setup,Extension
from Cython.Build import cythonize

import os
import sys
sys.argv.append("build_ext")

def compile_to_pyd(file):
    includePath = r"C:\Program Files\Autodesk\Maya2018\include\python2.7"
    libPath = r"C:\Program Files\Autodesk\Maya2018\lib"
    baseName = os.path.basename(file)
    name,_ = os.path.splitext(baseName)
    cn = cythonize(file, language_level=2)
    cn[0].libraries = ["python27"]
    cn[0].library_dirs = [libPath]
    cn[0].include_dirs = [includePath]
    setup(
        name=name,
        ext_modules=cn
    )

def get_all_files(rootDir):
    all_files = []
    for root,folder,files in os.walk(rootDir):
        for file in files:
            all_files.append(os.path.join(root,file))
    return all_files

if __name__ == "__main__":
    rootDir = "mayaTools"
    files = get_all_files(rootDir)
    for file in files:
        if not file.endswith(".py"):
            continue
        compile_to_pyd(file)
    files = get_all_files(rootDir)
    for file in files:
        if file.endswith(".c"):
            os.remove(file)


