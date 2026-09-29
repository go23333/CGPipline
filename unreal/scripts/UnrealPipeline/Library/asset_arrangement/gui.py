import unreal
from Qt.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QComboBox,QFileDialog,QMessageBox
from Qt.QtCore import Qt
from dayu_widgets.qt import application
import requests



class Backend:
    instance = None
    def __init__(self):
        self.address = "http://192.168.3.20:9007/uploadapi/"
    def is_backend_online(self):
        data = {}
        try:
            response = requests.post(self.address + "category/list",json=data,timeout=3)
        except requests.exceptions.ReadTimeout:
            return False
        if response.status_code == 200:
            return True
        return False
    def add_new_category(self,en_name:str,ch_name:str,des:str=""):
        data = dict(
            enName = en_name,
            chName = ch_name,
            prid = 0,
            description = des,
            sortOrder = 0
        )
        response = requests.post(self.address + "category/save",json=data,timeout=3)
        if response.status_code == 200:
            return response.json()["data"]
        return False
    def check_category_exiset_by_en_name(self,en_name:str):
        data = dict(
            enName = en_name
        )
        response = requests.post(self.address + "category/list",json=data,timeout=3)
        if response.json()["data"]:
            return response.json()["data"][0]["id"]
        return False
    def get_category_ch_name(self,en_name:str):
        data = dict(
            enName = en_name
        )
        response = requests.post(self.address + "category/list",json=data,timeout=3)
        if response.json()["data"]:
            return response.json()["data"][0]["chName"]
        return False
    def add_new_item(self,category_name:str,category_name_ch:str,description:str=""):
        categoryID = self.check_category_exiset_by_en_name(category_name)
        if not categoryID:
            categoryID = self.add_new_category(category_name,category_name_ch)
        
        assert categoryID,"获取分类ID失败"
        index = self.get_item_index_in_category(categoryID)
        assert index,f"获取分类{category_name}下,最新的ID失败"
        index_str = str(index)
        if 3 - len(index_str) >0:
            index_str = "0"*(3-len(index_str))+index_str

        name = f"{category_name}_{index_str}A"
        data = dict(
            name = name,
            categoryId = categoryID,
            sortOrder = 0,
            description = description,
            categoryIndex = index,
            path = ""
        )
        response = requests.post(self.address + "subCategory/save",json=data,timeout=3)
        if response.status_code == 200:
            return name
        return False
    def get_item_index_in_category(self,category_id:int):
        url = self.address + f"subCategory/nextIndex?categoryId={category_id}"
        response = requests.get(url,timeout=3)
        if response.status_code == 200:
            return response.json()['data']
        return False        
    @classmethod
    def get(cls):
        if not cls.instance:
            cls.instance = Backend()
        return cls.instance

class AssetArrangement(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.resize(600,300)
        self.setWindowTitle("资产整理工具")
        self.__initUI()
        self.file_root_path = "/Game/Scenes/Environment/Reuse/"
    def __initUI(self):
        ly_main = QVBoxLayout(self)
        ly_main.setAlignment(Qt.AlignmentFlag.AlignTop)
        ly_main.setSpacing(20)
        self.setLayout(ly_main)

        # w_path_select = QWidget(self)
        # ly_main.addWidget(w_path_select)
        # l_path_select = QHBoxLayout(w_path_select)
        # l_path_select.setContentsMargins(0,0,0,0)

        # l_path_select.addWidget(QLabel("指定路径:"))

        # self.le_path = QLineEdit(self)
        # l_path_select.addWidget(self.le_path)

        # pb_select_folder = QPushButton(self,text="...")
        # pb_select_folder.clicked.connect(self.__select_path)
        # pb_select_folder.setMaximumWidth(30)
        # l_path_select.addWidget(pb_select_folder)



        w_asset_type = QWidget(self)
        ly_main.addWidget(w_asset_type)
        ly_asset_type = QHBoxLayout(w_asset_type)
        ly_asset_type.setContentsMargins(0,0,0,0)


        self.cb_asset_type = QComboBox(self)
        self.cb_asset_type.addItems([
            "3D_Assets",
            "Decal",
            "Surface"
            ])
        ly_asset_type.addWidget(QLabel("资产类型:"))
        ly_asset_type.addWidget(self.cb_asset_type)



        ly_asset_type.addWidget(QLabel("资产类名(字母):"))
        self.le_asset_name = QLineEdit(self)
        self.le_asset_name.setPlaceholderText("输入资产类名:")
        self.le_asset_name.editingFinished.connect(self.__search_chinese_name)

        ly_asset_type.addWidget(self.le_asset_name)


        ly_asset_type.addWidget(QLabel("资产类名(中文):"))

        self.le_asset_name_ch = QLineEdit(self)
        self.le_asset_name_ch.setPlaceholderText("输入资产类名(中文):")


        ly_asset_type.addWidget(self.le_asset_name_ch)



        pb_move_asset = QPushButton(text="复制资产",parent=self)
        pb_move_asset.clicked.connect(self.__move_asset)

        ly_main.addWidget(pb_move_asset)
    def __select_path(self):
        unreal_content_path = unreal.Paths.project_content_dir()
        file_path = QFileDialog.getExistingDirectory(self,"选择目录",unreal_content_path)
        if not file_path:
            return
        if not file_path.startswith(unreal_content_path):
            return
        if "Collections" in file_path or "Developers" in file_path:
            return
        path_in_unreal = file_path.replace(unreal_content_path,"/Game/")
        self.le_path.setText(path_in_unreal)
    def __move_asset(self):
        asset = unreal.EditorUtilityLibrary.get_selected_assets()[0]
        asset_class_name = self.le_asset_name.text()
        asset_class_name_ch = self.le_asset_name_ch.text()

        if not asset_class_name or not asset_class_name_ch:
            QMessageBox.warning(self,"错误","请检查输入")
            return
        
        asset_type = self.cb_asset_type.currentText()
        asset_name = Backend.get().add_new_item(asset_class_name,asset_class_name_ch)
        asset_new_path = f"{self.file_root_path}{asset_type}/{asset_class_name}/{asset_name}/"
        unreal.PythonExtensionBPLibrary.copy_asset_and_dependency_to_folder(asset,asset_new_path)

        asset_path = asset_new_path + asset.get_name()
        renameed = asset_new_path + asset_name
        unreal.EditorAssetLibrary.rename_asset(asset_path,renameed)


        QMessageBox.information(self,"提示","资产整理完成")

    def __search_chinese_name(self,*a):
        en_name = self.le_asset_name.text()
        if not en_name:
            return
        
        ch_name = Backend.get().get_category_ch_name(en_name)
        if ch_name:
            self.le_asset_name_ch.setText(ch_name)
        else:
            self.le_asset_name_ch.clear() 


def show():
    with application() as app:
        global w
        w = AssetArrangement()
        w.show()
        unreal.parent_external_window_to_slate(int(w.winId()))

if __name__ == "__main__":
    show()

