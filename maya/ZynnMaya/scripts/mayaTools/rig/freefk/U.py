# -*-coding:utf-8 -*-

from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import maya.cmds as cmds

def get_object_type(selected_objects):
    obj_types = []

    print(selected_objects)
    if isinstance(selected_objects, list):
        for obj in selected_objects:

            if cmds.objectType(obj)=='joint':
                obj_type = 'joint'

                obj_types.append(obj_type)
                continue
            if cmds.objectType(obj) == 'boneDynamicsNode':
                obj_type = 'boneDynamicsNode'
                obj_types.append(obj_type)
                continue
            objshape=cmds.listRelatives(obj, shapes=True)[0]
            obj_type = cmds.objectType(objshape)
            if obj_type == 'nurbsCurve':
                pass

            else:
                pass

            obj_types.append(obj_type)

        if not selected_objects:
            print('没有选择任何对象。')
    elif selected_objects:# 如果选择了单个对象

        if cmds.objectType(selected_objects) == 'joint':
            obj_type = 'joint'

            obj_types.append(obj_type)
        elif cmds.objectType(selected_objects) == 'boneDynamicsNode':
            obj_type = 'boneDynamicsNode'
            obj_types.append(obj_type)
        else:
            objshape = cmds.listRelatives(selected_objects, shapes=True)[0]
            obj_type = cmds.objectType(objshape)
            if obj_type == 'nurbsCurve':
                pass

            else:
                pass

            obj_types.append(obj_type)

    else:print('没有选择任何对象。')

    return obj_types

if __name__ == '__main__':

    selected_objects = cmds.ls(selection=True)
    print(get_object_type(selected_objects))