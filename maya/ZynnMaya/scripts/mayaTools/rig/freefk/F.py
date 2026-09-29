# -*-coding:utf-8 -*-

from __future__ import unicode_literals, print_function, division
import os
import json
import maya.cmds as cmds

def get_shape(part,name):
    shape_map = {
        "方块":"cube"
    }
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir,"ctrl_data", "{}.json".format(shape_map[part]))
    if not os.path.isfile(data_file):
        print('路径{}不存在'.format(data_file))
        pass
    else:
        with open(data_file, "r") as fp:

            ss=json.load(fp)

    for data in ss:

        curve_point = [[data["points"][i + j] for j in range(3)] for i in range(0, len(data["points"]), 3)]
        if data["periodic"]:
            curve_point = curve_point + curve_point[:data["degree"]]

        curve_degree =data["degree"]
        curve_knot = data["knot"]

    ctrl= cmds.curve(degree=curve_degree,point=curve_point,knot=curve_knot,name=name)
    ctrl_shape=cmds.listRelatives(ctrl,shapes=True)[0]
    ctrl_shape=cmds.rename(ctrl_shape,ctrl+'shape')
    cmds.makeIdentity(ctrl,apply=True,translate=True,rotate=True,scale=True)
    return ctrl, ctrl_shape
