#-*- coding:utf-8 -*-

from PySide2.QtWidgets import (QWidget,QVBoxLayout,
                                QHBoxLayout,QListWidget,
                                QPushButton,QLabel,
                                QSpinBox,QMessageBox,QCheckBox,
                                QComboBox)
from PySide2.QtCore import Qt

import mayaTools.core.mayaLibrary as ML
import mayaTools.core.pathLibrary as PL

from mayaTools import PYTHONVERSION

import maya.cmds as cmds
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import os

import maya.api.OpenMaya as om
from maya.api.OpenMaya import MGlobal

import mayaTools.core.mayaLibrary as ml

abc_plugin_name = 'ZynnMaya1.0.mll'


ErrorShaderNames = [
    "lambert1",
    "lambert",
    "randshder",
    "pasted",
    "rsmaterial",
    "cccolorshading"
]

def ExportAbc(objects,StartFrame,EndFrame,Step,StartExpend,EndExpend,ExportPath,RefreshHair):
    cmds.loadPlugin(abc_plugin_name)
    try:
        cmds.AbcExportN(objects ,StartFrame,EndFrame,Step,StartExpend,EndExpend,ExportPath,RefreshHair)
    except:
        print("插件导出错误")
    finally:
        cmds.unloadPlugin(abc_plugin_name)



class Job:
    job_str = ""
    exportPath = ""
    def __repr__(self):
        return "<job_str:{},exportPath:{}>".format(self.job_str,self.exportPath)
    

def check_more_than_four_edge(fullName):
    sList = MGlobal.getSelectionListByName(fullName)

    if sList.length()==0:
        return False
    dagPath = sList.getDagPath(0)
    if dagPath.apiType() != om.MFn.kTransform:
        return False
    mitPoly = om.MItMeshPolygon(dagPath)
    while not mitPoly.isDone():
        verts = mitPoly.getVertices()
        edge_count = len(verts)
        if (edge_count > 4):
            return True
        if PYTHONVERSION == 2:
            mitPoly.next(0)
        else:
            mitPoly.next()
    return False

class ClothExportUI(MayaQWidgetDockableMixin,QWidget):
    def __init__(self,parent=None):
        super(ClothExportUI, self).__init__(parent)
        self.resize(400,400)
        self.setWindowTitle(u"布料缓存导出工具")
        self.__initUI()
        self.dec_project_from_file_name()
    def __initUI(self):
        lay_main = QVBoxLayout(self)
        self.setLayout(lay_main)


        lay_main.addWidget(QLabel(u"项目名称:"))
        self.cb_project = QComboBox()
        self.cb_project.addItems(ml.PROJECTINFO.keys())
        lay_main.addWidget(self.cb_project)



        self.lw_cloth_groups = QListWidget(self)
        self.lw_cloth_groups.setSelectionMode(QListWidget.ExtendedSelection)


        lay_main.addWidget(self.lw_cloth_groups)

        sb_width = 80

        #帧范围
        w_frame_range = QWidget(self)
        lay_main.addWidget(w_frame_range)
        lay_frame_range = QHBoxLayout(w_frame_range)
        lay_frame_range.setAlignment(Qt.AlignLeft)
        lay_frame_range.setContentsMargins(0,0,0,0)


        lay_frame_range.addWidget(QLabel(u"帧范围:"))

        self.sb_frame_start = QSpinBox(self)
        self.sb_frame_start.setButtonSymbols(QSpinBox.NoButtons)
        self.sb_frame_start.setMinimumWidth(sb_width)
        self.sb_frame_start.setMaximum(999)
        lay_frame_range.addWidget(self.sb_frame_start)
        lay_frame_range.addWidget(QLabel(u"~"))


        self.sb_frame_end = QSpinBox(self)
        self.sb_frame_end.setButtonSymbols(QSpinBox.NoButtons)
        self.sb_frame_end.setMinimumWidth(sb_width)
        self.sb_frame_end.setMaximum(999)
        lay_frame_range.addWidget(self.sb_frame_end)



        w_frame_expend = QWidget(self)
        lay_main.addWidget(w_frame_expend)
        lay_frame_expend = QHBoxLayout(w_frame_expend)
        lay_frame_expend.setAlignment(Qt.AlignLeft)
        lay_frame_expend.setContentsMargins(0,0,0,0)

        #帧扩展
        lay_frame_expend.addWidget(QLabel(u"帧扩展:"))

        self.sb_frame_expend_start = QSpinBox(self)
        self.sb_frame_expend_start.setButtonSymbols(QSpinBox.NoButtons)
        self.sb_frame_expend_start.setMinimumWidth(sb_width)
        lay_frame_expend.addWidget(self.sb_frame_expend_start)
        lay_frame_expend.addWidget(QLabel(u"~"))


        self.sb_frame_expend_end = QSpinBox(self)
        self.sb_frame_expend_end.setButtonSymbols(QSpinBox.NoButtons)
        self.sb_frame_expend_end.setMinimumWidth(sb_width)
        lay_frame_expend.addWidget(self.sb_frame_expend_end)



        pb_export = QPushButton(self,text=u"导出ABC")
        pb_export.clicked.connect(self._export_list)
        lay_main.addWidget(pb_export)


        self.cb_Export_Outline = QCheckBox(self,text=u"导出大纲中选择的物体")
        lay_main.addWidget(self.cb_Export_Outline)




        pb_export = QPushButton(self,text=u"打开导出目录")
        pb_export.clicked.connect(self._open_export_folder)
        lay_main.addWidget(pb_export)



    def dec_project_from_file_name(self):
        file_name = cmds.file(q=True, sn=True)
        index = 0
        for i,key in enumerate(ml.PROJECTINFO.keys()):
            if key.split("-")[-1].lower() in file_name.lower():
                index = i
        self.cb_project.setCurrentIndex(index)

    def _open_export_folder(self):
        os.startfile(self._get_export_root_path())
        pass
    def _export_list(self):
        select_groups = [item.text() for item in self.lw_cloth_groups.selectedItems()]

        final_trans = []
        for group in select_groups:
            final_trans.extend(cmds.listRelatives(group,type="transform"))

        if self.cb_Export_Outline.isChecked():
            sls = cmds.ls(sl=1)
            export_trans = []
            for sl in sls:
                shapes = cmds.listRelatives(sl,type="mesh")
                for shape in shapes:
                    if cmds.getAttr(shape+".intermediateObject"):
                        continue
                    sgs = cmds.listConnections(shape,type="shadingEngine")
                    for sg in sgs:
                        trans = cmds.listConnections(sg,type="mesh")
                        for tran in trans:
                            if tran not in export_trans:
                                export_trans.append(tran)
            final_trans.extend(export_trans)
        
        model_has_error = False
        for tran in final_trans:
            if check_more_than_four_edge(tran):
                model_has_error = True
                cmds.warning(u"模型{}有超过四边的面,检查后导出".format(tran))
            mesh = [m for m in cmds.listRelatives(tran,typ="mesh") if not cmds.getAttr(m+".intermediateObject")]
            if not mesh:
                continue

            mesh = mesh[0]
            shaders = []
            sgs = cmds.listConnections(mesh,type="shadingEngine")
            if not sgs:
                model_has_error = True
                cmds.warning(u"模型:{},上没有材质,导出取消".format(tran))
                break

            for sg in sgs:
                shader = cmds.listConnections(sg+".surfaceShader")
                if shader:
                    shaders.extend(shader)

            for shader in shaders:
                shader = shader.lower()
                for error in ErrorShaderNames:
                    if error in shader:
                        model_has_error = True
                        cmds.warning(u"模型:{},上存在错误材质,请检查后导出".format(tran))
                        break
                if model_has_error:
                    break
        if model_has_error:
            QMessageBox.warning(self, u"警告", u"模型存在错误,检查后重新导出")
        else:
            if len(final_trans) == 0:
                QMessageBox.warning(self, u"警告", u"未选择任何组")
            else:
                self._export_abc(final_trans)
    def _get_scenename(self):
        sceneName =  ML.getScenename_real()
        if "Ep" in sceneName and "sc" in sceneName:
            sceneNameParts = sceneName.split("_")
            sceneName = "{}_{}_{}".format(sceneNameParts[0],sceneNameParts[1],sceneNameParts[2])
        else:
            sceneName = ""
        return sceneName
    def _get_export_root_path(self):
        sceneName = self._get_scenename()
        ep,sc,cam = sceneName.split("_")[0:3]
        root_path = list(ml.PROJECTINFO.values())[self.cb_project.currentIndex()].format(ep,"nCloth_nCache",sc,"{}_{}_{}".format(ep,sc,cam),"")
        #确定根文件夹存在
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        return root_path
    def _export_abc(self,export_group):
        sceneName = self._get_scenename()
        root_path = self._get_export_root_path()
        start_frame = self.sb_frame_start.value()
        end_frame = self.sb_frame_end.value()
        start_frame_expend = self.sb_frame_expend_start.value()
        end_frame_expend = self.sb_frame_expend_end.value()
        cloth_and_characters = {}
        for group in export_group:
            character_name = group.split(":")[0].replace("_CH","")
            if character_name not in cloth_and_characters.keys():
                cloth_and_characters[character_name] = Job()

            file_name = "{}_{}_{}-{}_Cache.abc".format(sceneName,
                                                        character_name,
                                                        start_frame,
                                                        end_frame + start_frame_expend + end_frame_expend)
            cloth_and_characters[character_name].exportPath = os.path.join(root_path,file_name)
            cloth_and_characters[character_name].job_str = cloth_and_characters[character_name].job_str + group + ","
            

        jobs = []
        file_paths = []
        for j in cloth_and_characters.values():
            jobs.append(j.job_str)
            file_paths.append(j.exportPath)

        ExportAbc(jobs, start_frame, end_frame, 1, start_frame_expend, end_frame_expend,
                    file_paths, False)

        QMessageBox.information(self, u"提示", u"ABC导出完成")
    
    def showEvent(self,*args):
        #获取所有需要的transform名称
        objs = cmds.ls(type="transform",ln=0)
        targets = []
        for obj in objs:
            if "SK_G" in obj or "_CH_hair_Gro" in obj:
                targets.append(obj)

        self.lw_cloth_groups.addItems(targets)

        #设置帧数范围
        self.sb_frame_start.setValue(cmds.playbackOptions(q=1,min=1))
        self.sb_frame_end.setValue(cmds.playbackOptions(q=1,max=1))

        self._set_frame_expend()

        return super(ClothExportUI, self).showEvent(*args)
    
    def _set_frame_expend(self):
        """
        特定项目和集数设置帧拓展
        - 渲染有问题, 需要偏移帧数
        - SSDSY_CS前四集设置为10, 5, 其他的设置为0, 0
        """
        file_name = cmds.file(q=True, sn=True)
        scene_name = self._get_scenename().lower()
        expend_start, expend_end = 0, 1
        if "SSDSY_CS" in file_name:
            sort_list = sorted(["ep001_sc001_001", scene_name, "ep005_sc001_001"])
            if scene_name == sort_list[1] and scene_name != "ep005_sc001_001":
                expend_start, expend_end = 0, 1

        self.sb_frame_expend_start.setValue(expend_start)
        self.sb_frame_expend_end.setValue(expend_end)

def showUI():
    window = ClothExportUI()#实例化UI
    window.show(dockable=True)



if __name__ == "__main__":
    #from mayaTools import reloadModule
    #reloadModule()
    showUI()

        


