bl_info = {
        "name": "addon template",
        "description": "Single line describing my awesome add-on.",
        "author": "Aaron Powell",
        "version": (1, 0),
        "blender": (2, 90, 0),
        "location": "Properties > Render > My Awesome Panel",
        "warning": "", # used for warning icon and text in add-ons panel
        "wiki_url": "http://my.wiki.url",
        "tracker_url": "http://my.bugtracker.url",
        "support": "COMMUNITY",
        "category": "Render"
        }

import bpy


def register():
    from . import properties
    from . import ui
    properties.register()
    ui.register()

def unregister():
    from . import properties
    from . import ui
    properties.unregister()
    ui.unregister()

if __name__ == '__main__':
    register()
