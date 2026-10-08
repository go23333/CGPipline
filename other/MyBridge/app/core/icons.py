
from PyQt5.QtGui import QIcon

from app.core.common_widgets import scaleMap


class Icons():
    instance = None
    def __init__(self) -> None:
        self.heart = QIcon(scaleMap(32,32,r":/MyBridge/icons/heart.png"))
        self.heartField = QIcon(scaleMap(32,32,r":/MyBridge/icons/heart_filled.png"))
        self.fbx_flag = QIcon(scaleMap(32,32,r":/MyBridge/icons/fbx_flag.png"))
        self.unreal_flag = QIcon(scaleMap(32,32,r":/MyBridge/icons/unreal_flag.png"))
    @classmethod
    def get(cls):
        if cls.instance == None:
            cls.instance = cls()
        return cls.instance
