# -*- coding: utf-8 -*-

import re
import math
from collections import defaultdict

import maya.cmds as cmds
import maya.api.OpenMaya as om

from zynn_check.core.check import Check, register
from zynn_check.core.utils import get_node_name


@register
class SelfPenetratingUVs(Check):
    name = 'selfPenetratingUVs'
    label = u"UV重叠"
    category = u"UV"
    check_type = 'transform'
    result_type = 'face'
    # stages = ['shading']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        shapes = cmds.listRelatives(node_name, shapes=True, type="mesh", noIntermediate=True)
        if shapes:
            overlapping = cmds.polyUVOverlap('{}.f[*]'.format(shapes[0]), oc=True)
            if overlapping:
                formatted = [
                    re.search('\\[(\\d+)\\]', overlap).group(1)
                    for overlap in overlapping
                ]
                self.errors[node_uuid].extend(formatted)


@register
class MissingUVs(Check):
    name = 'missingUVs'
    label = u"UV缺失"
    category = u"UV"
    check_type = 'mesh_face'
    result_type = 'face'
    stages = ['shading']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, _, uuid, faceIt, face_index):
        if faceIt.hasUVs() is False:
            self.errors[uuid].append(face_index)


@register
class UvRange(Check):
    name = 'uvRange'
    label = u"UV范围"
    category = u"UV"
    check_type = 'mesh'
    result_type = 'uv'
    # stages = ['shading']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        sl_mesh = om.MSelectionList()
        sl_mesh.add(node_name)
        dag_path = sl_mesh.getDagPath(0)
        mesh = om.MFnMesh(dag_path)
        Us, Vs = mesh.getUVs()
        for i in range(len(Us)):
            if Us[i] < 0 or Vs[i] < 0:
                self.errors[node_uuid].append(i)


@register
class CrossBorder(Check):
    name = 'crossBorder'
    label = u"跨边界UV"
    category = u"UV"
    check_type = 'mesh_face'
    result_type = 'face'
    # stages = ['shading']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, _, uuid, faceIt, face_index):
        try:
            UVs = faceIt.getUVs()
            U, V = set(), set()
            Us, Vs = UVs[0], UVs[1]
            for i in range(len(Us)):
                uTile = math.floor(Us[i])
                vTile = math.floor(Vs[i])
                U.add(uTile)
                V.add(vTile)
            if len(U) > 1 or len(V) > 1:
                self.errors[uuid].append(face_index)
        except RuntimeError:
            pass


@register
class OnBorder(Check):
    name = 'onBorder'
    label = u"边界线UV"
    category = u"UV"
    check_type = 'mesh'
    result_type = 'uv'
    # stages = ['shading']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        if not node_name:
            return
        sl_mesh = om.MSelectionList()
        sl_mesh.add(node_name)
        dag_path = sl_mesh.getDagPath(0)
        mesh = om.MFnMesh(dag_path)
        Us, Vs = mesh.getUVs()
        for i in range(len(Us)):
            if abs(int(Us[i]) - Us[i]) < 0.00001 \
                    or abs(int(Vs[i]) - Vs[i]) < 0.00001:
                self.errors[node_uuid].append(i)


@register
class UvSet(Check):
    name = 'uv_set'
    label = u"uv集"
    category = u"UV"
    check_type = 'transform'
    result_type = 'node'
    # stages = ['shading']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        shapes = cmds.listRelatives(node_name, shapes=True, noIntermediate=True)
        uv_sets = cmds.polyUVSet(shapes, query=True, allUVSets=True)
        if shapes:
            rule = [u'map1', u'skinWeight'] if '_body' in shapes[0] else [u'map1']
            if uv_sets and uv_sets != rule:
                self.errors.append(node_uuid)


@register
class BodyUvHalf(Check):
    name = 'body_uv_half'
    label = u"人体uv"
    category = u"UV"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model-half']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        shapes = cmds.listRelatives(node_name, shapes=True, noIntermediate=True)
        if shapes and '_body' in shapes[0]:
            uv_sets = cmds.polyUVSet(shapes, query=True, allUVSets=True)
            if uv_sets and uv_sets != [u'map1', u'skinWeight']:
                self.errors.append(node_uuid)


@register
class BodyUvAll(Check):
    name = 'body_uv_all'
    label = u"人体uv"
    category = u"UV"
    check_type = 'transform'
    result_type = 'node'
    stages = ['model-all']

    def run(self, node_uuid):
        node_name = get_node_name(node_uuid)
        shapes = cmds.listRelatives(node_name, shapes=True, noIntermediate=True)
        if shapes and '_body' in shapes[0]:
            uv_sets = cmds.polyUVSet(shapes, query=True, allUVSets=True)
            if uv_sets and uv_sets != [u'map1']:
                self.errors.append(node_uuid)
