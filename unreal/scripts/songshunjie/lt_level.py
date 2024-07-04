import unreal
import time

import shutil
import os
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


from dayu_widgets.label import MLabel
from dayu_widgets.item_view import MTreeView
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.item_view import MTreeView
from dayu_widgets.avatar import MAvatar
from dayu_widgets.line_tab_widget import MLineTabWidget
from dayu_widgets import MTabWidget, dayu_theme
from dayu_widgets.qt import application
from dayu_widgets.qt import MPixmap
from dayu_widgets.qt import MIcon




print('lt_io')
   

class mw(QtWidgets.QWidget, MFieldMixin):

    asset_images=[]
    project_paths=[]
    select_names=[]
    old_name=''


    def __init__(self, parent=None):
            super().__init__(parent)
            # self.clearTempFile()
            
            self.uii()
            self.updataTree()


    def uii(self):

        self.setWindowTitle('灯光关卡的导入导出')
        self.resize(400,600)

        tab1=MTabWidget()

        lay=QtWidgets.QVBoxLayout()
        image_lay=QtWidgets.QVBoxLayout()
        box1=QtWidgets.QGroupBox()
        box1.setStyleSheet('QGroupBox{color:white;border:0px ;}')
        box2=QtWidgets.QGroupBox()
        box2.setStyleSheet('QGroupBox{color:white;border:0px ;}')
        
        #导出部分
        self.image_lable=MLabel()
        pixmap = QtGui.QPixmap('Y:/lt_cache/temp_image.png')
        pixmap.setDevicePixelRatio(4)
        self.image_lable.setPixmap(pixmap)
        image_display_lay=QtWidgets.QHBoxLayout()
        image_display_lay.addStretch(1)
        image_display_lay.addWidget(self.image_lable)
        image_display_lay.addStretch(1)


        screen_button=MPushButton(text="截取当前界面")
        #按下执行截图
        screen_button.pressed.connect(self.screen)
        #松开执行存图
        screen_button.clicked.connect(self.setImage)

        self.flie_name_line=MLineEdit().medium()
        self.flie_name_line.setPlaceholderText(self.tr("输入最终保存资产的名称,不输入则默认为项目名称"))

        level_export_button=MPushButton(text="创建所选文件的缓存")
        level_export_button.clicked.connect(self.createDirectory)

        image_lay.addLayout(image_display_lay)
        image_lay.addWidget(screen_button)
        image_lay.addWidget(self.flie_name_line)
        image_lay.addWidget(level_export_button)



        #导入部分
        import_lay=QtWidgets.QVBoxLayout()


        self.tree_image=MTreeView()
        self.tree_image.header().setStretchLastSection(True)
        self.tree_image.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree_image.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tree_image.setUniformRowHeights(True)
        self.tree_image.setIconSize(QtCore.QSize(160,160))
        self.model_map=QtGui.QStandardItemModel()
        self.model_map.setHorizontalHeaderLabels([self.tr("导入列表")])

        self.tree_image.setModel(self.model_map)
        self.tree_image.selectionModel().selectionChanged.connect(self.treeSelect)
        self.tree_image.header().headerDataChanged

        self.label_image_name=MTextEdit()
        self.label_image_name.setMaximumHeight(80)

        import_button=MPushButton(text="将选择的资产导入到当前项目")
        import_button.pressed.connect(self.importAsset)
        import_button.clicked.connect(self.rename_lt)

        rc_lay=QtWidgets.QHBoxLayout()

        renewal_button=MPushButton(text="刷新")
        renewal_button.clicked.connect(self.updataTree)

        clear_button=MPushButton(text="清除缓存文件")
        clear_button.clicked.connect(self.clearFolder)
        rc_lay.addWidget(renewal_button)
        rc_lay.addWidget(clear_button)

        



        import_lay.addWidget(self.tree_image)
        import_lay.addWidget(self.label_image_name)
        import_lay.addLayout(rc_lay)
        import_lay.addWidget(import_button)

        box1.setLayout(image_lay)
        box2.setLayout(import_lay)
        tab1.addTab(box1,"导出")
        tab1.addTab(box2,"导入")
        tab1.tabBarClicked.connect(self.updataTree)
        lay.addWidget(tab1)
        self.setLayout(lay)




    def screen(self):
        unreal.AutomationLibrary.take_high_res_screenshot(res_x=0,res_y=0,filename='Y:/lt_cache/temp_image')
        

    def setImage(self):
        time.sleep(0.3)
        pixmap = QtGui.QPixmap('Y:/lt_cache/temp_image.png')
        pixmap.setDevicePixelRatio(4)
        self.image_lable.setPixmap(pixmap)
    
         
    def createDirectory(self):
        
        #获取项目名称
        if self.flie_name_line.text():
            project_name=self.flie_name_line.text()
        else:
            project_name=unreal.Paths.project_dir().split('/')[-2]+'_cache'
        new_image_name=project_name+'_image'
        save_path='Y:/lt_cache/asset/%s/Content'%project_name
        new_image_path='Y:/lt_cache/asset/%s.png'%new_image_name
        #图片转移到新目录
        os.makedirs(save_path, exist_ok=True)
        shutil.copy2('Y:/lt_cache/temp_image.png',new_image_path)

        #创建虚假项目文件：
        fake_file=project_name+'.uproject'
        if not os.path.exists('Y:/lt_cache/asset/%s/%s'%(project_name,fake_file)):
            with open('Y:/lt_cache/asset/%s/%s'%(project_name,fake_file), 'w') as file:
                file.close()

        #迁出所选资产到指定路径
        s_assets=unreal.EditorUtilityLibrary.get_selected_assets()
        s_assets_path=[]
        for s_asset in s_assets:
            s_assets_path.append(s_asset.get_path_name())
        print(s_assets_path)
        unreal.AssetToolsHelpers.get_asset_tools().migrate_packages(s_assets_path,destination_path=save_path,
                                                                    options=[unreal.AssetMigrationConflict.SKIP, ""])


    def clearTempFile(self):
        if os.path.exists('Y:/lt_cache/temp_image.png'):
            os.remove('Y:/lt_cache/temp_image.png')




    def updataTree(self):

        self.getImage("Y:/lt_cache")

        # 创建TreeView数据树
        self.model_map.clear()
        self.model_map.setHorizontalHeaderLabels([self.tr("导入列表")])
        
        for project_path in self.project_paths:
            for asset_image in self.asset_images:
                if asset_image.rsplit('_image',1)[0]==project_path.rsplit('/Content',1)[0]:
                    icon=QtGui.QIcon(asset_image)
                    tree_1=QtGui.QStandardItem(icon,project_path.rsplit('/Content',1)[0].rsplit('/',1)[-1])
                    self.model_map.appendRow(tree_1)


    def treeSelect(self):
        item_names=[]
        self.select_names=[]
        item_name_str=''
        tree_map_indexs=self.tree_image.selectedIndexes()
        #获取tree选项名称
        for index in tree_map_indexs:
            item=self.model_map.itemFromIndex(index)
            item_names.append(item.text())

        #将名称写入label
        for item_name in item_names:
            if item_name not in self.select_names:
                self.select_names.append(item_name)
                item_name_str+=item_name
                if item_name!=item_names[-1]:
                    item_name_str+='、'
        self.label_image_name.setText(item_name_str)
 

    def getImage(self,folder_path):
        
        self.asset_images=[]
        self.project_paths=[]
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                if '.png' in filename:
                    image=dirpath+'/'+filename
                    self.asset_images.append(image.replace('\\','/'))
            if str(dirpath).split('\\')[-1]=='Content':
                self.project_paths.append(str(dirpath).replace('\\','/'))

    def importAsset(self):
        
        #保存全部创建的文件
        unreal.EditorAssetLibrary.save_directory('/Game')

        select_path=unreal.EditorUtilityLibrary.get_selected_path_view_folder_paths()
        current_path=unreal.SystemLibrary.get_project_directory()
        # print(current_path)
        
        for select_name in self.select_names:
            import_path='Y:/lt_cache/asset/%s/Content'%select_name
            for dirpath, dirnames, filenames in os.walk(import_path):
                for filename in filenames:
                    src=str(dirpath+'/'+filename).replace('\\','/')
                    self.old_name=src.split('.')[-2]+'.'+src.split('.')[-1]
                    new_name='lt_'+select_path[0].split('/')[-1].replace('Ep','').replace('sc','')
                    dst=current_path+'Content'+select_path[0].split('Game',1)[-1]

                    if '.umap' in filename:
                        os.makedirs(dst.rsplit('/',1)[0], exist_ok=True)
                        if not os.path.exists(dst+'/'+self.old_name):
                            # print('1')
                            shutil.copy2(src,dst+'/'+self.old_name)
                            

    def rename_lt(self):

        select_path=unreal.EditorUtilityLibrary.get_selected_path_view_folder_paths()
        list_obj=select_path[0].replace('/All','')
        
        asset_l=list_obj+'/'+self.old_name.split('.')[0]
        split_name=select_path[0].split('/')[-1].replace('Ep','').replace('sc','').split('_')
        new_name='lt'
        if len(split_name)>3:
            for item in split_name[:3]:
                new_name+='_'+str(int(item))

            asset=unreal.EditorAssetLibrary.find_asset_data(asset_l).get_asset()
            if asset:
                unreal.EditorUtilityLibrary.rename_asset(asset,new_name)
        


    def clearFolder(self):
        if os.path.exists('Y:/lt_cache/asset'):
            shutil.rmtree('Y:/lt_cache/asset')
        self.updataTree()


def start():
    with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
        



if __name__ == "__main__":
   
   with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))
