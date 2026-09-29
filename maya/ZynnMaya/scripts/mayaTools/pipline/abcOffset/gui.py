#coding=utf-8

import maya.cmds as cmds
import pymel.core as pm

import os
import shutil

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from dayu_widgets.message import MMessage
from dayu_widgets.label import MLabel
from dayu_widgets.line_edit import MClickBrowserFolderToolButton,MLineEdit
from dayu_widgets.push_button import MPushButton


import mayaTools.core.mayaLibrary as ML


def frameOffset(s_offset):
    meshs=pm.ls(type='mesh')
    cmds.select(all=1)
    nodes=cmds.ls(sl=1)
    abc_type='AlembicNode'
    mesh=meshs[0].getParent()
    mesh=str(mesh)
    for node in nodes:
        if cmds.objectType(node)==abc_type:
            s_frame=cmds.getAttr(node+'.startFrame')
            e_frame=cmds.getAttr(node+'.endFrame')+s_offset
            cmds.setAttr(node+'.offset',s_offset)
        
    return s_frame,e_frame,mesh
    
def abcGet(folder_path):
    abc_filses=[]
    
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            if '.abc' in filename and str(dirpath)==folder_path:
                file_path=os.path.join(dirpath, filename)
                abc_filses.append(file_path.replace('\\','/'))
    return abc_filses


def openAbc(abc_path):
    cmds.file(f=1,new=1)
    cmds.currentUnit( time='pal' )
    cmds.file(abc_path,i=1,type='Alembic')





class AbcOffsetWindow(QWidget):

    def __init__(self,parent=None):
        super(AbcOffsetWindow,self).__init__(parent)

        self.ui()


    def ui(self):
  
        self.setWindowTitle(u'abc帧偏移工具')
        self.resize(400,120)
        self.setStyleSheet("QWidget { background-color: #333333; }")
        lay=QVBoxLayout()

        offset_lay=QHBoxLayout()
        s_offset_label=MLabel(u'起始偏移帧')
        self.s_offset_line=MLineEdit('10')
        e_offset_label=MLabel(u'结束延长帧')
        self.e_offset_line=MLineEdit('5')
        
        offset_lay.addWidget(s_offset_label)
        offset_lay.addWidget(self.s_offset_line)
        offset_lay.addWidget(e_offset_label)
        offset_lay.addWidget(self.e_offset_line)
        
        

        self.flie_import=MLineEdit().folder().medium()
        self.flie_import.setMinimumHeight(30)
        self.flie_import.setPlaceholderText(u"请选择需执行的abc文件夹")
        

        start_button=MPushButton(text=u"执行")
        start_button.clicked.connect(self.start)
        
        
        self.folder_export=MLineEdit().folder().medium()
        self.folder_export.setMinimumHeight(30)
        self.folder_export.setPlaceholderText(u"请选择abc导出路径")
        
        hint_label=MLabel(u'执行后会直接关闭当前场景,请提前保存文件')


        self.execute_data=QPlainTextEdit()
        self.execute_data.setStyleSheet("color: #cccccc; border :1px solid black")
        self.execute_data.setMinimumHeight(50)
        self.execute_data.setReadOnly(True)
        

        #folder_lay.addWidget(self.flie_import)
        

        lay.addWidget(self.flie_import)
        lay.addLayout(offset_lay)
        lay.addWidget(self.folder_export)
        lay.addWidget(start_button)
        lay.addWidget(hint_label)
        
        #lay.addWidget(self.execute_data)

        
        self.setLayout(lay)


            
    def start(self):
        cmds.loadPlugin( 'AbcExport.mll' )
        cmds.loadPlugin( 'AbcImport.mll' )
        s_offset=int(self.s_offset_line.text())
        e_offset=int(self.e_offset_line.text())
        abc_path=self.flie_import.text()
        export_path=self.folder_export.text()
        abc_files=abcGet(abc_path)
        for abc_file in abc_files:
            old_frame = abc_file.split('_')[-2]
            old_end_frame = int(old_frame.split('-')[-1])
            new_end_frame = old_end_frame+s_offset+e_offset
            new_frame = old_frame.replace('-'+str(old_end_frame),'-'+str(new_end_frame))
            new_abc_name = abc_file.replace(old_frame,new_frame).split('/')[-1]
            abc_export_path=export_path+'/'+new_abc_name
            openAbc(abc_file)
            s_frame,e_frame,mesh=frameOffset(s_offset)
            ML.exportABC(mesh,s_frame,e_frame+e_offset,abc_export_path)
            json_path=abc_file.rsplit('.',1)[0]+'.json'
            if os.path.exists(json_path):
                old_json_name = json_path.rsplit('.',1)[0].split('/')[-1]
                new_json_name = new_abc_name.rsplit('.',1)[0]+'.json'
                new_json_path = export_path+'/'+new_json_name
                print(json_path, export_path)
                shutil.copy(json_path, export_path)
                #修改新json名称
                os.rename(export_path+'/'+json_path.split('/')[-1], new_json_path)
            print(abc_export_path)


def showUI():
    app=QApplication.instance()
    global win
    win=AbcOffsetWindow()
    win.show()
    win.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
    win.show()
    app.exec_()




if __name__=='__main__':
    showUI()










