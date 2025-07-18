
import unreal

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui



from dayu_widgets.label import MLabel
from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets.button_group import MCheckBoxGroup
from dayu_widgets.divider import MDivider
from dayu_widgets.browser import MClickBrowserFolderToolButton
from dayu_widgets.text_edit import MTextEdit
from dayu_widgets.splitter import MSplitter
from dayu_widgets.item_view import MTreeView
from dayu_widgets.check_box import MCheckBox
from dayu_widgets.spin_box import MSpinBox
from dayu_widgets.theme import MTheme

from dayu_widgets import dayu_theme
from dayu_widgets.qt import application


print('AAI 1.1')




class MCheckSpinBoxGroup(MCheckBoxGroup):
    def create_button(self, data_dict):
        return MCheckBox()

   

class mw(QtWidgets.QWidget, MFieldMixin):



    k=[]

    asset_level_list_name=[]
    select_world_names=[]

    world_asset_names=[]
    world_find_assets=[]

    light_sc_flie_list=[]
    ep_flie_list=[]

    level_path='/Game/AAI/Reference/Scenes'
    ch_path='/Game/AAI/Reference/Character'
    pro_path='/Game/AAI/Reference/Pro'

    level_assets=[]
    ch_assets=[]
    pro_assets=[]
    sequnence_find_assets=[]

    assets_ch=[]
    assets_pro=[]
    find_level_assets=[]
    find_ch_assets=[]
    find_pro_assets=[]
    

    def __init__(self, parent=None):
            super().__init__(parent)

            self.getEpList()
            
            self.uii()
            self.chQueryClicked()
            self.proQueryClicked()
            self.levelQueryClicked()
            self.getLightMap()
            
           

    def uii(self):

        self.setWindowTitle('AAI文件导入')
        self.resize(1000,420)

        
        lay=QtWidgets.QVBoxLayout()
        

        lay_asset=QtWidgets.QVBoxLayout()
        lay1=QtWidgets.QHBoxLayout()
        lay1_1=QtWidgets.QVBoxLayout()
        lay1_2=QtWidgets.QVBoxLayout()
        lay1_3=QtWidgets.QVBoxLayout()
        
        lay2=QtWidgets.QHBoxLayout()
        lay2s=QtWidgets.QVBoxLayout()
        lay2_1=QtWidgets.QVBoxLayout()
        lay2_2=QtWidgets.QVBoxLayout()

        #左侧窗口
        #角色列表

        self.ch_path_text=MLineEdit(text=self.ch_path).small()
        ch_path_text_button = MClickBrowserFolderToolButton()
        ch_path_text_button.sig_folder_changed.connect(self.ch_path_text.setText)
        self.ch_path_text.set_suffix_widget(ch_path_text_button)
        self.ch_path_text.returnPressed.connect(self.chQueryClicked)
        ch_path_text_button.clicked.connect(self.chQueryClicked)

        # #设置按钮组
        # self.radio_group_ch = MCheckBoxGroup(orientation=QtCore.Qt.Vertical)
        # self.radio_group_ch.set_button_list(self.k)
        # self.radio_group_ch.set_spacing(1)
        

        self.label_ch = MLabel()
        self.label_ch.setWordWrap(True)
        self.label_ch.setMaximumWidth(200)
        self.label_ch.setMinimumHeight(36)
        
        # self.register_field("asset_CH_app")
        # self.register_field(
        #     "asset_CH_app_text",lambda: " 、 ".join(self.field("asset_CH_app")) if self.field("asset_CH_app") else None
        # )
        # self.bind(
        #     "asset_CH_app", self.radio_group_ch, "dayu_checked", signal="sig_checked_changed"
        # )
        # self.bind("asset_CH_app_text", label_ch, "text")

        
        
        check_spin_box_ch = self.checkSpinBox(self.k)
        self.checkSpinData(check_spin_box_ch)
        
        self.scroll_ch=QtWidgets.QScrollArea()
        self.scroll_ch.setMinimumWidth(100)
        self.scroll_ch.setWidget(check_spin_box_ch)
        # scroll_ch.setWidget(self.radio_group_ch)



        #道具列表

        self.pro_path_text=MLineEdit(text=self.pro_path).small()
        pro_path_text_button = MClickBrowserFolderToolButton()
        pro_path_text_button.sig_folder_changed.connect(self.pro_path_text.setText)
        self.pro_path_text.set_suffix_widget(pro_path_text_button)
        self.pro_path_text.returnPressed.connect(self.proQueryClicked)
        pro_path_text_button.clicked.connect(self.proQueryClicked)

        self.label_pro = MLabel()
        self.label_pro.setWordWrap(True)
        self.label_pro.setMaximumWidth(200)
        self.label_pro.setMinimumHeight(36)

        check_spin_box_pro = self.checkSpinBox(self.k)
        self.checkSpinData(check_spin_box_pro)
        self.scroll_pro=QtWidgets.QScrollArea()
        self.scroll_pro.setWidget(check_spin_box_pro)



        #场景列表

        self.level_path_text=MLineEdit(text=self.level_path).small()
        level_path_text_button = MClickBrowserFolderToolButton()
        level_path_text_button.sig_folder_changed.connect(self.level_path_text.setText)
        # self.level_path_text.textChanged.connect(level_path_text_button.set_dayu_path)
        # level_path_text_button.setFixedWidth(45)
        self.level_path_text.set_suffix_widget(level_path_text_button)
        self.level_path_text.returnPressed.connect(self.levelQueryClicked)
        level_path_text_button.clicked.connect(self.levelQueryClicked)


        self.radio_group_level = MCheckBoxGroup(orientation=QtCore.Qt.Vertical)
        self.radio_group_level.set_button_list(self.k)
        self.radio_group_level.set_spacing(1)
        

        self.label_level = MLabel()
        self.label_level.setWordWrap(True)
        self.label_level.setMaximumWidth(200)
        self.label_level.setMinimumHeight(36)
        self.register_field("asset_level_app")
        self.register_field(
            "asset_level_app_text",lambda: "、".join(self.field("asset_level_app")) if self.field("asset_level_app") else None
        )
        self.bind(
            "asset_level_app", self.radio_group_level, "dayu_checked", signal="sig_checked_changed"
        )
        self.bind("asset_level_app_text", self.label_level, "text")
        
        scroll_level=QtWidgets.QScrollArea()
        scroll_level.setMinimumWidth(100)
        scroll_level.setWidget(self.radio_group_level)


        lay1_1.addWidget(MDivider("角色"))
        lay1_1.addWidget(self.ch_path_text)
        lay1_1.addWidget(self.scroll_ch)
        lay1_1.addWidget(self.label_ch)
        

        lay1_2.addWidget(MDivider("道具"))
        lay1_2.addWidget(self.pro_path_text)
        lay1_2.addWidget(self.scroll_pro)
        lay1_2.addWidget(self.label_pro)
        

        lay1_3.addWidget(MDivider("场景"))
        lay1_3.addWidget(self.level_path_text)
        lay1_3.addWidget(scroll_level)
        lay1_3.addWidget(self.label_level)

        lay1.addLayout(lay1_1)
        lay1.addLayout(lay1_2)
        lay1.addLayout(lay1_3)
        lay_asset.addWidget(MDivider("选择需要导入的资产"))
        lay_asset.addLayout(lay1)
        

        #右侧窗口
        #第一部分

        #ep列表
        radio_group_ep = MRadioButtonGroup(orientation=QtCore.Qt.Vertical)
        radio_group_ep.set_button_list(self.ep_flie_list)
        radio_group_ep.set_spacing(1)
        radio_group_ep.get_button_group().buttonClicked.connect(self.getLightMap)
        


        self.register_field("ep_app")
        self.register_field(
            "ep_app_text",lambda: " 、 ".join(self.field("ep_app")) if self.field("ep_app") else None
        )   
        self.bind(
            "ep_app", radio_group_ep, "dayu_checked", signal="sig_checked_changed"
        )
        
        scroll_ep=QtWidgets.QScrollArea()
        scroll_ep.setMinimumWidth(100)
        scroll_ep.setWidget(radio_group_ep)
        
        button_get = MPushButton(text="获取信息")
        button_get.clicked.connect(self.buttonGetClicked)

        button_clear = MPushButton(text="清除所有资产选择")
        button_clear.clicked.connect(self.buttonClearClicked)

        lay2_1.addWidget(scroll_ep)
        lay2_1.addWidget(button_get)
        lay2_1.addWidget(button_clear)


        #第二部分
        self.label_map = MTextEdit()
        # self.label_map.setWordWrap(True)
        self.label_map.setMaximumWidth(300)
        self.label_map.setMaximumHeight(80)

        self.tree_map=MTreeView()
        self.tree_map.header().setStretchLastSection(True)
        self.tree_map.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree_map.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.model_map=QtGui.QStandardItemModel()
        self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
        
        
        self.tree_map.setModel(self.model_map)
        self.tree_map.selectionModel().selectionChanged.connect(self.treeSelect)
        self.tree_map.header().headerDataChanged

        
        
        button_create = MPushButton(text="创建")
        button_create.clicked.connect(self.createCliced)

        
        lay2_2.addWidget(self.tree_map)
        lay2_2.addWidget(self.label_map)
        
        lay2_2.addWidget(button_create)

        
        lay2.addLayout(lay2_1)
        lay2.addLayout(lay2_2)

        lay2s.addWidget(MDivider("目标场景"))
        lay2s.addWidget(MDivider("选择需要导入的场景"))
        lay2s.addLayout(lay2)
        

        #将布局放到GroupBox中
        box_l=QtWidgets.QGroupBox()
        box_l.setLayout(lay_asset)
        box_l.setStyleSheet('QGroupBox{color:white;border:0px ;}')
        box_r=QtWidgets.QGroupBox()
        box_r.setFixedWidth(350)
        box_r.setLayout(lay2s)
        box_r.setStyleSheet('QGroupBox{color:white;border:0px ;}')

        #给布局添加调节滑块
        splitter= MSplitter()
        splitter.setHandleWidth(3)
        splitter.addWidget(box_l)
        splitter.addWidget(box_r)

        
        lay.addWidget(splitter)

        self.setLayout(lay)


    #创建check和Spin的集合widget
    def checkSpinBox(self,button_list:list):
        lay_zz = QtWidgets.QVBoxLayout()
        check_spin_box = QtWidgets.QGroupBox()
        for button_name in button_list: 
            lay_cs = QtWidgets.QHBoxLayout()
            checkBox = MCheckBox()
            checkBox.setMinimumSize(20,20)
            checkBox.setText(button_name)
            checkBox.stateChanged.connect(self.updateLable)
            spin_box1 = MSpinBox()
            spin_box1.setStyleSheet("QSpinBox::up-button { width: 15px; height: 4px; }\n"
                                "QSpinBox::down-button { width: 15px; height: 4px; }")
            spin_box1.setRange(1, 255)
            spin_box1.setMaximumSize(30,13)
            spin_box1.set_dayu_size(dayu_theme.badge_dot)
            spin_box1.setObjectName('spin_'+str(button_name))
            spin_box1.valueChanged.connect(self.updateLable)
            
            lay_cs.addWidget(spin_box1)
            lay_cs.addWidget(checkBox)
            lay_cs.setContentsMargins(0, 0, 0, 0)
            lay_cs.setSpacing(1)

            lay_zz.addLayout(lay_cs)
        lay_zz.setContentsMargins(0, 0, 0, 0)
        lay_zz.setSpacing(1)
        check_spin_box.setLayout(lay_zz)

        return check_spin_box

    #返回Check名称和Spin数量的字典数据
    def checkSpinData(self,check_spin_box:QtWidgets.QGroupBox):
        lay_box = check_spin_box.layout()
        check_spin_dict = {}
        for sub_lay in lay_box.children():
                #遍历子layout中的widget
                switch = False
                for i in range(sub_lay.count()):
                    widget = sub_lay.itemAt(i).widget()
                    if isinstance(widget,MCheckBox):
                        switch = widget.isChecked()
                        check_box = widget.text()
                    if isinstance(widget,MSpinBox):
                        spin_box = widget.objectName()
                        spin_box_value = widget.value()
                if switch == True:
                    check_spin_dict[check_box] = spin_box_value
                
        return check_spin_dict

    #更新角色道具的label信息
    def updateLable(self):
        asset_ch_names_dict = self.checkSpinData(self.scroll_ch.widget())
        asset_pro_names_dict = self.checkSpinData(self.scroll_pro.widget())
        label_ch_text = ''
        label_pro_text = ''
        for asset_ch_name,value in asset_ch_names_dict.items():
            if value>1:
                label_ch_text += asset_ch_name+f'*{value}、'
            else:
                label_ch_text += asset_ch_name+'、'
        label_ch_text = label_ch_text.rsplit('、',1)[0]

        for asset_pro_name,value in asset_pro_names_dict.items():
            if value>1:
                label_pro_text += asset_pro_name+f'*{value}、'
            else:
                label_pro_text += asset_pro_name+'、'
        label_pro_text = label_pro_text.rsplit('、',1)[0]

        self.label_ch.setText(label_ch_text)
        self.label_pro.setText(label_pro_text)



    def createCliced(self):

        world_asset_find_list=[]
        sequnence_asset_find_list=[]

        #获取UI选项名称
        # asset_ch_names=self.field("asset_CH_app")
        asset_ch_names_dict = self.checkSpinData(self.scroll_ch.widget())
        # asset_pro_names=self.field("asset_pro_app")
        asset_pro_names_dict = self.checkSpinData(self.scroll_pro.widget())
        asset_level_names=self.field("asset_level_app")
        ep_name=self.field("ep_app")



        if self.select_world_names:
            
            # 通过选择的场景获取对应的场景资产
            for select_world_name in self.select_world_names:
                for world_asset_find in self.world_find_assets:
                    if select_world_name==world_asset_find.get_asset().get_name():
                        world_asset_find_list.append(world_asset_find)
        #通过选择的关卡序列获取对应的关卡序列
                for sequnence_find_asset in self.sequnence_find_assets:
                    # print(sequnence_find_asset)
                    if select_world_name.replace('_Map','_an')==sequnence_find_asset.get_asset().get_name():
                        sequnence_asset_find_list.append(sequnence_find_asset)


            #对场景添加资产
            if asset_level_names:
                for map in world_asset_find_list: 
                    unreal.LevelEditorSubsystem().load_level(map.get_asset().get_path_name())
                    for find_level_asset in self.find_level_assets:
                        for asset_level_name in asset_level_names:
                            if find_level_asset.get_asset().get_name()==asset_level_name:
                                unreal.EditorLevelUtils().add_level_to_world(map.get_asset(),level_package_name=find_level_asset.get_asset().get_path_name(),level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
                                # unreal.EditorActorSubsystem().spawn_actor_from_object(find_level_asset.get_asset(),location=(0,0,0))
                                unreal.EditorAssetLibrary.save_directory('/Game/Shots')

            #对动画关卡序列添加资产
            for sequnence_asset_find in sequnence_asset_find_list:
                #添加道具
                if asset_pro_names_dict:
                    for find_pro_asset in self.find_pro_assets:   
                        for asset_pro_name,value in asset_pro_names_dict.items():  
                            if value > 1:
                                if asset_pro_name==find_pro_asset.get_asset().get_name():
                                    for i in range(value):
                                        sequnence_asset_find.get_asset().add_spawnable_from_instance(find_pro_asset.get_asset())
                            else:
                                if asset_pro_name==find_pro_asset.get_asset().get_name():
                                    sequnence_asset_find.get_asset().add_spawnable_from_instance(find_pro_asset.get_asset())
                # #添加角色
                # if asset_ch_names:
                #     for find_ch_asset in self.find_ch_assets:   
                #         for asset_ch_name in asset_ch_names:  
                #             if asset_ch_name==find_ch_asset.get_asset().get_name():
                #                 sequnence_asset_find.get_asset().add_spawnable_from_instance(find_ch_asset.get_asset())
                #添加角色
                if asset_ch_names_dict:
                    for find_ch_asset in self.find_ch_assets:   
                        for asset_ch_name,value in asset_ch_names_dict.items():                              
                            if value > 1:
                                if asset_ch_name==find_ch_asset.get_asset().get_name():                                 
                                    for i in range(value):
                                        sequnence_asset_find.get_asset().add_spawnable_from_instance(find_ch_asset.get_asset())
                            else:
                                if asset_ch_name==find_ch_asset.get_asset().get_name():
                                    sequnence_asset_find.get_asset().add_spawnable_from_instance(find_ch_asset.get_asset())
            unreal.EditorAssetLibrary.save_directory('/Game/Shots')



    def treeSelect(self):
        item_names=[]
        self.select_world_names=[]
        item_name_str=''
        tree_map_indexs=self.tree_map.selectedIndexes()
        #获取tree选项名称
        for index in tree_map_indexs:
            item=self.model_map.itemFromIndex(index)
            item_names.append(item.text())

        #将名称写入label
        for item_name in item_names:
            if item_name in self.world_asset_names and item_name not in self.select_world_names:
                self.select_world_names.append(item_name)
                item_name_str+=item_name
                if item_name!=item_names[-1]:
                    item_name_str+='、'
        self.label_map.setText(item_name_str)



    def buttonGetClicked(self):

        self.chQueryClicked()
        self.proQueryClicked()
        self.levelQueryClicked()
        self.getLightMap()

    def buttonClearClicked(self,check_spin_box:QtWidgets.QGroupBox):
        self.radio_group_level.set_dayu_checked([])                           

        check_spin_boxs=[]
        check_spin_boxs.append(self.scroll_ch.widget().layout())
        check_spin_boxs.append(self.scroll_pro.widget().layout())
        for check_spin_box in check_spin_boxs:
            lay_box = check_spin_box.layout()
            for sub_lay in lay_box.children():
                    #遍历子layout中的widget
                    for i in range(sub_lay.count()):
                        widget = sub_lay.itemAt(i).widget()
                        if isinstance(widget,MCheckBox):
                            widget.setChecked(False)        #取消勾选角色和道具的选项框


    def getEpList(self):
        self.ep_flie_list=[]
        ep_i=0
        self.tree_switch=0
        while ep_i<300:
            ep_i_str=str(ep_i).zfill(3)
            ep_path='/Game/Shots/Ep%s'%ep_i_str
            aa1=unreal.EditorAssetLibrary().does_directory_exist(ep_path)
            ep_path2='/Game/Shots/EP%s'%ep_i_str
            aa2=unreal.EditorAssetLibrary().does_directory_exist(ep_path2)
            if aa1==1 or aa2==1:
                self.ep_flie_list.append('EP%s'%ep_i_str)
                self.tree_switch=1
            ep_i+=1
        # print(self.ep_flie_list)


    def getLightMap(self):
        
        ep_name=self.field("ep_app")

        if self.tree_switch==1:
            light_folder_asset_list=unreal.EditorAssetLibrary.list_assets('/Game/Shots/%s'%(self.ep_flie_list[ep_name]))
            light_sc_flie_lists=[]
            self.world_find_assets=[]
            self.sequnence_find_assets=[]
            for light_folder_asset in light_folder_asset_list:
                asset_find=unreal.EditorAssetLibrary.find_asset_data(light_folder_asset)
                light_asset_class=asset_find.get_class().get_name()
                if '_Map' in light_folder_asset:
                    
                    if light_asset_class=='World':
                        #确定world资产
                        world_asset_name=asset_find.get_asset().get_name()
                        world_asset_path=asset_find.get_asset().get_path_name()
                        if '_Map' in world_asset_name and 'Preview' not in world_asset_path:
                            #获取灯光路径名
                            light_flie_sc_name=world_asset_path.rsplit('/')[-3]
                            #添加信息到列表
                            self.world_asset_names.append(world_asset_name)
                            self.world_find_assets.append(asset_find)
                            light_sc_flie_lists.append(light_flie_sc_name)
                if light_asset_class=='LevelSequence':
                    #收集sequnence资产
                    sequnence_asset=unreal.EditorAssetLibrary.find_asset_data(light_folder_asset)
                    self.sequnence_find_assets.append(sequnence_asset)

        
                
            #简化sc数据内容
            self.light_sc_flie_list=[]
            for sc_flie in light_sc_flie_lists:
                if sc_flie not in self.light_sc_flie_list:
                    self.light_sc_flie_list.append(sc_flie)

            
            #创建TreeView数据树
            self.model_map.clear()
            self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
            if self.light_sc_flie_list:
                for light_sc in self.light_sc_flie_list:
                    #创建一级菜单
                    tree_1=QtGui.QStandardItem(light_sc)
                    for world_assets_name in self.world_find_assets:
                        if light_sc==world_assets_name.get_asset().get_path_name().rsplit('/',3)[-3]:
                            tree_2=QtGui.QStandardItem(world_assets_name.get_asset().get_name())
                            tree_1.appendRow(tree_2)
                    self.model_map.appendRow(tree_1) 
            
    def chQueryClicked(self):
        if 'Content' in self.ch_path_text.text():
            self.ch_path_text.setText('/Game'+self.ch_path_text.text().split('Content',1)[1])
        self.find_ch_assets=[]
        self.queryPath(path_class='ch')
    def proQueryClicked(self):
        if 'Content' in self.pro_path_text.text():
            self.pro_path_text.setText('/Game'+self.pro_path_text.text().split('Content',1)[1])
        self.find_pro_assets=[]
        self.queryPath(path_class='pro')
    def levelQueryClicked(self):
        if 'Content' in self.level_path_text.text():
            self.level_path_text.setText('/Game'+self.level_path_text.text().split('Content',1)[1])
        self.find_level_assets=[]
        self.queryPath(path_class='level')

    def queryPath(self,path_class):

        asset_ch_list_name=[]
        asset_pro_list_name=[]
        asset_level_list_name=[]
        self.assets_ch=[]
        self.assets_pro=[]
        
     
        #同步列表信息
        if path_class=='ch':
            if unreal.EditorAssetLibrary().does_directory_exist(self.ch_path_text.text())==1:
                self.asset_ch_list=unreal.EditorAssetLibrary.list_assets(self.ch_path_text.text())
                for ch_name in self.asset_ch_list:
                    if unreal.EditorAssetLibrary.find_asset_data(ch_name).get_asset().get_class().get_name()=='Blueprint':
                        self.find_ch_assets.append(unreal.EditorAssetLibrary.find_asset_data(ch_name))
                        asset_ch_list_name.append(unreal.EditorAssetLibrary.find_asset_data(ch_name).get_asset().get_name())               
                # self.radio_group_ch.set_button_list(asset_ch_list_name) 
                # self.radio_group_ch.setMaximumHeight(len(asset_ch_list_name)*16)
                # self.radio_group_ch.setMinimumSize(300,len(asset_ch_list_name)*16)
                check_spin_box_ch = self.checkSpinBox(asset_ch_list_name)
                self.scroll_ch.setWidget(check_spin_box_ch)
                     
            else:
                pass

        if path_class=='pro':
            if unreal.EditorAssetLibrary().does_directory_exist(self.pro_path_text.text())==1:
                self.asset_pro_list=unreal.EditorAssetLibrary.list_assets(self.pro_path_text.text())
                for pro_name in self.asset_pro_list:
                    if unreal.EditorAssetLibrary.find_asset_data(pro_name).get_asset().get_class().get_name()=='Blueprint':
                        self.find_pro_assets.append(unreal.EditorAssetLibrary.find_asset_data(pro_name))
                        asset_pro_list_name.append(unreal.EditorAssetLibrary.find_asset_data(pro_name).get_asset().get_name())
                
                check_spin_box_pro = self.checkSpinBox(asset_pro_list_name)
                self.scroll_pro.setWidget(check_spin_box_pro)
        
                
        if path_class=='level':
            if unreal.EditorAssetLibrary().does_directory_exist(self.level_path_text.text()):
                self.asset_level_list=unreal.EditorAssetLibrary.list_assets(self.level_path_text.text())
                for level_name in self.asset_level_list:
                    level_asset_name=unreal.EditorAssetLibrary.find_asset_data(level_name).get_asset().get_name()
                    if unreal.EditorAssetLibrary.find_asset_data(level_name).get_asset().get_class().get_name()=='World' and 'Shade' == level_asset_name.split('_')[-1]:
                        self.find_level_assets.append(unreal.EditorAssetLibrary.find_asset_data(level_name))
                        asset_level_list_name.append(level_asset_name)
                    
                self.radio_group_level.set_button_list(asset_level_list_name)
                self.radio_group_level.setMaximumHeight(len(asset_level_list_name)*16)
                self.radio_group_level.setMinimumSize(300,len(asset_level_list_name)*16)
                



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
