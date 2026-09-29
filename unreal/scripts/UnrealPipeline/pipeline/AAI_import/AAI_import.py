
import unreal

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

import time


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
from dayu_widgets.switch import MSwitch

from dayu_widgets import dayu_theme
from dayu_widgets.qt import application

import UnrealPipeline.core.uSTools as uSTools


print('AAI 1.4')

level_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level_sequence_editor_subsystem = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)



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
    level_path_d='/Game/Assets/Scenes'
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
    clicked_name1=None
    button_name=None

    #流程模式shot目录
    shot_path='/Game/Shots'

    

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
        self.resize(1200,600)

        
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

        #场景下列表
        self.level_path_text_d=MLineEdit(text=self.level_path_d).small()

        level_path_text_button_d = MClickBrowserFolderToolButton()
        level_path_text_button_d.sig_folder_changed.connect(self.level_path_text_d.setText)
        level_path_text_button_d.clicked.connect(self.levelQueryClicked)

        self.level_path_text_d.set_suffix_widget(level_path_text_button_d)
        self.level_path_text_d.returnPressed.connect(self.levelQueryClicked)



        self.radio_group_level = MCheckBoxGroup(orientation=QtCore.Qt.Vertical)
        # self.radio_group_level = MRadioButtonGroup(orientation=QtCore.Qt.Vertical)
        self.radio_group_level.set_button_list(self.k)
        self.radio_group_level.set_spacing(1)
        # self.radio_group_level.sig_checked_changed.connect(lambda:self.soloButton('level1'))
        self.radio_group_level.get_button_group().buttonClicked.connect(lambda:self.soloButton('level1'))

        self.radio_group_level_d = MCheckBoxGroup(orientation=QtCore.Qt.Vertical)
        self.radio_group_level_d.set_button_list(self.k)
        self.radio_group_level_d.set_spacing(1)
        self.radio_group_level_d.get_button_group().buttonClicked.connect(lambda:self.soloButton('level2'))
        # self.radio_group_level_d.get_button_group().buttonClicked.connect(self.getLightMap)

        
        

        # self.label_level = MLabel()
        # self.label_level.setWordWrap(True)
        # self.label_level.setMaximumWidth(200)
        # self.label_level.setMinimumHeight(36)
        # self.register_field("asset_level_app")
        # self.register_field(
        #     "asset_level_app_text",lambda: "、".join(self.field("asset_level_app")) if self.field("asset_level_app") else None
        # )
        # self.bind(
        #     "asset_level_app", self.radio_group_level, "dayu_checked", signal="sig_checked_changed"
        # )
        # # self.bind("asset_level_app_text", self.label_level, "text")

        # self.register_field("asset_level_d_app")
        # self.bind(
        #     "asset_level_d_app", self.radio_group_level_d, "dayu_checked", signal="sig_checked_changed"
        # )
        
        scroll_level=QtWidgets.QScrollArea()
        scroll_level.setMinimumWidth(240)
        scroll_level.setWidget(self.radio_group_level)

        scroll_level_d=QtWidgets.QScrollArea()
        scroll_level_d.setMinimumWidth(240)
        scroll_level_d.setWidget(self.radio_group_level_d)


        lay1_1.addWidget(MDivider("角色"))
        lay1_1.addWidget(self.ch_path_text)
        lay1_1.addWidget(self.scroll_ch)
        # lay1_1.addWidget(self.label_ch)
        

        lay1_2.addWidget(MDivider("道具"))
        lay1_2.addWidget(self.pro_path_text)
        lay1_2.addWidget(self.scroll_pro)
        # lay1_2.addWidget(self.label_pro)
        

        lay1_3.addWidget(MDivider("场景"))
        lay1_3.addWidget(self.level_path_text)
        lay1_3.addWidget(scroll_level)
        lay1_3.addWidget(self.level_path_text_d)
        lay1_3.addWidget(scroll_level_d)
        # lay1_3.addWidget(self.label_level)

        lay1.addLayout(lay1_1)
        lay1.addLayout(lay1_2)
        lay1.addLayout(lay1_3)
        lay_asset.addWidget(MDivider("选择需要导入的资产"))
        lay_asset.addLayout(lay1)
        

        #右侧窗口
        #第一部分

        #ep列表
        self.radio_group_ep = MRadioButtonGroup(orientation=QtCore.Qt.Vertical)
        self.radio_group_ep.set_button_list(self.ep_flie_list)
        self.radio_group_ep.set_spacing(1)
        self.radio_group_ep.get_button_group().buttonClicked.connect(self.getLightMap)
        


        self.register_field("ep_app")
        self.register_field(
            "ep_app_text",lambda: " 、 ".join(self.field("ep_app")) if self.field("ep_app") else None
        )   
        self.bind(
            "ep_app", self.radio_group_ep, "dayu_checked", signal="sig_checked_changed"
        )
        
        scroll_ep=QtWidgets.QScrollArea()
        scroll_ep.setMinimumWidth(170)
        scroll_ep.setWidget(self.radio_group_ep)

        self.scence_bp_switch = MSwitch()
        self.scence_bp_switch.setChecked(True)
        scence_bp_switch_lay = QtWidgets.QFormLayout()
        scence_bp_switch_lay.addRow(self.scence_bp_switch,MLabel("导入场景BP"))    #关卡创建开关

        self.flow_switch = MSwitch()
        self.flow_switch.setChecked(False)
        self.flow_switch.clicked.connect(self.flowSwitch)
        flow_switch_lay = QtWidgets.QFormLayout()
        flow_switch_lay.addRow(self.flow_switch,MLabel("使用半流程规则"))    #关卡创建开关

        self.scence_retain_switch = MSwitch()
        self.scence_retain_switch.setChecked(False)
        self.scence_retain_switch.clicked.connect(self.scenceChangeSwitch)
        scence_retain_switch_lay = QtWidgets.QFormLayout()
        scence_retain_switch_lay.addRow(self.scence_retain_switch,MLabel("添加时是否保留旧场景"))    #场景替换规则开关

        self.scence_copy_switch = MSwitch()
        self.scence_copy_switch.setChecked(True)
        scence_copy_switch_lay = QtWidgets.QFormLayout()
        scence_copy_switch_lay.addRow(self.scence_copy_switch,MLabel("是否复制场景到镜头"))    #场景复制规则开关

        button_get = MPushButton(text="获取信息")
        button_get.clicked.connect(self.buttonGetClicked)

        button_clear = MPushButton(text="清除所有资产选择")
        button_clear.setMinimumWidth(135)
        button_clear.clicked.connect(self.buttonClearClicked)

        lay2_1.addWidget(scroll_ep)
        # lay2_1.addLayout(scence_bp_switch_lay)
        lay2_1.addLayout(flow_switch_lay)
        lay2_1.addLayout(scence_retain_switch_lay)
        lay2_1.addLayout(scence_copy_switch_lay)
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
        button_create.clicked.connect(self.createClicked)

        
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
        box_l.setMinimumWidth(700)
        box_l.setStyleSheet('QGroupBox{color:white;border:0px ;}')
        box_r=QtWidgets.QGroupBox()
        box_r.setMinimumWidth(350)
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



    def createClicked(self):

        world_asset_find_list=[]
        sequnence_asset_find_list=[]

        #获取UI选项名称
        # asset_ch_names=self.field("asset_CH_app")
        asset_ch_names_dict = self.checkSpinData(self.scroll_ch.widget())
        # asset_pro_names=self.field("asset_pro_app")
        asset_pro_names_dict = self.checkSpinData(self.scroll_pro.widget())
        # asset_level_names=self.field("asset_level_app")

        # level_BP = None
        level_BPs = []

        #获取所选场景资产名称
        
        asset_level_d_data=self.radio_group_level_d.get_dayu_checked()
        asset_level_names=self.radio_group_level.get_dayu_checked()
        if asset_level_d_data:
            asset_level_names = asset_level_d_data
            # asset_level_name=asset_level_d_data[0]
            for asset_level_name in asset_level_d_data:
                try:
                    #当场景后缀为Shade时,添加bp文件
                    if asset_level_name.split('_')[-1] == 'Shade':
                        level_BPs.append(self.asset_level_d_BP_dict[asset_level_name])
                    # level_BP=self.asset_level_d_BP_dict[asset_level_name]
                except:
                    pass
            find_level_assets=self.find_level_d_assets
        elif asset_level_names:
            # asset_level_name=asset_level_data[0]
            for asset_level_name in asset_level_names:
                try:
                    if asset_level_name.split('_')[-1] == 'Shade':
                        level_BPs.append(self.asset_level_BP_dict[asset_level_name])
                except:
                    pass
            find_level_assets=self.find_level_assets
        else :
            asset_level_names=None
        ep_name=self.field("ep_app")

        print(self.asset_level_d_BP_dict)

        if self.select_world_names:
            
            # 通过选择的场景获取对应的场景资产
            for select_world_name in self.select_world_names:
                for world_asset_find in self.world_find_assets:
                    if select_world_name==uSTools.assetDataToAssetName(world_asset_find):
                        world_asset_find_list.append(world_asset_find)
                #通过选择的关卡序列获取对应的关卡序列
                for sequnence_find_asset in self.sequnence_find_assets:
                    # print(sequnence_find_asset)
                    if select_world_name.replace('_Map','_an')==uSTools.assetDataToAssetName(sequnence_find_asset):
                        sequnence_asset_find_list.append(sequnence_find_asset)


            #对场景添加资产
            print(world_asset_find_list)
            for final_map_asset_data in world_asset_find_list: 
                # unreal.LevelEditorSubsystem().load_level(final_map_asset_data.get_asset().get_path_name())
                
                if asset_level_names:
                    for asset_level_name in asset_level_names:
                        for find_level_asset in find_level_assets:
                            find_level_asset_name=uSTools.assetDataToAssetName(find_level_asset)
                            
                            if find_level_asset_name==asset_level_name:
                                source_asset_level_path = find_level_asset.get_asset().get_path_name()
                                #Light场景放在Light文件夹,其余的放在Modify文件夹
                                if '_Light' in find_level_asset_name:
                                    des_level_path = final_map_asset_data.get_asset().get_path_name().rsplit('/',1)[0]+'/Lighting'
                                else:
                                    des_level_path = final_map_asset_data.get_asset().get_path_name().rsplit('/',1)[0]+'/Modify/Scenes'
                                asset_level_name = find_level_asset.get_asset().get_name()
                                asset_level_path = des_level_path+'/'+asset_level_name
                                unreal.LevelEditorSubsystem().load_level(final_map_asset_data.get_asset().get_path_name())
                                #判断是否保留旧场景
                                if self.scence_retain_switch.isChecked():
                                    #将源关卡复制到对应目录下,若已存在则跳过此场
                                    if unreal.EditorAssetLibrary().does_asset_exist(asset_level_path):
                                        asset_level_path = None
                                    #判断是否为复制添加
                                    elif self.scence_copy_switch.isChecked():
                                        unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(asset_name=asset_level_name,package_path=des_level_path,original_object=find_level_asset.get_asset())
                                    #不为复制模式时,直接调用源文件
                                    else:
                                        asset_level_path = source_asset_level_path
                                #不保留旧场景
                                else:
                                    #删除关卡中的同名关卡
                                    current_world = unreal_editor_subsystem.get_editor_world()
                                    levels = unreal.EditorLevelUtils().get_levels(current_world)
                                    #清除重复子level
                                    for level in levels:
                                        if level.get_path_name().split(':')[0].split('.')[-1] == asset_level_name:
                                            unreal.PythonExtensionBPLibrary.remove_level_from_world(level,True,False)
                                    try:
                                        unreal.EditorAssetLibrary().delete_asset(asset_level_path)
                                    except:
                                        pass
                                    #判断是否为复制添加
                                    if self.scence_copy_switch.isChecked():
                                        #将源关卡复制到对应目录下
                                        unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(asset_name=asset_level_name,package_path=des_level_path,original_object=find_level_asset.get_asset())
                                    #不为复制模式时,直接调用源文件
                                    else:
                                        asset_level_path = source_asset_level_path

                                print(asset_level_path)
                                if asset_level_path:
                                    unreal.EditorLevelUtils().add_level_to_world(final_map_asset_data.get_asset(),level_package_name=asset_level_path,level_streaming_class=unreal.LevelStreamingAlwaysLoaded)
                                    unreal.EditorAssetLibrary.save_directory('/Game')
                                    unreal.LevelEditorSubsystem().load_level(final_map_asset_data.get_asset().get_path_name())
                
                #打开an map
                an_map_basepath = final_map_asset_data.get_asset().get_path_name().rsplit('/',1)[0]
                an_map_name = final_map_asset_data.get_asset().get_name().replace('_Map','_an_Map')
                an_map_path = an_map_basepath+'/Animation/'+an_map_name
                if unreal.EditorAssetLibrary().does_asset_exist(an_map_path):
                    unreal.LevelEditorSubsystem().load_level(an_map_path)
                else:
                    unreal.LevelEditorSubsystem().load_level(final_map_asset_data.get_asset().get_path_name())

                #对动画关卡序列添加资产
                for sequnence_asset_find in sequnence_asset_find_list:
                    #添加道具
                    if final_map_asset_data.get_asset().get_name().replace('_Map','_an')==uSTools.assetDataToAssetName(sequnence_asset_find):
                        
                        if asset_pro_names_dict:
                            for find_pro_asset in self.find_pro_assets:
                                find_ch_asset_name=uSTools.assetDataToAssetName(find_pro_asset)
                                for asset_pro_name,value in asset_pro_names_dict.items():
                                    if value > 1:
                                        if asset_pro_name==find_ch_asset_name:
                                            for i in range(value):
                                                add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(find_pro_asset.get_asset(),unreal.Vector(0.0, 0.0, 0.0))
                                                sequnence_asset_find.get_asset().add_possessable(add_actor)
                                    else:
                                        if asset_pro_name==find_ch_asset_name:
                                            add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(find_pro_asset.get_asset(),unreal.Vector(0.0, 0.0, 0.0))
                                            sequnence_asset_find.get_asset().add_possessable(add_actor)

                        #添加角色
                        if asset_ch_names_dict:
                            for find_ch_asset in self.find_ch_assets:
                                find_ch_asset_name=uSTools.assetDataToAssetName(find_ch_asset)
                                for asset_ch_name,value in asset_ch_names_dict.items():
                                    if value > 1:
                                        if asset_ch_name==find_ch_asset_name:
                                            for i in range(value):
                                                # sequnence_asset_find.get_asset().add_spawnable_from_instance(find_ch_asset.get_asset())

                                                #创建actor并添加到关卡序列
                                                add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(find_ch_asset.get_asset(),unreal.Vector(0.0, 0.0, 0.0))
                                                sequnence_asset_find.get_asset().add_possessable(add_actor)
                                    else:
                                        if asset_ch_name==find_ch_asset_name:
                                            # sequnence_asset_find.get_asset().add_spawnable_from_instance(find_ch_asset.get_asset())

                                            add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(find_ch_asset.get_asset(),unreal.Vector(0.0, 0.0, 0.0))
                                            sequnence_asset_find.get_asset().add_possessable(add_actor)
                        #添加场景BP资产
                        for level_BP in level_BPs:
                            if level_BP and self.scence_bp_switch.isChecked():  #当打开导入开关时导入BP
                                print(level_BP)
                                #创建actor并添加到关卡序列
                                add_actor=unreal.EditorLevelLibrary.spawn_actor_from_object(level_BP,unreal.Vector(0.0, 0.0, 0.0))
                                sequnence_asset_find.get_asset().add_possessable(add_actor)
                unreal.EditorAssetLibrary.save_directory('/Game')



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
        

    def soloButton(self,widget_name):
        

        if widget_name=='level1':
            self.radio_group_level_d.set_dayu_checked([])
            button_group=self.radio_group_level.get_button_group()
            radio_group=self.radio_group_level
        elif widget_name=='level2':
            self.radio_group_level.set_dayu_checked([])
            button_group=self.radio_group_level_d.get_button_group()
            radio_group=self.radio_group_level_d

        # index=button_group.checkedId()
        # if index != -1:
        #     button_text=button_group.button(index).text()
        # else:
        #     button_text=None
        # if button_text!=self.button_name:
        #     self.button_name=button_text
        #     print(button_text)
        #     radio_group.set_dayu_checked([self.button_name])
        # else:
        #     pass


    def flowSwitch(self):
        if self.flow_switch.isChecked():
            self.scence_copy_switch.setChecked(False)
            # self.shot_path='/Game/Assets/Shots'
        # else:
            # self.shot_path='/Game/Shots'

        self.getEpList()
        self.radio_group_ep.set_button_list(self.ep_flie_list)
        self.getLightMap()
        self.levelQueryClicked()
    

    def scenceChangeSwitch(self):
        pass


        


    def buttonClearClicked(self,check_spin_box:QtWidgets.QGroupBox):
        # self.radio_group_level.set_button_list([])
        # self.radio_group_level.set_button_list(self.asset_level_list_name)

        # self.radio_group_level_d.set_button_list([])
        # self.radio_group_level_d.set_button_list(self.asset_level_list_d_name)


        self.radio_group_level.set_dayu_checked([])
        self.radio_group_level_d.set_dayu_checked([])




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
        shots_path=self.shot_path
        while ep_i<100:
            ep_i_str=str(ep_i).zfill(3)
            ep_path='%s/Ep%s'%(shots_path,ep_i_str)
            aa1=unreal.EditorAssetLibrary().does_directory_exist(ep_path)
            ep_path2='%s/EP%s'%(shots_path,ep_i_str)
            aa2=unreal.EditorAssetLibrary().does_directory_exist(ep_path2)
            if aa1==1 or aa2==1:
                self.ep_flie_list.append('EP%s'%ep_i_str)
                self.tree_switch=1
            ep_i+=1
        # print(self.ep_flie_list)


    def getLightMap(self):
        
        ep_name=self.field("ep_app")
        self.light_sc_flie_list=[]
        
            
        if self.tree_switch==1:
            world_all_find_assets=uSTools.assetFilter(class_name='World',folder='%s/%s'%(self.shot_path,self.ep_flie_list[ep_name]))
            self.world_find_assets=[]
            world_find_dict={}
            for world_find in world_all_find_assets:
                
                world_name=uSTools.assetDataToAssetName(world_find)
                #过滤名称
                if '_Map' in world_name and '_an_Map' not in world_name and '_VFX_Map' not in world_name and '_lt_Map' not in world_name :
                    #收集符合名称的world资产
                    self.world_find_assets.append(world_find)
                    
                    #确定world资产
                    # world_asset_path=world_find.get_asset().get_path_name()
                    world_asset_path=uSTools.assetDataToAssetPath(world_find)
                    if 'Preview' not in world_asset_path:
                        #获取灯光路径名
                        light_flie_sc_name=world_asset_path.rsplit('/')[-2]
                        # print(world_asset_path)

                        try:
                            world_find_dict[light_flie_sc_name].append(world_find)
                        except:
                            world_find_dict[light_flie_sc_name]=[]
                            world_find_dict[light_flie_sc_name].append(world_find)

                        #添加信息到列表
                        self.world_asset_names.append(world_name)
                        #获取场次名称
                        if light_flie_sc_name not in self.light_sc_flie_list:
                            self.light_sc_flie_list.append(light_flie_sc_name)
            
            # print(time.time()-aaa)

            #收集关卡序列
            self.sequnence_find_assets=uSTools.assetFilter(class_name='LevelSequence',folder='%s/%s'%(self.shot_path,self.ep_flie_list[ep_name]))

        

            
            
            #创建TreeView数据树
            self.model_map.clear()
            self.model_map.setHorizontalHeaderLabels([self.tr("目标场景目录")])
            if self.light_sc_flie_list:
                #列表排序
                self.light_sc_flie_list.sort()
                for light_sc in self.light_sc_flie_list:
                    #创建一级菜单
                    tree_1=QtGui.QStandardItem(light_sc)
                    for world_sc_name,world_find_list in world_find_dict.items():    
                        world_asset_names = []
                        for world_find in world_find_list:
                            world_asset_name=uSTools.assetDataToAssetName(world_find)
                            world_asset_names.append(world_asset_name)
                        world_asset_names.sort()
                        
                        if light_sc==world_sc_name:
                            for world_asset_name in world_asset_names:
                                tree_2=QtGui.QStandardItem(world_asset_name)
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
        if 'Content' in self.level_path_text_d.text():
            self.level_path_text_d.setText('/Game'+self.level_path_text_d.text().split('Content',1)[1])
        self.find_level_assets=[]
        self.queryPath(path_class='level')

    def queryPath(self,path_class):

        asset_ch_list_name=[]
        asset_pro_list_name=[]
        self.asset_level_list_name=[]
        self.asset_level_list_d_name=[]
        self.assets_ch=[]
        self.assets_pro=[]
        
     
        #同步列表信息
        if path_class=='ch':
            if unreal.EditorAssetLibrary().does_directory_exist(self.ch_path_text.text())==1:
                self.find_ch_assets=uSTools.assetFilter(class_name='Blueprint',folder=self.ch_path_text.text())
                
                # print(self.find_ch_assets)
                for ch_name in self.find_ch_assets:
                #     asset_ch_list_name.append(ch_name.get_asset().get_name())
                    asset_ch_list_name.append(uSTools.assetDataToAssetName(ch_name))
                asset_ch_list_name.sort()
                check_spin_box_ch = self.checkSpinBox(asset_ch_list_name)
                self.scroll_ch.setWidget(check_spin_box_ch)
                     
            else:
                pass

        if path_class=='pro':
            
            if unreal.EditorAssetLibrary().does_directory_exist(self.pro_path_text.text())==1:
                self.find_pro_assets=uSTools.assetFilter(class_name='Blueprint',folder=self.pro_path_text.text())
                
                # self.asset_pro_list=unreal.EditorAssetLibrary.list_assets(self.pro_path_text.text())

                for pro_name in self.find_pro_assets:
                    # print(pro_name)
                #     # if unreal.EditorAssetLibrary.find_asset_data(pro_name).get_asset().get_class().get_name()=='Blueprint':
                #         # self.find_pro_assets.append(unreal.EditorAssetLibrary.find_asset_data(pro_name))
                    # asset_pro_list_name.append(pro_name.get_asset().get_name())
                    asset_pro_list_name.append(uSTools.assetDataToAssetName(pro_name))
                asset_pro_list_name.sort()
                check_spin_box_pro = self.checkSpinBox(asset_pro_list_name)
                self.scroll_pro.setWidget(check_spin_box_pro)

            
                
        if path_class=='level':
            self.asset_level_BP_dict={}
            self.asset_level_d_BP_dict={}
            if unreal.EditorAssetLibrary().does_directory_exist(self.level_path_text.text()):
                self.find_level_assets=uSTools.assetFilter(class_name='World',folder=self.level_path_text.text())
                # self.asset_level_list=unreal.EditorAssetLibrary.list_assets(self.level_path_text.text())
                for level_data in self.find_level_assets:
                    # level_asset_name=level_name.get_asset().get_name()
                    level_asset_name=uSTools.assetDataToAssetName(level_data)
                    level_asset_path=uSTools.assetDataToAssetPath(level_data)
                    if '_Shade' in level_asset_name or '_VFX' in level_asset_name or '_Light' in level_asset_name:
                        # self.find_level_assets.append(unreal.EditorAssetLibrary.find_asset_data(level_name))
                        
                        self.asset_level_list_name.append(level_asset_name)
                        asset_path=level_asset_path+'/Scenes_Pro/'+level_asset_name.rsplit('_',1)[0]+'_BP'
                        if unreal.EditorAssetLibrary().does_asset_exist(asset_path) and 'Shade' == level_asset_name.split('_')[-1]:
                            #收集关卡里的BP资产
                            self.asset_level_BP_dict[level_asset_name]=unreal.EditorAssetLibrary().load_asset(asset_path)
                self.asset_level_list_name.sort()
                self.radio_group_level.set_button_list(self.asset_level_list_name)
                self.radio_group_level.setMaximumHeight(len(self.asset_level_list_name)*16)
                self.radio_group_level.setMinimumSize(300,len(self.asset_level_list_name)*16)
            
            if unreal.EditorAssetLibrary().does_directory_exist(self.level_path_text_d.text()):
                self.find_level_d_assets=uSTools.assetFilter(class_name='World',folder=self.level_path_text_d.text())
                # self.asset_level_list=unreal.EditorAssetLibrary.list_assets(self.level_path_text.text())
                for level_data in self.find_level_d_assets:
                    level_asset_path=uSTools.assetDataToAssetPath(level_data)
                    level_asset_name=uSTools.assetDataToAssetName(level_data)
                    #当模式为半流程时不做level名称过滤
                    if self.flow_switch.isChecked():
                        self.asset_level_list_d_name.append(level_asset_name)
                        asset_path=level_asset_path.replace('/Assets/','/AAI/Reference/').split('/Map/Level')[0]+'/Scenes_Pro/'+level_asset_name.rsplit('_',2)[0]+'_AAI_BP'
                        if unreal.EditorAssetLibrary().does_asset_exist(asset_path) and 'Shade' == level_asset_name.split('_')[-1]:
                            #收集关卡里的BP资产
                            self.asset_level_d_BP_dict[level_asset_name]=unreal.EditorAssetLibrary().load_asset(asset_path)

                    elif '_Shade' in level_asset_name or '_VFX' in level_asset_name or '_Light' in level_asset_name:
                        # self.find_level_assets.append(unreal.EditorAssetLibrary.find_asset_data(level_name))
                        self.asset_level_list_d_name.append(level_asset_name)
                        asset_path=level_asset_path.replace('/Assets/','/AAI/Reference/').split('/Map/Level')[0]+'/Scenes_Pro/'+level_asset_name.rsplit('_',2)[0]+'_AAI_BP'
                        if unreal.EditorAssetLibrary().does_asset_exist(asset_path) and 'Shade' == level_asset_name.split('_')[-1]:
                            #收集关卡里的BP资产
                            self.asset_level_d_BP_dict[level_asset_name]=unreal.EditorAssetLibrary().load_asset(asset_path)
                self.asset_level_list_d_name.sort()
                self.radio_group_level_d.set_button_list(self.asset_level_list_d_name)
                self.radio_group_level_d.setMaximumHeight(len(self.asset_level_list_d_name)*16)
                self.radio_group_level_d.setMinimumSize(300,len(self.asset_level_list_d_name)*16)
                



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
