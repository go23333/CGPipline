# -*- coding: utf-8 -*-

from collections import defaultdict

import maya.cmds as cmds
import maya.api.OpenMaya as om

from zynn_check.core.check import Check, register
from zynn_check.core.utils import get_node_name, names_to_uuids


def _fix_hard_edge(errors):
    uuids = errors['uuids']
    for uuid in uuids.keys():
        node_name = get_node_name(uuid)
        cmds.polySoftEdge(node_name, angle=180, constructionHistory=False)


def _fix_locked_normal(errors):
    uuids = errors['uuids']
    for uuid in uuids.keys():
        node_name = get_node_name(uuid)
        cmds.polyNormalPerVertex(node_name, unFreezeNormal=True)
        cmds.bakePartialHistory(node_name, prePostDeformers=True)


@register
class FreeVertex(Check):
    name = 'free_vertex'
    label = u"游离点"
    category = u"拓扑"
    check_type = 'mesh_vertex'
    result_type = 'vertex'
    stages = ['model']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, _, uuid, vertexIt, vertex_index):
        if vertexIt.numConnectedEdges() == 0:
            self.errors[uuid].append(vertex_index)


@register
class YAxisNegative(Check):
    name = 'y_axis_negative'
    label = u"负Y值点"
    category = u"拓扑"
    check_type = 'mesh_vertex'
    result_type = 'vertex'
    stages = ['model']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, _, uuid, vertexIt, vertex_index):
        position = vertexIt.position()
        if position[1] < -0.001:
            self.errors[uuid].append(vertex_index)


@register
class HardEdges(Check):
    name = 'hardEdges'
    label = u"硬边"
    category = u"拓扑"
    check_type = 'mesh_edge'
    result_type = 'edge'
    stages = ['model']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, _, uuid, edgeIt, edge_index):
        if not edgeIt.isSmooth and not edgeIt.onBoundary():
            self.errors[uuid].append(edge_index)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        _fix_hard_edge(errors)


@register
class NoneManifoldEdges(Check):
    name = 'noneManifoldEdges'
    label = u"非流形边"
    category = u"拓扑"
    check_type = 'mesh_edge'
    result_type = 'edge'
    stages = ['model']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, _, uuid, edgeIt, edge_index):
        if edgeIt.numConnectedFaces() > 2:
            self.errors[uuid].append(edge_index)


@register
class OpenEdges(Check):
    name = 'openEdges'
    label = u"单个未缝合面"
    category = u"拓扑"
    check_type = 'mesh_edge'
    result_type = 'edge'
    stages = ['model']

    ignores = ['hair', 'eyelash']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, dagPath, uuid, edgeIt, edge_index):
        if any(key in dagPath.fullPathName() for key in self.ignores):
            return

        if edgeIt.numConnectedFaces() < 2:
            visited = {edge_index}
            stack = list(edgeIt.getConnectedEdges())

            while stack:
                if len(visited) > 4:
                    break
                edge_id = stack.pop()
                if edge_id in visited:
                    continue

                old_index = edgeIt.index()
                edgeIt.setIndex(edge_id)
                if edgeIt.numConnectedFaces() < 2:
                    visited.add(edge_id)
                    stack.extend(
                        edge for edge in edgeIt.getConnectedEdges()
                        if edge not in visited
                    )
                edgeIt.setIndex(old_index)

            if len(visited) <= 4:
                self.errors[uuid].append(edge_index)


@register
class Ngons(Check):
    name = 'ngons'
    label = u"多边面"
    category = u"拓扑"
    check_type = 'mesh_face'
    result_type = 'face'
    stages = ['model']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, _, uuid, faceIt, face_index):
        if len(faceIt.getEdges()) > 4:
            self.errors[uuid].append(face_index)


@register
class Lamina(Check):
    name = 'lamina'
    label = u"层叠面"
    category = u"拓扑"
    check_type = 'mesh_face'
    result_type = 'face'
    stages = ['model']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, _, uuid, faceIt, face_index):
        if faceIt.isLamina():
            self.errors[uuid].append(face_index)


@register
class HairFaceCount(Check):
    name = 'hair_face_count'
    label = u"毛发面数"
    category = u"拓扑"
    check_type = 'scene'
    result_type = 'text'
    stages = ['model']

    def run(self):
        face_count = 0
        hairs = cmds.ls(['*hair*'], type='mesh')
        for hair in hairs:
            face = cmds.polyEvaluate(hair, face=True)
            face_count += face
        if face_count > 100000:
            self.errors.append(u'毛发总面数大于10万面, 共 {} 面'.format(face_count))


@register
class LipsClosed(Check):
    name = 'lips_closed'
    label = u"嘴唇闭合"
    category = u"拓扑"
    check_type = 'mesh_face'
    result_type = 'face'
    # stages = ['model-half']

    up_lip_faces = [1297, 2733, 1296, 1306, 1308, 2709, 1307, 1250, 4208, 4265, 5667, 4266, 4264, 4254, 5691, 4255]
    down_lip_faces = [1370, 1417, 1418, 1419, 1420, 1451, 1452, 1457, 4415, 4410, 4409, 4378, 4377, 4376, 4375, 4328]

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)
        self.up_lip = {}
        self.down_lip = {}
        bodys = cmds.ls('|*body*')
        self.bodys_uuid = names_to_uuids(bodys)

    def run(self, _, uuid, faceIt, face_index):
        if not self.bodys_uuid:
            return
        if self.bodys_uuid[0] != uuid:
            return
        if self.errors:
            return

        if face_index in self.up_lip_faces:
            self.up_lip[face_index] = faceIt.center()
        if face_index in self.down_lip_faces:
            self.down_lip[face_index] = faceIt.center()

        if len(self.up_lip_faces) == len(self.up_lip) and len(self.down_lip_faces) == len(self.down_lip):
            for up_face_id, down_face_id in zip(self.up_lip_faces, self.down_lip_faces):
                if self.up_lip[up_face_id][1] > self.down_lip[down_face_id][1]:
                    self.errors[uuid].append(up_face_id)
                    self.errors[uuid].append(down_face_id)


@register
class EyeLocatorCenter(Check):
    name = 'eye_locator_center'
    label = u"眼球定位器"
    category = u"拓扑"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model-half']

    def run(self):
        eye_locators = cmds.ls('*eye*', type='locator')
        if not eye_locators:
            return

        for locator in eye_locators:
            locator_position = [round(cmds.getAttr('{}.localPosition{}'.format(locator, i)), 3)
                                for i in ['X', 'Y', 'Z']]

            locator_parent = cmds.listRelatives(locator, p=1)[0]
            eye_nodes = cmds.listRelatives(locator_parent, c=1, type='transform')
            eye_bbox = cmds.exactWorldBoundingBox(eye_nodes)
            eye_center = [
                round((eye_bbox[0] + eye_bbox[3]) * 0.5, 3),
                round((eye_bbox[1] + eye_bbox[4]) * 0.5, 3),
                round((eye_bbox[2] + eye_bbox[5]) * 0.5, 3),
            ]

            if locator_position != eye_center:
                self.errors.append(locator_parent)

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        for locator in errors:
            locator_shape = cmds.listRelatives(locator, shapes=True, noIntermediate=True)[0]
            eye_nodes = cmds.listRelatives(locator, c=1, type='transform')
            eye_bbox = cmds.exactWorldBoundingBox(eye_nodes)
            eye_center = [
                round((eye_bbox[0] + eye_bbox[3]) * 0.5, 3),
                round((eye_bbox[1] + eye_bbox[4]) * 0.5, 3),
                round((eye_bbox[2] + eye_bbox[5]) * 0.5, 3),
            ]
            for axis, value in zip(['X', 'Y', 'Z'], eye_center):
                cmds.setAttr('{}.localPosition{}'.format(locator_shape, axis), value)


@register
class FitDefaultGird(Check):
    name = 'fit_default_gird'
    label = u"贴合十字网格"
    category = u"拓扑"
    check_type = 'scene'
    result_type = 'node'
    stages = ['model']

    def prepare(self):
        self.context['results'][self.name] = {}
        self.tolerance = 0.01       # 与十字网格(y=0)的容差

    def run(self):
        model_groups = cmds.ls('*_Mo', type='transform', long=True) or []
        if not model_groups:
            return

        if len(model_groups) > 1:
            for model_group in model_groups:
                self.errors[model_group] = u"存在多个_Mo组，请手动修复"
            return

        model_group = model_groups[0]
        # 十字网格即世界 y=0 平面，取模型组包围盒的最低点
        min_y = cmds.exactWorldBoundingBox(model_group)[1]
        if min_y < -self.tolerance:
            self.errors[model_group] = u"低于十字网格，最低点y={}".format(round(min_y, 4))
        elif min_y > self.tolerance:
            self.errors[model_group] = u"未贴合十字网格，最低点y={}".format(round(min_y, 4))

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        model_group = errors[0]
        min_y = cmds.exactWorldBoundingBox(model_group)[1]
        # 世界Y方向整体平移，使模型组最低点落在十字网格(y=0)上
        cmds.move(0, -min_y, 0, model_group, relative=True)


@register
class LockedNormal(Check):
    name = 'locked_normal'
    label = u"锁定法线"
    category = u"拓扑"
    check_type = 'mesh_face'
    result_type = 'face'
    stages = ['model', 'shading']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(list)

    def run(self, dagPath, uuid, faceIt, face_index):
        mesh_fn = om.MFnMesh(dagPath)
        for local_index in range(faceIt.polygonVertexCount()):
            normal_id = faceIt.normalIndex(local_index)
            if mesh_fn.isNormalLocked(normal_id):
                self.errors[uuid].append(face_index)
                break

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        _fix_locked_normal(errors)


@register
class RigLockedNormal(Check):
    name = 'rig_locked_normal'
    label = u"锁定法线"
    category = u"拓扑"
    check_type = 'scene'
    result_type = 'node'
    stages = ['rig-all']

    def prepare(self):
        self.context['results'][self.name] = defaultdict(str)

    def run(self):
        node_name = cmds.ls('head_lod0_mesh')
        if not node_name:
            return

        node_name = node_name[0]
        verts = cmds.polyListComponentConversion(node_name, toVertex=True)
        if not verts:
            self.errors[node_name] = u'该模型没有顶点'
            return

        normals = cmds.polyNormalPerVertex(verts, query=True, freezeNormal=True)
        if any(normals):
            self.errors[node_name] = u'顶点法线锁定'
            return

    def fix(self, errors=None):
        errors = self.selectable() if errors is None else errors
        cmds.setAttr('ctrlEye_L.blink', 10)
        cmds.setAttr('ctrlEye_R.blink', 10)
        cmds.polyNormalPerVertex(errors[0], unFreezeNormal=True)
        cmds.bakePartialHistory(errors[0], prePostDeformers=True)
        cmds.setAttr('ctrlEye_L.blink', 0)
        cmds.setAttr('ctrlEye_R.blink', 0)
