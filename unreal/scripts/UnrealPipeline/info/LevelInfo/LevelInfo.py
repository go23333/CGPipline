#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.9
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
from Qt.QtWidgets import QMainWindow,QApplication,QWidget
from Qt import QtWidgets
from Qt.QtCore import Qt



from dayu_widgets.qt import application
from dayu_widgets import dayu_theme
from dayu_widgets.item_view import MTableView,MTableModel
from dayu_widgets.item_model import MSortFilterModel
from dayu_widgets.push_button import MPushButton

import unreal


from UnrealPipeline.core.CommonWidget import CommonMenuBar
import UnrealPipeline.core.UnrealHelper as UH

class CommonMainWindow(QMainWindow):
    def __init__(self, parent = None)->None:
        super().__init__(parent)
        self.__initMenu()
    def MoveToCenter(self):
        desktop_width = QApplication.desktop().width()/4
        desktop_height = QApplication.desktop().height()/2
        self.move(int(desktop_width-self.width()/2.0),int(desktop_height-self.height()/2.0))
    def __initMenu(self):
        menuBar = CommonMenuBar()
        self.setMenuBar(menuBar)
        self.menuBar = menuBar



class LevelInfo(CommonMainWindow):
    def __init__(self, parent = None)->None:
        super().__init__(parent)
        self.resize(800,600)
        self.MoveToCenter()


        self.__initDatas()
        self.__initUI()
    def __initDatas(self):
        self._objectCountSum = 0
        self._verticesNumberSum = 0
        self.datas = []
    def __initUI(self):
        # UI
        Widget_main = QWidget()
        Layout_main = QtWidgets.QVBoxLayout()
        Widget_main.setLayout(Layout_main)

        layout_header = QtWidgets.QHBoxLayout()

        button_refresh = MPushButton("    刷新    ")
        button_refresh.clicked.connect(self.__refresh)


        layout_header.addWidget(button_refresh,alignment=Qt.AlignLeft)

        self.tvMain = MTableView(size=dayu_theme.medium, show_row_count=True)
        self.dataModle = MTableModel()
        self.ModelSort = MSortFilterModel()
        self.tvMain.setModel(self.ModelSort)
        self.__refreshTableView()



        Layout_main.addLayout(layout_header)
        Layout_main.addWidget(self.tvMain)
        self.setCentralWidget(Widget_main)
    def __refreshTableView(self):
        LevelInfoHeader = [
                {
                    "label": "对象\n",
                    "key": "Object",
                    "checkable": False,
                    "searchable": True,
                },
                {
                    "label": "Actor\n",
                    "key": "Actor",
                    "checkable": False,
                    "searchable": False,

                },
                {
                    "label": f"数量\n{self._objectCountSum}",
                    "key": "Count",
                    "checkable": False,
                    "searchable": False,
                },
                {
                    "label": f"顶点数量\n{self._verticesNumberSum}",
                    "key": "VerticesNumber",
                    "checkable": False,
                    "searchable": False,
                },
            ]
        self.dataModle.set_header_list(LevelInfoHeader)
        self.ModelSort.setSourceModel(self.dataModle)
    def __refresh(self):
        self.__initDatas()
        actors = UH.editorActorSubsystem.get_all_level_actors()
        staticMeshs = []
        for actor in actors:
            actor:unreal.Actor
            components = []
            componentsStaticmesh = actor.get_components_by_class(unreal.StaticMeshComponent)

            componentsFStaticmesh = actor.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent)

            if componentsStaticmesh:
                components += componentsStaticmesh
            if componentsFStaticmesh:
                components += componentsFStaticmesh
            if components  == []:
                continue

            for component in components:
                wrapStaticMesh = UH.WrapStaticMesh(component.static_mesh)
            if wrapStaticMesh.asset not in staticMeshs:
                data = dict(Object=wrapStaticMesh.get_asset_name(),Actor=actor.get_name(),Count=1,VerticesNumber = wrapStaticMesh.get_vertices_count())
                self.datas.append(data)
                staticMeshs.append(wrapStaticMesh.asset)
            else:
                self.datas[staticMeshs.index(wrapStaticMesh.asset)]["Count"] += 1
                self.datas[staticMeshs.index(wrapStaticMesh.asset)]["Actor"] = "Actors"
        for data in self.datas:
            self._objectCountSum += data["Count"]
            self._verticesNumberSum += (data["Count"] * data["VerticesNumber"])
        self.dataModle.set_data_list(self.datas)
        self.__refreshTableView()
        pass

        













def Start():
    with application() as app:
        global w
        w = LevelInfo()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()
