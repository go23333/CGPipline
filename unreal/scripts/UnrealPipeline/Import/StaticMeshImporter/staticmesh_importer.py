#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.8
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################

from Qt import QtWidgets,QtCore
import functools
import unreal
import importlib



from dayu_widgets.push_button import MPushButton
from dayu_widgets.combo_box import MComboBox
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.switch import MSwitch
from dayu_widgets.label import MLabel
from dayu_widgets.browser import MClickBrowserFileToolButton
from dayu_widgets.qt import application
from dayu_widgets import dayu_theme


from UnrealPipeline.core.CommonWidget import CommonMenuBar,folderSelectGroup,DateTableView
import UnrealPipeline.core.utilis as UU
import UnrealPipeline.core.UnrealHelper as UH

importlib.reload(UH)
importlib.reload(UU)






class StaticMeshImporter(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("地编静态网格体导入")
        self.resize(720,450)
        self.move(800,400)
        self.__init_ui()
    def __init_ui(self):

        layMain = QtWidgets.QVBoxLayout()   #定义主布局
        menubar = CommonMenuBar()  #定义菜单栏
        layMain.setMenuBar(menubar)
        layMain.menuBar = menubar

        self.folderSelectGroup = folderSelectGroup("网格体文件路径:") #定义路径选择组

        self.wCamera = DateTableView(UU.CameraHeader)  #定义相机数据表格

        context_menu = self.wCamera.MakeContexMenu()   # 获取相机表格的上下文菜单并自定义
        maImportSelectedItems = context_menu.addAction("导入选中项目")
        maImportSelectedItems.triggered.connect(
            functools.partial(self.importCameras,True)
            )
        # self.folderSelectGroup.setOnTextChanged(lambda:self.wCamera.fetchCamera('_'))        # 文字框改变时刷新
        self.folderSelectGroup.leFolderPath.textChanged.connect(lambda:self.wCamera.fetchCamera(path=self.folderSelectGroup.getFolderPath(),NameFilters=[".fbx"]))

        layImport = QtWidgets.QHBoxLayout()  #用于防止导入按钮的布局
        btnImport = MPushButton("导入模型")
        btnImport.clicked.connect(
            functools.partial(self.importCameras,False)
            )
        

        # self.cbSceneName = MComboBox()

        self.cbSceneName = QtWidgets.QComboBox()
        self.cbSceneName.addItems(UH.getAllScenesName())
        self.cbSceneName.setMinimumWidth(100)
        self.cbSceneName.setMinimumHeight(30)
        self.cbSceneName.setEditable(True)

        self.cbSceneName.setStyleSheet(
                                    "QComboBox{"
                                    "border-style: solid;" 
                                    "border-width: 1px;" 
                                    "border-color: #222222;"
                                    "}"
                                    "QComboBox QAbstractItemView{"
                                    "border-radius:0px 0px 5px 5px;"
                                    "}"
                                    )
        
        # self.cbSceneName=MLineEdit().medium()
        # self.cbSceneName.setPlaceholderText(self.tr("输入资产文件夹名称,不输入则使用网格自身名称"))
        # self.cbSceneName.setMinimumWidth(280)

        self.map_path_text=MLineEdit().small()
        map_path_text_button = MClickBrowserFileToolButton()
        map_path_text_button.set_dayu_filters(['umap'])
        map_path_text_button.set_dayu_path(unreal.Paths.project_content_dir())      #设置打开的初始目录
        map_path_text_button.sig_file_changed.connect(self.map_path_text.setText)
        map_path_text_button.clicked.connect(self.mapPathChange)
        self.map_path_text.set_suffix_widget(map_path_text_button)
        #self.map_path_text.returnPressed.connect(self.mapPathChange)
        self.map_path_text.setReadOnly(True)
        self.map_path_text.setStyleSheet("QLineEdit { color: gray; }")

        self.switch = MSwitch()
        self.switch.setChecked(False)
        switch_lay = QtWidgets.QFormLayout()
        switch_lay.addRow(MLabel("导入时是否创建关卡"), self.switch)    #关卡创建开关

        self.import_map_switch = MSwitch()
        self.import_map_switch.setChecked(False)
        self.import_map_switch.clicked.connect(self.mapSwitchChange)
        import_map_switch_lay = QtWidgets.QFormLayout()
        import_map_switch_lay.addRow(MLabel("导入时添加到对应Map中"), self.import_map_switch)

        self.ver_switch = MSwitch()
        self.ver_switch.setChecked(False)
        ver_switch_lay = QtWidgets.QFormLayout()
        ver_switch_lay.addRow(MLabel("启用踏星流程"), self.ver_switch)
        


        layImport.addWidget(self.cbSceneName,alignment=QtCore.Qt.AlignLeft)
        layImport.addLayout(switch_lay)
        layImport.addLayout(import_map_switch_lay)
        layImport.addLayout(ver_switch_lay)
        layImport.addWidget(btnImport,alignment=QtCore.Qt.AlignRight)
        # 依次添加布局
        layMain.addLayout(self.folderSelectGroup)
        layMain.addWidget(self.wCamera)
        layMain.addWidget(self.map_path_text)
        layMain.addLayout(layImport)
        self.setLayout(layMain)
    def closeEvent(self, event):
        return super().closeEvent(event)
    def showEvent(self, event):
        return super().showEvent(event)
    def importCameras(self,selected):
        waitImportedQueue = []
        if selected:
            for name in self.wCamera.getSelectNames():
                for data in self.wCamera.datas:
                    if data["name"] == name:
                        waitImportedQueue.append(data)
        else:
            for data in self.wCamera.datas:
                if not data["imported"]:
                    waitImportedQueue.append(data)
        if self.import_map_switch.isChecked():
            import_map = self.map_path_text.text()
        else:
            import_map = None
        #导入方式判断
        if self.ver_switch.isChecked():
            UH.importStaticmeshs57(waitImportedQueue,import_map)
        else:
            UH.importStaticmeshs(waitImportedQueue,self.cbSceneName.currentText(),self.switch.isChecked())

    def mapPathChange(self):
        if 'Content' in self.map_path_text.text():
            self.map_path_text.setText('/Game'+self.map_path_text.text().split('Content',1)[1].rsplit('.',1)[0])
    
    def mapSwitchChange(self):
        if self.import_map_switch.isChecked():
            self.map_path_text.setReadOnly(False)
            self.map_path_text.setStyleSheet("QLineEdit { color: white; }")
        else:
            self.map_path_text.setReadOnly(True)
            self.map_path_text.setStyleSheet("QLineEdit { color: gray; }")




def Start():
    with application() as app:
        global w
        w = StaticMeshImporter()
        dayu_theme.apply(w)
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))


if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()
    Start()
