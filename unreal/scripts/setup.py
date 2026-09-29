from setuptools import  setup
from Cython.Build import cythonize
import os


def compile_to_pyd(file:str):
    baseName = os.path.basename(file)
    name,_ = os.path.splitext(baseName)
    setup(
        name=name,
        ext_modules=cythonize(file),
    )


def get_all_files(rootDir:str)->list[str]:
    all_files = []
    for root,folder,files in os.walk(rootDir):
        for file in files:
            all_files.append(os.path.join(root,file))
    return all_files


if __name__ == "__main__":
    rootDir = "UnrealPipeline"
    files = get_all_files(rootDir)
    for file in files:
        if not file.endswith(".py"):
            continue
        compile_to_pyd(file)
    files = get_all_files(rootDir)
    #清理目录
    for file in files:
        if file.endswith(".c"):
            os.remove(file)


