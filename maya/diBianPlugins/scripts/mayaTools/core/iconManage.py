
import mayaTools.core.pathLibrary as pt




class IconManage(object):
    iconRootPath = pt.getRootPath().split("\\scripts\\")[0] + "\\icons\\"
    def __init__(self):
        pass
    @classmethod
    def Unfold(cls,shelf=True):
        if shelf:
            return cls.iconRootPath + "unfold_shelf.png"
        else:
            return cls.iconRootPath + "unfold_menu.png"

