# -*-coding:utf-8 -*-

from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import maya.cmds as cmds

def abs_connect(output_attr, connect_attr,add=True):
    global abs_last
    if connect_attr and connect_attr!=1:
        connect_attr_name = connect_attr.replace('.', '_')
    if isinstance(output_attr, list):
        sum_node = cmds.createNode('plusMinusAverage', name='sum_of_{}'.format('_'.join([attr.split('.')[-1] for attr in output_attr])))
        if add:
            cmds.setAttr(sum_node + '.operation', 1)  # 设置为加法
        else:
            cmds.setAttr(sum_node + '.operation', 2)  # 设置为减法
        for i, attr in enumerate(output_attr):
            cmds.connectAttr(attr, sum_node + '.input1D[' + str(i) + ']')

        output_attr = sum_node + '.output1D'

        output_attr_name = sum_node.split('|')[-1]  # 获取节点名称部分
    else:

        output_attr_name = output_attr.replace('.', '_')

    mult = cmds.createNode('multiplyDivide')
    condition = cmds.createNode('condition')
    if connect_attr and connect_attr!=1:
        mult = cmds.rename(mult, '{}_mult_{}'.format(output_attr_name, connect_attr_name))
        condition = cmds.rename(condition, '{}_condition_{}'.format(output_attr_name, connect_attr_name))
    else:
        mult = cmds.rename(mult, '{}_mult'.format(output_attr_name))
        condition = cmds.rename(condition, '{}_condition'.format(output_attr_name))

    cmds.setAttr(mult + '.input2X', -1)
    cmds.setAttr(condition + '.operation', 2)  # 设置为大于或等于
    cmds.setAttr(condition + '.secondTerm', 0)  # 设置第二个比较值为0

    cmds.connectAttr(output_attr, condition + '.firstTerm')
    cmds.connectAttr(output_attr, condition + '.colorIfTrueR')
    cmds.connectAttr(output_attr, mult + '.input1X')
    cmds.connectAttr(mult + '.outputX', condition + '.colorIfFalseR')
    abs_last = cmds.getAttr(condition + '.outColorR')
    if connect_attr and connect_attr!=1:
        cmds.connectAttr(condition + '.outColorR', connect_attr)
    elif connect_attr==1:
        pass
    else:
        cmds.delete(condition,mult)
    return condition