bl_info = {
        "name": "TXImport",
        "description": "ToolsForTXImport",
        "author": "zcx",
        "version": (1, 0),
        "blender": (2, 90, 0),
        "location": "",
        "warning": "", # used for warning icon and text in add-ons panel
        "wiki_url": "",
        "tracker_url": "",
        "support": "COMMUNITY",
        "category": "Import-Export"
        }

import bpy

def register():
    from . import tximport
    tximport.register()

def unregister():
    from . import tximport
    tximport.unregister()

if __name__ == '__main__':
    register()
