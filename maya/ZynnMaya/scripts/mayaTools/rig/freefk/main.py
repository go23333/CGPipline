# -*-coding:utf-8 -*-
from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import maya.cmds as cmds
def addAttr_nb(short_name, attr_list):
    matching_objs = cmds.ls(short_name, long=True)
    if not matching_objs:
        print("Warning: No objects found with the name '{}'.".format(short_name))
        return None
    full_attr_namesss = []
    for obj in matching_objs:
        cmds.select(obj)
        for attr_info in attr_list:
            attr_name, attr_type, attr_values = attr_info[:3]
            full_attr_name = "{}.{}".format(obj,attr_name)
            full_attr_namesss.append(full_attr_name)

            if attr_type == 'float':
                min_val, default_val, max_val, lock_attr = attr_values
                cmds.addAttr(ln=attr_name, at='float', min=min_val, max=max_val, dv=float(default_val), k=True)
                cmds.setAttr(full_attr_name, channelBox=True)
                cmds.setAttr(full_attr_name, keyable=lock_attr)

            elif attr_type == 'enum':
                enum_str = ':'.join(attr_values)
                cmds.addAttr(ln=attr_name, at='enum', en=enum_str)
                cmds.setAttr(full_attr_name, channelBox=True)
                cmds.setAttr(full_attr_name, lock=False)
            else:
                print("Warning: Unknown attribute type '{}' for '{}' on object '{}'.".format(attr_type,attr_name,obj))
    return full_attr_namesss
