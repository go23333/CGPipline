bl_info = {
        "name": "BlendShapeInput",
        "description": "import blendshape form maya",
        "author": "zcx",
        "version": (1, 0),
        "blender": (4,1,0),
        "location": "",
        "warning": "", # used for warning icon and text in add-ons panel
        "wiki_url": "",
        "tracker_url": "",
        "support": "COMMUNITY",
        "category": "Import-Export"
        }

import bpy


def register():
    from . import properties
    from . import ui
    from importlib import reload
    reload(ui)
    properties.register()
    ui.register()

def unregister():
    from . import properties
    from . import ui
    properties.unregister()
    ui.unregister()

if __name__ == '__main__':
    register()
