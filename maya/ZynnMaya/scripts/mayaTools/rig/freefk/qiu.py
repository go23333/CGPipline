# -*-coding:utf-8 -*-
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import maya.cmds as cmds
import maya.OpenMaya as om
def match_axes_and_position(rotobjed,source,axis_match=['xy','yx']):
    cmds.matchTransform(rotobjed, source, position=True, rotation=True)

    source_matrix = cmds.xform(source, query=True, worldSpace=True, matrix=True)

    source_x_axis = om.MVector(source_matrix[0], source_matrix[1], source_matrix[2])
    source_y_axis = om.MVector(source_matrix[4], source_matrix[5], source_matrix[6])
    source_Z_axis = om.MVector(source_matrix[8], source_matrix[9], source_matrix[10])
    source_translation = om.MVector(source_matrix[12], source_matrix[13], source_matrix[14])

    rotobjed_matrix = cmds.xform(rotobjed, query=True, worldSpace=True, matrix=True)

    rotobjed_x_axis = om.MVector(rotobjed_matrix[0], rotobjed_matrix[1], rotobjed_matrix[2])
    rotobjed_y_axis = om.MVector(rotobjed_matrix[4], rotobjed_matrix[5], rotobjed_matrix[6])
    rotobjed_z_axis = om.MVector(rotobjed_matrix[8], rotobjed_matrix[9], rotobjed_matrix[10])

    if axis_match == ['xy','yx']:

        new_matrix = [
            source_y_axis.x, source_y_axis.y, source_y_axis.z, 0,
            source_x_axis.x, source_x_axis.y, source_x_axis.z, 0,
            rotobjed_z_axis.x, rotobjed_z_axis.y, rotobjed_z_axis.z, 0,
            source_translation.x, source_translation.y, source_translation.z, 1]
    elif axis_match == ['xy','yz']:
        new_matrix = [
            source_y_axis.x, source_y_axis.y, source_y_axis.z, 0,
            source_Z_axis.x, source_Z_axis.y, source_Z_axis.z, 0,
            rotobjed_x_axis.x, rotobjed_x_axis.y, rotobjed_x_axis.z, 0,
            source_translation.x, source_translation.y, source_translation.z, 1]

    cmds.xform(rotobjed, worldSpace=True, matrix=new_matrix)
    print("{} 的x轴已匹配 {} 的y轴，同时 {} 的y轴已匹配 {} 的x轴，并且位置已匹配".format(rotobjed,source,rotobjed,source))




