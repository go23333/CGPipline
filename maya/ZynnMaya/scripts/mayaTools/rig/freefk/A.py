# -*-coding:utf-8 -*-

from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import maya.cmds as cmds

def create_flat_surface_from_joint_chain(bones,namm,axis_suf='z'):
    selected_joints = bones
    for bbb in selected_joints:
        if cmds.getAttr(bbb+'.rotate') != [(0.0, 0.0, 0.0)]:
            print('系统默认将{}骨骼链冻结变换了'.format(selected_joints[0]))
            cmds.makeIdentity(selected_joints[0], apply=True, translate=True, rotate=True, scale=True)

    if not selected_joints or len(selected_joints) < 2:
        cmds.error("请选择至少两个连续的骨骼")
        return

    for i in range(len(selected_joints) - 1):
        if cmds.listRelatives(selected_joints[i], children=True, type='joint')[0] != selected_joints[i + 1]:
            cmds.error("请选择一个连续的骨骼链")
            return
    joint_positions = [cmds.xform(joint, query=True, worldSpace=True, translation=True) for joint in selected_joints]
    offset = 2

    def get_joint_vector(joint, axis):
        joint_matrix = cmds.xform(joint, query=True, worldSpace=True, matrix=True)
        if axis == 'x' or axis =='X':
            return [joint_matrix[0], joint_matrix[1], joint_matrix[2]]
        elif axis == 'y'or axis =='Y':
            return [joint_matrix[4], joint_matrix[5], joint_matrix[6]]
        elif axis == 'z'or axis =='Z':
            return [joint_matrix[8], joint_matrix[9], joint_matrix[10]]
    another_positions = []
    for joint, pos in zip(selected_joints, joint_positions):
        y_vector = get_joint_vector(joint,axis_suf)
        another_pos = [pos[0] - y_vector[0] * offset, pos[1] - y_vector[1] * offset, pos[2] - y_vector[2] * offset]
        another_positions.append(another_pos)


    offset_positions = []
    for joint, pos in zip(selected_joints, joint_positions):
        y_vector = get_joint_vector(joint,axis_suf)
        offset_pos = [pos[0] + y_vector[0] * offset, pos[1] + y_vector[1] * offset, pos[2] + y_vector[2] * offset]
        offset_positions.append(offset_pos)
    curve = cmds.curve(degree=1, point=another_positions)
    offset_curve = cmds.curve(degree=1, point=offset_positions)
    loft_surface = cmds.loft(curve, offset_curve, name=namm, constructionHistory=False, uniform=True, close=False,autoReverse=True)[0]
    cmds.delete(curve, offset_curve)
    return loft_surface