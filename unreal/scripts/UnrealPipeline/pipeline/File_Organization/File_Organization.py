import unreal
import tkinter as tk
from tkinter import filedialog


def get_content_browser_path():
    root = tk.Tk()
    root.withdraw() 

    initial_dir = unreal.Paths.project_content_dir()

    file_path = filedialog.askdirectory(
        initialdir=initial_dir,
        title="Select a File",
    )

    root.destroy()
    file_path = file_path + "/"
    if not file_path:
        return False

    if not file_path.startswith(initial_dir):
        return False

    return file_path.replace(initial_dir,"/Game/")



def move_select_mesh():
    assets = unreal.EditorUtilityLibrary.get_selected_assets()
    path = get_content_browser_path()
    if not path:
        return
    for asset in assets:
        unreal.PythonExtensionBPLibrary.copy_asset_and_dependency_to_folder(asset,path)
    


if __name__ == "__main__":
    move_select_mesh()