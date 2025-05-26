# -*- coding: utf-8 -*-
import os,sys,json,re,time,datetime,collections,tempfile
from PySide2 import QtCore, QtGui, QtWidgets
import functools
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.mel as mel
import maya.cmds as cmds
import arnold as ar
from pprint import pprint
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI
# from dayu_widgets.toast import MToast


def mayaMainWindows():
    mainWindowsPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(mainWindowsPtr),QtWidgets.QWidget)

class Ui_Unt_Tool_Window(object):
    def __init__(self):
        self.project_path = "Z:/RcP"
        self.assembly_sel_path = ''#组装功能选择的路径
        self.simple_export_filepath = ""#标准组件导出路径
        self.simple_listwidget_itempath = {}#标准组件加载列表字典 {名字：路径}
        self.refresh_tablewidget_dic = {'path':"", "find_type":""}
        self.progressBar_maxvalue = 0
        self.menu_action_list = [] #右键筛选列表
        docpath = os.path.expanduser('~')
        self.json_path = u'''{}/hyperscene_default_setting.json'''.format(docpath).replace("\\","/")
        self.temp_file = '''{}/hyperscene_log.txt'''.format(tempfile.gettempdir()).replace("\\","/")
        self.icon_size = None
        self.unt_attr_dic = {'ass' : 'assShapePath',
                            'gpu'  : 'gpuShapePath',
                            'diy'  : 'gpuDIYPath',
                            'bbox' : 'gpuBBoxPath',
                            'ma'   : 'maPath',
                            'usd'  : 'usdPath'}
        self.bbox_color_dic = collections.OrderedDict()
        self.bbox_color_dic[u"树木Tree"]       = [[0.47,0.62,0.39],[121,159,100]]
        self.bbox_color_dic[u"草类Grass"]      = [[0.49,0.63,0.30],[125,160,77]]
        self.bbox_color_dic[u"带花植物Flower"] = [[0.85,0.62,0.49],[218,158,126]]
        self.bbox_color_dic[u"灌木Bush"]       = [[0.63,0.65,0.33],[161,165,85]]
        self.bbox_color_dic[u"山石Rock"]       = [[0.67,0.58,0.55],[170,148,139]]
        self.bbox_color_dic[u"建筑物Building"] = [[0.74,0.73,0.63],[188,186,160]]
        self.bbox_color_dic[u"地形Terrain"]    = [[0.67,0.67,0.67],[170,170,170]]
        self.bbox_color_dic[u"水体类Water"]    = [[0.43,0.91,0.85],[110,231,218]]
        self.bbox_color_dic[u"大杂烩Mix"]      = [[0.79,0.72,0.80],[201,183,203]]
        self.bbox_color_dic[u"其他Other"]      = [[0.53,0.59,0.53],[136,151,136]]
#################################################################################################################################################
#
#  UI
#
#################################################################################################################################################
    def setupUi(self, Unt_Tool_Window):
        Unt_Tool_Window.setObjectName("Unt_Tool_Window")
        Unt_Tool_Window.resize(563, 742)
        self.gridLayout_3 = QtWidgets.QGridLayout(Unt_Tool_Window)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tabWidget = QtWidgets.QTabWidget(Unt_Tool_Window)
        self.tabWidget.setObjectName("tabWidget")
        self.unt_cut = QtWidgets.QWidget()
        self.unt_cut.setObjectName("unt_cut")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.unt_cut)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.sel_unt_range_grp = QtWidgets.QGroupBox(self.unt_cut)
        self.sel_unt_range_grp.setMaximumSize(QtCore.QSize(16777215, 70))
        self.sel_unt_range_grp.setObjectName("sel_unt_range_grp")
        self.gridLayout = QtWidgets.QGridLayout(self.sel_unt_range_grp)
        self.gridLayout.setObjectName("gridLayout")
        self.sel_mod_all = QtWidgets.QRadioButton(self.sel_unt_range_grp)
        self.sel_mod_all.setMaximumSize(QtCore.QSize(16777215, 50))
        self.sel_mod_all.setObjectName("sel_mod_all")
        self.gridLayout.addWidget(self.sel_mod_all, 0, 1, 1, 1)
        self.sel_mod_selections = QtWidgets.QRadioButton(self.sel_unt_range_grp)
        self.sel_mod_selections.setMaximumSize(QtCore.QSize(16777215, 25))
        self.sel_mod_selections.setObjectName("sel_mod_selections")
        self.gridLayout.addWidget(self.sel_mod_selections, 0, 0, 1, 1)
        self.sel_mod_childs = QtWidgets.QCheckBox(self.sel_unt_range_grp)
        self.sel_mod_childs.setEnabled(True)
        self.sel_mod_childs.setMaximumSize(QtCore.QSize(16777215, 50))
        self.sel_mod_childs.setAcceptDrops(False)
        self.sel_mod_childs.setChecked(True)
        self.sel_mod_childs.setObjectName("sel_mod_childs")
        self.gridLayout.addWidget(self.sel_mod_childs, 1, 0, 1, 1)
        self.verticalLayout_14.addWidget(self.sel_unt_range_grp)
        self.groupBox_4 = QtWidgets.QGroupBox(self.unt_cut)
        self.groupBox_4.setMaximumSize(QtCore.QSize(16777215, 110))
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter_19 = QtWidgets.QSplitter(self.groupBox_4)
        self.splitter_19.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_19.setObjectName("splitter_19")
        self.select_obj_preview = QtWidgets.QPushButton(self.splitter_19)
        self.select_obj_preview.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_obj_preview.setObjectName("select_obj_preview")
        self.select_obj_cl = QtWidgets.QPushButton(self.splitter_19)
        self.select_obj_cl.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_obj_cl.setObjectName("select_obj_cl")
        self.select_obj_unt = QtWidgets.QPushButton(self.splitter_19)
        self.select_obj_unt.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_obj_unt.setObjectName("select_obj_unt")
        self.select_unt_reverse = QtWidgets.QPushButton(self.splitter_19)
        self.select_unt_reverse.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_unt_reverse.setObjectName("select_unt_reverse")
        self.select_cteate_set = QtWidgets.QPushButton(self.splitter_19)
        self.select_cteate_set.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_cteate_set.setObjectName("select_cteate_set")
        self.verticalLayout_2.addWidget(self.splitter_19)
        self.splitter_20 = QtWidgets.QSplitter(self.groupBox_4)
        self.splitter_20.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_20.setObjectName("splitter_20")
        self.select_gpumesh = QtWidgets.QPushButton(self.splitter_20)
        self.select_gpumesh.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_gpumesh.setObjectName("select_gpumesh")
        self.select_gpubbox = QtWidgets.QPushButton(self.splitter_20)
        self.select_gpubbox.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_gpubbox.setObjectName("select_gpubbox")
        self.select_gpudiy = QtWidgets.QPushButton(self.splitter_20)
        self.select_gpudiy.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_gpudiy.setObjectName("select_gpudiy")
        self.select_no_ass = QtWidgets.QPushButton(self.splitter_20)
        self.select_no_ass.setMaximumSize(QtCore.QSize(16777215, 50))
        self.select_no_ass.setObjectName("select_no_ass")
        self.verticalLayout_2.addWidget(self.splitter_20)
        self.verticalLayout_14.addWidget(self.groupBox_4)
        self.gpu_refacto_grp = QtWidgets.QGroupBox(self.unt_cut)
        self.gpu_refacto_grp.setObjectName("gpu_refacto_grp")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.gpu_refacto_grp)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.splitter_15 = QtWidgets.QSplitter(self.gpu_refacto_grp)
        self.splitter_15.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_15.setObjectName("splitter_15")
        self.gpu_refacto_unt_tex = QtWidgets.QLabel(self.splitter_15)
        self.gpu_refacto_unt_tex.setMinimumSize(QtCore.QSize(80, 0))
        self.gpu_refacto_unt_tex.setMaximumSize(QtCore.QSize(60, 16777215))
        self.gpu_refacto_unt_tex.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.gpu_refacto_unt_tex.setObjectName("gpu_refacto_unt_tex")
        self.gpu_refacto_refresh_but = QtWidgets.QPushButton(self.splitter_15)
        self.gpu_refacto_refresh_but.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_refacto_refresh_but.setObjectName("gpu_refacto_refresh_but")
        self.gpu_refacto_ma_ref = QtWidgets.QPushButton(self.splitter_15)
        self.gpu_refacto_ma_ref.setObjectName("gpu_refacto_ma_ref")
        self.gpu_refacto_ma_remove = QtWidgets.QPushButton(self.splitter_15)
        self.gpu_refacto_ma_remove.setObjectName("gpu_refacto_ma_remove")
        self.verticalLayout_7.addWidget(self.splitter_15)
        self.splitter_16 = QtWidgets.QSplitter(self.gpu_refacto_grp)
        self.splitter_16.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_16.setObjectName("splitter_16")
        self.gpu_refacto_gpu_tex = QtWidgets.QLabel(self.splitter_16)
        self.gpu_refacto_gpu_tex.setMinimumSize(QtCore.QSize(80, 0))
        self.gpu_refacto_gpu_tex.setMaximumSize(QtCore.QSize(60, 16777215))
        self.gpu_refacto_gpu_tex.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.gpu_refacto_gpu_tex.setObjectName("gpu_refacto_gpu_tex")
        self.gpu_refacto_gpu_add_bbox = QtWidgets.QPushButton(self.splitter_16)
        self.gpu_refacto_gpu_add_bbox.setObjectName("gpu_refacto_gpu_add_bbox")
        self.gpu_refacto_gpu_del = QtWidgets.QPushButton(self.splitter_16)
        self.gpu_refacto_gpu_del.setObjectName("gpu_refacto_gpu_del")
        self.verticalLayout_7.addWidget(self.splitter_16)
        self.splitter_17 = QtWidgets.QSplitter(self.gpu_refacto_grp)
        self.splitter_17.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_17.setObjectName("splitter_17")
        self.gpu_refacto_ass_tex = QtWidgets.QLabel(self.splitter_17)
        self.gpu_refacto_ass_tex.setMinimumSize(QtCore.QSize(80, 0))
        self.gpu_refacto_ass_tex.setMaximumSize(QtCore.QSize(60, 16777215))
        self.gpu_refacto_ass_tex.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.gpu_refacto_ass_tex.setObjectName("gpu_refacto_ass_tex")
        self.gpu_refacto_ass_add = QtWidgets.QPushButton(self.splitter_17)
        self.gpu_refacto_ass_add.setObjectName("gpu_refacto_ass_add")
        self.gpu_refacto_ass_del = QtWidgets.QPushButton(self.splitter_17)
        self.gpu_refacto_ass_del.setObjectName("gpu_refacto_ass_del")
        self.verticalLayout_7.addWidget(self.splitter_17)
        self.verticalLayout_14.addWidget(self.gpu_refacto_grp)
        self.unt_display_change_grp = QtWidgets.QGroupBox(self.unt_cut)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.unt_display_change_grp.sizePolicy().hasHeightForWidth())
        self.unt_display_change_grp.setSizePolicy(sizePolicy)
        self.unt_display_change_grp.setObjectName("unt_display_change_grp")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.unt_display_change_grp)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter_3 = QtWidgets.QSplitter(self.unt_display_change_grp)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName("splitter_3")
        self.cut_to = QtWidgets.QLabel(self.splitter_3)
        self.cut_to.setMaximumSize(QtCore.QSize(80, 50))
        self.cut_to.setObjectName("cut_to")
        self.gpu_bbox = QtWidgets.QPushButton(self.splitter_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_bbox.sizePolicy().hasHeightForWidth())
        self.gpu_bbox.setSizePolicy(sizePolicy)
        self.gpu_bbox.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_bbox.setObjectName("gpu_bbox")
        self.gpu_diy = QtWidgets.QPushButton(self.splitter_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_diy.sizePolicy().hasHeightForWidth())
        self.gpu_diy.setSizePolicy(sizePolicy)
        self.gpu_diy.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_diy.setObjectName("gpu_diy")
        self.gpu_geo = QtWidgets.QPushButton(self.splitter_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_geo.sizePolicy().hasHeightForWidth())
        self.gpu_geo.setSizePolicy(sizePolicy)
        self.gpu_geo.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_geo.setObjectName("gpu_geo")
        self.verticalLayout.addWidget(self.splitter_3)
        self.splitter_4 = QtWidgets.QSplitter(self.unt_display_change_grp)
        self.splitter_4.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_4.setObjectName("splitter_4")
        self.ass_pverride_label = QtWidgets.QLabel(self.splitter_4)
        self.ass_pverride_label.setMinimumSize(QtCore.QSize(120, 0))
        self.ass_pverride_label.setMaximumSize(QtCore.QSize(130, 50))
        self.ass_pverride_label.setObjectName("ass_pverride_label")
        self.ass_pverride_comboBox = QtWidgets.QComboBox(self.splitter_4)
        self.ass_pverride_comboBox.setObjectName("ass_pverride_comboBox")
        self.ass_drawmode_label = QtWidgets.QLabel(self.splitter_4)
        self.ass_drawmode_label.setMinimumSize(QtCore.QSize(120, 0))
        self.ass_drawmode_label.setMaximumSize(QtCore.QSize(140, 50))
        self.ass_drawmode_label.setObjectName("ass_drawmode_label")
        self.ass_drawmode_comboBox = QtWidgets.QComboBox(self.splitter_4)
        self.ass_drawmode_comboBox.setObjectName("ass_drawmode_comboBox")
        self.verticalLayout.addWidget(self.splitter_4)
        self.splitter = QtWidgets.QSplitter(self.unt_display_change_grp)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.show_gpu_checkBox = QtWidgets.QCheckBox(self.splitter)
        self.show_gpu_checkBox.setObjectName("show_gpu_checkBox")
        self.show_ass_checkBox = QtWidgets.QCheckBox(self.splitter)
        self.show_ass_checkBox.setObjectName("show_ass_checkBox")
        self.show_ins_checkBox = QtWidgets.QCheckBox(self.splitter)
        self.show_ins_checkBox.setObjectName("show_ins_checkBox")
        self.show_handel_checkbox = QtWidgets.QCheckBox(self.splitter)
        self.show_handel_checkbox.setObjectName("show_handel_checkbox")
        self.two_sidedlight_checkbox = QtWidgets.QCheckBox(self.splitter)
        self.two_sidedlight_checkbox.setObjectName("two_sidedlight_checkbox")
        self.verticalLayout.addWidget(self.splitter)
        self.splitter_6 = QtWidgets.QSplitter(self.unt_display_change_grp)
        self.splitter_6.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_6.setObjectName("splitter_6")
        self.ass_preview_label_2 = QtWidgets.QLabel(self.splitter_6)
        self.ass_preview_label_2.setMinimumSize(QtCore.QSize(120, 0))
        self.ass_preview_label_2.setMaximumSize(QtCore.QSize(130, 50))
        self.ass_preview_label_2.setObjectName("ass_preview_label_2")
        self.ass_preview_comboBox = QtWidgets.QComboBox(self.splitter_6)
        self.ass_preview_comboBox.setMinimumSize(QtCore.QSize(120, 0))
        self.ass_preview_comboBox.setObjectName("ass_preview_comboBox")
        self.ass_preview_ins_tex = QtWidgets.QLabel(self.splitter_6)
        self.ass_preview_ins_tex.setMinimumSize(QtCore.QSize(120, 0))
        self.ass_preview_ins_tex.setMaximumSize(QtCore.QSize(140, 50))
        self.ass_preview_ins_tex.setObjectName("ass_preview_ins_tex")
        self.ass_preview_ins_spinbox = QtWidgets.QSpinBox(self.splitter_6)
        self.ass_preview_ins_spinbox.setMaximum(100)
        self.ass_preview_ins_spinbox.setProperty("value", 5)
        self.ass_preview_ins_spinbox.setObjectName("ass_preview_ins_spinbox")
        self.label = QtWidgets.QLabel(self.splitter_6)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.splitter_6)
        self.splitter_5 = QtWidgets.QSplitter(self.unt_display_change_grp)
        self.splitter_5.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_5.setObjectName("splitter_5")
        self.handle_on_button = QtWidgets.QPushButton(self.splitter_5)
        self.handle_on_button.setMaximumSize(QtCore.QSize(16777215, 50))
        self.handle_on_button.setObjectName("handle_on_button")
        self.handle_off_button = QtWidgets.QPushButton(self.splitter_5)
        self.handle_off_button.setMaximumSize(QtCore.QSize(16777215, 50))
        self.handle_off_button.setObjectName("handle_off_button")
        self.gpu_refresh_button = QtWidgets.QPushButton(self.splitter_5)
        self.gpu_refresh_button.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_refresh_button.setObjectName("gpu_refresh_button")
        self.ass_refresh = QtWidgets.QPushButton(self.splitter_5)
        self.ass_refresh.setMaximumSize(QtCore.QSize(16777215, 50))
        self.ass_refresh.setObjectName("ass_refresh")
        self.verticalLayout.addWidget(self.splitter_5)
        self.refresh_ogs = QtWidgets.QPushButton(self.unt_display_change_grp)
        self.refresh_ogs.setObjectName("refresh_ogs")
        self.verticalLayout.addWidget(self.refresh_ogs)
        self.verticalLayout_14.addWidget(self.unt_display_change_grp)
        self.gpu_attr_set_lay = QtWidgets.QGroupBox(self.unt_cut)
        self.gpu_attr_set_lay.setObjectName("gpu_attr_set_lay")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gpu_attr_set_lay)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gpu_renderset_on = QtWidgets.QPushButton(self.gpu_attr_set_lay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_renderset_on.sizePolicy().hasHeightForWidth())
        self.gpu_renderset_on.setSizePolicy(sizePolicy)
        self.gpu_renderset_on.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_renderset_on.setObjectName("gpu_renderset_on")
        self.gridLayout_4.addWidget(self.gpu_renderset_on, 0, 1, 1, 1)
        self.gpu_renderattr_set = QtWidgets.QLabel(self.gpu_attr_set_lay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_renderattr_set.sizePolicy().hasHeightForWidth())
        self.gpu_renderattr_set.setSizePolicy(sizePolicy)
        self.gpu_renderattr_set.setMinimumSize(QtCore.QSize(110, 0))
        self.gpu_renderattr_set.setMaximumSize(QtCore.QSize(800, 800))
        self.gpu_renderattr_set.setObjectName("gpu_renderattr_set")
        self.gridLayout_4.addWidget(self.gpu_renderattr_set, 0, 0, 1, 1)
        self.gpu_renderset_off = QtWidgets.QPushButton(self.gpu_attr_set_lay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_renderset_off.sizePolicy().hasHeightForWidth())
        self.gpu_renderset_off.setSizePolicy(sizePolicy)
        self.gpu_renderset_off.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_renderset_off.setObjectName("gpu_renderset_off")
        self.gridLayout_4.addWidget(self.gpu_renderset_off, 0, 2, 1, 1)
        self.ass_setting_off = QtWidgets.QPushButton(self.gpu_attr_set_lay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ass_setting_off.sizePolicy().hasHeightForWidth())
        self.ass_setting_off.setSizePolicy(sizePolicy)
        self.ass_setting_off.setObjectName("ass_setting_off")
        self.gridLayout_4.addWidget(self.ass_setting_off, 0, 5, 1, 1)
        self.ass_setting_label = QtWidgets.QLabel(self.gpu_attr_set_lay)
        self.ass_setting_label.setMaximumSize(QtCore.QSize(80, 50))
        self.ass_setting_label.setObjectName("ass_setting_label")
        self.gridLayout_4.addWidget(self.ass_setting_label, 0, 3, 1, 1)
        self.ass_setting_on = QtWidgets.QPushButton(self.gpu_attr_set_lay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ass_setting_on.sizePolicy().hasHeightForWidth())
        self.ass_setting_on.setSizePolicy(sizePolicy)
        self.ass_setting_on.setObjectName("ass_setting_on")
        self.gridLayout_4.addWidget(self.ass_setting_on, 0, 4, 1, 1)
        self.gpu_vis_label = QtWidgets.QLabel(self.gpu_attr_set_lay)
        self.gpu_vis_label.setObjectName("gpu_vis_label")
        self.gridLayout_4.addWidget(self.gpu_vis_label, 1, 0, 1, 1)
        self.gpu_vis_on = QtWidgets.QPushButton(self.gpu_attr_set_lay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_vis_on.sizePolicy().hasHeightForWidth())
        self.gpu_vis_on.setSizePolicy(sizePolicy)
        self.gpu_vis_on.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_vis_on.setObjectName("gpu_vis_on")
        self.gridLayout_4.addWidget(self.gpu_vis_on, 1, 1, 1, 1)
        self.gpu_vis_off = QtWidgets.QPushButton(self.gpu_attr_set_lay)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gpu_vis_off.sizePolicy().hasHeightForWidth())
        self.gpu_vis_off.setSizePolicy(sizePolicy)
        self.gpu_vis_off.setMaximumSize(QtCore.QSize(16777215, 50))
        self.gpu_vis_off.setObjectName("gpu_vis_off")
        self.gridLayout_4.addWidget(self.gpu_vis_off, 1, 2, 1, 1)
        self.verticalLayout_14.addWidget(self.gpu_attr_set_lay)
        self.groupBox = QtWidgets.QGroupBox(self.unt_cut)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.splitter_21 = QtWidgets.QSplitter(self.groupBox)
        self.splitter_21.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_21.setObjectName("splitter_21")
        self.env_check_label = QtWidgets.QLabel(self.splitter_21)
        self.env_check_label.setMaximumSize(QtCore.QSize(120, 50))
        self.env_check_label.setObjectName("env_check_label")
        self.open_filepathedit = QtWidgets.QPushButton(self.splitter_21)
        self.open_filepathedit.setMaximumSize(QtCore.QSize(16777215, 50))
        self.open_filepathedit.setObjectName("open_filepathedit")
        self.open_txmanager = QtWidgets.QPushButton(self.splitter_21)
        self.open_txmanager.setMaximumSize(QtCore.QSize(16777215, 50))
        self.open_txmanager.setObjectName("open_txmanager")
        self.check_sel_ass_tex = QtWidgets.QPushButton(self.splitter_21)
        self.check_sel_ass_tex.setMaximumSize(QtCore.QSize(16777215, 50))
        self.check_sel_ass_tex.setObjectName("check_sel_ass_tex")
        self.verticalLayout_13.addWidget(self.splitter_21)
        self.splitter_22 = QtWidgets.QSplitter(self.groupBox)
        self.splitter_22.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_22.setObjectName("splitter_22")
        self.lookattr_combobox = QtWidgets.QComboBox(self.splitter_22)
        self.lookattr_combobox.setMaximumSize(QtCore.QSize(16777215, 50))
        self.lookattr_combobox.setObjectName("lookattr_combobox")
        self.dispalyattr_combobox = QtWidgets.QComboBox(self.splitter_22)
        self.dispalyattr_combobox.setMaximumSize(QtCore.QSize(16777215, 50))
        self.dispalyattr_combobox.setObjectName("dispalyattr_combobox")
        self.verticalLayout_13.addWidget(self.splitter_22)
        self.verticalLayout_14.addWidget(self.groupBox)
        self.splitter_2 = QtWidgets.QSplitter(self.unt_cut)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.cut_progressBar = QtWidgets.QProgressBar(self.splitter_2)
        self.cut_progressBar.setMinimumSize(QtCore.QSize(0, 25))
        self.cut_progressBar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.cut_progressBar.setProperty("value", 0)
        self.cut_progressBar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.cut_progressBar.setTextVisible(True)
        self.cut_progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.cut_progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.cut_progressBar.setObjectName("cut_progressBar")
        self.cut_log_button = QtWidgets.QPushButton(self.splitter_2)
        self.cut_log_button.setMinimumSize(QtCore.QSize(50, 25))
        self.cut_log_button.setMaximumSize(QtCore.QSize(50, 25))
        self.cut_log_button.setObjectName("cut_log_button")
        self.verticalLayout_14.addWidget(self.splitter_2)
        self.tabWidget.addTab(self.unt_cut, "")
        self.unt_simple = QtWidgets.QWidget()
        self.unt_simple.setObjectName("unt_simple")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.unt_simple)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.export_simple_grp = QtWidgets.QGroupBox(self.unt_simple)
        self.export_simple_grp.setObjectName("export_simple_grp")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.export_simple_grp)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.simple_export_lay = QtWidgets.QSplitter(self.export_simple_grp)
        self.simple_export_lay.setOrientation(QtCore.Qt.Horizontal)
        self.simple_export_lay.setObjectName("simple_export_lay")
        self.export_mods_lay = QtWidgets.QSplitter(self.simple_export_lay)
        self.export_mods_lay.setOrientation(QtCore.Qt.Horizontal)
        self.export_mods_lay.setObjectName("export_mods_lay")
        self.export_mod_lay = QtWidgets.QSplitter(self.export_mods_lay)
        self.export_mod_lay.setOrientation(QtCore.Qt.Vertical)
        self.export_mod_lay.setObjectName("export_mod_lay")
        self.export_path_mod_lay = QtWidgets.QSplitter(self.simple_export_lay)
        self.export_path_mod_lay.setOrientation(QtCore.Qt.Horizontal)
        self.export_path_mod_lay.setObjectName("export_path_mod_lay")
        self.export_path_mod = QtWidgets.QLabel(self.export_path_mod_lay)
        self.export_path_mod.setMaximumSize(QtCore.QSize(16777215, 50))
        self.export_path_mod.setObjectName("export_path_mod")
        self.export_mod_lay_2 = QtWidgets.QSplitter(self.export_path_mod_lay)
        self.export_mod_lay_2.setOrientation(QtCore.Qt.Vertical)
        self.export_mod_lay_2.setObjectName("export_mod_lay_2")
        self.export_mod_ma = QtWidgets.QRadioButton(self.export_mod_lay_2)
        self.export_mod_ma.setMaximumSize(QtCore.QSize(16777215, 25))
        self.export_mod_ma.setObjectName("export_mod_ma")
        self.export_mod_asset = QtWidgets.QRadioButton(self.export_mod_lay_2)
        self.export_mod_asset.setMaximumSize(QtCore.QSize(16777215, 25))
        self.export_mod_asset.setObjectName("export_mod_asset")
        self.verticalLayout_4.addWidget(self.simple_export_lay)
        self.export_path_lay = QtWidgets.QSplitter(self.export_simple_grp)
        self.export_path_lay.setOrientation(QtCore.Qt.Horizontal)
        self.export_path_lay.setObjectName("export_path_lay")
        self.export_path_label = QtWidgets.QLabel(self.export_path_lay)
        self.export_path_label.setMaximumSize(QtCore.QSize(60, 16777215))
        self.export_path_label.setObjectName("export_path_label")
        self.export_path_lineedit = QtWidgets.QLineEdit(self.export_path_lay)
        self.export_path_lineedit.setMaximumSize(QtCore.QSize(16777215, 50))
        self.export_path_lineedit.setText("")
        self.export_path_lineedit.setObjectName("export_path_lineedit")
        self.export_path_get = QtWidgets.QPushButton(self.export_path_lay)
        self.export_path_get.setMaximumSize(QtCore.QSize(30, 16777215))
        self.export_path_get.setObjectName("export_path_get")
        self.verticalLayout_4.addWidget(self.export_path_lay)
        self.splitter_18 = QtWidgets.QSplitter(self.export_simple_grp)
        self.splitter_18.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_18.setObjectName("splitter_18")
        self.simple_ass = QtWidgets.QCheckBox(self.splitter_18)
        self.simple_ass.setChecked(True)
        self.simple_ass.setObjectName("simple_ass")
        self.simple_bbox = QtWidgets.QCheckBox(self.splitter_18)
        self.simple_bbox.setChecked(True)
        self.simple_bbox.setObjectName("simple_bbox")
        self.simple_diy = QtWidgets.QCheckBox(self.splitter_18)
        self.simple_diy.setChecked(True)
        self.simple_diy.setObjectName("simple_diy")
        self.simple_gpu = QtWidgets.QCheckBox(self.splitter_18)
        self.simple_gpu.setChecked(True)
        self.simple_gpu.setObjectName("simple_gpu")
        self.verticalLayout_4.addWidget(self.splitter_18)
        self.splitter_14 = QtWidgets.QSplitter(self.export_simple_grp)
        self.splitter_14.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_14.setObjectName("splitter_14")
        self.simple_type_listwidget = QtWidgets.QListWidget(self.splitter_14)
        self.simple_type_listwidget.setObjectName("simple_type_listwidget")
        self.splitter_13 = QtWidgets.QSplitter(self.splitter_14)
        self.splitter_13.setOrientation(QtCore.Qt.Vertical)
        self.splitter_13.setObjectName("splitter_13")
        self.splitter_12 = QtWidgets.QSplitter(self.splitter_13)
        self.splitter_12.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_12.setObjectName("splitter_12")
        self.export_simple_openpath = QtWidgets.QCheckBox(self.splitter_12)
        self.export_simple_openpath.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.export_simple_openpath.setObjectName("export_simple_openpath")
        self.check_tex_on_z = QtWidgets.QCheckBox(self.splitter_12)
        self.check_tex_on_z.setObjectName("check_tex_on_z")
        self.export_lay = QtWidgets.QSplitter(self.splitter_13)
        self.export_lay.setOrientation(QtCore.Qt.Horizontal)
        self.export_lay.setObjectName("export_lay")
        self.export_simple_button = QtWidgets.QPushButton(self.export_lay)
        self.export_simple_button.setMinimumSize(QtCore.QSize(180, 0))
        self.export_simple_button.setObjectName("export_simple_button")
        self.import_simple_button = QtWidgets.QPushButton(self.export_lay)
        self.import_simple_button.setMaximumSize(QtCore.QSize(100, 16777215))
        self.import_simple_button.setObjectName("import_simple_button")
        self.verticalLayout_4.addWidget(self.splitter_14)
        self.verticalLayout_5.addWidget(self.export_simple_grp)
        self.simple_input_grp = QtWidgets.QGroupBox(self.unt_simple)
        self.simple_input_grp.setMaximumSize(QtCore.QSize(16777215, 250))
        self.simple_input_grp.setObjectName("simple_input_grp")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.simple_input_grp)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.simple_input_list = QtWidgets.QListWidget(self.simple_input_grp)
        self.simple_input_list.setMaximumSize(QtCore.QSize(300, 200))
        self.simple_input_list.setObjectName("simple_input_list")
        self.horizontalLayout_2.addWidget(self.simple_input_list)
        self.simple_input_button = QtWidgets.QPushButton(self.simple_input_grp)
        self.simple_input_button.setMinimumSize(QtCore.QSize(0, 150))
        self.simple_input_button.setObjectName("simple_input_button")
        self.horizontalLayout_2.addWidget(self.simple_input_button)
        self.verticalLayout_5.addWidget(self.simple_input_grp)
        self.splitter_7 = QtWidgets.QSplitter(self.unt_simple)
        self.splitter_7.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_7.setObjectName("splitter_7")
        self.simple_progressBar = QtWidgets.QProgressBar(self.splitter_7)
        self.simple_progressBar.setMinimumSize(QtCore.QSize(0, 25))
        self.simple_progressBar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.simple_progressBar.setProperty("value", 0)
        self.simple_progressBar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.simple_progressBar.setTextVisible(True)
        self.simple_progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.simple_progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.simple_progressBar.setObjectName("simple_progressBar")
        self.simple_log_button = QtWidgets.QPushButton(self.splitter_7)
        self.simple_log_button.setMinimumSize(QtCore.QSize(50, 25))
        self.simple_log_button.setMaximumSize(QtCore.QSize(50, 25))
        self.simple_log_button.setObjectName("simple_log_button")
        self.verticalLayout_5.addWidget(self.splitter_7)
        self.tabWidget.addTab(self.unt_simple, "")
        self.export_data = QtWidgets.QWidget()
        self.export_data.setObjectName("export_data")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.export_data)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.data_import_unt_checkbox = QtWidgets.QCheckBox(self.export_data)
        self.data_import_unt_checkbox.setObjectName("data_import_unt_checkbox")
        self.gridLayout_2.addWidget(self.data_import_unt_checkbox, 2, 0, 1, 1)
        self.data_ref_ma_checkbox = QtWidgets.QCheckBox(self.export_data)
        self.data_ref_ma_checkbox.setObjectName("data_ref_ma_checkbox")
        self.gridLayout_2.addWidget(self.data_ref_ma_checkbox, 2, 1, 1, 2)
        self.data_type_listwidget = QtWidgets.QListWidget(self.export_data)
        self.data_type_listwidget.setMaximumSize(QtCore.QSize(200, 16777215))
        self.data_type_listwidget.setObjectName("data_type_listwidget")
        self.gridLayout_2.addWidget(self.data_type_listwidget, 3, 0, 1, 1)
        self.splitter_24 = QtWidgets.QSplitter(self.export_data)
        self.splitter_24.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_24.setObjectName("splitter_24")
        self.dt_progressBar = QtWidgets.QProgressBar(self.splitter_24)
        self.dt_progressBar.setMinimumSize(QtCore.QSize(0, 25))
        self.dt_progressBar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.dt_progressBar.setProperty("value", 0)
        self.dt_progressBar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.dt_progressBar.setTextVisible(True)
        self.dt_progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.dt_progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.dt_progressBar.setObjectName("dt_progressBar")
        self.dt_log_button = QtWidgets.QPushButton(self.splitter_24)
        self.dt_log_button.setMinimumSize(QtCore.QSize(50, 25))
        self.dt_log_button.setMaximumSize(QtCore.QSize(50, 25))
        self.dt_log_button.setObjectName("dt_log_button")
        self.gridLayout_2.addWidget(self.splitter_24, 4, 0, 1, 4)
        self.data_grp = QtWidgets.QGroupBox(self.export_data)
        self.data_grp.setObjectName("data_grp")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.data_grp)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.splitter_11 = QtWidgets.QSplitter(self.data_grp)
        self.splitter_11.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_11.setObjectName("splitter_11")
        self.high_radiobutton = QtWidgets.QRadioButton(self.splitter_11)
        self.high_radiobutton.setMaximumSize(QtCore.QSize(16777215, 25))
        self.high_radiobutton.setObjectName("high_radiobutton")
        self.low_radiobutton = QtWidgets.QRadioButton(self.splitter_11)
        self.low_radiobutton.setMaximumSize(QtCore.QSize(16777215, 25))
        self.low_radiobutton.setObjectName("low_radiobutton")
        self.verticalLayout_10.addWidget(self.splitter_11)
        self.splitter_10 = QtWidgets.QSplitter(self.data_grp)
        self.splitter_10.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_10.setObjectName("splitter_10")
        self.ex_ass_checkBox = QtWidgets.QCheckBox(self.splitter_10)
        self.ex_ass_checkBox.setEnabled(True)
        self.ex_ass_checkBox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.ex_ass_checkBox.setMouseTracking(True)
        self.ex_ass_checkBox.setChecked(True)
        self.ex_ass_checkBox.setAutoExclusive(False)
        self.ex_ass_checkBox.setObjectName("ex_ass_checkBox")
        self.ex_bbox_checkBox = QtWidgets.QCheckBox(self.splitter_10)
        self.ex_bbox_checkBox.setEnabled(True)
        self.ex_bbox_checkBox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.ex_bbox_checkBox.setMouseTracking(True)
        self.ex_bbox_checkBox.setChecked(True)
        self.ex_bbox_checkBox.setAutoExclusive(False)
        self.ex_bbox_checkBox.setObjectName("ex_bbox_checkBox")
        self.ex_diy_checkBox = QtWidgets.QCheckBox(self.splitter_10)
        self.ex_diy_checkBox.setEnabled(True)
        self.ex_diy_checkBox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.ex_diy_checkBox.setMouseTracking(True)
        self.ex_diy_checkBox.setChecked(False)
        self.ex_diy_checkBox.setAutoExclusive(False)
        self.ex_diy_checkBox.setObjectName("ex_diy_checkBox")
        self.ex_gpu_checkBox = QtWidgets.QCheckBox(self.splitter_10)
        self.ex_gpu_checkBox.setEnabled(True)
        self.ex_gpu_checkBox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.ex_gpu_checkBox.setMouseTracking(True)
        self.ex_gpu_checkBox.setChecked(True)
        self.ex_gpu_checkBox.setAutoExclusive(False)
        self.ex_gpu_checkBox.setObjectName("ex_gpu_checkBox")
        self.ex_ma_checkBox = QtWidgets.QCheckBox(self.splitter_10)
        self.ex_ma_checkBox.setEnabled(True)
        self.ex_ma_checkBox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.ex_ma_checkBox.setMouseTracking(True)
        self.ex_ma_checkBox.setChecked(True)
        self.ex_ma_checkBox.setAutoExclusive(False)
        self.ex_ma_checkBox.setObjectName("ex_ma_checkBox")
        self.verticalLayout_10.addWidget(self.splitter_10)
        self.gridLayout_2.addWidget(self.data_grp, 1, 0, 1, 4)
        self.sel_unt_range_grp_2 = QtWidgets.QGroupBox(self.export_data)
        self.sel_unt_range_grp_2.setMaximumSize(QtCore.QSize(16777215, 200))
        self.sel_unt_range_grp_2.setObjectName("sel_unt_range_grp_2")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.sel_unt_range_grp_2)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.operation_textedit = QtWidgets.QTextEdit(self.sel_unt_range_grp_2)
        self.operation_textedit.setMaximumSize(QtCore.QSize(16777215, 150))
        self.operation_textedit.setObjectName("operation_textedit")
        self.verticalLayout_9.addWidget(self.operation_textedit)
        self.gridLayout_2.addWidget(self.sel_unt_range_grp_2, 0, 0, 1, 4)
        self.start_export_button = QtWidgets.QPushButton(self.export_data)
        self.start_export_button.setMinimumSize(QtCore.QSize(0, 100))
        self.start_export_button.setMaximumSize(QtCore.QSize(16777215, 100))
        self.start_export_button.setObjectName("start_export_button")
        self.gridLayout_2.addWidget(self.start_export_button, 3, 2, 1, 2)
        self.tabWidget.addTab(self.export_data, "")
        self.unt_assembly = QtWidgets.QWidget()
        self.unt_assembly.setObjectName("unt_assembly")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.unt_assembly)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.unt_assembly_grp = QtWidgets.QGroupBox(self.unt_assembly)
        self.unt_assembly_grp.setObjectName("unt_assembly_grp")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.unt_assembly_grp)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.unt_assembly_lay = QtWidgets.QSplitter(self.unt_assembly_grp)
        self.unt_assembly_lay.setOrientation(QtCore.Qt.Horizontal)
        self.unt_assembly_lay.setObjectName("unt_assembly_lay")
        self.project_label = QtWidgets.QLabel(self.unt_assembly_lay)
        self.project_label.setMaximumSize(QtCore.QSize(30, 25))
        self.project_label.setObjectName("project_label")
        self.project_comboBox = QtWidgets.QComboBox(self.unt_assembly_lay)
        self.project_comboBox.setMaximumSize(QtCore.QSize(16777215, 25))
        self.project_comboBox.setObjectName("project_comboBox")
        self.assembly_get_path = QtWidgets.QPushButton(self.unt_assembly_lay)
        self.assembly_get_path.setMaximumSize(QtCore.QSize(100, 25))
        self.assembly_get_path.setObjectName("assembly_get_path")
        self.search_label = QtWidgets.QLabel(self.unt_assembly_lay)
        self.search_label.setMaximumSize(QtCore.QSize(30, 25))
        self.search_label.setObjectName("search_label")
        self.search_lineedit = QtWidgets.QLineEdit(self.unt_assembly_lay)
        self.search_lineedit.setMaximumSize(QtCore.QSize(16777215, 25))
        self.search_lineedit.setObjectName("search_lineedit")
        self.scale_label = QtWidgets.QLabel(self.unt_assembly_lay)
        self.scale_label.setMaximumSize(QtCore.QSize(50, 25))
        self.scale_label.setObjectName("scale_label")
        self.scale_slider = QtWidgets.QSlider(self.unt_assembly_lay)
        self.scale_slider.setMaximumSize(QtCore.QSize(16777215, 25))
        self.scale_slider.setOrientation(QtCore.Qt.Horizontal)
        self.scale_slider.setObjectName("scale_slider")
        self.verticalLayout_8.addWidget(self.unt_assembly_lay)
        self.unt_assembly_select_lay = QtWidgets.QSplitter(self.unt_assembly_grp)
        self.unt_assembly_select_lay.setOrientation(QtCore.Qt.Horizontal)
        self.unt_assembly_select_lay.setObjectName("unt_assembly_select_lay")
        self.unt_assembly_tree = QtWidgets.QTreeWidget(self.unt_assembly_select_lay)
        self.unt_assembly_tree.setMaximumSize(QtCore.QSize(250, 16777215))
        self.unt_assembly_tree.setObjectName("unt_assembly_tree")
        self.unt_assembly_tree.headerItem().setText(0, "1")
        self.unt_assembly_table = QtWidgets.QTableWidget(self.unt_assembly_select_lay)
        self.unt_assembly_table.setObjectName("unt_assembly_table")
        self.unt_assembly_table.setColumnCount(0)
        self.unt_assembly_table.setRowCount(0)
        self.verticalLayout_8.addWidget(self.unt_assembly_select_lay)
        self.verticalLayout_6.addWidget(self.unt_assembly_grp)
        self.splitter_9 = QtWidgets.QSplitter(self.unt_assembly)
        self.splitter_9.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_9.setObjectName("splitter_9")
        self.assembly_progressBar = QtWidgets.QProgressBar(self.splitter_9)
        self.assembly_progressBar.setMinimumSize(QtCore.QSize(0, 25))
        self.assembly_progressBar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.assembly_progressBar.setProperty("value", 0)
        self.assembly_progressBar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.assembly_progressBar.setTextVisible(True)
        self.assembly_progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.assembly_progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.assembly_progressBar.setObjectName("assembly_progressBar")
        self.assembly_log_button = QtWidgets.QPushButton(self.splitter_9)
        self.assembly_log_button.setMinimumSize(QtCore.QSize(50, 25))
        self.assembly_log_button.setMaximumSize(QtCore.QSize(50, 25))
        self.assembly_log_button.setObjectName("assembly_log_button")
        self.verticalLayout_6.addWidget(self.splitter_9)
        self.tabWidget.addTab(self.unt_assembly, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.to_analyze = QtWidgets.QPushButton(self.tab)
        self.to_analyze.setMaximumSize(QtCore.QSize(16777215, 50))
        self.to_analyze.setObjectName("to_analyze")
        self.verticalLayout_12.addWidget(self.to_analyze)
        self.splitter_8 = QtWidgets.QSplitter(self.tab)
        self.splitter_8.setOrientation(QtCore.Qt.Vertical)
        self.splitter_8.setObjectName("splitter_8")
        self.groupBox_2 = QtWidgets.QGroupBox(self.splitter_8)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.key_table = QtWidgets.QTableWidget(self.groupBox_2)
        self.key_table.setObjectName("key_table")
        self.key_table.setColumnCount(0)
        self.key_table.setRowCount(0)
        self.verticalLayout_3.addWidget(self.key_table)
        self.groupBox_3 = QtWidgets.QGroupBox(self.splitter_8)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.instancer_table = QtWidgets.QTableWidget(self.groupBox_3)
        self.instancer_table.setObjectName("instancer_table")
        self.instancer_table.setColumnCount(0)
        self.instancer_table.setRowCount(0)
        self.verticalLayout_11.addWidget(self.instancer_table)
        self.verticalLayout_12.addWidget(self.splitter_8)
        self.splitter_23 = QtWidgets.QSplitter(self.tab)
        self.splitter_23.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_23.setObjectName("splitter_23")
        self.check_progressBar = QtWidgets.QProgressBar(self.splitter_23)
        self.check_progressBar.setMinimumSize(QtCore.QSize(0, 25))
        self.check_progressBar.setMaximumSize(QtCore.QSize(16777215, 25))
        self.check_progressBar.setProperty("value", 0)
        self.check_progressBar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.check_progressBar.setTextVisible(True)
        self.check_progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.check_progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.check_progressBar.setObjectName("check_progressBar")
        self.check_log_button = QtWidgets.QPushButton(self.splitter_23)
        self.check_log_button.setMinimumSize(QtCore.QSize(50, 25))
        self.check_log_button.setMaximumSize(QtCore.QSize(50, 25))
        self.check_log_button.setObjectName("check_log_button")
        self.verticalLayout_12.addWidget(self.splitter_23)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(self.tab_2)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_5.setMaximumSize(QtCore.QSize(16777215, 160))
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.textBrowser = QtWidgets.QTextBrowser(self.groupBox_5)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setOpenLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_15.addWidget(self.textBrowser)
        self.verticalLayout_17.addWidget(self.groupBox_5)
        self.groupBox_6 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.groupBox_6)
        self.textBrowser_2.setOpenExternalLinks(True)
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.verticalLayout_16.addWidget(self.textBrowser_2)
        self.verticalLayout_17.addWidget(self.groupBox_6)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(Unt_Tool_Window)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Unt_Tool_Window)

        #UI文字设置
        self.retranslateUi(Unt_Tool_Window)
        
        #设置窗口flags
        self.setWindowFlags(QtCore.Qt.Window)
        #置顶
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Window)

        #ui控制
        self.ui_ctrl(Unt_Tool_Window)
        #切换到tab1
        self.sel_mod_selections.setChecked(1)
    
    #Unt资产显示切换
        #添加GPUcache（bbox形态）右键
        self.gpu_refacto_gpu_add_bbox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.gpu_refacto_gpu_add_bbox.customContextMenuRequested.connect(self.show_gpu_add_custom_menu)
        self.create_gpu_add_right_menu()
        #锁定，隐藏属性
        for item in [u'锁定通道栏TRS', u'解锁通道栏TRS', u'锁定通道栏Visibility', u'解锁通道栏Visibility']:
            self.lookattr_combobox.addItem(item)
        for item in [u'显示通道栏TRS', u'隐藏通道栏TRS', u'显示通道栏Visibility', u'隐藏通道栏Visibility']:
            self.dispalyattr_combobox.addItem(item)
    #简单组件    
            #简单组件默认输出模式
        self.export_path_lineedit.setEnabled(False)
        self.check_tex_on_z.setChecked(False)
            #简单组件类型
        for k,v in self.bbox_color_dic.items():
            icon_color = QtGui.QIcon()
            
            color_pixmap = QtGui.QPixmap(10,10)
            color_pixmap.fill(QtGui.QColor(v[1][0],v[1][1],v[1][2]))

            icon_color.addPixmap(color_pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)

            item = QtWidgets.QListWidgetItem(self.simple_type_listwidget)
            item.setText(k)
            item.setIcon(icon_color)

            #简单组件listwidget多选
        self.simple_input_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            #简单组件listwidget右键UI
        self.simple_input_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.simple_input_list.customContextMenuRequested.connect(self.show_simple_custom_menu)
        self.create_simple_right_menu()
        self.setAcceptDrops(True)
        self.simple_input_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    #转换数据
        self.operation_textedit.setReadOnly(True)
            #radiobutton默认选择
        self.high_radiobutton.setChecked(True)

        self.data_import_unt_checkbox.setChecked(True)
            #导出类型
        for k,v in self.bbox_color_dic.items():
            icon_color = QtGui.QIcon()
            
            color_pixmap = QtGui.QPixmap(10,10)
            color_pixmap.fill(QtGui.QColor(v[1][0],v[1][1],v[1][2]))

            icon_color.addPixmap(color_pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)

            item = QtWidgets.QListWidgetItem(self.data_type_listwidget)
            item.setText(k)
            item.setIcon(icon_color)
    #拼装
        if os.path.exists(self.json_path):
            with open(self.json_path,'r') as load_f:
                json_dic = json.load(load_f)
                #是否有key  assembly_default
                if "assembly_default" in json_dic:
                    for i in json_dic["assembly_default"]:
                        self.project_comboBox.addItem(i)
                    self.combobox_refresh_tree()
        #预设右键
        self.project_comboBox.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.project_comboBox.customContextMenuRequested.connect(self.show_del_defaultset_menu)
        self.create_del_defaultset()

        self.scale_slider.setMinimum(40)
        self.scale_slider.setMaximum(200)

        #设置水平方向表格为自适应的伸缩模式
        # self.unt_assembly_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #将表格变为禁止编辑
        self.unt_assembly_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #设置表格整行选中
        self.unt_assembly_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #treewidget右键
        self.unt_assembly_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.unt_assembly_tree.customContextMenuRequested.connect(self.show_assemblytree_custom_menu)
        self.create_assemblytree_right_menu()
        #tablewidget右键
        self.unt_assembly_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.unt_assembly_table.customContextMenuRequested.connect(self.show_assembly_custom_menu)
        self.create_assembly_right_menu()
    #分析
        #将表格变为禁止编辑
        self.key_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.instancer_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    #帮助文档
    ################################################################
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Unt_Tool_Window)
#################################################################################################################################################
#
#UI的文字设置
#
#################################################################################################################################################
    def retranslateUi(self, Unt_Tool_Window):
        Unt_Tool_Window.setWindowTitle(u"HyperScene场景管理工具 V1.5.6")
        self.sel_unt_range_grp.setTitle(u"操作范围")
        self.sel_mod_all.setText(u"All")
        self.sel_mod_selections.setText(u"所选")
        self.sel_mod_childs.setText(u"包含子物体")
        self.groupBox_4.setTitle(u"辅助选择")
        self.select_obj_preview.setText(u"选中视口内物体")
        self.select_obj_cl.setText(u"清除选择")
        self.select_obj_unt.setText(u"滤出Unt")
        self.select_unt_reverse.setText(u"Unt反选")
        self.select_cteate_set.setText(u"为所选创建Set")
        self.select_gpumesh.setText(u"滤出GPUmesh")
        self.select_gpubbox.setText(u"滤出GPU_BBox")
        self.select_gpudiy.setText(u"滤出GPU_DIY")
        self.select_no_ass.setText(u"滤出没有渲染代理的Unt")
        self.gpu_refacto_grp.setTitle(u"Unt创建与删除")
        self.gpu_refacto_unt_tex.setText(u"Unt牛逼操作 ")
        self.gpu_refacto_refresh_but.setText(u"依据GPU创建Unt")
        self.gpu_refacto_ma_ref.setText(u"Ref Ma")
        self.gpu_refacto_ma_remove.setText(u"De-Ref Ma")
        self.gpu_refacto_gpu_tex.setText(u"GPUcache操作 ")
        self.gpu_refacto_gpu_add_bbox.setText(u"添加GPUcache(BBox形态优先)")
        self.gpu_refacto_gpu_del.setText(u"删除GPUcache")
        self.gpu_refacto_ass_tex.setText(u"ASS操作 ")
        self.gpu_refacto_ass_add.setText(u"添加ASS节点(BBox线框形态)")
        self.gpu_refacto_ass_del.setText(u"删除ASS节点")
        self.unt_display_change_grp.setTitle(u"Unt视口显示切换")
        self.cut_to.setText(u"GPU形态切换")
        self.gpu_bbox.setText(u"GPUcache_BBox")
        self.gpu_diy.setText(u"GPUcache_DIY")
        self.gpu_geo.setText(u"GPUcache实模")
        self.ass_pverride_label.setText(u"ASS Viewport Override:")
        self.ass_drawmode_label.setText(u"ASS Viewport Draw Mode:")
        self.show_gpu_checkBox.setText(u"视口GPUcache")
        self.show_ass_checkBox.setText(u"视口ASS")
        self.show_ins_checkBox.setText(u"视口Instancer")
        self.show_handel_checkbox.setText(u"视口Handle")
        self.two_sidedlight_checkbox.setText(u"双面照明")
        self.ass_preview_label_2.setText(u"Instancer显示为:")
        self.ass_preview_ins_tex.setText(u"Instancer显示比例:")
        self.label.setText(u"%")
        self.handle_on_button.setText(u"Unt显示Handle")
        self.handle_off_button.setText(u"Unt隐藏Handle")
        self.gpu_refresh_button.setText(u"GPUcache刷新")
        self.ass_refresh.setText(u"ASS刷新")
        self.refresh_ogs.setText(u"修复：保存文件后视口不显示GPU/Ass")
        self.gpu_attr_set_lay.setTitle(u"Unt渲染设置")
        self.gpu_renderattr_set.setText(u"GPUcache渲染&投影")
        self.gpu_renderset_on.setText(u"ON")
        self.gpu_renderset_off.setText(u"OFF")
        self.ass_setting_label.setText(u"ASS渲染")
        self.ass_setting_on.setText(u"ON")
        self.ass_setting_off.setText(u"OFF")
        self.gpu_vis_label.setText(u"GPUcache显示&隐藏")
        self.gpu_vis_on.setText(u"ON")
        self.gpu_vis_off.setText(u"OFF")
        self.groupBox.setTitle(u"其他工具")
        self.env_check_label.setText(u"贴图路径检查：")
        self.open_filepathedit.setText(u"FilePathEditor")
        self.open_txmanager.setText(u"txManager分析")
        self.check_sel_ass_tex.setText(u".ass文件外链分析")
        self.cut_progressBar.setFormat(u"%p%")
        self.cut_log_button.setText(u"Log")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.unt_cut), u"Unt资产显示切换")
        self.export_simple_grp.setTitle(u"标准组件生成")
        self.export_path_mod.setText(u"输出路径方式：")
        self.export_mod_ma.setText(u"maya文件所在路径")
        self.export_mod_asset.setText(u"项目资产路径")
        self.export_path_label.setText(u"输出路径：")
        self.export_path_get.setText(u"...")
        self.simple_ass.setText(u"ASS")
        self.simple_bbox.setText(u"GPU_BBox")
        self.simple_diy.setText(u"GPU_DIY")
        self.simple_gpu.setText(u"GPU实模")
        self.export_simple_openpath.setText(u"生成组件后打开生成路径")
        self.check_tex_on_z.setText(u"检查贴图是否在Z盘")
        self.export_simple_button.setText(u"生成标准组件")
        self.import_simple_button.setText(u"添加到调用列表")
        self.simple_input_grp.setTitle(u"调用标准组件")
        self.simple_input_button.setText(u"调用")
        self.simple_progressBar.setFormat(u"%p%")
        self.simple_log_button.setText(u"Log")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.unt_simple), u"生成标准组件")
        self.data_import_unt_checkbox.setText(u"操作完成后加载该Unt")
        self.data_grp.setTitle(u"需要生成的数据形态")
        self.high_radiobutton.setText(u"创建为可GPU高端显示+可渲染")
        self.low_radiobutton.setText(u"创建为GPU凑合显示+可渲染")
        self.ex_ass_checkBox.setText(u"ASS")
        self.ex_bbox_checkBox.setText(u"GPU_BBOX")
        self.ex_diy_checkBox.setText(u"GPU_DIY")
        self.ex_gpu_checkBox.setText(u"GPU实模")
        self.ex_ma_checkBox.setText(u"MA")
        self.sel_unt_range_grp_2.setTitle(u"操作说明")
        self.operation_textedit.setHtml(u"""<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n
<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n
p, li { white-space: pre-wrap; }\n
</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">1、选中需要转换的Transform节点，选择所需要的资产形态，然后点“生成”就会自动在当前maya文件路径下生成对应的资产数据形态。</p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">2、如果勾选了GPU_DIY，则需要多加选一个当做自定义边界盒的物体（的Transform节点）。</p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">3、如果勾选了GPU实模（假面片），则会用一个最简单的四方面片来替代输出GPU实模。</p></body></html>""")
        self.start_export_button.setText(u"开始转换")
        self.data_ref_ma_checkbox.setText(u"操作完成后Ref刚刚导出的Maya文件\n（检查输出文件是否OK）")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.export_data), u"生成多态")
        self.unt_assembly_grp.setTitle(u"项目Unt资产库")
        self.project_label.setText(u"预设：")
        self.assembly_get_path.setText(u"...")
        self.search_label.setText(u"搜索：")
        self.scale_label.setText(u"调整缩放")
        self.assembly_progressBar.setFormat(u"%p%")
        self.assembly_log_button.setText(u"Log")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.unt_assembly), u"场景拼装/地编")
        self.to_analyze.setText(u"开始分析")
        self.groupBox_2.setTitle(u"关键指标总表")
        self.groupBox_3.setTitle(u"Instancer细表")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), u"场景性能分析")
        self.groupBox_5.setTitle(u"帮助文档")
        self.textBrowser.setHtml(u"""<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n
<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n
p, li { white-space: pre-wrap; }\n
</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">链接1：<a href=\"https://zhuanlan.zhihu.com/p/414998594\"><span style=\" text-decoration: underline; color:#ff8000;\">(知乎)HyperScene场景管理工具-官方教程</span></a></p>""")
        self.groupBox_6.setTitle(u"贡献者们")
        self.textBrowser_2.setHtml(u"""<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n
<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n
p, li { white-space: pre-wrap; }\n
</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">概念提出：CG风火连城</p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">::【开发阶段一】</p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">周期：2021/8/13-2021/9/18,从0到HyperScene V1.52（公开发布版）</p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">开发目标：遵循德式开发逻辑，以解决场景师动画师灯光师痛点、可在剧集项目中投产为目标。</p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">策划&amp;需求文档&amp;帮助文档：CG风火连城（技师陈）</p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">程序：热冬</p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">版本测试：CG风火连城（技师陈）、热冬、<a href=\"http://www.yangyijun.artstation.com\"><span style=\" text-decoration: underline; color:#ff8000;\">杨军</span></a>、程晓堃、<a href=\"https://www.artstation.com/zhensen_qin\"><span style=\" text-decoration: underline; color:#ff8000;\">刷碗的神</span></a></p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">技术切磋：Terrorist刘定俊、拉倒解放、<a href=\"https://www.artstation.com/artist/mlsr\"><span style=\" text-decoration: underline; color:#ff8000;\">李松然（树库佬）</span></a>、<a href=\"http://www.mstools.work\"><span style=\" text-decoration: underline; color:#ff8000;\">劲爆羊厂长（JB.Young）</span></a>、<a href=\"http://www.iiicg.com/\"><span style=\" text-decoration: underline; color:#ff8000;\">画忆</span></a></p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n
<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">----------------------------</p></body></html>""")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), u"帮助文档")
        #组装功能的tablewidget   UI设置
        self.unt_assembly_tree.headerItem().setText(0, u"Folder")

        self.unt_assembly_table.setColumnCount(8)
        # item = QtWidgets.QTableWidgetItem()
        # self.unt_assembly_table.setVerticalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.unt_assembly_table.setHorizontalHeaderItem(0, item)
        # self.unt_assembly_table.verticalHeaderItem(0).setText(u"1")
        self.unt_assembly_table.setHorizontalHeaderLabels([u"缩略图", u"资产名", "Ma", u"GPUcache", "ASS", "Boundingbox", "GPUcache_DIY", "Folder"])
        

#################################################################################################################################################
#
#控件执行的方法
#
#################################################################################################################################################
    def change_window_size(self,index):
        if self.tabWidget.currentIndex() == 3:
            self.resize(1100, 600)
        else:
            self.resize(617, 500)

    def ui_ctrl(self,Unt_Tool_Window):
        self.tabWidget.currentChanged.connect(self.change_window_size)

    #unt资产显示切换
        #操作范围------------------------------------------------------------------------------------------------
        self.sel_mod_selections.clicked.connect(self.change_select_mod)
        self.sel_mod_all.clicked.connect(self.change_select_mod)
        #辅助选择
        self.select_obj_preview.clicked.connect(functools.partial(self.select_object_mode,"preview"))
        self.select_obj_cl.clicked.connect(functools.partial(self.select_object_mode,"clear"))
        self.select_obj_unt.clicked.connect(functools.partial(self.select_object_mode,"sel_unt"))
        self.select_unt_reverse.clicked.connect(functools.partial(self.select_object_mode,"unt_reverse"))
        self.select_cteate_set.clicked.connect(functools.partial(self.select_object_mode,"set"))

        self.select_gpumesh.clicked.connect(functools.partial(self.filtration_unt,"gpu"))
        self.select_gpubbox.clicked.connect(functools.partial(self.filtration_unt,"bbox"))
        self.select_gpudiy.clicked.connect(functools.partial(self.filtration_unt,"diy"))
        self.select_no_ass.clicked.connect(self.filtration_no_rendershape)

        #unt创建与删除------------------------------------------------------------------------------------------------
        self.gpu_refacto_refresh_but.clicked.connect(self.refresh_transform_node)
        self.gpu_refacto_ma_ref.clicked.connect(self.add_ref_maya)
        self.gpu_refacto_ma_remove.clicked.connect(self.del_ref_maya)

        self.gpu_refacto_gpu_add_bbox.clicked.connect(self.add_gpu_bbox_diy_gpu)
        self.gpu_refacto_gpu_del.clicked.connect(self.del_gpucache_node)

        self.gpu_refacto_ass_add.clicked.connect(self.add_ass_node)
        self.gpu_refacto_ass_del.clicked.connect(self.del_ass_node)
        #GPU视口显示切换------------------------------------------------------------------------------------------------
        self.gpu_bbox.clicked.connect(functools.partial(self.change_gpu_display,"bbox"))
        self.gpu_diy.clicked.connect(functools.partial(self.change_gpu_display,"diy"))
        self.gpu_geo.clicked.connect(functools.partial(self.change_gpu_display,"gpu"))
        
        #viewport_override
        for item in ['Use Global Settings','Use Local Settings','Bounding Box','Disable Draw','Disable Load']:
            self.ass_pverride_comboBox.addItem(item)
        self.ass_pverride_comboBox.activated.connect(functools.partial(self.change_ass_display, "viewport_override"))
        #viewport_draw_mode
        for item in ['Bounding Box','Per Object Bounding Box','Polywire','Wireframe','Point Cloud','Shaded Polywire','Shaded']:
            self.ass_drawmode_comboBox.addItem(item)
        self.ass_drawmode_comboBox.activated.connect(functools.partial(self.change_ass_display, "viewport_draw_mode"))

        #show_gpu_checkBox   show_ass_checkBox   show_ins_checkBox
        self.show_gpu_checkBox.clicked.connect(functools.partial(self.change_proview_display, "gpucache"))
        self.show_ass_checkBox.clicked.connect(functools.partial(self.change_proview_display, "ass"))
        self.show_ins_checkBox.clicked.connect(functools.partial(self.change_proview_display, "instancer"))
        self.show_handel_checkbox.clicked.connect(functools.partial(self.change_proview_display, "handles"))
        self.two_sidedlight_checkbox.clicked.connect(functools.partial(self.change_proview_display, "twoSidedLighting"))
        
        for item in ['Geometry','BoundingBoxes','BoundingBox']:
            self.ass_preview_comboBox.addItem(item)
        self.ass_preview_comboBox.activated.connect(self.change_instancer_display)
        self.ass_preview_ins_spinbox.valueChanged.connect(self.change_instancer_show_num)

        self.handle_on_button.clicked.connect(functools.partial(self.display_handle, True))
        self.handle_off_button.clicked.connect(functools.partial(self.display_handle, False))
        self.gpu_refresh_button.clicked.connect(self.refresh_gpucahce_shape)
        self.ass_refresh.clicked.connect(self.print_text)

        self.refresh_ogs.clicked.connect(self.refresh_preview_ogs)

        #unt渲染设置------------------------------------------------------------------------------------------------
        self.gpu_renderset_on.clicked.connect(functools.partial(self.change_gpu_attr, True, "renderset"))
        self.gpu_renderset_off.clicked.connect(functools.partial(self.change_gpu_attr, False, "renderset"))
        

        self.ass_setting_on.clicked.connect(functools.partial(self.change_ass_attr,True))
        self.ass_setting_off.clicked.connect(functools.partial(self.change_ass_attr,False))

        self.gpu_vis_on.clicked.connect(functools.partial(self.change_gpu_attr, True, "vis"))
        self.gpu_vis_off.clicked.connect(functools.partial(self.change_gpu_attr, False, "vis"))

        self.check_sel_ass_tex.clicked.connect(self.check_ass_texture_path)
        self.open_filepathedit.clicked.connect(self.open_filepathedit_win)
        self.open_txmanager.clicked.connect(self.open_txmanager_win)

        self.lookattr_combobox.activated.connect(self.simple_lock_setattr)
        self.dispalyattr_combobox.activated.connect(self.simple_display_setattr)

        self.cut_log_button.clicked.connect(self.open_log)
    #标准组件
        #输出路径方式
        self.export_mod_ma.clicked.connect(self.refresh_export_path)
        self.export_mod_asset.clicked.connect(self.refresh_export_path)
        #拾取路径
        self.export_path_get.clicked.connect(self.get_simple_export_filepath)
        #导出
        self.export_simple_button.clicked.connect(self.export_simple_apply)
        #加入列表
        self.import_simple_button.clicked.connect(self.add_to_import_listwidget)
        #导入
        self.simple_input_button.clicked.connect(self.assembly_simple_complex)

        self.simple_log_button.clicked.connect(self.open_log)
    #多态
        self.high_radiobutton.clicked.connect(self.change_mod_and_plan)
        self.low_radiobutton.clicked.connect(self.change_mod_and_plan)

        self.start_export_button.clicked.connect(self.export_polymorphic)

        self.dt_log_button.clicked.connect(self.open_log)
    #拼装
        self.project_comboBox.activated.connect(self.combobox_refresh_tree)
        self.assembly_get_path.clicked.connect(self.get_assembly_export_filepath)
        self.search_lineedit.textChanged.connect(self.search_have_text)
        self.scale_slider.valueChanged.connect(self.change_table_iconsize)

        self.unt_assembly_tree.itemDoubleClicked.connect(self.Treewidget_click)
        self.unt_assembly_table.cellDoubleClicked.connect(self.assembly_unt_complex)
        self.assembly_log_button.clicked.connect(self.open_log)

    #分析
        self.to_analyze.clicked.connect(self.analysis_of_the_scene)
        self.check_log_button.clicked.connect(self.open_log)
    #窗口关闭，杀掉创建的scriptjob
    def closeEvent(self, event):
        print u"Σ(⊙▽⊙\"窗口关闭了,开始清理HyperScene的scriptjob"
        for item in cmds.scriptJob(lj=1 ):
            if "change_display_combbox" in item:
                cmds.scriptJob(k=int(item.split(":",1)[0]),f=1 )
                print u"清理成功"
        if os.path.isfile(self.temp_file):
            try:
                os.remove(self.temp_file)
                print u"HyperScene的log文件清理成功"
            except:
                print u"HyperScene的log文件清理失败，文件被占用"
    def takesleep(self):
        print u"在这里停顿"
        time.sleep(3)

    def write_log(self,text):
        with open(self.temp_file, 'a') as f:
            f.write(text.encode("utf-8"))
            f.write("\n")

    def open_log(self):
        if os.path.isfile(self.temp_file):
            os.startfile(self.temp_file)
        else:
            print u"HyperScene的log文件不存在"
#################################################################################################################################################
#
#unt资产显示切换执行方法
#
#################################################################################################################################################
    #辅助选择
    def select_object_mode(self,selected_mode):
        self.sel_mod_selections.setChecked(True)
        self.sel_mod_childs.setEnabled(True)
        #选中呢视窗内所有物体
        if selected_mode == "preview":
            view = OpenMayaUI.M3dView.active3dView()
            cam_dag = OpenMaya.MDagPath()
            view.getCamera(cam_dag)
            # 遍历视口
            draw_traversal = OpenMayaUI.MDrawTraversal()
            # 设置视锥
            draw_traversal.setFrustum(cam_dag, view.portWidth(), view.portHeight()) 
            draw_traversal.traverse() 
            obj_list = []
            for i in range(draw_traversal.numberOfItems()):
                # 在找到的项目列表中获取给定项目的路径
                shape_dag_path = OpenMaya.MDagPath()
                draw_traversal.itemPath(i, shape_dag_path)
                transform_dag_path = OpenMaya.MDagPath()
                # 确定指定DAG节点的路径
                OpenMaya.MDagPath.getAPathTo(shape_dag_path.transform(), transform_dag_path)
                obj = transform_dag_path.fullPathName()
                # print obj
                if cmds.objExists(obj) and cmds.objectType(obj) == "transform":
                    obj_list.append(obj)
            cmds.select(obj_list,r=1)
        #反选
        elif selected_mode == "reverse":
            select_objs = cmds.ls(sl=1,l=1)
            all_objs = cmds.ls(type="transform",l=1)
            replace_select = []
            for i in all_objs:
                if not i in select_objs:
                    replace_select.append(i)
            cmds.select(replace_select,r=1)
        elif selected_mode == "clear":
            cmds.select(cl=1)
        #过滤unt
        elif selected_mode == "sel_unt":
            select_list = []
            select_objs = cmds.ls(sl=1,l=1)
            for selobj in select_objs:
                if self.return_unt_bool(selobj):
                    select_list.append(selobj)
            cmds.select(select_list,r=1)
        #Unt反选
        elif selected_mode == "unt_reverse":
            all_objs = cmds.ls(type="transform",l=1)
            allunt_list = []
            select_objs = cmds.ls(sl=1,l=1)
            replace_select = []
            for i in select_objs:
                if not self.return_unt_bool(i):
                    cmds.confirmDialog( title=u'警告!!',icon='question', message=u"选择的物体中有不是unt的物体", button=[u'关闭'])
                    return
            
            for i in all_objs:
                if self.return_unt_bool(i):
                    if i not in select_objs:
                        replace_select.append(i)
            
            cmds.select(replace_select,r=1)
        elif selected_mode == "set":
            mel.eval("CreateQuickSelectSet;")
    def filtration_unt(self,file_type):
        sel_objs = cmds.ls(sl=1, l=1)
        for i in sel_objs:
            if not self.return_unt_bool(i):
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u"选择的物体中有不是unt的物体", button=[u'关闭'])
                return
        mesh_list = []
        for i in sel_objs:
            try:
                unt_path = cmds.getAttr(i + '.' + self.unt_attr_dic[file_type])
                gpu_node = cmds.listRelatives(i, c=1, type='gpuCache', f=1)
                if gpu_node:
                    _path = cmds.getAttr(gpu_node[0] + '.cacheFileName')
                    if unt_path == _path:
                        mesh_list.append(i)
            except:
                pass
        cmds.select(mesh_list, r=1)
    def filtration_no_rendershape(self):
        sel_objs = cmds.ls(sl=1, l=1)
        for i in sel_objs:
            if not self.return_unt_bool(i):
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u"选择的物体中有不是unt的物体", button=[u'关闭'])
                return
        no_rendershape_list = []
        rendershape_list = ['aiStandIn']
        for i in sel_objs:
            yes_bool = False
            for k in rendershape_list:
                if cmds.listRelatives(i, c=1, f=1, type=k):
                    yes_bool = True
            if not yes_bool:
                no_rendershape_list.append(i)
        cmds.select(no_rendershape_list, r=1)


    #添加GPUcache（bbox形态）右键
    def create_gpu_add_right_menu(self):
        #创建右键菜单 
        self.gpuaddRightMenu = QtWidgets.QMenu(self)
        menuitemA = self.gpuaddRightMenu.addAction(u'添加GPUcache(DIY形态)')
        self.gpuaddRightMenu.addSeparator()
        menuitemB = self.gpuaddRightMenu.addAction(u'添加GPUcache(实模形态)')
        self.gpuaddRightMenu.addSeparator()
        menuitemC = self.gpuaddRightMenu.addAction(u'添加GPUcache(BBox形态)')

        menuitemA.triggered.connect(functools.partial(self.add_gpucache_node,"diy"))
        menuitemB.triggered.connect(functools.partial(self.add_gpucache_node,"gpu"))
        menuitemC.triggered.connect(functools.partial(self.add_gpucache_node,"bbox"))
    def show_gpu_add_custom_menu(self):
        # 菜单在鼠标点击的位置显示
        self.gpuaddRightMenu.exec_(QtGui.QCursor().pos())
    
    def print_text(self):
        print u"恭喜你点了个寂寞！"
    def return_select_obj(self,objtype):
        #如果选择了物体，自动切换为所选
        if cmds.ls(sl=1):
            self.sel_mod_selections.setChecked(True)
            self.sel_mod_childs.setEnabled(True)
        aimobj_list = []
        if self.sel_mod_selections.isChecked():#选择的物体
            #是否包含子物体
            if self.sel_mod_childs.isChecked():
                cmds.select(hi=1)
            for item in cmds.ls(sl=1,l=1):
                if cmds.objectType(item) == objtype:
                    if not item in aimobj_list:
                        aimobj_list.append(item)
                child_list = cmds.listRelatives(item,c=1,pa=1,f=1)
                if child_list:
                    for ite in child_list:
                        if cmds.objectType(ite) == objtype:
                            if not ite in aimobj_list:
                                aimobj_list.append(ite)
        elif self.sel_mod_all.isChecked():#所有物体
            aimobj_list = cmds.ls(l=1, type=objtype)

        # cmds.select(cl=1)
        return aimobj_list
    ####返回一个场景中没有重名的名字
    def return_new_shapename(self,shapename):
        int_list = [0]
        for i in cmds.ls(shapename+"__*"):
            try:
                int_list.append(int(i.rsplit("_",1)[-1]))
            except:
                pass
        new_list = sorted(int_list)
        return '''{}__{}'''.format(shapename, (new_list[-1] + 1))
    def return_unt_fullpath(self,filepath):
        filepath_dic = {}
        if filepath.endswith("_BBox.abc") or filepath.endswith("_DIY.abc"):
            gpu_path  = filepath.rsplit("_",1)[0] + ".abc"
            ass_path  = filepath.rsplit("_",1)[0] + ".ass"
            bbox_path = filepath.rsplit("_",1)[0] + "_BBox.abc"
            diy_path  = filepath.rsplit("_",1)[0] + "_DIY.abc"
            ma_path   = filepath.rsplit("_",1)[0] + ".ma"
            if os.path.exists(gpu_path):
                filepath_dic["gpu"] = gpu_path
            if os.path.exists(ass_path):
                filepath_dic["ass"] = ass_path
            if os.path.exists(bbox_path):
                filepath_dic["bbox"] = bbox_path
            if os.path.exists(diy_path):
                filepath_dic["diy"] = diy_path
            if os.path.exists(ma_path):
                filepath_dic["ma"] = ma_path
            return filepath_dic
        else:
            gpu_path  = filepath.rsplit(".",1)[0] + ".abc"
            ass_path  = filepath.rsplit(".",1)[0] + ".ass"
            bbox_path = filepath.rsplit(".",1)[0] + "_BBox.abc"
            diy_path  = filepath.rsplit(".",1)[0] + "_DIY.abc"
            ma_path   = filepath.rsplit(".",1)[0] + ".ma"
            if os.path.exists(gpu_path):
                filepath_dic["gpu"] = gpu_path
            if os.path.exists(ass_path):
                filepath_dic["ass"] = ass_path
            if os.path.exists(bbox_path):
                filepath_dic["bbox"] = bbox_path
            if os.path.exists(diy_path):
                filepath_dic["diy"] = diy_path
            if os.path.exists(ma_path):
                filepath_dic["ma"] = ma_path
        return filepath_dic
    def return_unt_color(self,file_dic):
        if len(file_dic) == 3 and "ass" in file_dic and "gpu" in file_dic and "bbox" in file_dic:
            return [0.74,1,1]
        elif len(file_dic) == 4 and "ass" in file_dic and "gpu" in file_dic and "bbox" in file_dic and "ma" in file_dic:
            return [0.91,1,0.91]
        elif len(file_dic) == 5 and "ass" in file_dic and "gpu" in file_dic and "bbox" in file_dic and "diy" in file_dic and "ma" in file_dic:
            return [0.91,0.85,1]
        else:
            return [1,0.91,0.91]

    def return_unt_bool(self,transform_node):
        return_list = []
        for obj_atter in self.unt_attr_dic.values():
            try:
                if cmds.getAttr(transform_node + "." + obj_atter) != "":
                    return_list.append(True)
            except:
                return_list.append(False)
        if True in return_list:
            return True
        else:
            return False

    
    #操作范围------------------------------------------------------------------------------------------------
    def change_select_mod(self):
        if self.sel_mod_selections.isChecked():#选择的物体
            self.sel_mod_childs.setChecked(True)
            self.sel_mod_childs.setEnabled(True)
        elif self.sel_mod_all.isChecked():#所有物体
            self.sel_mod_childs.setChecked(False)
            self.sel_mod_childs.setEnabled(False)
    #unt创建与删除-------------------------------------------------------------------------- ----------------------
    ####更新unt的transform信息
    def set_object_outline_color(self,obj,color_list):
        cmds.setAttr(( obj + ".useOutlinerColor"), 1)
        cmds.setAttr(( obj + ".outlinerColor"), color_list[0], color_list[1], color_list[2])
    def add_refresh_unt_attr(self,sel_node,file_dic):
        for attr,filepath in file_dic.items():
            try:
                #获取属性
                ass_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic[attr])
                print u"----->>检测到属性{}".format(self.unt_attr_dic[attr])
                self.write_log(u"{}:----->>检测到属性{}".format(datetime.datetime.now(),self.unt_attr_dic[attr]))
                #如果文件路径与属性路径不通，更新属性路径
                if filepath != ass_shape_path:
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]),l=0)
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]), filepath, type="string")
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]),l=1)
                    print u"----->>更新属性{}".format(self.unt_attr_dic[attr])
                    self.write_log(u"{}:----->>更新属性{}".format(datetime.datetime.now(),self.unt_attr_dic[attr]))
                else:
                    print u"{}:----->>{}属性正确".format(datetime.datetime.now(),self.unt_attr_dic[attr])
                    self.write_log(u"{}:----->>{}属性正确".format(datetime.datetime.now(),self.unt_attr_dic[attr]))
                    #锁定属性
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]),l=1)
            except:
                #没有属性，创建
                try:
                    cmds.addAttr(sel_node, longName=self.unt_attr_dic[attr], dataType='string' )
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]), filepath, type="string")
                    cmds.setAttr((sel_node + "." + self.unt_attr_dic[attr]),l=1)
                    print u"----->>添加属性{}".format(self.unt_attr_dic[attr])
                    self.write_log(u"{}:----->>添加属性{}".format(datetime.datetime.now(),self.unt_attr_dic[attr]))
                except:
                    print u"----->>{}添加失败".format(self.unt_attr_dic[attr])
                    self.write_log(u"{}:----->>{}添加失败".format(datetime.datetime.now(),self.unt_attr_dic[attr]))
    def del_refresh_unt_attr(self,sel_node):
        for del_attr in self.unt_attr_dic.values():
            try:
                cmds.setAttr((sel_node + "." + del_attr),l=0)
                cmds.deleteAttr(sel_node, attribute=del_attr)
            except:
                print u"----->>{}删除失败".format(sel_node + "." + del_attr)
                self.write_log(u"{}:----->>{}删除失败".format(datetime.datetime.now(),(sel_node + "." + del_attr)))
    def refresh_transform_node(self):
        #开始时间
        begin = datetime.datetime.now()

        sel_trs_nodes = self.return_select_obj("transform")
        bar_num = 1
        if sel_trs_nodes:
            if len(sel_trs_nodes) > 2000:
                if cmds.confirmDialog( title=u'警告!!',icon='question', message=u'操作队列超过2000个物体，\n需要等待时间大于50秒，\n是否继续？', button=[u'继续', u'取消']) == u'取消':
                    return
            self.cut_progressBar.setMaximum(len(sel_trs_nodes))
            for sel_node in sel_trs_nodes:
                print u"依据GPUshape创建unt",sel_node
                self.write_log(u"{}:{}-----{}".format(datetime.datetime.now(),u"依据GPUshape创建unt",sel_node))
                # if cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="aiStandIn") and cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache"):
                #     print u"----->>检测到双shape结构"
                #     gpunode = cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache")
                #     assnode = cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="aiStandIn")
                #     if len(gpunode) == 1 and len(assnode) == 1:
                #         ass_path = cmds.getAttr(assnode[0] + ".dso")
                #         file_dic = self.return_unt_fullpath(ass_path)
                #         #添加属性
                #         self.add_refresh_unt_attr(sel_node,file_dic)
                #         #颜色
                #         color = self.return_unt_color(file_dic)
                #         self.set_object_outline_color(sel_node,color)
                # elif cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="aiStandIn"):
                #     print u"----->>检测到arnold"
                #     assnode = cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="aiStandIn")
                #     if len(assnode) == 1:
                #         ass_path = cmds.getAttr(assnode[0] + ".dso")
                #         file_dic = self.return_unt_fullpath(ass_path)
                #         #添加属性
                #         self.add_refresh_unt_attr(sel_node,file_dic)
                #         #颜色
                #         color = self.return_unt_color(file_dic)
                #         self.set_object_outline_color(sel_node,color)
                if cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache"):
                    print u"----->>检测到gpucache"
                    self.write_log(u"{}:----->>检测到gpucache".format(datetime.datetime.now()))
                    gpunode = cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache")
                    if len(gpunode) == 1 :
                        gpu_path = cmds.getAttr(gpunode[0] + ".cacheFileName")
                        file_dic = self.return_unt_fullpath(gpu_path)
                        #删除有属性
                        self.del_refresh_unt_attr(sel_node)
                        #添加属性
                        self.add_refresh_unt_attr(sel_node,file_dic)
                        #颜色
                        color = self.return_unt_color(file_dic)
                        self.set_object_outline_color(sel_node,color)
                self.cut_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(sel_trs_nodes)))
                self.cut_progressBar.setValue(bar_num)
                bar_num += 1
            #进度条完成
            self.cut_progressBar.setFormat(u"完成")
            #运行时间
            end = datetime.datetime.now()
            print end - begin
            self.write_log(u"{}:----->>检测到gpucache".format(datetime.datetime.now()))
    def add_ref_maya(self):
        if self.sel_mod_all.isChecked():
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"禁止选择All，添加ma文件", button=[u'关闭'])
            return
        else:
            sel_obj_list = self.return_select_obj("transform")
            unt_list = []
            for i in sel_obj_list:
                if self.return_unt_bool(i):
                    unt_list.append(i)
            
            for selobj in unt_list:
                
                print u"添加ref Maya文件",selobj
                self.write_log(u"{}:{}-----{}".format(datetime.datetime.now(),u"添加ref Maya文件",selobj))
                try:
                    #获取属性
                    ma_path = cmds.getAttr(selobj + "." + self.unt_attr_dic['ma'])
                    print u"----->>开始Ref Maya文件",ma_path
                    self.write_log(u"{}:{}-----{}".format(datetime.datetime.now(),u"----->>开始Ref Maya文件",ma_path))
                    if os.path.exists(ma_path):#文件是否存在
                        ns=ma_path.rsplit("/",1)[-1].rsplit(".",1)[0]
                        grp_name = selobj.rsplit("|",1)[-1] + "_ma"
                        refnode = cmds.file(ma_path, r=1, type="mayaAscii", mergeNamespacesOnClash=False, namespace=ns, gr=1, gn=grp_name)
                        grp_name = cmds.ls(sl=1,l=1)[0]
                        #设置xform
                        cmds.xform(selobj, rp=[0,0,0])
                        cmds.xform(selobj, sp=[0,0,0])
                        cmds.xform(grp_name, rp=[0,0,0])
                        cmds.xform(grp_name, sp=[0,0,0])
                        #锁定属性
                        cmds.setAttr((grp_name + ".tx"), l=1)
                        cmds.setAttr((grp_name + ".ty"), l=1)
                        cmds.setAttr((grp_name + ".tz"), l=1)
                        cmds.setAttr((grp_name + ".rx"), l=1)
                        cmds.setAttr((grp_name + ".ry"), l=1)
                        cmds.setAttr((grp_name + ".rz"), l=1)
                        cmds.setAttr((grp_name + ".sx"), l=1)
                        cmds.setAttr((grp_name + ".sy"), l=1)
                        cmds.setAttr((grp_name + ".sz"), l=1)
                        cmds.setAttr((grp_name + ".v" ), l=1)
                        try:
                            if not cmds.listRelatives(selobj,c=1,pa=1,f=1):
                                cmds.setAttr((cmds.createNode("transform", n=self.return_new_shapename("loc_pos"),p=selobj) + ".visibility"), 0)
                            cmds.parent(grp_name, selobj)
                        except:
                            print u"{}:----->>移动失败，开始remove".format(datetime.datetime.now())
                            self.write_log(u"{}:----->>移动失败，开始remove".format(datetime.datetime.now()))
                            cmds.file(refnode, rr=1)
                            
                    else:
                        print u"----->>maya文件不存在{}".format(ma_path)
                        self.write_log(u"{}:----->>maya文件不存在{}".format(datetime.datetime.now(),ma_path))
                except:
                    print u"----->>获取maPath属性失败"
                    self.write_log(u"{}:----->>获取maPath属性失败".format(datetime.datetime.now(),ma_path))
    def del_ref_maya(self):
        if self.sel_mod_all.isChecked():
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"禁止选择All，添加ma文件", button=[u'关闭'])
            return
        else:
            try:
                sel_obj = self.return_select_obj("transform")
                refnode_list = []
                for i in sel_obj:
                    ref_node = cmds.referenceQuery(i,rfn=1)
                    if not ref_node in refnode_list:
                        refnode_list.append(ref_node)
                for refnode in refnode_list:
                    filepath = cmds.referenceQuery(refnode,f=1)
                    cmds.file(filepath,rr=1,f=1)
            except:
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u"选择的节点不是ref节点", button=[u'关闭'])
                return

    def add_gpu_bbox_diy_gpu(self):
        begin = datetime.datetime.now()

        #获取选择物体
        return_sel = cmds.ls(sl=1,l=1)
        select_node_list = self.return_select_obj('transform')
        #过滤unt
        new_list = []
        if select_node_list:
            for sel_node in select_node_list:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        select_node_list = new_list
        #增加节点
        if select_node_list:
            bar_num = 1
            self.cut_progressBar.setMaximum(len(select_node_list))
            for sel_node in select_node_list:
                print sel_node
                self.write_log(u"{}:{}-----{}".format(datetime.datetime.now(),u"添加GPU Shape节点",sel_node))
                gpu_shape_path = ""
                try:
                    gpu_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic['bbox'])
                except:
                    try:
                        gpu_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic['diy'])
                    except:
                        try:
                            gpu_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic['gpu'])
                        except:
                            print u"----->>获取gpuShapePath属性失败"
                            self.write_log(u"{}:----->>获取gpuShapePath属性失败".format(datetime.datetime.now()))
                            continue
                #获取属性
                if not cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache"):
                    if os.path.exists(gpu_shape_path):#abc文件是否存在
                        short_name = gpu_shape_path.rsplit('/',1)[-1].rsplit('.',1)[0]
                        #创建GPUcache节点
                        gpu_node = cmds.createNode("gpuCache", p=sel_node)
                        #设置路径
                        cmds.setAttr((gpu_node + ".cacheFileName"), gpu_shape_path, type = "string")
                        cmds.setAttr((gpu_node + ".cacheGeomPath"), "|", type = "string")
                        #设置属性
                        self.set_gpucache_attr(gpu_node,False)
                        #设置顺序
                        if len(cmds.listRelatives(sel_node,c=1,pa=1,s=1)) > 1:
                            cmds.reorder(gpu_node,f=1)
                        #重命名shape节点
                        shapename = "GPU_" + ''.join(filter(str.isalnum, str(short_name+'Shape')))
                        new_name = self.return_new_shapename(shapename)
                        gpuNod = cmds.rename(gpu_node,new_name)
                    else:
                        print u"----->>未找到文件{}".format(gpu_shape_path)
                        self.write_log(u"{}:----->>未找到文件{}".format(datetime.datetime.now(), gpu_shape_path))
                else:
                    print u"----->>已经存在gpuCache"
                    self.write_log(u"{}:----->>已经存在gpuCache".format(datetime.datetime.now()))
                self.cut_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(select_node_list)))
                self.cut_progressBar.setValue(bar_num)
                bar_num += 1
            self.cut_progressBar.setFormat(u"完成")
        #维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print end - begin
    def add_gpucache_node(self, gpu_type):
        begin = datetime.datetime.now()

        #获取选择物体
        return_sel = cmds.ls(sl=1,l=1)
        select_node_list = self.return_select_obj('transform')
        #过滤unt
        new_list = []
        if select_node_list:
            for sel_node in select_node_list:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        select_node_list = new_list
        #增加节点
        if select_node_list:
            bar_num = 1
            self.cut_progressBar.setMaximum(len(select_node_list))
            for sel_node in select_node_list:
                print sel_node
                self.write_log(u"{}:{}-----{}".format(datetime.datetime.now(),u"添加GPU {}节点".format(gpu_type),sel_node))
                gpu_shape_path = ""
                try:
                    #获取属性
                    gpu_shape_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic[gpu_type])
                    if not cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="gpuCache"):
                        if os.path.exists(gpu_shape_path):#abc文件是否存在
                            short_name = gpu_shape_path.rsplit('/',1)[-1].rsplit('.',1)[0]
                            #创建GPUcache节点
                            gpu_node = cmds.createNode("gpuCache", p=sel_node)
                            #设置路径
                            cmds.setAttr((gpu_node + ".cacheFileName"), gpu_shape_path, type = "string")
                            cmds.setAttr((gpu_node + ".cacheGeomPath"), "|", type = "string")
                            #设置属性
                            self.set_gpucache_attr(gpu_node,False)
                            #设置顺序
                            if len(cmds.listRelatives(sel_node,c=1,pa=1,s=1)) > 1:
                                cmds.reorder(gpu_node,f=1)
                            #重命名shape节点
                            shapename = "GPU_" + ''.join(filter(str.isalnum, str(short_name+'Shape')))
                            new_name = self.return_new_shapename(shapename)
                            gpuNod = cmds.rename(gpu_node,new_name)
                        else:
                            print u"----->>未找到文件{}".format(gpu_shape_path)
                            self.write_log(u"{}:----->>未找到文件{}".format(datetime.datetime.now(),gpu_shape_path))
                    else:
                        print u"----->>已经存在gpuCache"
                        self.write_log(u"{}:----->>已经存在gpuCache".format(datetime.datetime.now()))
                except:
                    print u"----->>获取gpuShapePath属性失败"
                    self.write_log(u"{}:----->>获取gpuShapePath属性失败".format(datetime.datetime.now()))
                self.cut_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(select_node_list)))
                self.cut_progressBar.setValue(bar_num)
                bar_num += 1
            self.cut_progressBar.setFormat(u"完成")
        #维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print end - begin
    def del_gpucache_node(self):
        begin = datetime.datetime.now()
        delete_list = []

        #获取选择物体
        return_sel = cmds.ls(sl=1,l=1)
        gpucachelist = self.return_select_obj('transform')
        #过滤unt
        new_list = []
        if gpucachelist:
            for sel_node in gpucachelist:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        gpucachelist = new_list
        #删除有属性的节点
        if gpucachelist:
            bar_num = 1
            self.cut_progressBar.setMaximum(len(gpucachelist))
            for item in gpucachelist:
                print item
                self.write_log(u"{}:{}-----{}".format(datetime.datetime.now(),u"删除GPUcache",item))
                if self.return_unt_bool(item):
                    _c = cmds.listRelatives(item, c=1, pa=1, f=1, type="gpuCache")
                    if _c:
                        delete_list = (delete_list + _c)
                else:
                    print u"----->>不是组件"
                    self.write_log(u"{}:----->>不是组件".format(datetime.datetime.now()))
                self.cut_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(gpucachelist)))
                self.cut_progressBar.setValue(bar_num)
                bar_num += 1
            self.cut_progressBar.setFormat(u"完成")
        cmds.delete(delete_list)
        #维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print end - begin
    def add_ass_node(self):
        begin = datetime.datetime.now()
        #获取选择物体
        return_sel = cmds.ls(sl=1,l=1)
        error_list = []
        select_node_list = self.return_select_obj('transform')
        #过滤unt
        new_list = []
        if select_node_list:
            for sel_node in select_node_list:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        select_node_list = new_list
        #增加节点
        if select_node_list:
            bar_num = 1
            self.cut_progressBar.setMaximum(len(select_node_list))
            for sel_node in select_node_list:
                print sel_node
                self.write_log(u"{}:{}-----{}".format(datetime.datetime.now(),u"添加GPU ASS节点",sel_node))
                ass_shape_path = ""
                try:
                    #获取属性
                    ass_shape_path = cmds.getAttr(sel_node + ".assShapePath")
                    if not cmds.listRelatives(sel_node, c=1, pa=1, f=1, type="aiStandIn"):
                        if os.path.exists(ass_shape_path):#abc文件是否存在
                            short_name = ass_shape_path.rsplit('/',1)[-1].rsplit('.',1)[0]
                            #创建Asscache节点
                            ass_node = cmds.createNode("aiStandIn", p=sel_node)
                            #设置属性
                            cmds.setAttr((ass_node + ".standInDrawOverride"),0)
                            #设置路径
                            cmds.setAttr((ass_node + ".dso"), ass_shape_path, type = "string")
                            #rename node
                            #
                            shapename = "ASS_" + ''.join(filter(str.isalnum, str(short_name+'Shape')))
                            new_name = self.return_new_shapename(shapename)
                            assNod = cmds.rename(ass_node,new_name)
                        else:
                            print u"----->>未找到文件{}".format(ass_shape_path)
                            self.write_log(u"{}:----->>未找到文件{}".format(datetime.datetime.now(),ass_shape_path))
                    else:
                        print u"----->>已经存在aiStandIn"
                        self.write_log(u"{}:----->>已经存在aiStandIn".format(datetime.datetime.now()))
                except:
                    print u"----->>获取assShapePath属性失败"
                    self.write_log(u"{}:----->>获取assShapePath属性失败".format(datetime.datetime.now()))
                self.cut_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(select_node_list)))
                self.cut_progressBar.setValue(bar_num)
                bar_num += 1
            self.cut_progressBar.setFormat(u"完成")
        #维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print end - begin
    def del_ass_node(self): 
        begin = datetime.datetime.now()
        delete_list = []

        #获取选择物体
        return_sel = cmds.ls(sl=1,l=1)
        asscachelist = self.return_select_obj('transform')
        #过滤unt
        new_list = []
        if asscachelist:
            for sel_node in asscachelist:
                if self.return_unt_bool(sel_node):
                    new_list.append(sel_node)
        asscachelist = new_list
        #删除有属性的节点
        if asscachelist:
            bar_num = 1
            self.cut_progressBar.setMaximum(len(asscachelist))
            for item in asscachelist:
                print item
                self.write_log(u"{}:{}-----{}".format(datetime.datetime.now(),u"删除aistandIn",item))
                if self.return_unt_bool(item):
                    _c = cmds.listRelatives(item, c=1, pa=1, f=1, type="aiStandIn")
                    if _c:
                        delete_list = (delete_list + _c)
                else:
                    print u"----->>不是组件"
                    self.write_log(u"{}:----->>不是组件".format(datetime.datetime.now()))
                self.cut_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(asscachelist)))
                self.cut_progressBar.setValue(bar_num)
                bar_num += 1
            self.cut_progressBar.setFormat(u"完成")
        cmds.delete(delete_list)
        #维持选择
        cmds.select(return_sel, r=1)
        end = datetime.datetime.now()
        print end - begin
    #GPUcache视口切换------------------------------------------------------------------------------------------------
    def change_gpu_display(self,gpu_type):
        return_sel = cmds.ls(sl=1,l=1)
        #获取选择物体
        sel_transform_list = self.return_select_obj('transform')
        error_list = []
        errpr_obj = []
        #设置属性
        bar_num = 1
        self.cut_progressBar.setMaximum(len(sel_transform_list))
        for sel_node in sel_transform_list:
            self.cut_progressBar.setValue(bar_num)
            self.cut_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(sel_transform_list)))
            bar_num += 1
            if not self.return_unt_bool(sel_node):
                continue
            try:
                #获取属性
                file_path = cmds.getAttr(sel_node + "." + self.unt_attr_dic[gpu_type])
                gpu_shape = cmds.listRelatives(sel_node,c=1,f=1,type="gpuCache")
                if os.path.exists(file_path):
                    if gpu_shape:
                        cmds.setAttr((gpu_shape[0] + ".cacheFileName"), file_path, type = "string")
                    else:
                        error_list.append((sel_node + u"未发现GPU节点"))
                        self.write_log(u"{}:GPUcache视口切换-----".format(datetime.datetime.now()) + sel_node + u"未发现GPU节点")
                        errpr_obj.append(sel_node)
                else:
                    error_list.append((sel_node + u"文件不存在"))
                    self.write_log(u"{}:GPUcache视口切换-----".format(datetime.datetime.now()) + sel_node + u"文件不存在")
                    errpr_obj.append(sel_node)
            except:
                error_list.append((sel_node + u"未找到属性" + self.unt_attr_dic[gpu_type]))
                self.write_log(u"{}:GPUcache视口切换-----".format(datetime.datetime.now()) + sel_node + u"未找到属性" + self.unt_attr_dic[gpu_type])
                errpr_obj.append(sel_node)
            
        self.cut_progressBar.setFormat(u"完成")
        if error_list:
            message = ""
            if len(error_list) > 3:
                for i in range(3):
                    message += (error_list[i] + "\n")
            else:
                for i in error_list:
                    message += (i + "\n")
            message += "\n ......"
            if cmds.confirmDialog( title=u'警告!!',icon='question', message=u"以下{}个物体切换失败\n{}".format(len(error_list), message), button=[u'选择出错物体',u'关闭']) == u'选择出错物体':
                cmds.select(errpr_obj, r=1)
                return
            
        #维持选择
        cmds.select(return_sel, r=1)

    def change_ass_display(self,attr_type,index):
        return_sel = cmds.ls(sl=1,l=1)
        #获取选择物体
        select_node_list = self.return_select_obj('aiStandIn')
        #设置属性
        if select_node_list:
            for assnode in select_node_list:
                if attr_type == "viewport_override":
                    cmds.setAttr((assnode + ".standInDrawOverride"), self.ass_pverride_comboBox.currentIndex())
                elif attr_type == "viewport_draw_mode":
                    cmds.setAttr((assnode + ".mode"), self.ass_drawmode_comboBox.currentIndex())
        #维持选择
        cmds.select(return_sel, r=1)

    def change_proview_display(self,checkbox_type):
        #show_gpu_checkBox   show_ass_checkBox   show_ins_checkBox
        wf_panel = cmds.getPanel(wf=True)
        all_modelpanel=cmds.getPanel( type='modelPanel' )
        if wf_panel in all_modelpanel:
            if checkbox_type == "gpucache":
                #show_gpu_checkBox
                if self.show_gpu_checkBox.isChecked():
                    cmds.modelEditor(wf_panel,e=1,pluginObjects=['gpuCacheDisplayFilter',True])
                else:
                    cmds.modelEditor(wf_panel,e=1,pluginObjects=['gpuCacheDisplayFilter',False])
            elif checkbox_type == "ass":
                #show_ass_checkBox
                if self.show_ass_checkBox.isChecked():
                    cmds.modelEditor(wf_panel,e=1,pluginShapes=True)
                else:
                    cmds.modelEditor(wf_panel,e=1,pluginShapes=False)
            elif checkbox_type == "instancer":
                #show_ins_checkBox
                if self.show_ins_checkBox.isChecked():
                    cmds.modelEditor(wf_panel,e=1,particleInstancers=True)
                else:
                    cmds.modelEditor(wf_panel,e=1,particleInstancers=False)
            elif checkbox_type == "handles":
                #视口handel
                if self.show_handel_checkbox.isChecked():
                    cmds.modelEditor(wf_panel,e=1,handles=True)
                else:
                    cmds.modelEditor(wf_panel,e=1,handles=False)
            elif checkbox_type == "twoSidedLighting":
                #双面照明
                if self.two_sidedlight_checkbox.isChecked():
                    cmds.modelEditor(wf_panel,e=1,twoSidedLighting=True)
                else:
                    cmds.modelEditor(wf_panel,e=1,twoSidedLighting=False)
    
    def change_instancer_display(self,index):
        sel_obj_list = self.return_select_obj('instancer')
        for item in sel_obj_list:
            cmds.setAttr((item + ".levelOfDetail"), index)
    def change_instancer_show_num(self,index):
        sel_obj_list = self.return_select_obj('instancer')
        for item in sel_obj_list:
            cmds.setAttr((item + ".displayPercentage"), index)

    def display_handle(self,on_off):
        select_obj = self.return_select_obj("transform")
        for selobj in select_obj:
            if self.return_unt_bool(selobj):
                cmds.setAttr((selobj + ".displayHandle"), on_off)
        pass
    def refresh_gpucahce_shape(self):
        mel.eval("gpuCache -refreshAll;")
    
    def refresh_preview_ogs(self):
        #重置
        cmds.ogs( reset=True )
    #unt渲染设置------------------------------------------------------------------------------------------------
    def set_gpucache_renderset(self, gpu_shape_node, on_off):
        if on_off:
            cmds.setAttr((gpu_shape_node + ".castsShadows"), 1)
            cmds.setAttr((gpu_shape_node + ".receiveShadows"),1)
            cmds.setAttr((gpu_shape_node + ".motionBlur"),1)
            cmds.setAttr((gpu_shape_node + ".primaryVisibility"),1)
            cmds.setAttr((gpu_shape_node + ".smoothShading"),1)
            cmds.setAttr((gpu_shape_node + ".visibleInReflections"),0)
            cmds.setAttr((gpu_shape_node + ".visibleInRefractions"),0)
            cmds.setAttr((gpu_shape_node + ".doubleSided"),1)
            cmds.setAttr((gpu_shape_node + ".geometryAntialiasingOverride"),0)

            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseReflection"),1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularReflection"),1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseTransmission"),1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularTransmission"),1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInVolume"),1)
            cmds.setAttr((gpu_shape_node + ".aiSelfShadows"),1)

        else:
            cmds.setAttr((gpu_shape_node + ".castsShadows"),0)
            cmds.setAttr((gpu_shape_node + ".receiveShadows"),0)
            cmds.setAttr((gpu_shape_node + ".motionBlur"),0)
            cmds.setAttr((gpu_shape_node + ".primaryVisibility"),0)
            cmds.setAttr((gpu_shape_node + ".smoothShading"),0)
            cmds.setAttr((gpu_shape_node + ".visibleInReflections"),0)
            cmds.setAttr((gpu_shape_node + ".visibleInRefractions"),0)
            cmds.setAttr((gpu_shape_node + ".doubleSided"),0)
            cmds.setAttr((gpu_shape_node + ".geometryAntialiasingOverride"),0)

            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseReflection"),0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularReflection"),0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseTransmission"),0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularTransmission"),0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInVolume"),0)

    def set_gpucache_attr(self, gpu_shape_node, on_off):
        if on_off:
            cmds.setAttr((gpu_shape_node + ".castsShadows"), 1)
            cmds.setAttr((gpu_shape_node + ".receiveShadows"),1)
            cmds.setAttr((gpu_shape_node + ".motionBlur"),1)
            cmds.setAttr((gpu_shape_node + ".primaryVisibility"),1)
            cmds.setAttr((gpu_shape_node + ".smoothShading"),1)
            cmds.setAttr((gpu_shape_node + ".visibleInReflections"),0)
            cmds.setAttr((gpu_shape_node + ".visibleInRefractions"),0)
            cmds.setAttr((gpu_shape_node + ".doubleSided"),1)
            cmds.setAttr((gpu_shape_node + ".geometryAntialiasingOverride"),0)

            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseReflection"),1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularReflection"),1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseTransmission"),1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularTransmission"),1)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInVolume"),1)
        else:
            cmds.setAttr((gpu_shape_node + ".castsShadows"),0)
            cmds.setAttr((gpu_shape_node + ".receiveShadows"),0)
            cmds.setAttr((gpu_shape_node + ".motionBlur"),0)
            cmds.setAttr((gpu_shape_node + ".primaryVisibility"),0)
            cmds.setAttr((gpu_shape_node + ".smoothShading"),0)
            cmds.setAttr((gpu_shape_node + ".visibleInReflections"),0)
            cmds.setAttr((gpu_shape_node + ".visibleInRefractions"),0)
            cmds.setAttr((gpu_shape_node + ".doubleSided"),0)
            cmds.setAttr((gpu_shape_node + ".geometryAntialiasingOverride"),0)

            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseReflection"),0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularReflection"),0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInDiffuseTransmission"),0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInSpecularTransmission"),0)
            cmds.setAttr((gpu_shape_node + ".aiVisibleInVolume"),0)
    def change_gpu_attr(self,on_off,attr_type):
        return_sel = cmds.ls(sl=1,l=1)
        #获取选择物体
        gpucachelist = self.return_select_obj('gpuCache')
        #设置属性
        if gpucachelist:
            for gpu_node in gpucachelist:
                if attr_type == "renderset":
                    self.set_gpucache_renderset(gpu_node,on_off)
                elif attr_type == "vis":
                    cmds.setAttr((gpu_node + ".v"),on_off) 
    
        #维持选择
        cmds.select(return_sel, r=1)
    def set_ass_renderset(self, ass_shape_node, on_off):
        if on_off:
            cmds.setAttr((ass_shape_node + ".castsShadows"), 1)
            cmds.setAttr((ass_shape_node + ".motionBlur"),1)
            cmds.setAttr((ass_shape_node + ".primaryVisibility"),1)
            cmds.setAttr((ass_shape_node + ".aiVisibleInDiffuseReflection"),1)
            cmds.setAttr((ass_shape_node + ".aiVisibleInSpecularReflection"),1)
            cmds.setAttr((ass_shape_node + ".aiVisibleInDiffuseTransmission"),1)
            cmds.setAttr((ass_shape_node + ".aiVisibleInSpecularTransmission"),1)
            cmds.setAttr((ass_shape_node + ".aiVisibleInVolume"),1)

        else:
            cmds.setAttr((ass_shape_node + ".castsShadows"), 0)
            cmds.setAttr((ass_shape_node + ".motionBlur"),0)
            cmds.setAttr((ass_shape_node + ".primaryVisibility"),0)
            cmds.setAttr((ass_shape_node + ".aiVisibleInDiffuseReflection"),0)
            cmds.setAttr((ass_shape_node + ".aiVisibleInSpecularReflection"),0)
            cmds.setAttr((ass_shape_node + ".aiVisibleInDiffuseTransmission"),0)
            cmds.setAttr((ass_shape_node + ".aiVisibleInSpecularTransmission"),0)
            cmds.setAttr((ass_shape_node + ".aiVisibleInVolume"),0)
    def change_ass_attr(self,on_off):
        return_sel = cmds.ls(sl=1,l=1)
        #获取选择物体
        select_node_list = self.return_select_obj('aiStandIn')
        #设置属性
        if select_node_list:
            for assnode in select_node_list:
                self.set_ass_renderset(assnode, on_off)

        #维持选择
        cmds.select(return_sel, r=1)
        
    #其他------------------------------------------------------------------------------------------------
    def check_ass_texture_path(self):
        #获取选择物体
        error_list = []
        asslist = self.return_select_obj('aiStandIn')
        #设置属性
        if asslist:
            # 分析ass代理文件贴图路径
            getAllAss = []
            getAllNodes = asslist

            for node in getAllNodes:
                getPath = cmds.getAttr(node + ".dso")
                if getPath and getPath not in getAllAss:
                    getAllAss.append(getPath)

            for ass in getAllAss:
                getAllPath = []
                print(ass)
                ar.AiBegin()
                ar.AiMsgSetConsoleFlags(ar.AI_LOG_ALL)
                ar.AiASSLoad(ass, ar.AI_NODE_ALL)
                iterator = ar.AiUniverseGetNodeIterator(ar.AI_NODE_ALL)

                while not ar.AiNodeIteratorFinished(iterator):
                    node = ar.AiNodeIteratorGetNext(iterator)

                    if ar.AiNodeIs(node, "MayaFile") or ar.AiNodeIs(node, "image"):
                        getPath = ar.AiNodeGetStr(node, "filename")

                        if getPath and getPath not in getAllPath:
                            getAllPath.append(getPath)

                ar.AiNodeIteratorDestroy(iterator)
                ar.AiEnd()
                pprint(getAllPath)
    def open_filepathedit_win(self):
        mel.eval("filePathEditorWin")
    def open_txmanager_win(self):
        import mtoa.ui.arnoldmenu
        mtoa.ui.arnoldmenu.arnoldTxManager()

    def set_lock_attr(self,obj,on_off,menu_text):
        if menu_text == 'trs':
            cmds.setAttr((obj + ".tx"), l=on_off)
            cmds.setAttr((obj + ".ty"), l=on_off)
            cmds.setAttr((obj + ".tz"), l=on_off)
            cmds.setAttr((obj + ".rx"), l=on_off)
            cmds.setAttr((obj + ".ry"), l=on_off)
            cmds.setAttr((obj + ".rz"), l=on_off)
            cmds.setAttr((obj + ".sx"), l=on_off)
            cmds.setAttr((obj + ".sy"), l=on_off)
            cmds.setAttr((obj + ".sz"), l=on_off)
        elif menu_text == "v":
            cmds.setAttr((obj + ".v" ), l=on_off)
    def simple_lock_setattr(self):
        combobox_text = self.lookattr_combobox.currentText()
        for selobj in self.return_select_obj("transform"):
            if combobox_text == u'锁定通道栏TRS':
                self.set_lock_attr(selobj,True,"trs")
            elif combobox_text == u"解锁通道栏TRS":
                self.set_lock_attr(selobj,False,"trs")
            elif combobox_text == u"锁定通道栏Visibility":
                self.set_lock_attr(selobj,True,"v")
            elif combobox_text == u"解锁通道栏Visibility":
                self.set_lock_attr(selobj,False,"v")

    def set_display_attr(self,obj,on_off,menu_text):
        if menu_text == 'trs':
            cmds.setAttr((obj + ".tx"), k=on_off)
            cmds.setAttr((obj + ".ty"), k=on_off)
            cmds.setAttr((obj + ".tz"), k=on_off)
            cmds.setAttr((obj + ".rx"), k=on_off)
            cmds.setAttr((obj + ".ry"), k=on_off)
            cmds.setAttr((obj + ".rz"), k=on_off)
            cmds.setAttr((obj + ".sx"), k=on_off)
            cmds.setAttr((obj + ".sy"), k=on_off)
            cmds.setAttr((obj + ".sz"), k=on_off)
        elif menu_text == "v":
            cmds.setAttr((obj + ".v" ), k=on_off)
    def simple_display_setattr(self):
        combobox_text = self.dispalyattr_combobox.currentText()
        for selobj in self.return_select_obj("transform"):
            if combobox_text == u'显示通道栏TRS':
                self.set_display_attr(selobj,True,"trs")
            elif combobox_text == u"隐藏通道栏TRS":
                self.set_display_attr(selobj,False,"trs")
            elif combobox_text == u"显示通道栏Visibility":
                self.set_display_attr(selobj,True,"v")
            elif combobox_text == u"隐藏通道栏Visibility":
                self.set_display_attr(selobj,False,"v")
#################################################################################################################################################
#
#标准组件   执行方法
#
#################################################################################################################################################
    #简单组件listwidget右键菜单
    def create_simple_right_menu(self):
        #创建右键菜单 
        self.simpleRightMenu = QtWidgets.QMenu(self)
        menuitemB = self.simpleRightMenu.addAction(u'删除选择')
        self.simpleRightMenu.addSeparator()
        menuitemA = self.simpleRightMenu.addAction(u'清空')

        menuitemA.triggered.connect(self.delete_simple_all_item)
        menuitemB.triggered.connect(self.delete_simple_select_item)
    def show_simple_custom_menu(self):
        # 菜单在鼠标点击的位置显示
        self.simpleRightMenu.exec_(QtGui.QCursor().pos())
    def delete_simple_all_item(self):
        oldlist=self.simple_input_list.count()
        if oldlist:
            self.simple_input_list.clear()
        self.simple_listwidget_itempath = {}
    def delete_simple_select_item(self):
        selectitem = self.simple_input_list.selectedItems()
        for item in selectitem:
            line_num = self.simple_input_list.row(item)
            text = self.simple_input_list.item(line_num).text()
            self.simple_input_list.takeItem(line_num)
            if text in self.simple_listwidget_itempath:
                del self.simple_listwidget_itempath[text]
            else:
                print "未找到相关数据信息",text
        
    #简单组件拖入文件
    def dragEnterEvent(self,event):
        event.accept()
    def dropEvent(self, event):
        oldlist=self.simple_input_list.count()
        urls=event.mimeData().urls()
        num=oldlist
        for url in urls:
            fullflname=str(url).split("file:///",1)[-1][:-2]
            #获取路径下文件，看是否有ass和gpu
            file_dic = self.return_unt_fullpath(fullflname)
            shortname = fullflname.rsplit("/",1)[-1].rsplit(".",1)[0]
            if shortname in self.simple_listwidget_itempath:
                print u"列表内有同名的资产文件",fullflname
            else:
                if "ass" in file_dic and "gpu" in file_dic:
                    assfile_shortname = file_dic["ass"].rsplit("/",1)[-1].rsplit(".",1)[0]
                    if file_dic["ass"] in self.simple_listwidget_itempath.values():
                        print u"列表内有同名的资产文件",fullflname
                    else:
                        self.simple_listwidget_itempath[assfile_shortname] = file_dic["ass"]
                        #图标
                        icon = QtGui.QIcon()
                        icon.addPixmap(QtGui.QPixmap(":\eye.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                        #添加item
                        item = QtWidgets.QListWidgetItem(self.simple_input_list)
                        item.setIcon(icon)
                        item.setText(assfile_shortname)
                else:
                    print u"缺少对应的gpucache或者aistandin",fullflname
    
    def refresh_export_path(self):
        #当前的文件名
        file = OpenMaya.MFileIO()
        fullpath = file.currentFile()
        shortname_array = fullpath.rsplit("/",1)[-1].split(".",1)[0].split("_")
        if fullpath == "":
            cmds.error(u"请先保存文件")
        #选择Maya文件所在路径
        if self.export_mod_ma.isChecked():
            self.simple_export_filepath = fullpath.rsplit("/",1)[0]
        #选择项目路径
        elif self.export_mod_asset.isChecked():
            #检查文件名
            check_filename = self.filepath_array()
            if not check_filename[0]:
                cmds.confirmDialog( title=u'警告!!',icon='question', message=check_filename[1], button=[u'关闭'])
                self.export_path_lineedit.setText("")
                return
            self.simple_export_filepath = '''{proj_path}/{proj}/Assets/{asset_type}/{asset_name}/SHD'''.format(proj_path = self.project_path,
                                                                                                                proj = shortname_array[0],
                                                                                                                asset_type = shortname_array[1],
                                                                                                                asset_name = shortname_array[2])
        #设置UI输出路径
        self.export_path_lineedit.setText(self.simple_export_filepath)
        pass
    #检查贴图
    def check_texture_path(self):
        all_nodes = cmds.ls(type="file")
        if all_nodes:
            for filenode in all_nodes:
                if not cmds.getAttr(filenode + ".ftn").startswith("Z:/"):
                    print cmds.getAttr(filenode + ".ftn").startswith("Z:/")
                    return False
        all_nodes = cmds.ls(type="aiImage")
        if all_nodes:
            for filenode in all_nodes:
                if not cmds.getAttr(filenode + ".filename").startswith("Z:/"):
                    return False
        return True

    #导出组件
    def get_simple_export_filepath(self):
        fielpath=cmds.fileDialog2(fm=3, dialogStyle=1,cap=u'导出路径',okc=u'确定',cc=u'取消')
    
        if fielpath!=None and os.path.exists(fielpath[0]):
            self.simple_export_filepath = fielpath[0]
        self.export_path_lineedit.setText(self.simple_export_filepath)
    def filepath_array(self):
        module = ""
        #项目代号
        proj_name = ""
        #asset
        asset_type = ""
        asset_name = ""
        task_name = ""
        #获取文件名
        file = OpenMaya.MFileIO()
        filename = file.currentFile().rsplit("/",1)[-1]
        if filename == "":
            return [False, u"文件名获取失败"]
        proj_name = filename.split("_")[0]
        #确定属于什么模块，资产还是镜头
        asset_mod = re.match((proj_name + '_([a-zA-Z0-9]*)_([a-zA-Z0-9]*\d*)_([a-zA-Z0-9]*)(\w*)?\.ma') , filename )
        shot_mod = re.match((proj_name + '_(e\d{2})(s\d{3})(c\d{4})_([a-zA-Z0-9]*)(\w*)?\.ma') , filename )
        if not asset_mod and not shot_mod:
            return [False, u"文件名不符合提交审核命名规范"]
        if asset_mod:
            asset_type = asset_mod.groups()[0]
            asset_name = asset_mod.groups()[1]
            task_name = asset_mod.groups()[2]
            return [True, proj_name, asset_type, asset_name, task_name]
    def export_gpuass(self, selobj, aimfilepath):
        
        if not cmds.ogs(q=1, pause=True ):
            cmds.ogs( pause=True )
        cmds.select(selobj, r=1)
        #选择的bbox颜色type
        select_export_item = self.simple_type_listwidget.selectedItems()[0]
        color = self.bbox_color_dic[select_export_item.text()][0]
        #export file-----------------------------------------------------------------------
        short_name=cmds.file(q=1,sn=1,shn=1).rsplit('.',1)[0]
        path=aimfilepath
        error_message = ""
        
        self.progressBar_maxvalue = 4
        self.simple_progressBar.setValue(0)
        self.simple_progressBar.setMaximum(self.progressBar_maxvalue)
        
        self.write_log(u"{}:-----导出标准组件".format(datetime.datetime.now()))
        #导出ass
        exp_bool = False
        old_file = path+'/'+short_name+'.ass'
        new_file = path+'/'+short_name+'_.ass'
        if os.path.exists(old_file):
            try:
                if self.simple_ass.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过Ass导出\n".format(old_file)
        else:
            exp_bool = True
        if self.simple_ass.isChecked() and exp_bool:
            ass_fullpath = path+'/'+short_name+'.ass'
            cmds.file(ass_fullpath,f=1,options="-shadowLinks 1;-mask 6399;-lightLinks 1;-boundingBox",type="ASS Export",pr=1,es=1)
            print '--------------------->>',ass_fullpath
            self.write_log(u"{}:-----{}".format(datetime.datetime.now(), ass_fullpath))
        if os.path.exists(new_file):
            os.remove(new_file)
        self.add_progressbar_value(self.simple_progressBar, 1)
        #导出GPUcache
        exp_bool = False
        old_file = path+'/'+short_name+'.abc'
        new_file = path+'/'+short_name+'_.abc'
        if os.path.exists(old_file):
            try:
                if self.simple_gpu.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过GPUcache导出\n".format(old_file)
        else:
            exp_bool = True
        if self.simple_gpu.isChecked() and exp_bool:
            cmds.undoInfo(state=True,infinity=True)
            cmds.undoInfo(ock=True)
            copy_obj = cmds.duplicate(selobj, rr=1)[0]

            #代码
            shader_node = ''
            sg_node = ''
            if select_export_item.text() == u"水体类Water":
                    #创建材质
                shader_node = cmds.shadingNode("phong",asShader=1,n="BBox_material")
                cmds.setAttr((shader_node + ".transparency"),0.6,0.6,0.6)
                sg_node = cmds.sets(renderable=1,noSurfaceShader=1,empty=1,n="BBox_materialSG")
                cmds.connectAttr((shader_node+".color"),((sg_node+".surfaceShader")),f=1)
            else:
                    #创建材质
                shader_node = cmds.shadingNode("lambert",asShader=1,n="BBox_material")
                sg_node = cmds.sets(renderable=1,noSurfaceShader=1,empty=1,n="BBox_materialSG")
                cmds.connectAttr((shader_node+".color"),((sg_node+".surfaceShader")),f=1)
            
            
                    #上色
            cmds.setAttr((shader_node + '.color'),color[0],color[1],color[2])
                    #赋予材质
            cmds.sets(copy_obj, edit = 1, forceElement = sg_node)
            #
            cmds.undoInfo(cck=True)

            gpu_fullpath = path+'/'+short_name+'.abc'
            cmds.gpuCache(copy_obj, startTime=1, endTime=1, optimize=1, optimizationThreshold=4000, writeMaterials=1, dataFormat="ogawa", directory=path, fileName=short_name)
            # mel.eval('''gpuCache -startTime {startFrame} 
            #                     -endTime {endFrame} 
            #                     -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa 
            #                     -directory "{filePath}" 
            #                     -fileName "{fileName}" 
            #                     {objectName};'''.format(startFrame=1,
            #                                             endFrame=1,
            #                                             filePath=path,
            #                                             fileName=short_name,
            #                                             objectName=selobj))
            
            cmds.undo()
            cmds.undoInfo(state=True, infinity=False)
            print '--------------------->>',gpu_fullpath
            self.write_log(u"{}:-----{}".format(datetime.datetime.now(), gpu_fullpath))
        if os.path.exists(new_file):
            os.remove(new_file)
        self.add_progressbar_value(self.simple_progressBar, 1)
        #导出DIY
        exp_bool = False
        old_file = path+'/'+short_name+'_DIY.abc'
        new_file = path+'/'+short_name+'_DIY_.abc'
        if os.path.exists(old_file):
            try:
                if self.simple_diy.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过DIY导出\n".format(old_file)
        else:
            exp_bool = True
        if self.simple_diy.isChecked() and exp_bool:
            if cmds.objExists("|DIY"):
                cmds.setAttr("|DIY.v", 1)
                diy_fullpath = path+'/'+short_name+'_DIY.abc'
                cmds.select("|DIY", r=1)
                cmds.gpuCache("|DIY", startTime=1, endTime=1, optimize=1, optimizationThreshold=4000, writeMaterials=1, dataFormat="ogawa", directory=path, fileName=(short_name+'_DIY'))
                print '--------------------->>',diy_fullpath
                self.write_log(u"{}:-----{}".format(datetime.datetime.now(), diy_fullpath))
        if os.path.exists(new_file):
            os.remove(new_file)
        self.add_progressbar_value(self.simple_progressBar, 1)
        #导出bbox
        exp_bool = False
        old_file = path+'/'+short_name+'_BBox.abc'
        new_file = path+'/'+short_name+'_BBox_.abc'
        if os.path.exists(old_file):
            try:
                if self.simple_bbox.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过BBox导出\n".format(old_file)
        else:
            exp_bool = True
        if self.simple_bbox.isChecked() and exp_bool:
            #导出BBox
                #创建namespace，
            cmds.undoInfo(state=True,infinity=True)
            cmds.undoInfo(ock=True)
            shader_node = ''
            sg_node = ''
            if select_export_item.text() == u"水体类Water":
                    #创建材质
                shader_node = cmds.shadingNode("phong",asShader=1,n="BBox_material")
                cmds.setAttr((shader_node + ".transparency"),0.6,0.6,0.6)
                sg_node = cmds.sets(renderable=1,noSurfaceShader=1,empty=1,n="BBox_materialSG")
                cmds.connectAttr((shader_node+".color"),((sg_node+".surfaceShader")),f=1)
            else:
                    #创建材质
                shader_node = cmds.shadingNode("lambert",asShader=1,n="BBox_material")
                sg_node = cmds.sets(renderable=1,noSurfaceShader=1,empty=1,n="BBox_materialSG")
                cmds.connectAttr((shader_node+".color"),((sg_node+".surfaceShader")),f=1)
            
            
                    #上色
            cmds.setAttr((shader_node + '.color'),color[0],color[1],color[2])
                    #转bbox
            cmds.select(selobj, r=1)
            bbox_fullpath = path+'/'+short_name+'_BBox.abc'
            bbox_obj = cmds.geomToBBox(nameSuffix='_BBox',single=1,keepOriginal=1)
                    #赋予材质
            cmds.sets(bbox_obj, edit = 1, forceElement = sg_node)
            #
            cmds.undoInfo(cck=True)
                    #导出
            # cmds.gpuCache(bbox_obj[0], startTime=1, endTime=1, directory=path, fileName=(short_name+'_BBox'))
            cmds.gpuCache(bbox_obj[0], startTime=1, endTime=1, optimize=1, optimizationThreshold=4000, writeMaterials=1, dataFormat="ogawa", directory=path, fileName=(short_name+'_BBox'))
            
            # mel.eval('''gpuCache -startTime {startFrame} 
            #                     -endTime {endFrame} 
            #                     -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa 
            #                     -directory "{filePath}" 
            #                     -fileName "{fileName}" 
            #                     {objectName};'''.format(startFrame=1,
            #                                             endFrame=1,
            #                                             filePath=path,
            #                                             fileName=(short_name+'_BBox'),
            #                                             objectName=bbox_obj[0]))
            cmds.undo()
            cmds.undoInfo(state=True, infinity=False)
            print '--------------------->>',bbox_fullpath
            self.write_log(u"{}:-----{}".format(datetime.datetime.now(), bbox_fullpath))
        if os.path.exists(new_file):
            os.remove(new_file)
        self.add_progressbar_value(self.simple_progressBar, 1)
        

        if cmds.ogs(q=1, pause=True ):
            cmds.ogs( pause=True )

        if error_message:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=error_message, button=[u'关闭'])
    def export_simple_apply(self):
        #刷新Arnold贴图缓存
        maya.cmds.arnoldFlushCache(selected_textures=True)
        #目录不存在
        if not os.path.exists(self.simple_export_filepath):
            try:
                os.makedirs(self.simple_export_filepath)
            except:
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u'路径创建失败', button=[u'关闭'])
                return
        if self.export_mod_asset.isChecked():
            #检查文件名
            check_filename = self.filepath_array()
            if not check_filename[0]:
                cmds.confirmDialog( title=u'警告!!',icon='question', message=check_filename[1], button=[u'关闭'])
                return
        #是否选中类型
        if not self.simple_type_listwidget.selectedItems():
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"选择导出组件的类型", button=[u'关闭'])
            return
        #检查贴图路径file,aiimage
        if self.check_tex_on_z.isChecked():
            if not self.check_texture_path():
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u"检测到贴图文件不在Z盘，请检查文件", button=[u'关闭'])
                return
        #检查DIY
        if self.simple_diy.isChecked():
            if not cmds.objExists("|DIY"):
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u"未发现DIY物体", button=[u'关闭'])
                return
            else:
                try:
                    cmds.setAttr("|DIY.v",l=0)
                    cmds.setAttr("|DIY.v",1)
                except:
                    print u"设置|DIY显示失败"
                    self.write_log(u"{}:-----设置|DIY显示失败".format(datetime.datetime.now()))
        #导出
        if cmds.objExists("|Mesh"):
            try:
                cmds.setAttr("|Mesh.v",l=0)
                cmds.setAttr("|Mesh.v",1)
            except:
                print u"设置|Mesh显示失败"
                self.write_log(u"{}:-----设置|Mesh显示失败".format(datetime.datetime.now()))
            self.export_gpuass("|Mesh", self.simple_export_filepath)
        else:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"未发现|Mesh物体", button=[u'关闭'])
            return
        #打开导出路径
        if self.export_simple_openpath.isChecked():
            os.startfile(self.simple_export_filepath)
    #添加到导入列表
    def add_to_import_listwidget(self):
        #simple_input_list,        self.simple_listwidget_itempath = {}
        #目录不存在
        if not os.path.exists(self.simple_export_filepath):
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u'路径不存在', button=[u'关闭'])
            return
        #获取路径下所有ass文件
        assfile_list = cmds.getFileList(fld=self.simple_export_filepath,fs='*.abc')
        for assfile in assfile_list:
            assfile_shortname = assfile.rsplit(".",1)[0].replace("","").replace("_BBox","").replace("_DIY","")
            assfullpath = self.simple_export_filepath + "/" + assfile
            #判断是否有重复的资产名，防止二次添加
            if assfile_shortname in self.simple_listwidget_itempath:
                pass
                # print u"列表内有同名的资产文件",assfullpath
            else:
                #获取路径下文件，看是否有ass和gpu
                file_dic = self.return_unt_fullpath(assfullpath)
                if file_dic:
                    self.simple_listwidget_itempath[assfile_shortname] = assfullpath
                    #图标
                    icon = QtGui.QIcon()
                    icon.addPixmap(QtGui.QPixmap(":\eye.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                    #添加item
                    item = QtWidgets.QListWidgetItem(self.simple_input_list)
                    item.setIcon(icon)
                    item.setText(assfile_shortname)
    #导入
    def create_gpu_and_ass(self,file_dic):
        #创建transform节点
        short_name = file_dic.values()[0].rsplit('/',1)[-1].rsplit('.',1)[0].replace("_BBox","").replace("_DIY","")
        transform_node = cmds.createNode("transform", n=('GPU_'+short_name))

        cmds.select(transform_node, r=1)
        self.sel_mod_selections.setChecked(True)
        #添加unt属性
        self.add_refresh_unt_attr(transform_node,file_dic)

        #添加GPU
        if "gpu" in file_dic:
            self.add_gpucache_node("gpu")
        elif "diy" in file_dic:
            self.add_gpucache_node("diy")
        elif "bbox" in file_dic:
            self.add_gpucache_node("bbox")
        
        #添加ass
        self.add_ass_node()
        
        return transform_node
    def assembly_simple_complex(self):
        if self.simple_input_list.selectedItems():
            for sel_list_item in self.simple_input_list.selectedItems():
                sel_item = sel_list_item.text()
                asspath = self.simple_listwidget_itempath[sel_item]
                file_dic = self.return_unt_fullpath(asspath)
                self.assembly_create_gpu_and_ass(file_dic)
        else:
            print u"请在左侧选择一个或者多个进行导入"
        pass
#################################################################################################################################################
#
#转换数据   执行方法
#
#################################################################################################################################################
    #UI显示，实模和伪实模
    def change_mod_and_plan(self):
        if self.high_radiobutton.isChecked():
            self.ex_gpu_checkBox.setText(u"GPU实模")
        elif self.low_radiobutton.isChecked():
            self.ex_gpu_checkBox.setText(u"GPU伪实模")

    #导出
    def export_polymorphic(self):
        
        #是否选中类型
        if not self.data_type_listwidget.selectedItems():
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"选择导出组件的类型", button=[u'关闭'])
            return
        #refMaya是否勾选导出Maya
        if self.data_ref_ma_checkbox.isChecked() and not self.ex_ma_checkBox.isChecked():
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"请勾选导出Maya文件", button=[u'关闭'])
            return
        #选择的bbox颜色type
        select_export_item = self.data_type_listwidget.selectedItems()[0]
        color = self.bbox_color_dic[select_export_item.text()][0]
        #是否是伪实模
        geo_sky = ""
        if self.high_radiobutton.isChecked():
            geo_sky = "geo"
        elif self.low_radiobutton.isChecked():
            geo_sky = "sky"
        #文件路径
        file = OpenMaya.MFileIO()
        filefullpath = file.currentFile().rsplit("/",1)[0]
        #物体筛选
        source_obj = ""
        exp_obj = ""
        exp_diy = ""
        select_object = cmds.ls(sl=1,l=1)
        if not select_object:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"请选择物体", button=[u'关闭'])
            return
        if len(select_object) > 2:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"选择物体过多", button=[u'关闭'])
            return
        if len(select_object) == 2:
            if "_DIY" in select_object[0]:
                exp_obj = select_object[1]
                exp_diy = select_object[0]
                if not exp_diy.rsplit("|")[-1] == (exp_obj.rsplit("|")[-1] + "_DIY"):
                    cmds.confirmDialog( title=u'警告!!',icon='question', message=u"请选择对应的DIY", button=[u'关闭'])
                    return
            elif "_DIY" in select_object[1]:
                exp_obj = select_object[0]
                exp_diy = select_object[1]
                if not exp_diy.rsplit("|")[-1] == (exp_obj.rsplit("|")[-1] + "_DIY"):
                    cmds.confirmDialog( title=u'警告!!',icon='question', message=u"请选择对应的DIY", button=[u'关闭'])
                    return
            else:
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u"请选择一个物体，和该物体的DIY自定义边界盒", button=[u'关闭'])
                return
        elif len(select_object) == 1:
            if "_DIY" in select_object[0]:
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u"DIY物体必须配合本体一起选择才能使用", button=[u'关闭'])
                return
            else:
                exp_obj = select_object[0]
                if self.ex_diy_checkBox.isChecked():
                    cmds.confirmDialog( title=u'警告!!',icon='question', message=u"未选择DIY物体", button=[u'关闭'])
                    return
        
        #导出文件名
        save_file_name = ""
        if len(exp_obj.split("|")) > 4:
            save_file_name = """_DT_{}__{}__{}""".format(exp_obj.split("|")[1], exp_obj.split("|")[2], exp_obj.split("|")[-1]).replace(":","_")
        else:
            save_file_name = "_DT_" + exp_obj[1:].replace("|","__").replace(":","_")
        save_diyfile_name = save_file_name + "_DIY"
        #复制物体，放到最上层级
        source_obj = exp_obj
        if cmds.objExists(exp_obj):
            copy_obj = cmds.duplicate(exp_obj,rr=1,n=save_file_name)
            try:
                root_obj = cmds.parent(copy_obj,w=1)
                exp_obj = root_obj[0]
            except:
                exp_obj = copy_obj[0]
                pass
            

        if cmds.objExists(exp_diy):
            copy_diy = cmds.duplicate(exp_diy,rr=1,n=save_diyfile_name)
            try:
                root_diy = cmds.parent(copy_diy,w=1)
                exp_diy = root_diy[0]
            except:
                exp_diy = copy_diy[0]
                pass

        try:
            cmds.setAttr((exp_obj + ".v"),l=0)
            cmds.setAttr((exp_obj + ".v"),1)
        except:
            print u"设置{}显示失败".format(exp_obj)
        try:
            cmds.setAttr((exp_diy + ".v"),l=0)
            cmds.setAttr((exp_diy + ".v"),1)
        except:
            print u"设置{}显示失败".format(exp_diy)

        if not cmds.ogs(q=1, pause=True ):
            cmds.ogs( pause=True )
        error_message = ""
        
        
        self.progressBar_maxvalue = 5
        self.dt_progressBar.setValue(0)
        self.dt_progressBar.setMaximum(self.progressBar_maxvalue)
        
        self.write_log(u"{}:-----导出多态组件".format(datetime.datetime.now()))
        #导出ass
        exp_bool = False
        old_file = filefullpath+'/'+save_file_name+'.ass'
        new_file = filefullpath+'/'+save_file_name+'_.ass'
        if os.path.exists(old_file):
            try:
                if self.ex_ass_checkBox.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过Ass导出\n".format(old_file)
        else:
            exp_bool = True
        if self.ex_ass_checkBox.isChecked() and exp_bool:
            if cmds.objExists(exp_obj):
                cmds.select(exp_obj, r=1)
                #导出ass
                ass_fullpath = filefullpath+'/'+save_file_name+'.ass'
                cmds.file(ass_fullpath,f=1,options="-shadowLinks 1;-mask 6399;-lightLinks 1;-boundingBox",type="ASS Export",pr=1,es=1)
                print u'ass导出完成\n----->>',ass_fullpath
                self.write_log(u"{}:-----ass导出完成{}".format(datetime.datetime.now(), ass_fullpath))
        if os.path.exists(new_file):
            os.remove(new_file)
        
        self.add_progressbar_value(self.dt_progressBar, 1)
        #导出bbox
        exp_bool = False
        old_file = filefullpath + "/" + save_file_name + '_BBox.abc'
        new_file = filefullpath + "/" + save_file_name + '_BBox_.abc'
        if os.path.exists(old_file):
            try:
                if self.ex_bbox_checkBox.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过BBox导出\n".format(old_file)
        else:
            exp_bool = True
        if self.ex_bbox_checkBox.isChecked() and exp_bool:
            if cmds.objExists(exp_obj):
                cmds.select(exp_obj, r=1)
                #导出BBox
                cmds.undoInfo(state=True,infinity=True)
                cmds.undoInfo(ock=True)

                shader_node = ''
                sg_node = ''
                if select_export_item.text() == u"水体类Water":
                        #创建材质
                    shader_node = cmds.shadingNode("phong",asShader=1,n="BBox_material")
                    cmds.setAttr((shader_node + ".transparency"),0.6,0.6,0.6)
                    sg_node = cmds.sets(renderable=1,noSurfaceShader=1,empty=1,n="BBox_materialSG")
                    cmds.connectAttr((shader_node+".color"),((sg_node+".surfaceShader")),f=1)
                else:
                        #创建材质
                    shader_node = cmds.shadingNode("lambert",asShader=1,n="BBox_material")
                    sg_node = cmds.sets(renderable=1,noSurfaceShader=1,empty=1,n="BBox_materialSG")
                    cmds.connectAttr((shader_node+".color"),((sg_node+".surfaceShader")),f=1)
                
                
                        #上色
                cmds.setAttr((shader_node + '.color'),color[0],color[1],color[2])
                        #转bbox
                cmds.select(exp_obj, r=1)
                bbox_obj = cmds.geomToBBox(nameSuffix='_BBox',single=1,keepOriginal=1)
                        #赋予材质
                cmds.sets(bbox_obj, edit = 1, forceElement = sg_node)
                        #导出
                #
                cmds.undoInfo(cck=True)

                cmds.gpuCache(bbox_obj[0], startTime=1, endTime=1, optimize=1, optimizationThreshold=4000, writeMaterials=1, dataFormat="ogawa", directory=filefullpath, fileName=(save_file_name+'_BBox'))
                # mel.eval('''gpuCache -startTime {startFrame} 
                #                     -endTime {endFrame} 
                #                     -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa 
                #                     -directory "{filePath}" 
                #                     -fileName "{fileName}" 
                #                     {objectName};'''.format(startFrame=1,
                #                                             endFrame=1,
                #                                             filePath=filefullpath,
                #                                             fileName=(save_file_name+'_BBox'),
                #                                             objectName=bbox_obj[0]))
                cmds.undo()
                cmds.undoInfo(state=True, infinity=False)
                print u'bbox导出完成\n----->>',filefullpath + "/" + save_file_name + '_BBox.abc'
                self.write_log(u"{}:-----bbox导出完成{}".format(datetime.datetime.now(), (filefullpath + "/" + save_file_name + '_BBox.abc')))
        if os.path.exists(new_file):
            os.remove(new_file)

        self.add_progressbar_value(self.dt_progressBar, 1)
        #导出diy
        exp_bool = False
        old_file = filefullpath + "/" + save_diyfile_name + '.abc'
        new_file = filefullpath + "/" + save_diyfile_name + '_.abc'
        if os.path.exists(old_file):
            try:
                if self.ex_diy_checkBox.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过DIY导出\n".format(old_file)
        else:
            exp_bool = True
        if self.ex_diy_checkBox.isChecked() and exp_bool:
            if cmds.objExists(exp_diy):
                cmds.setAttr((exp_diy + ".v"), 1)
                cmds.select(exp_diy, r=1)
                cmds.gpuCache(exp_diy, startTime=1, endTime=1, optimize=1, optimizationThreshold=4000, writeMaterials=1, dataFormat="ogawa", directory=filefullpath, fileName=save_diyfile_name)
                print u'diy导出完成\n----->>',filefullpath + "/" + save_diyfile_name + '.abc'
                self.write_log(u"{}:-----diy导出完成{}".format(datetime.datetime.now(), (filefullpath + "/" + save_diyfile_name + '.abc')))
        if os.path.exists(new_file):
            os.remove(new_file)
        
        self.add_progressbar_value(self.dt_progressBar, 1)
        #导出gpu
        exp_bool = False
        old_file = filefullpath + "/" + save_file_name + '.abc'
        new_file = filefullpath + "/" + save_file_name + '_.abc'
        if os.path.exists(old_file):
            try:
                if self.ex_gpu_checkBox.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过GPU导出\n".format(old_file)
        else:
            exp_bool = True
        if self.ex_gpu_checkBox.isChecked():
            if cmds.objExists(exp_obj):
                cmds.select(exp_obj, r=1)
                print "++++++++++++++++++++++++++++++",exp_obj
                if geo_sky == "geo":
                    cmds.undoInfo(state=True,infinity=True)
                    cmds.undoInfo(ock=True)
                    #代码
                    shader_node = ''
                    sg_node = ''
                    if select_export_item.text() == u"水体类Water":
                            #创建材质
                        shader_node = cmds.shadingNode("phong",asShader=1,n="BBox_material")
                        cmds.setAttr((shader_node + ".transparency"),0.6,0.6,0.6)
                        sg_node = cmds.sets(renderable=1,noSurfaceShader=1,empty=1,n="BBox_materialSG")
                        cmds.connectAttr((shader_node+".color"),((sg_node+".surfaceShader")),f=1)
                    else:
                            #创建材质
                        shader_node = cmds.shadingNode("lambert",asShader=1,n="BBox_material")
                        sg_node = cmds.sets(renderable=1,noSurfaceShader=1,empty=1,n="BBox_materialSG")
                        cmds.connectAttr((shader_node+".color"),((sg_node+".surfaceShader")),f=1)
                    
                    
                            #上色
                    cmds.setAttr((shader_node + '.color'),color[0],color[1],color[2])
                            #赋予材质
                    cmds.sets(exp_obj, edit = 1, forceElement = sg_node)
                    cmds.undoInfo(cck=True)
                    #导出GPUcache
                    cmds.gpuCache(exp_obj, startTime=1, endTime=1, optimize=1, optimizationThreshold=4000, writeMaterials=1, dataFormat="ogawa", directory=filefullpath, fileName=save_file_name)
                    cmds.undo()
                    cmds.undoInfo(state=True, infinity=False)
                elif geo_sky == "sky":
                    #导出替代geo的plane
                    cmds.polyPlane(ch=0,n="geo_sky",sx=1,sy=1)
                    cmds.setAttr("geo_sky.rx",90)
                    cmds.setAttr("geo_sky.ty",0.5)
                    cmds.gpuCache("|geo_sky", startTime=1, endTime=1, optimize=1, optimizationThreshold=4000, writeMaterials=1, dataFormat="ogawa", directory=filefullpath, fileName=save_file_name)
                    cmds.delete("|geo_sky")
                print u'gpu导出完成\n----->>',filefullpath + "/" + save_file_name + '.abc'
                self.write_log(u"{}:-----gpu导出完成{}".format(datetime.datetime.now(), (filefullpath + "/" + save_file_name + '.abc')))
        if os.path.exists(new_file):
            os.remove(new_file)

        self.add_progressbar_value(self.dt_progressBar, 1)
        #导出ma
        exp_bool = False
        old_file = filefullpath+'/'+save_file_name+'.ma'
        new_file = filefullpath+'/'+save_file_name+'_.ma'
        if os.path.exists(old_file):
            try:
                if self.ex_ma_checkBox.isChecked():
                    os.rename(old_file,new_file)
                    exp_bool = True
            except:
                error_message += u"{}文件被占用，跳过Ma导出\n".format(old_file)
        else:
            exp_bool = True
        if self.ex_ma_checkBox.isChecked() and exp_bool:
            #导出ma
            if cmds.objExists(exp_obj):
                cmds.select(exp_obj, r=1)
                ma_fullpath = filefullpath+'/'+save_file_name+'.ma'
                cmds.file(ma_fullpath,f=1,type="mayaAscii",pr=1,es=1)
                print u'ma导出完成\n----->>',ma_fullpath
                self.write_log(u"{}:-----ma导出完成{}".format(datetime.datetime.now(), ma_fullpath))
        if os.path.exists(new_file):
            os.remove(new_file)
        
        self.add_progressbar_value(self.dt_progressBar, 1)
        #删除复制物体
        if cmds.objExists(exp_obj):
            cmds.delete(exp_obj)
        if cmds.objExists(exp_diy):
            cmds.delete(exp_diy)
        
        #组装多态
        if self.data_import_unt_checkbox.isChecked():
            file_dic = self.return_unt_fullpath(filefullpath+'/'+save_file_name+'.ass')
            if file_dic:
                gpu_node = self.create_gpu_and_ass(file_dic)
                _p = cmds.listRelatives(source_obj,p=1,pa=1)
                if _p:
                    all_child = cmds.listRelatives(_p[0], c=1, pa=1, f=1, type="transform")
                    for index,val in enumerate(all_child):
                        if val == source_obj:
                            num = len(all_child)-index - 1
                            cmds.parent(gpu_node, _p[0])
                            cmds.reorder(gpu_node, relative=-num)
        #refMaya文件
        if self.data_ref_ma_checkbox.isChecked() and self.ex_ma_checkBox.isChecked():
            ma_fullpath = filefullpath+'/'+save_file_name+'.ma'
            ref_loc_name = save_file_name.rsplit("_",1)[-1] + "_ma"
            refList = cmds.ls(references = True)
            for refnode in refList:
                filepath = cmds.referenceQuery(refnode, f=1)
                if ma_fullpath == filepath or ma_fullpath in filepath:
                    cmds.confirmDialog( title=u'警告!!',icon='question', message=u"场景中有ref相同文件", button=[u'关闭'])
                    return
            
            if cmds.objExists(ref_loc_name):
                cmds.confirmDialog( title=u'警告!!',icon='question', message=u"场景中有同名节点，请更改{}".format(ref_loc_name), button=[u'关闭'])
                return
            else:
                refnode = cmds.file(ma_fullpath, r=1, type="mayaAscii", mergeNamespacesOnClash=False, namespace=save_file_name, gr=1, gn=ref_loc_name)
                _p = cmds.listRelatives(source_obj,p=1,pa=1)
                if _p:
                    all_child = cmds.listRelatives(_p[0], c=1, pa=1, f=1, type="transform")
                    for index,val in enumerate(all_child):
                        if val == source_obj:
                            num = len(all_child)-index - 1
                            cmds.parent(ref_loc_name, _p[0])
                            cmds.reorder(ref_loc_name, relative=-num)
        elif self.data_ref_ma_checkbox.isChecked() and not self.ex_ma_checkBox.isChecked():
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"请勾选导出Maya文件", button=[u'关闭'])
            if cmds.ogs(q=1, pause=True ):
                cmds.ogs( pause=True )
            return
        if cmds.ogs(q=1, pause=True ):
            cmds.ogs( pause=True )

        if error_message:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=error_message, button=[u'关闭'])

#################################################################################################################################################
#
#组装工具   执行方法
#
#################################################################################################################################################
    #预设右键
    def create_del_defaultset(self):
        #创建右键菜单 
        self.del_defaultsetMenu = QtWidgets.QMenu(self)
        menuitemA = self.del_defaultsetMenu.addAction(u'删除')

        menuitemA.triggered.connect(self.delete_default_setting)
    def show_del_defaultset_menu(self):
        # 菜单在鼠标点击的位置显示
        self.del_defaultsetMenu.exec_(QtGui.QCursor().pos())
    #treewidget右键
    def create_assemblytree_right_menu(self):
        # icon_load = QtGui.QIcon()
        # icon_load.addPixmap(QtGui.QPixmap(":/CN_refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #创建右键菜单 
        self.assemblyTreeMenu = QtWidgets.QMenu(self)
        menuitemD = self.assemblyTreeMenu.addAction(u'上级路径')
        self.assemblyTreeMenu.addSeparator()
        menuitemA = self.assemblyTreeMenu.addAction(u'加载Unt(当前路径)')
        menuitemB = self.assemblyTreeMenu.addAction(u'加载Unt(包括子路径)')
        self.assemblyTreeMenu.addSeparator()
        menuitemC = self.assemblyTreeMenu.addAction(u'保存预设')

        menuitemA.triggered.connect(functools.partial(self.from_path_get_unt,"this"))
        menuitemB.triggered.connect(functools.partial(self.from_path_get_unt,"child"))
        menuitemC.triggered.connect(self.save_json_dic)
        menuitemD.triggered.connect(self.get_tree_sup_path)
        # self.menuitemB.triggered.connect(self.delete_simple_select_item)
    def show_assemblytree_custom_menu(self):
        # 菜单在鼠标点击的位置显示
        self.assemblyTreeMenu.exec_(QtGui.QCursor().pos())
    #tablewidget右键
    def create_assembly_right_menu(self):
        icon_load = QtGui.QIcon()
        icon_load.addPixmap(QtGui.QPixmap(":/CN_refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon_openpath = QtGui.QIcon()
        icon_openpath.addPixmap(QtGui.QPixmap(":/folder-open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon_assembly = QtGui.QIcon()
        icon_assembly.addPixmap(QtGui.QPixmap(":/filtersOn.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #创建右键菜单 
        self.assemblyRightMenu = QtWidgets.QMenu(self)
        menuitemA = self.assemblyRightMenu.addAction(icon_load, u'刷新')
        self.assemblyRightMenu.addSeparator()
        menuitemB = self.assemblyRightMenu.addAction(icon_openpath, u'打开路径')
        self.assemblyRightMenu.addSeparator()
        menuitemC = self.assemblyRightMenu.addAction(icon_assembly, u'导入组件')
        self.assemblyRightMenu.addSeparator()
        menuitemD = self.assemblyRightMenu.addMenu(u'筛选')
        #([u"缩略图", u"资产名", "Ma", u"GPUcache", "Ass", "Boundingbox", "GPUcache_DIY", "Folder"])
        menuitemD_All = menuitemD.addAction(u"All")
        menuitemD_None = menuitemD.addAction(u"None")
        self.assemblyRightMenu.addSeparator()
        menuitemD_itemA = menuitemD.addAction(u'Ma')
        menuitemD_itemA.setCheckable(True)
        self.menu_action_list.append(menuitemD_itemA)
        menuitemD_itemB = menuitemD.addAction(u'GPUcache')
        menuitemD_itemB.setCheckable(True)
        self.menu_action_list.append(menuitemD_itemB)
        menuitemD_itemC = menuitemD.addAction(u'Ass')
        menuitemD_itemC.setCheckable(True)
        self.menu_action_list.append(menuitemD_itemC)
        menuitemD_itemD = menuitemD.addAction(u'Boundingbox')
        menuitemD_itemD.setCheckable(True)
        self.menu_action_list.append(menuitemD_itemD)
        menuitemD_itemE = menuitemD.addAction(u'GPUcache_DIY')
        menuitemD_itemE.setCheckable(True)
        self.menu_action_list.append(menuitemD_itemE)

        menuitemD_All.triggered.connect(functools.partial(self.search_all_none,"all"))
        menuitemD_None.triggered.connect(functools.partial(self.search_all_none,"none"))
        menuitemA.triggered.connect(self.refresh_assembly_table)
        menuitemB.triggered.connect(self.assembly_open_filepath)
        menuitemC.triggered.connect(self.assembly_unt_complex)
        menuitemD_itemA.triggered.connect(self.search_have_text)
        menuitemD_itemB.triggered.connect(self.search_have_text)
        menuitemD_itemC.triggered.connect(self.search_have_text)
        menuitemD_itemD.triggered.connect(self.search_have_text)
        menuitemD_itemE.triggered.connect(self.search_have_text)
        # self.menuitemB.triggered.connect(self.delete_simple_select_item)
    def show_assembly_custom_menu(self):
        # 菜单在鼠标点击的位置显示
        self.assemblyRightMenu.exec_(QtGui.QCursor().pos())
    
    def search_all_none(self, search_type):
        if search_type == "all":
            for action_widget in self.menu_action_list:
                action_widget.setChecked(True)
            self.search_have_text()
        if search_type == "none":
            for action_widget in self.menu_action_list:
                action_widget.setChecked(False)
            self.search_have_text()

    #删除预设
    def delete_default_setting(self):
        sel_menu_text = self.project_comboBox.currentText()
        sel_item = self.project_comboBox.findText(sel_menu_text)
        if sel_item >= 0:
            self.project_comboBox.removeItem(sel_item)

        with open(self.json_path,'r') as load_f:
            json_dic = json.load(load_f)
            if sel_menu_text in json_dic['assembly_default']:
                del json_dic['assembly_default'][sel_menu_text]
                with open(self.json_path,"w") as f:
                    json.dump(json_dic,f,indent=4)

    #获取路径
    def get_assembly_export_filepath(self):
        fielpath=cmds.fileDialog2(fm=3, dialogStyle=1,cap=u'加载路径',okc=u'确定',cc=u'取消')
    
        if fielpath!=None and os.path.exists(fielpath[0]):
            self.assembly_sel_path = fielpath[0]
            self.get_path_refresh_tree()
    #拼装treewidget
    def combobox_refresh_tree(self):
        sel_default = self.project_comboBox.currentText()
        #读取json,获取当前选择的path
        if os.path.exists(self.json_path):
            with open(self.json_path,'r') as load_f:
                json_dic = json.load(load_f)
                #是否有key  assembly_default
                if "assembly_default" in json_dic:
                    if sel_default in json_dic["assembly_default"]:
                        self.assembly_sel_path = json_dic["assembly_default"][sel_default]
                        self.get_path_refresh_tree()
                        self.unt_assembly_table.clearContents()
                    else:
                        print u"未找到预设",sel_default
                else:
                    print u"未找到assembly_default"
    def get_path_refresh_tree(self):
        # 清空treewidget
        if self.unt_assembly_tree.topLevelItemCount():
            self.unt_assembly_tree.clear()
        # proj_str = self.project_comboBox.currentText()
        if os.path.exists(self.assembly_sel_path):
            for item in os.listdir(self.assembly_sel_path):
                itempath = self.assembly_sel_path + '/' + item
                if os.path.isdir(itempath):
                    newItem=QtWidgets.QTreeWidgetItem(self.unt_assembly_tree)
                    newItem.setText(0,item)
        else:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"路径不存在\n{}".format(self.assembly_sel_path), button=[u'关闭'])
            return
        pass
    # def search_tablewidgetitem(self):
    #     text = self.search_lineedit.text()
    #     if text == "":
    #         for i in range(self.unt_assembly_table.rowCount()):
    #             self.unt_assembly_table.setRowHidden(i,False)
    #     else:
    #         row_list = []
    #         items = self.unt_assembly_table.findItems(text, Qt.MatchContains)
    #         for item in items:
    #             item_row = item.row()
    #             row_list.append(item_row)
    #         for i in range(self.unt_assembly_table.rowCount()):
    #             if i in row_list:
    #                 self.unt_assembly_table.setRowHidden(i,False)
    #             else:
    #                 self.unt_assembly_table.setRowHidden(i,True)
    def change_table_iconsize(self,value):
        #获取表格的icon宽高
        self.icon_size = self.unt_assembly_table.iconSize()
        self.icon_size.setWidth(value)
        self.icon_size.setHeight(value)
        self.unt_assembly_table.setIconSize(self.icon_size)
        #将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeColumnsToContents(self.unt_assembly_table)
        QTableWidget.resizeRowsToContents(self.unt_assembly_table)
    
    def get_treewidgetitem_parent(self,treeitem,back_list):
        try:
            parent_item = treeitem.parent()
            back_list.append(parent_item.text(0))
            self.get_treewidgetitem_parent(parent_item,back_list)
        except:
            pass
    def VisitDir(self,path,file_suffix):
        filepathlist=[]
        for root,dirs,files in os.walk(path):
            for filespath in files:
                ImageName=os.path.join(root,filespath)
                if ImageName.endswith(file_suffix):
                    filepathlist.append(ImageName.replace("\\","/"))
        return filepathlist
    def set_table_item(self,row,item_dic):
        for key,val in item_dic.items():
            if key == 0 or key == "0":
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(val), QtGui.QIcon.Normal, QtGui.QIcon.Off)

                newItem=QTableWidgetItem()
                newItem.setIcon(icon)
                self.unt_assembly_table.setItem(int(row), int(key), newItem)
            else:
                newItem=QTableWidgetItem(val)
                self.unt_assembly_table.setItem(int(row), int(key), newItem)
    def return_filesize(self,filepath):
        filesize = os.stat(filepath).st_size/1024
        if filesize > 1024:
            if filesize/1024 > 1024:
                return '{}GB'.format(filesize/1024/1024)
            else:
                return '{}MB'.format(filesize/1024)
        else:
            return '{}KB'.format(filesize)
    #treewidget双击
    def Treewidget_click(self):
        selitem = self.unt_assembly_tree.selectedItems()[0]
        #清除选择的item下的item
        if selitem.childCount():
            selitem.takeChildren()
        #查找选择的item的所有parent
        parent_str_list = []
        self.get_treewidgetitem_parent(selitem,parent_str_list)
        #翻转获取到的parent列表
        parent_str_list = list(reversed(parent_str_list))
        #项目路径+项目名
        filepath = self.assembly_sel_path
        #添加parent名字
        if parent_str_list != []:
            for item in parent_str_list:
                filepath +=('/' + item)
        #添加选择的item的text
        asset_type = selitem.text(0)
        filepath = filepath + '/'+ selitem.text(0)
        #添加treewidgetitem
        for item in os.listdir(filepath):
            itempath = filepath+'/'+item
            if os.path.isdir(itempath):
                newItem=QtWidgets.QTreeWidgetItem(selitem)
                newItem.setText(0,item)
    #加载unt
    def get_tree_sup_path(self):
        self.assembly_sel_path = self.assembly_sel_path.rsplit("/",1)[0]
        self.get_path_refresh_tree()
    def return_tablewidget_rowtext(self,file_dic):
        row_dic = {}
        if file_dic:
            png_path = u'''{}/{}.png'''.format(file_dic.values()[0].rsplit("/",1)[0], file_dic.values()[0].rsplit("/",1)[-1].rsplit(".",1)[0].replace("_BBox","").replace("_DIY",""))
            if os.path.exists(png_path):
                row_dic[0] = png_path
            row_dic[1] = file_dic.values()[0].rsplit("/",1)[-1].rsplit(".",1)[0].replace("_BBox","").replace("_DIY","")
            if "ma" in file_dic:
                row_dic[2] = self.return_filesize(file_dic["ma"])
            if "gpu" in file_dic:
                row_dic[3] = self.return_filesize(file_dic["gpu"])
            if "ass" in file_dic:
                row_dic[4] = self.return_filesize(file_dic["ass"])
            if "bbox" in file_dic:
                row_dic[5] = self.return_filesize(file_dic["bbox"])
            if "diy" in file_dic:
                row_dic[6] = self.return_filesize(file_dic["diy"])
            row_dic[7] = file_dic.values()[0].rsplit("/",1)[0]
            
        return row_dic
    def get_path_allchild(self,path):
        filepathlist=[]
        for root,dirs,files in os.walk(path):
            for filespath in files:
                ImageName=os.path.join(root,filespath)
                filepathlist.append(ImageName.replace("\\","/"))
        return filepathlist
    def from_path_get_unt(self, find_type):
        selitem = self.unt_assembly_tree.selectedItems()[0]
        #清除选择的item下的item
        if selitem.childCount():
            selitem.takeChildren()
        #查找选择的item的所有parent
        parent_str_list = []
        self.get_treewidgetitem_parent(selitem,parent_str_list)
        #翻转获取到的parent列表
        parent_str_list = list(reversed(parent_str_list))
        #项目路径+项目名
        filepath = self.assembly_sel_path
        #路径-添加parent名字
        if parent_str_list != []:
            for item in parent_str_list:
                filepath +=('/' + item)
        #路径-添加选择的item的text
        filepath = filepath + '/'+ selitem.text(0)
        #获取文件,查看是否是组件的一部分
        json_dic = {}
        table_widget_dic = {}
        row_num = 0
        bar_num = 0
        file_list = []
        if os.path.exists(self.json_path):#json文件存在
            with open(self.json_path,'r') as load_f:
                json_dic = json.load(load_f)
                if filepath in json_dic:#加载路径在json里
                    if find_type in json_dic[filepath]:#加载方式在路径里
                        self.refresh_tablewidget_dic = {'path':filepath, "find_type":find_type}

                        self.assembly_progressBar.setMaximum(len(json_dic[filepath][find_type]))#进度条
                        self.unt_assembly_table.clearContents()#tahlewidget清除
                        self.unt_assembly_table.setRowCount(len(json_dic[filepath][find_type]))#tahlewidget行数

                        for k,v in json_dic[filepath][find_type].items():# k 行数,v 字典
                            self.set_table_item(k,v)
                            #设置进度条
                            self.assembly_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(json_dic[filepath][find_type])))
                            self.assembly_progressBar.setValue(bar_num)
                            bar_num += 1
                        
                        self.assembly_progressBar.setValue(len(json_dic[filepath][find_type]))
                        self.assembly_progressBar.setFormat(u"完成")
                        #将行与列的高度设置为所显示的内容的宽度高度匹配
                        QTableWidget.resizeColumnsToContents(self.unt_assembly_table)
                        QTableWidget.resizeRowsToContents(self.unt_assembly_table)
                        
                        return
 
        #没有json文件，或者条件不符合
        if find_type == "this":
            self.refresh_tablewidget_dic = {'path':filepath, "find_type":"this"}
            for item in os.listdir(filepath):
                if os.path.isfile(filepath+'/'+item):
                    file_list.append(filepath+'/'+item)
        elif find_type == "child":
            self.refresh_tablewidget_dic = {'path':filepath, "find_type":"child"}
            file_list = self.get_path_allchild(filepath)
        
        self.assembly_progressBar.setMaximum(len(file_list))#进度条
        self.unt_assembly_table.clearContents()#tahlewidget清除
        self.unt_assembly_table.setRowCount(len(file_list))#tahlewidget行数
        see_list = []
        if file_list:
            for item_path in file_list:
                item_dic = {}
                if os.path.isfile(item_path):
                    file_dic = self.return_unt_fullpath(item_path)
                    if file_dic:
                        #去重
                        _see = u'''{}/{}'''.format(file_dic.values()[0].rsplit("/",1)[0], file_dic.values()[0].rsplit("/",1)[-1].rsplit(".",1)[0].replace("_BBox","").replace("_DIY",""))
                        if _see in see_list:
                            continue
                        else:
                            see_list.append(_see)
                        #
                        item_dic = self.return_tablewidget_rowtext(file_dic)
                        table_widget_dic[row_num] = item_dic
                        self.set_table_item(row_num, item_dic) #设置tablewidge-item
                        row_num += 1
                #设置进度条
                self.assembly_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(file_list)))
                self.assembly_progressBar.setValue(bar_num)
                bar_num += 1
        else:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"未找到任何文件", button=[u'关闭'])
            return
        #准备保存字典
        if find_type == "this":
            if filepath in json_dic:
                json_dic[filepath][find_type] = table_widget_dic
            else:
                json_dic[filepath] = {}
                json_dic[filepath][find_type] = table_widget_dic
            #保存json
            with open(self.json_path,"w") as f:
                json.dump(json_dic,f,indent=4)
        elif find_type == "child":
            if filepath in json_dic:
                json_dic[filepath][find_type] = table_widget_dic
            else:
                json_dic[filepath] = {}
                json_dic[filepath][find_type] = table_widget_dic
            #保存json
            with open(self.json_path,"w") as f:
                json.dump(json_dic,f,indent=4)

        self.assembly_progressBar.setValue(len(file_list))
        self.assembly_progressBar.setFormat(u"完成")
        #将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeColumnsToContents(self.unt_assembly_table)
        QTableWidget.resizeRowsToContents(self.unt_assembly_table)
    #保存预设
    def save_json_dic(self):
        if not self.unt_assembly_tree.selectedItems():
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"选择要保存的文件夹", button=[u'关闭'])
            return
        selitem = self.unt_assembly_tree.selectedItems()[0]
        #清除选择的item下的item
        if selitem.childCount():
            selitem.takeChildren()
        #查找选择的item的所有parent
        parent_str_list = []
        self.get_treewidgetitem_parent(selitem,parent_str_list)
        #翻转获取到的parent列表
        parent_str_list = list(reversed(parent_str_list))
        #项目路径+项目名
        filepath = self.assembly_sel_path
        #路径-添加parent名字
        if parent_str_list != []:
            for item in parent_str_list:
                filepath +=('/' + item)
        #路径-添加选择的item的text
        asset_type = selitem.text(0)
        filepath = filepath + '/'+ selitem.text(0)
        #预设的名字
        save_text = ""
        result = cmds.promptDialog(title=u'保存预设',
                                    message=u'名称：',
                                    button=['OK', 'Cancel'],
                                    defaultButton='OK',
                                    cancelButton='Cancel',
                                    dismissString='Cancel')
        if result == 'OK':
            save_text = cmds.promptDialog(query=True, text=True)
        else:
            return
        self.assembly_sel_path = filepath
        #json是否存在
        json_dic = {}
        if os.path.exists(self.json_path):
            with open(self.json_path,'r') as load_f:
                json_dic = json.load(load_f)
                #是否有key  assembly_default
                if "assembly_default" in json_dic:
                    json_dic["assembly_default"][save_text] = self.assembly_sel_path
                else:
                    json_dic["assembly_default"] = {}
                    json_dic["assembly_default"][save_text] = self.assembly_sel_path
        else:
            json_dic["assembly_default"] = {}
            json_dic["assembly_default"][save_text] = self.assembly_sel_path
        #刷新ui
        if self.project_comboBox.count() > 0:
            self.project_comboBox.clear()
        for i in json_dic["assembly_default"]:
            self.project_comboBox.addItem(i)
        #保存json
        with open(self.json_path,"w") as f:
            json.dump(json_dic,f,indent=4)

    def search_have_text(self):
        menu_list = [u"缩略图", u"资产名", "Ma", u"GPUcache", "Ass", "Boundingbox", "GPUcache_DIY", "Folder"]
        column_num_list = []
        #筛选的列
        for action_widget in self.menu_action_list:
            action_checked = action_widget.isChecked()
            action_text = action_widget.text()
            #查看UI对应第几列
            for index,val in enumerate(menu_list):
                if val == action_text and action_checked:
                    column_num_list.append(index)
        #搜索筛选
        search_text_hidden_row = []
        text = self.search_lineedit.text()
        if text != "":
            items = self.unt_assembly_table.findItems(text, Qt.MatchContains)
            for item in items:
                item_row = item.row()
                search_text_hidden_row.append(item_row)

        #查找为空的tablewidgetitem
        for row_num in range(self.unt_assembly_table.rowCount()):
            _list = [] #ture 是有item，false是没有item
            for column_num in column_num_list:
                #判断第几行第几列是否有item
                if self.unt_assembly_table.item(row_num,column_num):
                    _list.append(True)
                else:
                    _list.append(False)
            if text == "":
                if False in _list:
                    self.unt_assembly_table.setRowHidden(row_num,True)
                else:
                    self.unt_assembly_table.setRowHidden(row_num,False)
            else:
                if False in _list:
                    self.unt_assembly_table.setRowHidden(row_num,True)
                else:
                    if row_num in search_text_hidden_row:
                        self.unt_assembly_table.setRowHidden(row_num,False)
                    else:
                        self.unt_assembly_table.setRowHidden(row_num,True)

    def refresh_assembly_table(self):
        if self.refresh_tablewidget_dic['path'] == "" or self.refresh_tablewidget_dic['find_type'] == "":
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"未加载任何文件夹，请先加载Unt", button=[u'关闭'])
            return

        #路径-
        filepath = self.refresh_tablewidget_dic['path']
        find_type = self.refresh_tablewidget_dic['find_type']
        #获取文件,查看是否是组件的一部分
        json_dic = {}
        table_widget_dic = {}
        row_num = 0
        bar_num = 0
        file_list = []
        
        if os.path.exists(self.json_path):#json文件存在
            with open(self.json_path,'r') as load_f:
                json_dic = json.load(load_f)
        
        if find_type == "this":
            self.refresh_tablewidget_dic = {'path':filepath, "find_type":"this"}
            for item in os.listdir(filepath):
                if os.path.isfile(filepath+'/'+item):
                    file_list.append(filepath+'/'+item)
        elif find_type == "child":
            self.refresh_tablewidget_dic = {'path':filepath, "find_type":"child"}
            file_list = self.get_path_allchild(filepath)
            
        self.assembly_progressBar.setMaximum(len(file_list))#进度条
        self.unt_assembly_table.clearContents()#tahlewidget清除
        self.unt_assembly_table.setRowCount(len(file_list))#tahlewidget行数
        see_list = []
        if file_list:
            for item_path in file_list:
                item_dic = {}
                if os.path.isfile(item_path):
                    file_dic = self.return_unt_fullpath(item_path)
                    if file_dic:
                        #去重
                        _see = u'''{}/{}'''.format(file_dic.values()[0].rsplit("/",1)[0], file_dic.values()[0].rsplit("/",1)[-1].rsplit(".",1)[0].replace("_BBox","").replace("_DIY",""))
                        if _see in see_list:
                            continue
                        else:
                            see_list.append(_see)
                        #
                        item_dic = self.return_tablewidget_rowtext(file_dic)
                        table_widget_dic[row_num] = item_dic
                        self.set_table_item(row_num, item_dic) #设置tablewidge-item
                        row_num += 1
                #设置进度条
                self.assembly_progressBar.setFormat(u"%p%   {}/{}".format(bar_num, len(file_list)))
                self.assembly_progressBar.setValue(bar_num)
                bar_num += 1
        else:
            cmds.confirmDialog( title=u'警告!!',icon='question', message=u"未找到任何文件", button=[u'关闭'])
            return
        #准备保存字典
        if find_type == "this":
            if filepath in json_dic:
                json_dic[filepath][find_type] = table_widget_dic
            else:
                json_dic[filepath] = {}
                json_dic[filepath][find_type] = table_widget_dic
            #保存json
            with open(self.json_path,"w") as f:
                json.dump(json_dic,f,indent=4)
        elif find_type == "child":
            if filepath in json_dic:
                json_dic[filepath][find_type] = table_widget_dic
            else:
                json_dic[filepath] = {}
                json_dic[filepath][find_type] = table_widget_dic
            #保存json
            with open(self.json_path,"w") as f:
                json.dump(json_dic,f,indent=4)

        self.assembly_progressBar.setValue(len(file_list))
        self.assembly_progressBar.setFormat(u"完成")
        #将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeColumnsToContents(self.unt_assembly_table)
        QTableWidget.resizeRowsToContents(self.unt_assembly_table)
    def assembly_open_filepath(self):
        select_items = self.unt_assembly_table.selectedItems()
        for sel_item in select_items:
            item_row = sel_item.row()
            file_path = self.unt_assembly_table.item(item_row, 7).text()
            os.startfile(file_path)

    #导入
    def assembly_create_gpu_and_ass(self,file_dic):
        #创建transform节点
        short_name = file_dic.values()[0].rsplit('/',1)[-1].rsplit('.',1)[0].replace("_BBox","").replace("_DIY","")
        transform_node = cmds.createNode("transform", n=('GPU_'+short_name))

        cmds.select(transform_node, r=1)
        self.sel_mod_selections.setChecked(True)
        #添加unt属性
        self.add_refresh_unt_attr(transform_node,file_dic)

        #添加GPU
        if "diy" in file_dic:
            self.add_gpucache_node("diy")
        elif "gpu" in file_dic:
            self.add_gpucache_node("gpu")
        elif "bbox" in file_dic:
            self.add_gpucache_node("bbox")
        
        #添加ass
        self.add_ass_node()
        
        return transform_node
    def assembly_unt_complex(self):
        select_items = self.unt_assembly_table.selectedItems()
        mapath_list = []
        for sel_item in select_items:
            item_row = sel_item.row()
            file_path = """{}/{}.ma""".format(self.unt_assembly_table.item(item_row, 7).text(), self.unt_assembly_table.item(item_row, 1).text())
            if not file_path in mapath_list:
                mapath_list.append(file_path)
        for mapath in mapath_list:
            print mapath
            file_dic = self.return_unt_fullpath(mapath)
            if file_dic:
                self.assembly_create_gpu_and_ass(file_dic)
#################################################################################################################################################
#
#场景性能分析   执行方法
#
#################################################################################################################################################
    def add_progressbar_value(self, widget ,add_num ):
        num = widget.value()
        widget.setFormat(u"%p%   {}/{}".format((num + add_num), self.progressBar_maxvalue))
        widget.setValue(num + add_num)
        if widget.value() >= self.progressBar_maxvalue:
            widget.setValue(self.progressBar_maxvalue)
            widget.setFormat(u"完成")
    def return_instancer(self, dis_node):
        right_nodes = cmds.listConnections(dis_node, s=0, d=1)
        for r_node in right_nodes:
            if cmds.objectType(r_node) == "instancer":
                return r_node
            else:
                if cmds.listConnections(r_node, s=0, d=1):
                    return self.return_instancer(r_node)
    def return_instancer_inf(self, dis_node):
        _dic = {0:"Geometry" ,1:"BoundingBoxes" ,2:"BoundingBox"}
        ins_node = self.return_instancer(dis_node)
        all_instancer = cmds.getAttr(dis_node + ".pointCount")
        _num = None
        display_on = None
        display_mode = _dic[cmds.getAttr(ins_node + ".levelOfDetail")]
        if ins_node:
            _num = cmds.getAttr(ins_node + ".displayPercentage")
            display_on = int(all_instancer*_num/100)
        return {0:display_on, 1:all_instancer, 2:_num, 3:display_mode}
    def return_mash(self, dis_node):
        right_nodes = cmds.listConnections(dis_node, s=0, d=1)
        for r_node in right_nodes:
            if cmds.objectType(r_node) == "MASH_Waiter":
                return r_node
            else:
                if cmds.listConnections(r_node, s=0, d=1):
                    return self.return_mash(r_node)

    def analysis_of_the_scene(self):
        self.progressBar_maxvalue = 14
        self.check_progressBar.setValue(0)
        self.check_progressBar.setMaximum(self.progressBar_maxvalue)
    #关键指标总表     self.key_table
        #设置行
        self.key_table.setColumnCount(2)
        self.key_table.setHorizontalHeaderLabels([u"数据(仅Unt)", u"数据(Unt除外)"])
        self.key_table.setRowCount(14)
        self.key_table.setVerticalHeaderLabels([u"Transform节点数量", 
                                                u"GPUcache Shape计数：", 
                                                u"GPUcache Shape计数(BBox)：", 
                                                u"GPUcache Shape计数(DIY)：", 
                                                u"GPUcache Shape计数(实模显示)：", 
                                                u"Instancer总显示计数：", 
                                                u"Instancer总渲染计数：", 
                                                u"aiStandIn Shape计数：",
                                                u"aiStandIn外链计数：",
                                                u"aiStandIn平均复用率（不含Mash）：",
                                                u"aiStandIn最大复用率（不含Mash）：",
                                                u"mesh Shape计数",
                                                u"mesh总面数：",
                                                u"Handle计数："])
        #Transform节点数量
        all_trans = cmds.ls(type="transform")
        unt_trans = []
        for i in all_trans:
            if self.return_unt_bool(i):
                unt_trans.append(i)
            #添加item
        newItem=QTableWidgetItem(str(len(unt_trans)))
        self.key_table.setItem(0, 0, newItem)
        newItem=QTableWidgetItem(str(len(all_trans) - len(unt_trans)))
        self.key_table.setItem(0, 1, newItem)
        
        self.add_progressbar_value(self.check_progressBar, 1)

        #GPUcache Shape计数
        unt_gpu_list = []
        for i in unt_trans:
            if cmds.listRelatives(i,c=1,f=1,type="gpuCache"):
                unt_gpu_list.append(i)
        all_gpu_list = cmds.ls(type="gpuCache")
            #添加item
        newItem=QTableWidgetItem(str(len(unt_gpu_list)))
        self.key_table.setItem(1, 0, newItem)
        newItem=QTableWidgetItem(str(len(all_gpu_list) - len(unt_gpu_list)))
        self.key_table.setItem(1, 1, newItem)

        self.add_progressbar_value(self.check_progressBar, 1)

        #GPUcache Shape计数(BBox)        #GPUcache Shape计数(DIY)        #GPUcache Shape计数(实模显示)
        gpu_bbox_list = []
        gpu_diy_list = []
        gpu_mesh_list = []
        for item in unt_gpu_list:
            _c = cmds.listRelatives(item,c=1,f=1,type="gpuCache")
            if _c:
                _path = cmds.getAttr(_c[0] + ".cacheFileName")
                if _path.endswith("BBox.abc"):
                    gpu_bbox_list.append(item)
                elif _path.endswith("DIY.abc"):
                    gpu_diy_list.append(item)
                else :
                    gpu_mesh_list.append(item)
            #添加item
        newItem=QTableWidgetItem(str(len(gpu_bbox_list)))
        self.key_table.setItem(2, 0, newItem)
        newItem=QTableWidgetItem(str(len(gpu_diy_list)))
        self.key_table.setItem(3, 0, newItem)
        newItem=QTableWidgetItem(str(len(gpu_mesh_list)))
        self.key_table.setItem(4, 0, newItem)

        self.add_progressbar_value(self.check_progressBar, 3)

        #Instancer总显示计数        #Instancer总渲染计数
        display_on = 0
        all_instancer = 0
        for item in cmds.ls(type="MASH_Distribute", l=1):
            this_instancer = cmds.getAttr(item + ".pointCount")
            instancer_node = self.return_instancer(item)
            if instancer_node:
                all_instancer += cmds.getAttr(item + ".pointCount")
                _num = cmds.getAttr(instancer_node + ".displayPercentage")
                display_on += int(this_instancer*_num/100)

        newItem=QTableWidgetItem(str(display_on))
        self.key_table.setItem(5, 1, newItem)
        newItem=QTableWidgetItem(str(all_instancer))
        self.key_table.setItem(6, 1, newItem)

        self.add_progressbar_value(self.check_progressBar, 2)

        #aiStandIn Shape计数        #aiStandIn外链计数        #aiStandIn平均复用率（不含Mash）        #aiStandIn最大复用率（不含Mash）
        all_aistandin = cmds.ls(type="aiStandIn", l=1)
        aistandin_unt = []
        aistandin_other = []
        aistandin_unt_link = []
        aistandin_other_link = []
        aistandin_unt_link_dic = {}
        aistandin_other_link_dic = {}
        unt_fuyong = 0
        other_fuyong = 0
        for ai_node in all_aistandin:
            _p = cmds.listRelatives(ai_node, p=1, pa=1, f=1, type="transform")
            if _p :
                if self.return_unt_bool(_p[0]):
                    aistandin_unt.append(ai_node)
                    ass_path = cmds.getAttr(ai_node + ".dso")
                    if not ass_path in aistandin_unt_link:
                        aistandin_unt_link.append(ai_node)
                    if ass_path in aistandin_unt_link_dic:
                        aistandin_unt_link_dic[ass_path] = aistandin_unt_link_dic[ass_path] + 1
                    else:
                        aistandin_unt_link_dic[ass_path] = 1
                else:
                    aistandin_other.append(ai_node)
                    ass_path = cmds.getAttr(ai_node + ".dso")
                    if not ass_path in aistandin_other_link:
                        aistandin_other_link.append(ai_node)
                    if ass_path in aistandin_other_link_dic:
                        aistandin_other_link_dic[ass_path] = aistandin_other_link_dic[ass_path] + 1
                    else:
                        aistandin_other_link_dic[ass_path] = 1
        for i in aistandin_unt_link_dic.values():
            if i > unt_fuyong:
                unt_fuyong = i
        for i in aistandin_other_link_dic.values():
            if i > other_fuyong:
                other_fuyong = i

        newItem=QTableWidgetItem(str(len(aistandin_unt)))
        self.key_table.setItem(7, 0, newItem)
        newItem=QTableWidgetItem(str(len(aistandin_other)))
        self.key_table.setItem(7, 1, newItem)

        newItem=QTableWidgetItem(str(len(aistandin_unt_link)))
        self.key_table.setItem(8, 0, newItem)
        newItem=QTableWidgetItem(str(len(aistandin_other_link)))
        self.key_table.setItem(8, 1, newItem)

        if len(aistandin_unt_link_dic)>0:
            newItem=QTableWidgetItem(str(len(aistandin_unt)/len(aistandin_unt_link_dic)))
            self.key_table.setItem(9, 0, newItem)
        else:
            newItem=QTableWidgetItem(str(0))
            self.key_table.setItem(9, 0, newItem)        
        if len(aistandin_other_link_dic)>0:
            newItem=QTableWidgetItem(str(len(aistandin_other)/len(aistandin_other_link_dic)))
            self.key_table.setItem(9, 1, newItem)
        else:
            newItem=QTableWidgetItem(str(0))
            self.key_table.setItem(9, 1, newItem)

        newItem=QTableWidgetItem(str(unt_fuyong))
        self.key_table.setItem(10, 0, newItem)
        newItem=QTableWidgetItem(str(other_fuyong))
        self.key_table.setItem(10, 1, newItem)
        
        self.add_progressbar_value(self.check_progressBar, 4)
        
        #mesh Shape计数
        all_mesh_shape = cmds.ls(type="mesh")
        newItem=QTableWidgetItem(str(len(all_mesh_shape)))
        self.key_table.setItem(11, 1, newItem)

        self.add_progressbar_value(self.check_progressBar, 1)

        #mesh总面数
        mesh_face_num = 0
        for i in all_mesh_shape:
            mesh_face_num += len(cmds.ls((i + ".f[*]"),fl=1))

        newItem=QTableWidgetItem(str(mesh_face_num))
        self.key_table.setItem(12, 1, newItem)

        self.add_progressbar_value(self.check_progressBar, 1)

        #Handle计数
        Handle_unt = 0
        Handle_other = 0
        for i in cmds.ls(type="transform"):
            if self.return_unt_bool(i):
                if cmds.getAttr(i + ".displayHandle"):
                    Handle_unt += 1
            else:
                if cmds.getAttr(i + ".displayHandle"):
                    Handle_other += 1
        newItem=QTableWidgetItem(str(Handle_unt))
        self.key_table.setItem(13, 0, newItem)
        newItem=QTableWidgetItem(str(Handle_other))
        self.key_table.setItem(13, 1, newItem)
        
        self.add_progressbar_value(self.check_progressBar, 1)

        #将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeColumnsToContents(self.unt_assembly_table)
        QTableWidget.resizeRowsToContents(self.unt_assembly_table)
    #Instancer细表   self.instancer_table
        self.instancer_table.setColumnCount(5)
        self.instancer_table.setHorizontalHeaderLabels([u"显示计数", u"渲染计数",u"显示百分比",u"显示模式",u"关联Mash"])
        # 
        all_dis = cmds.ls(type="MASH_Distribute", l=1)
        self.instancer_table.setRowCount(len(all_dis))
        row_num = 0
        for item in all_dis:
            instancer_node = self.return_instancer(item)
            if instancer_node:
                newItem=QTableWidgetItem(instancer_node)
                self.instancer_table.setVerticalHeaderItem(row_num,newItem)
                inf = self.return_instancer_inf(item)
                if inf:
                    inf[4] = self.return_mash(item)
                for k,v in inf.items():
                    newItem=QTableWidgetItem(str(v))
                    self.instancer_table.setItem(row_num, k, newItem)
                row_num += 1

        #将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeColumnsToContents(self.unt_assembly_table)
        QTableWidget.resizeRowsToContents(self.unt_assembly_table)


class MainWindow(Ui_Unt_Tool_Window,QtWidgets.QWidget):
    def __init__(self,parent=mayaMainWindows()):
        Ui_Unt_Tool_Window.__init__(self)
        QtWidgets.QWidget.__init__(self,parent)
        self.setupUi(self)
        self.retranslateUi(self)
def change_display_combbox():
    wf_panel = cmds.getPanel(wf=True)
    all_modelpanel=cmds.getPanel( type='modelPanel' )
    if wf_panel in all_modelpanel:
        UntToolWindow.show_gpu_checkBox.setChecked(cmds.modelEditor(wf_panel, q=1, queryPluginObjects="gpuCacheDisplayFilter"))
        UntToolWindow.show_ass_checkBox.setChecked(cmds.modelEditor(wf_panel, q=1, pluginShapes=True))
        UntToolWindow.show_ins_checkBox.setChecked(cmds.modelEditor(wf_panel, q=1, particleInstancers=True))
        UntToolWindow.show_handel_checkbox.setChecked(cmds.modelEditor(wf_panel, q=1, handles=True))
        UntToolWindow.two_sidedlight_checkbox.setChecked(cmds.modelEditor(wf_panel, q=1, twoSidedLighting=True))
if __name__ == "__main__":
    try:
        cmds.loadPlugin("gpuCache")
        cmds.loadPlugin( 'AbcBullet' )
        cmds.loadPlugin( 'AbcExport' )
        cmds.loadPlugin( 'AbcImport' )
        cmds.loadPlugin( 'mtoa' )
    except:
        pass
    try:
        UntToolWindow.close()
        UntToolWindow.deleteLater()
    except:
        pass
    UntToolWindow = MainWindow()
    UntToolWindow.show()
    cmds.scriptJob(e=('idle','change_display_combbox()') )

