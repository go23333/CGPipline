# -*- coding: utf-8 -*-

import os
import logging

import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMayaUI as omui

from shiboken2 import wrapInstance
from PySide2 import QtCore, QtWidgets


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
    def __init__(self, adv_tree, sy_group_trees=[], sk_group_trees=[], remove_trees=[]):
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
        self.remove_trees = remove_trees
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

        # 记录移除的模型
        remove_trees = []
        remove_rules = ['*_hair_Gro', '*eye*', '*teeth*', '*tongue', '*saliva']
        remove_transforms = [i for rule in remove_rules for i in cmds.ls(rule, type='transform', long=True)]
        for remove_transform in remove_transforms:
            if 'Geometry' in remove_transform:
                remove_transform_tree = cls._node_tree_info(remove_transform)
                remove_trees.append(remove_transform_tree)

        return cls(adv_tree, sy_group_trees, sk_group_trees, remove_trees)
    
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
    
    def _set_normal(self):
        if not cmds.objExists(self.switch_con):
            cmds.warning(u'未找到切换节点: {}'.format(self.switch_con))

        enum_str = cmds.attributeQuery('Enable_Overrides', node=self.switch_con, listEnum=True)
        enum_list = enum_str[0].split(':')
        
        target_value = enum_list.index('Normal')
        current_value = cmds.getAttr('{}.Enable_Overrides'.format(self.switch_con))
        if current_value != target_value:
            cmds.setAttr('{}.Enable_Overrides'.format(self.switch_con), target_value)
    
    def _export(self, save_path, export_node, node_trees):
        try:
            self._set_parent_world(node_trees)
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
            logging.info(u'已保存UE资产: {}'.format(save_path))
        except Exception as e:
            logging.critical(u'导出UE资产失败, {}'.format(e))
        finally:
            self._restore_parent(node_trees)
    
    def export_fbx(self):
        """
        保存 fbx 文件
        """
        if self.get_project() == 'SSDSY_CS':
            prefix = 'UE'
        else:
            prefix = 'SK'

        if 'ADV_Body:pelvis' in self.adv_tree['node']:
            node_trees = [self.adv_tree] + self.sy_group_trees
        else:
            node_trees = self.sy_group_trees
        self._set_normal()
        self._set_parent_world(node_trees)

        # 有SK
        save_path = os.path.join(self.get_folder(), '{}_{}_Hight.fbx'.format(prefix, self.get_character_name()))
        self._export(save_path, self.export_nodes, [])
        
        # 无SK
        save_path = os.path.join(self.get_folder(), '{}_{}_NoSkHight.fbx'.format(prefix, self.get_character_name()))
        self._export(save_path, self.export_nodes, self.sk_group_trees)

        self._restore_parent(node_trees)


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle(u'UE资产导出')
        self.setFixedSize(400, 150)
        self.setWindowFlags(QtCore.Qt.Window | 
                            QtCore.Qt.WindowMinimizeButtonHint | 
                            # QtCore.Qt.WindowMaximizeButtonHint | 
                            QtCore.Qt.WindowCloseButtonHint)
        
        self.file_info = None
        self.update_file_info()
        project_label = QtWidgets.QLabel(u'当前项目：{}'.format(self.file_info.get_project()))

        smooth_label = QtWidgets.QLabel(u'平滑等级：')
        self.smooth_spin = QtWidgets.QSpinBox()
        self.smooth_spin.setFixedWidth(60)
        self.smooth_spin.setRange(0, 6)
        self.smooth_spin.setValue(1)
        
        self.smooth_widget = QtWidgets.QWidget()
        smooth_widget_layout = QtWidgets.QHBoxLayout(self.smooth_widget)
        smooth_widget_layout.addWidget(smooth_label)
        smooth_widget_layout.addWidget(self.smooth_spin)

        self.smooth_check = QtWidgets.QCheckBox(u'导出前smooth选中的节点')
        self.smooth_check.setFixedHeight(45)
        self.smooth_check.setChecked(True)

        export_botton = QtWidgets.QPushButton(u'导出')
        open_folder = QtWidgets.QPushButton(u'打开导出目录')

        smooth_layout = QtWidgets.QHBoxLayout()
        smooth_layout.addWidget(self.smooth_check)
        smooth_layout.addStretch()
        smooth_layout.addWidget(self.smooth_widget)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(project_label)
        main_layout.addLayout(smooth_layout)
        main_layout.addWidget(export_botton)
        main_layout.addWidget(open_folder)

        self.smooth_check.toggled.connect(self.smooth_widget.setVisible)
        export_botton.clicked.connect(self.on_export)
        open_folder.clicked.connect(lambda : self.update_file_info(True))
    
    def on_export(self):
        if self.smooth_check.isChecked():
            select_nodes = cmds.ls(sl=1, type='transform')
            divisions = self.smooth_spin.value()
            smooth(select_nodes, divisions)
        
        character_sk = CharacterSkeletalMesh.init_node()
        character_sk.export_fbx()
        QtWidgets.QMessageBox.information(self, u'结果', u'导出完成！')
    
    def update_file_info(self, clicked=False):
        self.file_info = FileInfo()
        if not self.file_info.file_path:
            cmds.error(u'无法识别项目，请在标准目录中打开！')
        
        if clicked:
            os.startfile(self.file_info.get_folder())


def smooth(nodes, divisions):
    cmds.waitCursor(state=True)        
    for node in nodes:
        print(node)
        cmds.polySmooth(node, dv=divisions)
        cmds.bakePartialHistory(node, prePostDeformers=True)
    cmds.waitCursor(state=False)


def showUI():
    ptr = omui.MQtUtil.mainWindow()
    parent = wrapInstance(int(ptr), QtWidgets.QWidget)

    WINDOW_NAME = 'UEAssetExport'

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
    showUI()
