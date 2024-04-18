#coding=utf-8

import pymel.core as pm
import maya.cmds as cmds
#导入自定义模块
import mayaTools.core.mayaLibrary as ML
import mayaTools.core.pathLibrary as PL


class gpuCacheToolUI:
    def __init__(self):
        pm.loadPlugin('gpuCache.mell') #loadplugins
        window_name = "gpuCacheToolWindow" #define main window name
        window_title = u"GPU Cahce工具" #define window title
        window_width = 400
        window_height = 200

        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name)           #delete repeate window

        cmds.window(window_name, title=window_title, widthHeight=(window_width, window_height))  #create window
        main_layout = cmds.columnLayout(adjustableColumn=True)                                   #create main layout

        # 设置窗口背景颜色
        cmds.layout(main_layout, edit=True, backgroundColor=[0.3, 0.3, 0.3],)
        cmds.text(label=u"导出路径(ABC):", align="left", font="boldLabelFont", height=20)
        path_row_layout = cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=[300, 60])
        self.path_text_field_ABC = cmds.textField("path_text_field",tcc=lambda *arg: self.normalizeTextFieldTex(self.path_text_field_ABC))
        path_button = cmds.button(label="...",c=lambda *arg: ML.fileDialog(u'选择ABC文件存放路径',3,self.path_text_field_ABC))
        cmds.setParent("..")

        cmds.layout(main_layout, edit=True, backgroundColor=[0.3, 0.3, 0.3],)
        cmds.text(label=u"导出路径(MB):", align="left", font="boldLabelFont", height=20)
        path_row_layout = cmds.rowLayout(numberOfColumns=2, adjustableColumn=1, columnWidth2=[300, 60])
        self.path_text_field_MB = cmds.textField("path_text_field",tcc=lambda *arg: self.normalizeTextFieldTex(self.path_text_field_MB))
        path_button = cmds.button(label="...",c=lambda *arg: ML.fileDialog(u'选择MB文件存放路径',3,self.path_text_field_MB))
        cmds.setParent("..")

        cmds.text(label=u"导出名称", align="left", font="boldLabelFont", height=20)
        self.name_text_field = cmds.textField("name_text_field")

        cmds.separator(height=20, style="none")

        cmds.button(label=u"转换为GPUCache", c=self.convertToCache)
        cmds.separator(height=20, style="none")
        convertTOMesh_row_layout = cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
        #是否继承变换
        self.inherit_transform_checkBox = cmds.checkBox("inherit_transform_checkBox",label=u"继承变换",v=1)
        cmds.button(label=u"转换为网格体", c=self.convertToMesh)


        cmds.showWindow(window_name)
    def normalizeTextFieldTex(self,target):
        cmds.textField(target, edit=True, text=PL.normailizePath(cmds.textField(target, query=True, text=True)))
    def convertToCache(self,*args):
        export_path_mb = cmds.textField(self.path_text_field_MB, query=True, text=True)
        export_path_abc = cmds.textField(self.path_text_field_ABC, query=True, text=True)
        export_name = cmds.textField(self.name_text_field, query=True, text=True)
        if export_path_mb == '' or export_path_abc == '':
            cmds.error(u'请选择导出目录')
            return False
        obj = pm.ls(sl=True)[0]
        if export_name == '':
            cmds.warning(u'未输出导出名称,将使用当前选择节点的名称作为导出名称')
            export_name = str(obj)
        exportAbcPath = export_path_abc + export_name +'.abc'
        exportMBPath = export_path_mb + export_name +'.mb'
        parentNode = obj.getParent()
        obj.setParent(None)
        self.addAndSetAttr(obj,exportAbcPath,exportMBPath)
        ML.exportGpuCache(obj,exportAbcPath)#导出GPUCache
        cmds.file( exportMBPath, force=1, type='mayaBinary', pr=1, es=1)#导出mb文件
        pm.delete(obj)#删除对象
        transform_node = pm.createNode("transform",name=str(obj)+'_GC')
        if parentNode:
            transform_node.setParent(parentNode)
        self.addAndSetAttr(transform_node,exportAbcPath,exportMBPath)
        gpu_cache_node = pm.createNode("gpuCache", parent=transform_node)
        gpu_cache_node.setAttr('cacheFileName', exportAbcPath)
        # 优化场景大小
        ML.deleteUnusedNode()
    def addAndSetAttr(self,obj,exportAbcPath,exportMBPath):
        try:
            obj.addAttr('abcFilePath', dt  ='string')
            obj.addAttr('mbFilePath', dt  ='string')
        except RuntimeError:
            pass
        obj.setAttr('abcFilePath', exportAbcPath)
        obj.setAttr('mbFilePath', exportMBPath)
    def convertToMesh(self,*args):
        original_root_nodes = pm.ls(assemblies=True)  #保存导入前场景中的根节点
        obj = pm.ls(sl=True)[0]
        mbfilepath = obj.getAttr('mbFilePath')
        parent = obj.getParent()
        # get obj transform
        Translation = obj.getTranslation()
        Rotation = obj.getRotation()
        scale = obj.getScale()

        pm.delete(obj)#删除对象
        pm.importFile(mbfilepath,returnNewNodes=True) #导入mb文件
        afterImportRootNodes = pm.ls(assemblies=True)  #保存导入后场景中的根节点
        for node in afterImportRootNodes:
            if node not in original_root_nodes:
                node.setParent(parent)             #设置新导入的根节点的父级
                if cmds.checkBox(self.inherit_transform_checkBox,query=True,value=True):
                    node.setTranslation(Translation)
                    node.setRotation(Rotation)
                    node.setScale(scale)






def showUI():
    UI = gpuCacheToolUI()#实例化UI













