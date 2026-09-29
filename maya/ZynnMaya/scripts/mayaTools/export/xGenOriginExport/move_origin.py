# -*- coding:utf-8 -*-

"""
移动原点
"""

import maya.cmds as cmds


def create_binder(node, joint):
    def _is_have_blend_shape(history):
        blend_shapes = cmds.ls(history, type='blendShape')
        if blend_shapes:
            targets = cmds.blendShape(blend_shapes[0], q=True, t=True)
            deduplication_targets = set(targets)
            if len(deduplication_targets) > 1:
                target_parents = cmds.listRelatives(targets[0], p=True, f=True)
                if 'TouPi' in target_parents[0]:
                    return None
                else:
                    return target_parents[0]
            elif len(deduplication_targets) == 1:
                if 'TouPi' in targets[0]:
                    return None
                else:
                    return targets[0]
            else:
                return None

    def _is_have_wrap(history):
        wraps = cmds.ls(history, type='wrap')
        if wraps:
            wrap_driver = cmds.listConnections('{}.driverPoints'.format(wraps[0]), s=True, d=False)[0]
            if 'TouPi' in wrap_driver:
                return None
            else:
                return wrap_driver
        else:
            return None
    
    if '_BD' in node:
        return [GroomGuideBinder(node, joint)]

    # 以下是导线操作
    node_children = cmds.listRelatives(node, c=1, f=1)
    # 取一条曲线的构建历史
    history = cmds.listHistory(node_children[0])
    blend_shape = _is_have_blend_shape(history)
    wrap_driver = _is_have_wrap(history)

    if not blend_shape and not wrap_driver:
        return [GroomGuideBinder(node, joint)]

    if blend_shape and not wrap_driver:
        return [GroomGuideBinder(node, joint), GroomGuideBinder(blend_shape, joint)]
    
    if not blend_shape and wrap_driver:
        return [GroomGuideBinder(wrap_driver, joint)]
    
    if blend_shape and wrap_driver:
        return [GroomGuideBinder(blend_shape, joint), GroomGuideBinder(wrap_driver, joint)]


class GroomGuideBinder():
    """
    用于将导线或毛发组绑定至骨骼  
    提供以下功能: 

        - 移动至世界坐标原点
        - 复原位置
    """
    def __init__(self, node, joint):
        """
        :param rotate_node: 需要旋转的节点
        :type rotate_node: str
        :param connect_nodes: 需要连接的节点列表
        :type connect_nodes: list
        :param joint: 需要绑定的骨骼节点
        :type joint: str
        """
        self.node = node
        self.joint = joint
        
        self.is_move = False
        self.matrix = None
        self.matrix_locator = None
        self.driver_group = None
        self._init_driver()

    def _init_driver(self):
        # 创建驱动组
        self.transform_group = cmds.group(em=1, name='{}'.format(self.node + '_transform'))
        self.rotate_group = cmds.group(self.transform_group, name='{}'.format(self.node + '_rotate'))
        self.driver_group = cmds.group(self.rotate_group, name='{}'.format(self.node + '_driver'))

        # 创建约束定位器
        constraint_locator_name = '{}_constraint_locator'.format(self.node)
        self.constraint_locator = cmds.spaceLocator(name=constraint_locator_name, position=[0,0,0], absolute=True)[0]
        cmds.parent(self.constraint_locator, self.transform_group)
        cmds.parentConstraint(self.constraint_locator, self.node, mo=1, w=1)

        # 创建矩阵分解
        matrix_name = '{}_{}_matrix'.format(self.joint, self.node)
        self.matrix = cmds.createNode('decomposeMatrix', n=matrix_name)

        # 创建矩阵分解定位器
        matrix_locator_name = '{}_{}_matrix_locator'.format(self.joint, self.node)
        self.matrix_locator = cmds.spaceLocator(name=matrix_locator_name, position=[0,0,0], absolute=True)[0]
        cmds.parent(self.matrix_locator, self.driver_group)

        # 构建空间驱动
        cmds.parentConstraint(self.joint, self.matrix_locator, mo=0, w=1)
        cmds.connectAttr('{}.worldInverseMatrix[0]'.format(self.matrix_locator),
                         '{}.inputMatrix'.format(self.matrix), f=1)

    def move_to_locator(self):
        """
        将节点移动到定位器位置
        """
        cmds.connectAttr('{}.outputTranslate'.format(self.matrix), 
                         '{}.translate'.format(self.transform_group), f=1)
        cmds.connectAttr('{}.outputRotate'.format(self.matrix), 
                         '{}.rotate'.format(self.transform_group), f=1)
        
        cmds.setAttr('{}.rotateX'.format(self.rotate_group), 90)
        cmds.setAttr('{}.rotateZ'.format(self.rotate_group), 90)

        self.is_move = True

    def restore_node_position(self):
        """
        恢复节点位置
        """
        cmds.setAttr('{}.rotateX'.format(self.rotate_group), 0)
        cmds.setAttr('{}.rotateZ'.format(self.rotate_group), 0)

        cmds.disconnectAttr('{}.outputTranslate'.format(self.matrix), 
                            '{}.translate'.format(self.transform_group))
        cmds.disconnectAttr('{}.outputRotate'.format(self.matrix), 
                            '{}.rotate'.format(self.transform_group))
        cmds.xform(self.transform_group, ws=True, t=(0, 0, 0), ro=(0, 0, 0))

        self.is_move = False

    def close(self):
        """
        关闭绑定器
        """
        if self.is_move:
            self.restore_node_position()
        if self.matrix:
            cmds.delete(self.matrix)
        if self.matrix_locator:
            cmds.delete(self.matrix_locator)
        if self.driver_group:
            cmds.delete(self.driver_group)
    
    def __repr__(self):
        return 'GroomGuideBinder(node={}, joint={})'.format(self.node, self.joint)


if __name__ == '__main__':
    joint_head = 'Head_M'
    # joint_head = 'DouZhanLong_ErShiSui_CH:Head_M'

    binders = []
    binder_nodes = set()
    xgen_groups = cmds.ls('*_BD')
    # xgen_groups = cmds.ls('DouZhanLong_ErShiSui_CH:*_BD')
    for xgen_group in xgen_groups:
        if 'Hair01' not in xgen_group:
            continue
        binder_nodes.add((xgen_group, joint_head))
        xgen_nodes = cmds.listRelatives(xgen_group, c=1)
        for xgen in xgen_nodes:
            guide = cmds.listConnections(xgen + '.GuideGroupName')[0]
            binder_nodes.add((guide, joint_head))
    # 移动至世界坐标原点
    for binder_node in binder_nodes:
        binders.extend(create_binder(*binder_node))
    for binder in binders:
        binder.move_to_locator()

    for binder in binders:
        binder.close()
