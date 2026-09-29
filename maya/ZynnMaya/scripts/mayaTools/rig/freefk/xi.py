# -*-coding:utf-8 -*-

from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import maya.cmds as cmds
def scin(input001, output, sin=False, cos=True, valueScale=1):
    inp_name= input001.split('.')
    if output:
        out_name= output.split('.')
        eulerToQuat001=cmds.createNode('eulerToQuat',name='eulq_{}_to_{}'.format(inp_name[0],out_name[0]))
        multDoubleLinear001=cmds.createNode('multDoubleLinear', name='mult_{}_{}'.format(inp_name[0],out_name[0]))
        cmds.setAttr(multDoubleLinear001 + '.input1', 180 / valueScale)
        cmds.connectAttr(input001, multDoubleLinear001 + '.input2')
        if sin:
            cmds.connectAttr(multDoubleLinear001 + '.output', eulerToQuat001 + '.inputRotateX')
            cmds.connectAttr(eulerToQuat001 + '.outputQuatX', output)
            return eulerToQuat001 + '.outputQuatX'
        elif cos:
            cmds.connectAttr(multDoubleLinear001 + '.output', eulerToQuat001 + '.inputRotateY')
            cmds.connectAttr(eulerToQuat001 + '.outputQuatW', output)
            return eulerToQuat001 + '.outputQuatW'
    else:
        eulerToQuat001 = cmds.createNode('eulerToQuat', name='eulq_{}'.format(inp_name[0]))
        multDoubleLinear001 = cmds.createNode('multDoubleLinear', name='mult_{}'.format(inp_name[0]))
        cmds.setAttr(multDoubleLinear001 + '.input1', 180 / valueScale)
        cmds.connectAttr(input001, multDoubleLinear001 + '.input2')
        if sin:
            cmds.connectAttr(multDoubleLinear001 + '.output', eulerToQuat001 + '.inputRotateX')
            return eulerToQuat001 + '.outputQuatX'
        elif cos:
            cmds.connectAttr(multDoubleLinear001 + '.output', eulerToQuat001 + '.inputRotateY')
            return eulerToQuat001 + '.outputQuatW'


