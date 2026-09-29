# -*- coding:utf-8 -*-

from __future__ import division, print_function

import os
import tempfile
import time

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

import xgenm as xg

import maya.mel as mel
import maya.cmds as cmds
import maya.api.OpenMaya as om

from maya.api.OpenMaya import MGlobal
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from mayaTools.export.xGenOriginExport.export_xgen import export_xgen
from mayaTools.export.xGenOriginExport.move_origin import create_binder

from mayaTools.core.mayaLibrary import PROJECTINFO, getScenename_real
from mayaTools.core.widgets import ComboxGroup, LineEditGroup, Line, WidgetGroup


callbacks = {}


def clear_selection_callback():
    for _editor in cmds.lsUI(editors=True):
        if not cmds.outlinerEditor(_editor, query=True, exists=True):
            continue
        _sel_cmd = cmds.outlinerEditor(_editor, query=True, selectCommand=True)
        if not _sel_cmd or not _sel_cmd.startswith('<function selCom at '):
            continue
        cmds.outlinerEditor(_editor, edit=True, selectCommand='pass')


def add_selection_changed_callback(name, fun):
    remove_callback(name)
    callbacks[name] = om.MEventMessage.addEventCallback(
        "SelectionChanged",
        fun
    )
    MGlobal.displayInfo("callback function {} has been set".format(name))


def remove_callback(name):
    if name not in callbacks.keys():
        return
    handler = callbacks[name]
    try:
        om.MDGMessage.removeCallback(handler)
    except RuntimeError:
        return
    MGlobal.displayInfo("callback function {} has been removed".format(name))


def is_attr_exists(obj, name):
    attrs = cmds.listAttr(obj, ud=1) or []
    return name in attrs


def safe_set_attr(obj, name, value, type):
    if not is_attr_exists(obj, name):
        if type == "string":
            cmds.addAttr(obj, longName=name, dataType=type, keyable=True)
        else:
            cmds.addAttr(obj, longName=name, at=type, keyable=True)
    if value is None:
        return
    if type == "string":
        cmds.setAttr("{}.{}".format(obj, name), value, type=type)
    else:
        cmds.setAttr("{}.{}".format(obj, name), value)


def safe_get_attr(obj, name):
    if not is_attr_exists(obj, name):
        return False
    attr = cmds.getAttr("{}.{}".format(obj, name))
    if attr == "None":
        return False
    return attr


def get_all_descriptions():
    descriptions = []
    palettes = xg.palettes()
    for palette in palettes:
        descriptions.extend(xg.descriptions(palette))
    return descriptions


def get_all_splines():
    inters = []
    shapes = cmds.ls(typ="xgmSplineDescription")
    for shape in shapes:
        inters.append(cmds.listRelatives(shape, ap=1, type='transform')[0])
    return inters


class XGenToolsUI(MayaQWidgetDockableMixin, QWidget):
    def __init__(self, parent=None):
        super(XGenToolsUI, self).__init__(parent)
        self.resize(400, 400)
        self.setWindowTitle(u"XGen工具---世界坐标原点导出")

        self.groups = []
        self.currentSelectXgen = None
        self.currentSelectGuide = None
        self.currentSelectMesh = None
        self.followBoneTransform = None
        self.savePath = "."

        self.attrGroupName = 'GroupName'
        self.attrGuideGroupName = 'GuideGroupName'
        self.attrMeshUVName = "MeshUVName"
        self.attrUVSetIndexName = "MeshUVSetIndex"
        self.attrIsExport = "IsExport"
        self.attrCharacterName = "CharachterName"
        self.attrExportGuideAnim = "GuideAnimation"
        self.attrExportSplineAnim = "SplineAnimaiton"

        self._initUI()
        self._init_scence_info()
        self._updateUI()
        self.tabMain.currentChanged.connect(self._updateUI)

        self.dec_project_from_file_name()

    # ==================== UI 初始化 ====================

    def _initUI(self):
        lMain = QVBoxLayout(self)
        self.setLayout(lMain)
        lMain.setSpacing(0)
        lMain.setContentsMargins(5, 10, 5, 0)
        self.tabMain = QTabWidget(self)
        self.tabMain.setStyleSheet("""
        QTabWidget::pane {
            border: none;
        }
        QTabBar::tab {
            background-color: rgb(55, 55, 55);
        }
        """)
        lMain.addWidget(self.tabMain)

        self._init_tab_des_settings()
        self._init_tab_spline_settings()

    def _init_tab_des_settings(self):
        wlDesSettings = WidgetGroup(False, self)
        wlDesSettings.setContentsMargins(0, 5, 0, 0)
        wlDesSettings.setSpacing(10)
        self.tabMain.addTab(wlDesSettings, u"xGen描述设置")

        self.lgDesName = LineEditGroup(u"名称:", label_width=50, parent=self)
        self.lgDesName.lineEdit.setReadOnly(True)
        wlDesSettings.addWidget(self.lgDesName)

        self.cbDesGroupName = ComboxGroup(u"组名称:", 50, self)
        self.cbDesGroupName.textChanged.connect(self._on_group_changed)
        wlDesSettings.addWidget(self.cbDesGroupName)

        wdAddNewGroup = QWidget(self)
        lyAddNewGroup = QHBoxLayout(wdAddNewGroup)
        wlDesSettings.addWidget(wdAddNewGroup)
        lyAddNewGroup.setContentsMargins(0, 0, 0, 0)
        lyAddNewGroup.setSpacing(10)

        self.leNewGroupName = QLineEdit(self)
        self.leNewGroupName.returnPressed.connect(self._add_new_group)
        lyAddNewGroup.addWidget(self.leNewGroupName)

        pbAddnewGroup = QPushButton(text=u"添加新组", parent=self)
        pbAddnewGroup.clicked.connect(self._add_new_group)
        lyAddNewGroup.addWidget(pbAddnewGroup)

        wlDesSettings.addWidget(Line(True, 1, self))

        pbConvertToInteractive = QPushButton(text=u"转换为交互式", parent=self)
        pbConvertToInteractive.clicked.connect(self._convert_to_interactivate)
        wlDesSettings.addWidget(pbConvertToInteractive)

    def _init_tab_spline_settings(self):
        wlSplineSetting = WidgetGroup(False, self)
        wlSplineSetting.setContentsMargins(0, 5, 0, 0)
        self.tabMain.addTab(wlSplineSetting, u"交互式毛发设置")

        wlSplineSetting.addWidget(QLabel(u"项目名称:"))
        self.cb_project = QComboBox()
        self.cb_project.addItems(PROJECTINFO.keys())
        wlSplineSetting.addWidget(self.cb_project)

        self.leSplineName = LineEditGroup(u"名称:", label_width=50, parent=self)
        self.leSplineName.lineEdit.setReadOnly(True)
        wlSplineSetting.addWidget(self.leSplineName)

        self.lgSplineGroupName = LineEditGroup(u"组名称:", label_width=50, parent=self)
        self.lgSplineGroupName.lineEdit.setReadOnly(True)
        wlSplineSetting.addWidget(self.lgSplineGroupName)

        wlExportState = WidgetGroup(True, wlSplineSetting)

        self.chbExportGuideAnim = QCheckBox(text=u"导线动画", parent=self)
        self.chbExportGuideAnim.stateChanged.connect(self._on_export_guide_anim_state_changed)

        self.chbExportSplineAnim = QCheckBox(text=u"曲线动画", parent=self)
        self.chbExportSplineAnim.stateChanged.connect(self._on_export_spline_anim_state_changed)

        wlExportState.addWidget(self.chbExportGuideAnim)
        wlExportState.addWidget(self.chbExportSplineAnim)

        wlSplineSetting.addWidget(Line(True, 1, self))

        self.leSplineGuideName = LineEditGroup(u"导线名称:", label_width=50, parent=self)
        self.leSplineGuideName.lineEdit.setReadOnly(True)
        wlSplineSetting.addWidget(self.leSplineGuideName)

        wlGuideButtons = WidgetGroup(True, wlSplineSetting)
        wlGuideButtons.setAlignment(Qt.AlignCenter)

        pbAssignGuide = QPushButton(text=u"指定导线", parent=self)
        pbAssignGuide.clicked.connect(self._assign_guide_group)
        wlGuideButtons.addWidget(pbAssignGuide)

        pbClearGuide = QPushButton(text=u"清除导线", parent=self)
        pbClearGuide.clicked.connect(self._clear_guide)
        wlGuideButtons.addWidget(pbClearGuide)

        pbSelectGuide = QPushButton(text=u"选择导线", parent=self)
        pbSelectGuide.clicked.connect(self._select_guide)
        wlGuideButtons.addWidget(pbSelectGuide)

        wlSplineSetting.addWidget(Line(True, 1, self))

        self.lw_groom_groups = QListWidget(self)
        self.lw_groom_groups.setSelectionMode(QListWidget.ExtendedSelection)
        wlSplineSetting.addWidget(self.lw_groom_groups)

        widgetExportPath = WidgetGroup(True, wlSplineSetting)
        self.leExportPath = LineEditGroup(u"导出路径:", label_width=80, parent=self)
        widgetExportPath.addWidget(self.leExportPath)
        self.pbSelectPath = QPushButton(text=u"选择", parent=self)
        self.pbSelectPath.clicked.connect(self.selectExportPath)
        widgetExportPath.addWidget(self.pbSelectPath)

        pbExportStatic = QPushButton(text=u"导出静态毛发", parent=self)
        pbExportStatic.clicked.connect(lambda: self._export_as_abc(True))
        wlSplineSetting.addWidget(pbExportStatic)

        wlSplineSetting.addWidget(Line(True, 1, self))

        wlFrameRange = WidgetGroup(True, wlSplineSetting)
        wlFrameRange.addWidget(QLabel(text=u"帧范围:", parent=self))
        self.sbFrameStart = QSpinBox(self)
        self.sbFrameStart.setButtonSymbols(QSpinBox.NoButtons)
        self.sbFrameStart.setMinimumWidth(100)
        self.sbFrameStart.setMaximum(99999)
        self.sbFrameStart.setMinimum(-9999)
        wlFrameRange.addWidget(self.sbFrameStart)
        wlFrameRange.addWidget(QLabel(text=u" ~ ", parent=self))
        self.sbFrameEnd = QSpinBox(self)
        self.sbFrameEnd.setButtonSymbols(QSpinBox.NoButtons)
        self.sbFrameEnd.setMinimumWidth(100)
        self.sbFrameEnd.setMaximum(99999)
        self.sbFrameEnd.setMinimum(-9999)
        wlFrameRange.addWidget(self.sbFrameEnd)

        wlFrameExpend = WidgetGroup(True, wlSplineSetting)
        wlFrameExpend.addWidget(QLabel(text=u"向前扩展:"))
        self.sbFrameExpendStart = QSpinBox(self)
        self.sbFrameExpendStart.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.sbFrameExpendStart.setMinimumWidth(100)
        self.sbFrameExpendStart.setMaximum(50)
        self.sbFrameExpendStart.setValue(0)
        self.sbFrameExpendStart.setMinimum(0)
        wlFrameExpend.addWidget(self.sbFrameExpendStart)
        wlFrameExpend.addWidget(QLabel(text=u"向后扩展:"))
        self.sbFrameExpendEnd = QSpinBox(self)
        self.sbFrameExpendEnd.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.sbFrameExpendEnd.setMinimumWidth(100)
        self.sbFrameExpendEnd.setMaximum(50)
        self.sbFrameExpendEnd.setValue(1)
        self.sbFrameExpendEnd.setMinimum(0)
        wlFrameExpend.addWidget(self.sbFrameExpendEnd)

        self.refreshPerFrame = QCheckBox(text=u"逐帧刷新毛发")
        self.refreshPerFrame.setChecked(True)
        wlSplineSetting.addWidget(self.refreshPerFrame)

        pbExportGroom = QPushButton(text=u"导出缓存", parent=self)
        pbExportGroom.clicked.connect(self._export_as_abc)
        wlSplineSetting.addWidget(pbExportGroom)

        pbOpenExportDir = QPushButton(text=u"打开导出目录", parent=self)
        pbOpenExportDir.clicked.connect(lambda: os.startfile(self._get_root_path()))
        wlSplineSetting.addWidget(pbOpenExportDir)

    # ==================== 路径选择 ====================

    def selectExportPath(self):
        folder = QFileDialog.getExistingDirectory(self, '选择需要执行的文件夹', self.savePath)
        if not folder:
            return
        self.savePath = folder
        self.leExportPath.setText(folder)

    # ==================== 节点判断 ====================

    def DeterminNodeIsGuide(self, node):
        """判断一个给定的字符串代表的maya节点是不是导线节点"""
        dagNode = MGlobal.getSelectionListByName(node).getDependNode(0)
        itdag = om.MItDag()
        itdag.reset(dagNode, om.MItDag.kDepthFirst, om.MFn.kCurve)
        while not itdag.isDone():
            dn = om.MFnDependencyNode(itdag.currentItem())
            if dn.typeName == "nurbsCurve":
                return True
            itdag.next()
        return False

    def DeterminNodeIsMesh(self, node):
        """判断一个给定的字符串代表的maya节点是不是网格"""
        dagNode = MGlobal.getSelectionListByName(node).getDependNode(0)
        itdag = om.MItDag()
        itdag.reset(dagNode, om.MItDag.kDepthFirst, om.MFn.kMesh)
        while not itdag.isDone():
            dn = om.MFnDependencyNode(itdag.currentItem())
            if dn.typeName == "mesh":
                return True
            itdag.next()
        return False

    # ==================== 项目信息 ====================

    def dec_project_from_file_name(self):
        file_name = cmds.file(q=True, sn=True)
        index = 0
        for i, key in enumerate(PROJECTINFO.keys()):
            if key.split("-")[-1].lower() in file_name.lower():
                index = i
        self.cb_project.setCurrentIndex(index)

    def _get_scene_name(self):
        sceneName = getScenename_real()
        if "Ep" in sceneName and "sc" in sceneName:
            sceneNameParts = sceneName.split("_")
            sceneName = "{}_{}_{}".format(sceneNameParts[0], sceneNameParts[1], sceneNameParts[2])
        else:
            sceneName = ""
        return sceneName

    def _get_root_path(self):
        sceneName = self._get_scene_name()
        try:
            ep, sc, cam = sceneName.split("_")[0:3]
        except ValueError:
            MGlobal.displayError(u"当前文件名不正确,修正后重试")
            return
        root_path = list(PROJECTINFO.values())[self.cb_project.currentIndex()].format(
            ep, "nHair_nCache", sc, "{}_{}_{}".format(ep, sc, cam)
        )
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        return root_path

    # ==================== UI 更新 ====================

    def _updateUI(self, *args):
        MGlobal.displayInfo("update UI")
        self.currentSelectXgen = []
        self.currentSelectGuide = None
        self.currentSelectMesh = None
        selections = cmds.ls(sl=1)

        if self.tabMain.currentIndex() == 0:
            self.cbDesGroupName.set_current_index(0)
            if len(selections) == 0:
                self.lgDesName.setText(u"请选择Xgen描述节点")
                return
            for obj in selections:
                if obj not in get_all_descriptions():
                    self.lgDesName.setText(u"请选择Xgen描述节点")
                    return
            self.currentSelectXgen = selections
            self._update_page_des_setting()
        elif self.tabMain.currentIndex() == 1:
            self._clear_spline_page()
            if len(selections) == 0:
                self.leSplineName.setText(u"请选择交互式毛发")
                return
            for sel in selections:
                if any(string in sel.lower() for string in ['locator', 'matrix']):
                    continue
                if self.DeterminNodeIsGuide(sel):
                    self.currentSelectGuide = sel
                elif self.DeterminNodeIsMesh(sel):
                    self.currentSelectMesh = sel
                elif sel in get_all_splines():
                    self.currentSelectXgen.append(sel)
            if len(self.currentSelectXgen) == 0:
                self.leSplineName.setText(u"请选择交互式毛发")
                return
            self._update_page_spline_setting()

    def _clear_spline_page(self):
        self.leSplineName.clear()
        self.lgSplineGroupName.clear()
        self.leSplineGuideName.clear()

    def _update_page_spline_setting(self):
        if len(self.currentSelectXgen) == 1:
            currentXgen = self.currentSelectXgen[0]

            self.leSplineName.setText(str(currentXgen))
            groupName = safe_get_attr(currentXgen, self.attrGroupName)
            isExportGuideAnim = safe_get_attr(currentXgen, self.attrExportGuideAnim)
            isExportSplineAnim = safe_get_attr(currentXgen, self.attrExportSplineAnim)
            self.lgSplineGroupName.setText(groupName)
            GuideGroupName = cmds.listConnections(currentXgen + "." + self.attrGuideGroupName)[0]

            if not GuideGroupName:
                self.leSplineGuideName.setText("None")
            else:
                self.leSplineGuideName.setText(GuideGroupName)

            self.chbExportGuideAnim.setChecked(isExportGuideAnim)
            self.chbExportSplineAnim.setChecked(isExportSplineAnim)
        else:
            name = ""
            guideAnim = True
            SplineAnim = True
            groupName = ""
            for currentXgen in self.currentSelectXgen:
                name = name + ";" + str(currentXgen)
                if not safe_get_attr(currentXgen, self.attrExportGuideAnim):
                    guideAnim = False
                if not safe_get_attr(currentXgen, self.attrExportSplineAnim):
                    SplineAnim = False
                if groupName == "":
                    groupName = safe_get_attr(currentXgen, self.attrGroupName)
                elif groupName == False:
                    pass
                else:
                    if groupName != safe_get_attr(currentXgen, self.attrGroupName):
                        groupName = False

            self.leSplineName.setText(name)
            self.chbExportGuideAnim.setChecked(guideAnim)
            self.chbExportSplineAnim.setChecked(SplineAnim)
            if groupName:
                self.lgSplineGroupName.setText(groupName)

    def _update_page_des_setting(self):
        textName = self.currentSelectXgen[0]
        for xgen in self.currentSelectXgen[1:]:
            textName = textName + "," + str(xgen)
        self.lgDesName.setText(textName)

        if len(self.currentSelectXgen) == 1:
            groupName = safe_get_attr(self.currentSelectXgen[0], self.attrGroupName)
        else:
            groupName = False

        if not groupName:
            self.cbDesGroupName.set_current_index(0)
        else:
            index = self.groups.index(groupName)
            self.cbDesGroupName.set_current_index(index + 1)

    def _update_cb_groups(self):
        self.cbDesGroupName.clear()
        self.cbDesGroupName.add_item(" ")
        self.cbDesGroupName.add_items(self.groups)

    # ==================== 组操作 ====================

    def _add_new_group(self):
        newGroupName = self.leNewGroupName.text()
        if not newGroupName:
            return
        if newGroupName not in self.groups:
            self.groups.append(newGroupName)
            self._update_cb_groups()
        self.leNewGroupName.clear()

    def _on_group_changed(self, text):
        if not self.currentSelectXgen:
            return
        for xgen in self.currentSelectXgen:
            if text == " ":
                safe_set_attr(xgen, self.attrGroupName, "", "string")
            else:
                safe_set_attr(xgen, self.attrGroupName, text, "string")

    # ==================== 导线操作 ====================

    def _select_guide(self):
        if len(self.currentSelectXgen) > 1:
            MGlobal.displayWarning("More than one object has been selected!")
            return
        currentXgen = self.currentSelectXgen[0]
        guide = cmds.listConnections(currentXgen + "." + self.attrGuideGroupName)[0]
        if not guide:
            return
        cmds.select(cl=1)
        cmds.select(guide)

    def _clear_guide(self):
        if len(self.currentSelectXgen) > 1:
            MGlobal.displayWarning("More than one object has been selected!")
            return
        currentXgen = self.currentSelectXgen[0]
        currentGuide = cmds.listConnections(currentXgen + "." + self.attrGuideGroupName)[0]
        if not currentGuide:
            return
        cmds.disconnectAttr(currentGuide + ".message", currentXgen + "." + self.attrGuideGroupName)
        self._updateUI()

    def _assign_guide_group(self):
        if not self.currentSelectGuide:
            return
        if len(self.currentSelectXgen) > 1:
            MGlobal.displayWarning("More than one object has been selected!")
            return
        currentXgen = self.currentSelectXgen[0]
        currentGuide = cmds.listConnections(currentXgen + "." + self.attrGuideGroupName)[0]
        if currentGuide:
            cmds.disconnectAttr(currentGuide + ".message", currentXgen + "." + self.attrGuideGroupName)
        cmds.connectAttr(self.currentSelectGuide + ".message", currentXgen + "." + self.attrGuideGroupName)
        self._updateUI()

    # ==================== 状态变更回调 ====================

    def _on_export_guide_anim_state_changed(self, state):
        for currentXgen in self.currentSelectXgen:
            safe_set_attr(currentXgen, self.attrExportGuideAnim, bool(state), "bool")

    def _on_export_spline_anim_state_changed(self, state):
        for currentXgen in self.currentSelectXgen:
            safe_set_attr(currentXgen, self.attrExportSplineAnim, bool(state), "bool")

    # ==================== 交互式转换 ====================

    def _convert_to_interactivate(self):
        descriptions = get_all_descriptions()
        interactiveGroupName = "interactives"
        if cmds.objExists(interactiveGroupName):
            cmds.delete(interactiveGroupName, hi="below")
        interactiveGroup = cmds.createNode('transform', name=interactiveGroupName)

        guideGroupName = "guides"
        if cmds.objExists(guideGroupName):
            cmds.delete(guideGroupName, hi="below")
        guideGroup = cmds.createNode('transform', name=guideGroupName)

        for description in descriptions:
            palette = xg.palette(description)
            groupName = safe_get_attr(description, 'GroupName') or "HairGroup"
            meshName = self._get_bound_mesh(description)
            cmds.select(description, r=1)
            curve_group_name = description + "_guides"
            mel.eval('xgmCreateCurvesFromGuidesOption(0, 0, "{}")'.format(curve_group_name))
            curve_group = cmds.ls(curve_group_name)
            cmds.parent(curve_group, guideGroup)

            interactive_shape = cmds.xgmGroomConvert(description)
            interactive_transfrom = cmds.listRelatives(interactive_shape, ap=1, type='transform')[0]
            cmds.parent(interactive_transfrom, interactiveGroup)

            safe_set_attr(interactive_transfrom, self.attrGroupName, groupName, "string")
            safe_set_attr(interactive_transfrom, self.attrCharacterName, palette, "string")
            safe_set_attr(interactive_transfrom, self.attrUVSetIndexName, 0, "short")
            safe_set_attr(interactive_transfrom, self.attrIsExport, True, "bool")
            safe_set_attr(interactive_transfrom, self.attrExportGuideAnim, True, "bool")
            safe_set_attr(interactive_transfrom, self.attrExportSplineAnim, False, "bool")

            safe_set_attr(interactive_transfrom, self.attrGuideGroupName, None, "message")
            cmds.connectAttr(curve_group_name + ".message", interactive_transfrom + "." + self.attrGuideGroupName)

            safe_set_attr(interactive_transfrom, self.attrMeshUVName, None, "message")
            cmds.connectAttr(meshName + ".message", interactive_transfrom + "." + self.attrMeshUVName)

            cmds.delete("xgGroom")

        QMessageBox.information(self, u"提示", u"交互式转换完成")

    # ==================== 导出 ====================

    def _export_as_abc(self, isStatic=False):
        sceneName = self._get_scene_name()
        project = list(PROJECTINFO.keys())[self.cb_project.currentIndex()]
        select_groom_groups = [item.text() for item in self.lw_groom_groups.selectedItems()]

        if len(select_groom_groups) == 0:
            QMessageBox.warning(self, u"警告", u"未选择任何毛发组")
            return

        refreshHair = self.refreshPerFrame.isChecked()
        if isStatic:
            frameStart = 0
            frameEnd = 1
            frameExpendForward = 0
            frameExpendBackward = 0
            root_path = self.leExportPath.text
            if not root_path:
                QMessageBox.warning(self, u"警告", u"未设置导出目录")
                return
        else:
            frameStart = self.sbFrameStart.value()
            frameEnd = self.sbFrameEnd.value()
            frameExpendForward = self.sbFrameExpendStart.value()
            frameExpendBackward = self.sbFrameExpendEnd.value()
            root_path = self._get_root_path()

        jobs = []
        file_paths = []
        binders = []
        binder_nodes = set()

        for groom_group in select_groom_groups:
            xgen_nodes = cmds.listRelatives(groom_group, type="transform")
            if not xgen_nodes:
                MGlobal.displayWarning("There is no xgen node in group :{}".format(groom_group))
                continue

            gg_split = groom_group.split(":")
            character_name, index = gg_split[-1].split("_Hair")
            index = index.replace("_BD", "")

            if isStatic:
                fileName = "{}_Hair{}_BD.abc".format(character_name, index)
            else:
                fileName = "{}_{}_Hair{}_{}-{}_hCache.abc".format(
                    sceneName, character_name, index, 1, frameEnd + frameExpendForward + frameExpendBackward
                )
            MGlobal.displayInfo(
                "\nExport Group:{}\nCharacter Name:{}\nindex:{}\nRootPath:{}\nFileName:{}".format(
                    groom_group, character_name, index, root_path, fileName
                )
            )
            file_path = os.path.normpath(os.path.join(root_path, fileName))
            file_paths.append(file_path)
            jobs.append(groom_group)

            # 移动至原点
            if 'SSDSY_CS' in project and 'Hair01' not in groom_group:
                continue
            if len(gg_split) > 1:
                namespace = gg_split[0:-1]
                joint = ':'.join(namespace) + ":Head_M"
            else:
                joint = "Head_M"
            binder_nodes.add((groom_group, joint))
            for xgen in xgen_nodes:
                try:
                    guide = cmds.listConnections(xgen + '.' + self.attrGuideGroupName)[0]
                    binder_nodes.add((guide, joint))
                except (TypeError, IndexError):
                    cmds.warning("No guide group connected to xgen node: {}".format(xgen))

        while True:
            tempPath = os.path.join(tempfile.gettempdir(), str(time.time()).split(".")[0] + ".abc")
            if not os.path.exists(tempPath):
                break
            time.sleep(1)

        for binder_node in binder_nodes:
            binders.extend(create_binder(*binder_node))
        for binder in binders:
            binder.move_to_locator()

        export_xgen(jobs, file_paths, project, 
                    frameStart, frameEnd, frameExpendForward, frameExpendBackward, 
                    refreshHair, isStatic)

        for binder in binders:
            binder.close()

        QMessageBox.information(self, u"提示", u"ABC导出完成")

    # ==================== 场景初始化 ====================

    def _init_groom_group(self):
        transforms = cmds.ls(type="transform")
        groom_root_group = [tran for tran in transforms if "interactives" in tran]
        groom_groups = []
        for root in groom_root_group:
            groom_groups.extend(cmds.listRelatives(root, type="transform"))
        self.lw_groom_groups.clear()
        self.lw_groom_groups.addItems(groom_groups)

    def _init_scence_info(self):
        self.groups = []
        for des in get_all_descriptions():
            name = safe_get_attr(des, self.attrGroupName)
            if name and name not in self.groups:
                self.groups.append(name)
        self._init_groom_group()

        start = cmds.playbackOptions(q=1, min=1)
        end = cmds.playbackOptions(q=1, max=1)
        self.sbFrameStart.setValue(start)
        self.sbFrameEnd.setValue(end)

        self._update_cb_groups()

    # ==================== 工具方法 ====================

    def _get_uv_sets(self, meshpath):
        sl = MGlobal.getSelectionListByName(meshpath).getDagPath(0)
        mesh = om.MFnMesh(sl)
        return mesh.getUVSetNames()

    def _get_bound_mesh(self, obj):
        sl = MGlobal.getSelectionListByName(obj).getDependNode(0)
        itDg = om.MItDag()
        itDg.reset(sl, om.MItDag.kDepthFirst, om.MFn.kPluginShape)
        boundMesh = None
        while not itDg.isDone():
            dn = om.MFnDependencyNode(itDg.currentItem())
            if dn.typeName == "xgmSubdPatch":
                boundMeshPlug = dn.findPlug('geometry', False)
                boundMesh = om.MFnMesh(
                    om.MDagPath.getAPathTo(boundMeshPlug.source().node()))
                break
            itDg.next()
        return str(boundMesh.dagPath())

    # ==================== 事件重写 ====================

    def showEvent(self, e):
        add_selection_changed_callback("selectionChanged", self._updateUI)

    def hideEvent(self, e):
        remove_callback("selectionChanged")
        mel.eval('outlinerEditor -edit -selectCommand "" "outlinerPanel1";')


def showUI():
    window = XGenToolsUI()
    window.show(dockable=True)


if __name__ == "__main__":
    showUI()
