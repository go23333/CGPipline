# -*- coding: utf-8 -*-

import os
import logging

import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMayaUI as omui

from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets

from mayaTools.core.widgets import Line
from mayaTools.export.xGenOriginExport.export_xgen import export_xgen
from mayaTools.export.xGenOriginExport.move_origin import create_binder


class FileInfo():
    """
    当前打开的文件信息
    """
    def __init__(self):
        self.file_path = cmds.file(q=True, sn=True)
    
    def get_project(self):
        """
        获取所属项目

        :return: 所属项目
        :rtype: str
        """
        return self.file_path.split('/')[1]
    
    def get_name(self):
        """
        获取文件名

        :return: 文件名
        :rtype: str
        """
        return os.path.basename(self.file_path)

    def get_folder(self):
        """
        获取所属文件夹

        :return: 所属文件夹
        :rtype: str
        """
        return os.path.dirname(self.file_path)
    
    def get_stem(self):
        """
        获取文件名（不含后缀）

        :return: 文件名（不含后缀）
        :rtype: str
        """
        return os.path.splitext(self.get_name())[0]
    
    def get_suffix(self):
        """
        获取文件后缀

        :return: 文件后缀
        :rtype: str
        """
        return os.path.splitext(self.get_name())[1]
    
    def get_type(self):
        """
        获取文件类型

        :return: 文件类型
        :rtype: str
        """
        return self.get_stem().split('_')[-1]


class Character(FileInfo):
    """
    角色
    """
    def __init__(self):
        FileInfo.__init__(self)
    
    def get_character_name(self):
        """
        获取角色名

        :return: 角色名
        :rtype: str
        """
        return '_'.join(self.get_stem().split('_')[0: -1])


class CharacterSkeletalMesh(Character):
    """
    角色SK
    """
    def __init__(self, adv_tree, sy_group_trees=[], sk_group_trees=[], texiao_group_trees=[], remove_trees=[]):
        """
        :param stem: 文件名（不含后缀）
        :type stem: str
        :param sy_group_trees: SY_Gro节点信息列表, 每个元素包含sy_group, parent, index
        :type sy_group_trees: list
        :param meta_human_adv_trees: meta_human_adv节点信息列表, 每个元素包含sy_group, parent, index
        :type meta_human_adv_trees: list
        """
        Character.__init__(self)
        self.adv_tree = adv_tree
        self.sy_group_trees = sy_group_trees
        self.sk_group_trees = sk_group_trees
        self.texiao_group_trees = texiao_group_trees
        self.remove_trees = remove_trees
        self.save_folder = os.path.dirname(cmds.file(q=True, sn=True))
        self.export_nodes = ['Geometry', adv_tree['node'].split('|')[-1]]
        self.switch_con = 'QieHuan_Con'

    @classmethod
    def init_node(cls):
        """
        通过场景中的节点信息初始化 CharacterSK 实例

        :return: 初始化后的 CharacterSK 实例
        :rtype: CharacterSK
        """
        # 记录骨骼
        if cmds.objExists('ADV_Body:pelvis'):
            adv_group = 'ADV_Body:pelvis'
        else:
            adv_group = 'DeformationSystem'
        adv_tree = cls._node_tree_info(cmds.ls(adv_group, long=True)[0])       # 只记录一套骨骼

        # 记录SY_Gro
        sy_group_trees = []      # 可能会有多个
        sy_groups = cmds.ls('*_SY_Gro', long=True)
        for sy_group in sy_groups:
            if 'Geometry' in sy_group:
                sy_group_tree = cls._node_tree_info(sy_group)
                sy_group_trees.append(sy_group_tree)

        # 记录sk
        sk_group_trees = []
        sk_groups = cmds.ls('SK_*', long=True)
        for sk_group in sk_groups:
            if 'Geometry' in sk_group:
                sk_group_tree = cls._node_tree_info(sk_group)
                sk_group_trees.append(sk_group_tree)

        # 记录TeXiao_JianMo
        texiao_group_trees = []
        texiao_groups = cmds.ls('TeXiao_JianMo', long=True)
        for texiao_group in texiao_groups:
            if 'Geometry' in texiao_group:
                sk_group_tree = cls._node_tree_info(texiao_group)
                texiao_group_trees.append(sk_group_tree)

        # 记录移除的模型
        remove_trees = []
        remove_rules = ['*_hair_Gro', '*eye*', '*teeth*', '*tongue', '*saliva']
        remove_transforms = [i for rule in remove_rules for i in cmds.ls(rule, type='transform', long=True)]
        for remove_transform in remove_transforms:
            if 'Geometry' in remove_transform:
                remove_transform_tree = cls._node_tree_info(remove_transform)
                remove_trees.append(remove_transform_tree)

        return cls(adv_tree, sy_group_trees, sk_group_trees, texiao_group_trees, remove_trees)
    
    @staticmethod
    def _node_tree_info(node):
        """
        获取节点的层级信息

        :param node: 节点
        :type node: str
        :return: 节点层级信息
        :rtype: dict[str, str | int | None]
        """
        parent = cmds.listRelatives(node, 
                                    parent=True, 
                                    type='transform', 
                                    fullPath=True) or None
        if parent:
            siblings = cmds.listRelatives(parent, 
                                          children=True, 
                                          type='transform', 
                                          fullPath=True) or None
            index = siblings.index(node)
        else:
            index = None

        return {
            'node': node,
            'parent': parent[0] if parent else parent,
            'index': index
        }

    @staticmethod
    def _get_current_parent(node):
        """
        获取当前父节点

        :param node: 节点
        :type node: str
        :return: 父节点
        :rtype: str | None
        """
        parent = cmds.listRelatives(
            node,
            parent=True,
            type='transform',
            fullPath=True
        )

        return parent[0] if parent else None
    
    def _set_parent_world(self, trees):
        """
        将节点父级设置为 world

        :param trees: 节点信息列表
        :type trees: list
        """
        for index, tree in enumerate(trees):
            try:
                current_parent = self._get_current_parent(tree['node'])
                if tree['parent'] and tree['parent'] == current_parent:
                    new_node = cmds.parent(tree['node'], world=True)
                    trees[index]['node'] = new_node[0]
            except ValueError:
                continue
    
    def _restore_parent(self, trees):
        """
        恢复节点父级以及层级顺序

        :param trees: 节点信息列表
        :type trees: list
        """
        for index, tree in enumerate(trees):
            try:
                current_parent = self._get_current_parent(tree['node'])
                if tree['parent'] and tree['parent'] != current_parent:
                    new_node = cmds.parent(tree['node'], tree['parent'])
                    trees[index]['node'] = new_node[0]
                    cmds.reorder(tree['node'], front=True)
                    cmds.reorder(tree['node'], relative=tree['index'])
            except ValueError:
                continue

    def _unlock_normal(self, root_node):
        """解锁模型法线"""
        cmds.waitCursor(state=True)
        mesh_shapes = cmds.listRelatives(root_node, allDescendents=True, type='mesh', fullPath=True)
        for mesh_shape in mesh_shapes:
            cmds.polyNormalPerVertex(mesh_shape, unFreezeNormal=True)
        cmds.waitCursor(state=False)

    def _smooth(self, root_node):
        cmds.waitCursor(state=True)
        smooth_transforms = set()
        mesh_shapes = cmds.listRelatives(root_node, allDescendents=True, type='mesh', fullPath=True)
        for mesh_shape in mesh_shapes:
            if 'SK_' in mesh_shape:
                continue
            transform = cmds.listRelatives(mesh_shape, parent=True, fullPath=True)[0]
            smooth_transforms.add(transform)
        
        for smooth_transform in smooth_transforms:
            print(smooth_transform)
            cmds.polySmooth(smooth_transform, dv=1)
            cmds.bakePartialHistory(smooth_transform, prePostDeformers=True)
        cmds.waitCursor(state=False)
    
    def _set_normal(self):
        if not cmds.objExists(self.switch_con):
            cmds.warning(u'未找到切换节点: {}'.format(self.switch_con))

        enum_str = cmds.attributeQuery('Enable_Overrides', node=self.switch_con, listEnum=True)
        enum_list = enum_str[0].split(':')
        
        target_value = enum_list.index('Normal')
        current_value = cmds.getAttr('{}.Enable_Overrides'.format(self.switch_con))
        if current_value != target_value:
            cmds.setAttr('{}.Enable_Overrides'.format(self.switch_con), target_value)
    
    def _export(self, save_path, export_node, remove_node_trees):
        try:
            self._set_parent_world(remove_node_trees)
            cmds.select(export_node, replace=True)
            # 重置 FBX 导出设置
            mel.eval('FBXResetExport')
            # 关闭动画
            mel.eval('FBXExportBakeComplexAnimation -v false')
            # 关闭输入连接
            mel.eval('FBXExportInputConnections -v false')
            mel.eval(
                'FBXExport -f "{}" -s'.format(
                    save_path.replace('\\', '/')
                )
            )
            logging.info(u'已自动保存UE资产: {}'.format(save_path))
        except Exception as e:
            logging.critical(u'导出UE资产失败, {}'.format(e))
        finally:
            self._restore_parent(remove_node_trees)
    
    def export_fbx(self, whole_process_radio, semi_process_radio, 
                   unlock_normal_check, smooth_check):
        """
        保存 fbx 文件
        """
        if 'SSDSY_CS' in self.get_project():
            prefix = 'UE'
        else:
            prefix = 'SK'
        if whole_process_radio.isChecked():
            if 'ADV_Body:pelvis' in self.adv_tree['node']:
                node_trees = [self.adv_tree] + self.sy_group_trees + self.texiao_group_trees
            else:
                node_trees = self.sy_group_trees + self.texiao_group_trees
            self._set_parent_world(node_trees)

            if unlock_normal_check.isChecked():
                self._unlock_normal(self.export_nodes)

            # 有SK
            save_path = os.path.join(self.get_folder(), '{}_{}.fbx'.format(prefix, self.get_character_name()))
            self._export(save_path, self.export_nodes, [])
            
            # 无SK
            save_path = os.path.join(self.get_folder(), '{}_{}_NoSK.fbx'.format(prefix, self.get_character_name()))
            remove_node_trees = self.sk_group_trees + self.texiao_group_trees
            self._export(save_path, self.export_nodes, remove_node_trees)
            
            # 只有SK
            save_path = os.path.join(self.get_folder(), '{}_{}_nCloth.fbx'.format(prefix, self.get_character_name()))
            export_node = [tree['node'] for tree in self.sk_group_trees]
            self._export(save_path, export_node, [])

            self._restore_parent(node_trees)

            # 只有特效
            save_path = os.path.join(self.get_folder(), 'TX_{}.fbx'.format(self.get_character_name()))
            export_node = [tree['node'] for tree in self.texiao_group_trees]
            export_node.append(self.adv_tree['node'].split('|')[-1])
            self._export(save_path, export_node, [])
            
        if semi_process_radio.isChecked():
            if 'ADV_Body:pelvis' in self.adv_tree['node']:
                node_trees = [self.adv_tree] + self.sy_group_trees + self.remove_trees
            else:
                node_trees = self.sy_group_trees + self.remove_trees
            self._set_normal()
            self._set_parent_world(node_trees)

            if smooth_check.isChecked():
                self._smooth(self.export_nodes[0])

            # 有SK
            save_path = os.path.join(self.get_folder(), '{}_{}.fbx'.format(prefix, self.get_character_name()))
            self._export(save_path, self.export_nodes, [])
            # 无SK
            save_path = os.path.join(self.get_folder(), '{}_{}_NoSK.fbx'.format(prefix, self.get_character_name()))
            remove_node_trees = self.sk_group_trees + self.texiao_group_trees
            self._export(save_path, self.export_nodes, remove_node_trees)

            self._restore_parent(node_trees)


class CharacterXgen(Character):
    def __init__(self):
        Character.__init__(self)
        self.joint = 'Head_M'

    def export_abc(self):
        xgen_groups = cmds.ls('*_Hair*_BD')
        if not xgen_groups:
            logging.info(u'当前文件没有交互式毛发')
            return

        file_paths = []
        jobs = []
        binders = []
        binder_nodes = set()
        try:
            for xgen_group in xgen_groups:
                file_name = '{}.abc'.format(xgen_group)
                file_path = os.path.normpath(os.path.join(self.get_folder(), file_name))
                file_paths.append(file_path)
                jobs.append(xgen_group)
                
                # 移动至原点
                if 'SSDSY_CS' in self.get_project() and 'Hair01' not in xgen_group:
                    continue
                binder_nodes.add((xgen_group, self.joint))
                xgen_nodes = cmds.listRelatives(xgen_group, c=1)
                for xgen in xgen_nodes:
                    guide = cmds.listConnections(xgen + '.GuideGroupName')[0]
                    binder_nodes.add((guide, self.joint))
            
            # 移动至世界坐标原点
            for binder_node in binder_nodes:
                binders.extend(create_binder(*binder_node))
            for binder in binders:
                binder.move_to_locator()
            
            export_xgen(jobs, file_paths, self.get_project(), 
                        0, 1, 0, 0, 
                        0, 1)
            logging.info(u'已自动保存毛发abc文件: {}'.format('; '.join(xgen_groups)))

        except Exception as e:
            logging.critical(u'导出毛发abc失败, {}'.format(e))
        
        finally:
            for binder in binders:
                binder.close()


class Watcher():
    """
    监听
    """
    def __init__(self, export_ue_check, export_xgen_check, 
                 whole_process_radio, semi_process_radio, 
                 unlock_normal_check, smooth_check):
        """
        :param export_ue_check: 
        :type export_ue_check: QtWidgets.QCheckBox
        :param export_xgen_check: 
        :type export_xgen_check: QtWidgets.QCheckBox
        :param whole_process_radio: 
        :type whole_process_radio: QtWidgets.QRadioButton
        :param semi_process_radio: 
        :type semi_process_radio: QtWidgets.QRadioButton
        :param unlock_normal_check: 
        :type unlock_normal_check: QtWidgets.QCheckBox
        :param smooth_check: 
        :type smooth_check: QtWidgets.QCheckBox
        """
        self.export_ue_check = export_ue_check
        self.export_xgen_check = export_xgen_check
        self.whole_process_radio = whole_process_radio
        self.semi_process_radio = semi_process_radio
        self.unlock_normal_check = unlock_normal_check
        self.smooth_check = smooth_check
        self.script_jobs = None
        self._do_func_lock = False

    def _on_changed(self):
        """
        防抖处理
        """
        if self._do_func_lock:
            return
        self._do_func_lock = True
        cmds.evalDeferred(self._do_export)

    def _do_export(self):
        """
        执行func
        """
        self._do_func_lock = False
        self.export()

    def start(self):
        """
        启动监听
        """
        if self.script_jobs:
            return
        
        self.script_jobs = cmds.scriptJob(
            event=["SceneSaved", self._on_changed], 
            protected=True
        )

    def stop(self):
        """
        停止监听
        """
        if not self.script_jobs:
            return

        if cmds.scriptJob(exists=self.script_jobs):
            cmds.scriptJob(kill=self.script_jobs, force=True)

        self.script_jobs = None
    
    def export(self):
        if self.export_ue_check.isChecked():
            character_sk = CharacterSkeletalMesh.init_node()
            character_sk.export_fbx(self.whole_process_radio, self.semi_process_radio, 
                                    self.unlock_normal_check, self.smooth_check)

        if self.export_xgen_check.isChecked():
            character_xgen = CharacterXgen()
            if character_xgen.get_type() != 'CH':
                logging.warning(u'当前不是角色(_CH)文件, 不执行自动保存')
                return
            character_xgen.export_abc()


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle(u'自动保存---UE资产&Xgen毛发')
        self.setFixedSize(450, 220)
        self.setWindowFlags(QtCore.Qt.Window | 
                            QtCore.Qt.WindowMinimizeButtonHint | 
                            # QtCore.Qt.WindowMaximizeButtonHint | 
                            QtCore.Qt.WindowCloseButtonHint)

        # 组件
        self.state_label = QtWidgets.QLabel(u'当前状态: 关闭')
        export_label = QtWidgets.QLabel(u'导出设置:')
        self.export_ue_check = QtWidgets.QCheckBox(u'导出UE资产')
        self.export_xgen_check = QtWidgets.QCheckBox(u'导出Xgen毛发')
        ue_process_label = QtWidgets.QLabel(u'流程设置:')
        self.whole_process_radio = QtWidgets.QRadioButton(u'UE全流程')
        self.semi_process_radio = QtWidgets.QRadioButton(u'UE半流程')
        self.unlock_normal_check = QtWidgets.QCheckBox(u'解锁法线（该选项只针对全流程）')
        self.smooth_check = QtWidgets.QCheckBox(u'是否平滑（该选项只针对半流程）')
        start_watch_button = QtWidgets.QPushButton(u'开启---自动保存')
        stop_watch_button = QtWidgets.QPushButton(u'关闭---自动保存')

        # 信号
        start_watch_button.clicked.connect(self.on_start_watch)
        stop_watch_button.clicked.connect(self.on_stop_watch)

        # 布局
        export_layout = QtWidgets.QHBoxLayout()
        export_layout.addWidget(export_label)
        export_layout.addWidget(self.export_ue_check)
        export_layout.addWidget(self.export_xgen_check)
        self.export_ue_check.setChecked(True)

        ue_process_layout = QtWidgets.QHBoxLayout()
        ue_process_layout.addWidget(ue_process_label)
        ue_process_layout.addWidget(self.whole_process_radio)
        ue_process_layout.addWidget(self.semi_process_radio)
        self.whole_process_radio.setChecked(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.state_label)
        layout.addWidget(Line(1, 1, self))
        layout.addLayout(export_layout)
        layout.addLayout(ue_process_layout)
        layout.addWidget(Line(1, 1, self))
        layout.addWidget(self.unlock_normal_check)
        layout.addWidget(self.smooth_check)
        layout.addWidget(start_watch_button)
        layout.addWidget(stop_watch_button)

        self.init_plugins()
        self.watcher = None

    @staticmethod
    def init_plugins():
        """
        初始化插件
         - fbxmaya
         - xgenToolkit
        """
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            cmds.loadPlugin('fbxmaya')

        if not cmds.pluginInfo('xgenToolkit', query=True, loaded=True):
            cmds.loadPlugin('xgenToolkit')

    def on_start_watch(self):
        """
        start_watch_button 点击事件，开启监听
        """
        if not self.watcher:
            self.watcher = Watcher(self.export_ue_check, self.export_xgen_check, 
                                   self.whole_process_radio, self.semi_process_radio, 
                                   self.unlock_normal_check, self.smooth_check)
            self.watcher.start()
            self.state_label.setText(u'当前状态: 开启')
            logging.info(u'已开启自动保存, script job id: {}'.format(self.watcher.script_jobs))

    def on_stop_watch(self):
        """
        stop_watch_button 点击事件，停止监听
        """
        if isinstance(self.watcher, Watcher):
            self.watcher.stop()
            self.state_label.setText(u'当前状态: 关闭')
            logging.info(u'已关闭自动保存')
            self.watcher = None
    
    def on_export_xgen(self):
        """
        export_xgen_button 点击事件, 导出XGen
        """

        logging.info(u'正在导出XGen...')

    def closeEvent(self, event):
        """
        关闭窗口事件
        """
        self.on_stop_watch()
        event.accept()


def main():
    ptr = omui.MQtUtil.mainWindow()
    parent = wrapInstance(int(ptr), QtWidgets.QWidget)

    WINDOW_NAME = 'AutoSaveSKWindow'

    # 判断窗口是否存在
    if hasattr(parent, WINDOW_NAME) and getattr(parent, WINDOW_NAME) is not None:
        getattr(parent, WINDOW_NAME).raise_()
        getattr(parent, WINDOW_NAME).showNormal()
    else:
        dlg = Window(parent)
        setattr(parent, WINDOW_NAME, dlg)
        # 关闭时销毁
        dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        dlg.destroyed.connect(lambda: setattr(parent, WINDOW_NAME, None))
        dlg.show()


if __name__ == '__main__':
    main()
