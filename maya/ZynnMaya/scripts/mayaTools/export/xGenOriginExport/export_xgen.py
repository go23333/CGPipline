# -*- coding:utf-8 -*-

"""
将 Maya XGen 交互式毛发 / nurbsCurve 导出为 Alembic 缓存文件 (.abc)
"""

import json
import zlib
import array
import imath
import struct
import numbers

from collections import OrderedDict

import xgenm as xg

import maya.mel as mel
import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as omAnim

import alembic.Abc as abc
import alembic.AbcGeom as abcGeom
import alembic.AbcCoreAbstract as abcA


# ===========================================================================
# 工具函数
# ===========================================================================

def _list_to_imath_array(lst, arr_type):
    """将 Python list 转为 Alembic 所需的 imath 数组 (V3fArray / FloatArray / ...)"""
    arr = arr_type(len(lst))
    for i, val in enumerate(lst):
        arr[i] = val
    return arr


def _float_list_to_v3f_array(floats):
    """将扁平化的 float list (xyzxyz...) 转为 imath.V3fArray"""
    count = len(floats) // 3
    arr = imath.V3fArray(count)
    for i in range(count):
        arr[i].x = floats[i * 3]
        arr[i].y = floats[i * 3 + 1]
        arr[i].z = floats[i * 3 + 2]
    return arr


def _build_knots(num_cvs, degree=3):
    """
    构建 Nurbs 曲线的节点向量 (knot vector)

    标准均匀 B-spline 节点序列:
      degree 个 0.0 + [0, 1, 2, ...] + degree 个 max
    """
    inside_count = num_cvs - degree + 1
    knots = [0.0] * degree + list(range(inside_count)) + [inside_count - 1.0] * degree
    return knots


# ===========================================================================
# CurvesProxy - 将 Maya nurbsCurve 导出为 Alembic 曲线
#
# Alembic 结构:
#   OCurves
#     ├── schema (OCurvesSchema)        ← 曲线几何 (位置/阶数/节点/顶点数)
#     └── arbGeomParams                 ← 自定义属性 (groom_group_name / group_id / ...)
# ===========================================================================

class CurvesProxy(object):
    CURVE_DEGREE = 3
    CURVE_ORDER = CURVE_DEGREE + 1

    def __init__(self, curve_obj, fn_dep_node, need_bake_uv=False, animation=False, bake_mesh=None, uv_set=None):
        """
        Args:
            curve_obj: alembic.AbcGeom.OCurves — Alembic 曲线对象
            fn_dep_node: MFnDependencyNode     — 场景中的 nurbsCurve 变换节点
            need_bake_uv: 是否烘焙根部 UV 到 arbGeomParams
            animation: 是否逐帧导出 (False=仅首帧)
            bake_mesh: MFnMesh                  — 用于 UV 烘焙的网格
            uv_set: str                         — UV 集名称
        """
        # OCurves.getSchema() 返回 OCurvesSchema，是写入曲线数据的核心接口
        self.schema = curve_obj.getSchema()
        self.fn_dep_node = fn_dep_node
        self.need_bake_uv = need_bake_uv
        self.animation = animation
        self.bake_mesh = bake_mesh
        self.uv_set = uv_set

        # 缓存首帧的采样，后续帧可复用拓扑（顶点数 / 阶数 / 节点向量不变）
        self.first_sample = abcGeom.OCurvesSchemaSample()
        self.curve_dag_paths = None
        self.hair_root_list = None
        self.group_name = None

    # ---- 自定义属性写入 (ArbGeomParams) ----

    def write_group_name(self, group_name):
        """在 arbGeomParams 下写入 groom_group_name (字符串数组)"""
        arb_params = self.schema.getArbGeomParams()           # 获取 Arbitrary Geometry Parameters
        prop = abc.OStringArrayProperty(arb_params, "groom_group_name")  # 创建字符串数组属性
        prop.setValue(_list_to_imath_array([str(group_name)], imath.StringArray))
        self.group_name = group_name

    def write_is_guide(self, is_guide=True):
        """标记为导引线 (groom_guide = 1, int16)"""
        if not is_guide:
            return
        arb_params = self.schema.getArbGeomParams()
        prop = abc.OInt16ArrayProperty(arb_params, "groom_guide")
        prop.setValue(_list_to_imath_array([1], imath.ShortArray))

    def write_group_id(self, group_id):
        """写入分组 ID (groom_group_id, int32)"""
        arb_params = self.schema.getArbGeomParams()
        prop = abc.OInt32ArrayProperty(arb_params, "groom_group_id")
        prop.setValue(_list_to_imath_array([group_id], imath.IntArray))

    # ---- 曲线拓扑发现 ----

    def _discover_curves(self):
        """从场景中找出当前 transform 下的所有 nurbsCurve 形状"""
        full_path = self.fn_dep_node.name()
        curve_names = cmds.listRelatives(
            full_path, allDescendents=True, fullPath=True, type="nurbsCurve"
        ) or []

        dag_paths = []
        for name in curve_names:
            if not cmds.objExists(name):
                continue
            if cmds.getAttr(name + ".intermediateObject"):
                continue
            try:
                sel = om.MSelectionList()
                sel.add(name)
                dag_paths.append(sel.getDagPath(0))
            except RuntimeError:
                pass
        self.curve_dag_paths = dag_paths

    # ---- 帧数据写入 ----

    def write_first_frame(self):
        """写入首帧 (含拓扑定义: 顶点数 / 阶数 / 节点向量 / 位置)"""
        self._discover_curves()
        if not self.curve_dag_paths:
            return

        num_curves = len(self.curve_dag_paths)
        orders = imath.UnsignedCharArray(num_curves)
        num_vertices = imath.IntArray(num_curves)
        positions_flat = []
        all_knots = []

        if self.need_bake_uv:
            self.hair_root_list = []

        degree = self.CURVE_DEGREE
        order = self.CURVE_ORDER

        for i, dag_path in enumerate(self.curve_dag_paths):
            curve_fn = om.MFnNurbsCurve(dag_path)
            num_cvs = curve_fn.numCVs

            orders[i] = order
            num_vertices[i] = num_cvs

            # 读取世界空间 CV 位置
            cvs = curve_fn.cvPositions(om.MSpace.kWorld)
            for cv in cvs:
                positions_flat.append(cv.x)
                positions_flat.append(cv.y)
                positions_flat.append(cv.z)

            if self.need_bake_uv:
                self.hair_root_list.append(cvs[0])  # 根部 (首个 CV) 用于 UV 烘焙

            all_knots.extend(_build_knots(num_cvs, degree))

        # 组装 Alembic 采样
        samp = self.first_sample
        samp.setBasis(abcGeom.BasisType.kBsplineBasis)          # B-spline 基函数
        samp.setWrap(abcGeom.CurvePeriodicity.kNonPeriodic)     # 非周期 (开放曲线)
        samp.setType(abcGeom.CurveType.kCubic)                  # 三次曲线
        samp.setCurvesNumVertices(num_vertices)                  # 每条曲线的 CV 数量
        samp.setPositions(_float_list_to_v3f_array(positions_flat))  # 所有 CV 位置
        samp.setOrders(orders)                                   # 每条曲线的阶数 (次数+1)
        samp.setKnots(_list_to_imath_array(all_knots, imath.FloatArray))  # 节点向量

        # OCurvesSchema.set() 将采样写入 Alembic 归档
        self.schema.set(samp)

    def write_frame(self):
        """写入后续帧 (仅更新位置，复用首帧的拓扑)"""
        if not self.curve_dag_paths:
            return

        # 从首帧采样复制拓扑信息
        samp = abcGeom.OCurvesSchemaSample()
        samp.setBasis(self.first_sample.getBasis())
        samp.setWrap(self.first_sample.getWrap())
        samp.setType(self.first_sample.getType())
        samp.setCurvesNumVertices(self.first_sample.getCurvesNumVertices())
        samp.setOrders(self.first_sample.getOrders())
        samp.setKnots(self.first_sample.getKnots())

        positions_flat = []
        for dag_path in self.curve_dag_paths:
            curve_fn = om.MFnNurbsCurve(dag_path)
            cvs = curve_fn.cvPositions(om.MSpace.kWorld)
            for cv in cvs:
                positions_flat.append(cv.x)
                positions_flat.append(cv.y)
                positions_flat.append(cv.z)

        samp.setPositions(_float_list_to_v3f_array(positions_flat))
        self.schema.set(samp)

    # ---- UV 烘焙 ----

    def bake_uv(self):
        """将每根毛发的根部世界坐标投影到网格 UV，写入 groom_root_uv"""
        if self.hair_root_list is None or self.bake_mesh is None:
            return
        if self.uv_set is None:
            self.uv_set = self.bake_mesh.currentUVSetName()
        elif self.uv_set not in self.bake_mesh.getUVSetNames():
            raise ValueError("Invalid UV Set: {}".format(self.uv_set))

        uvs = imath.V2fArray(len(self.hair_root_list))
        for i, root_pt in enumerate(self.hair_root_list):
            # MFnMesh.getUVAtPoint(): 将世界空间点投影到网格并取 UV
            u, v = self.bake_mesh.getUVAtPoint(root_pt, om.MSpace.kWorld, uvSet=self.uv_set)
            uvs[i].x = u
            uvs[i].y = v

        arb_params = self.schema.getArbGeomParams()
        uv_prop = abc.OV2fArrayProperty(arb_params, "groom_root_uv")
        uv_prop.setValue(uvs)


# ===========================================================================
# XGenProxy - 将 XGen 交互式毛发导出为 Alembic 曲线
#
# 数据来源: XGen 的 outSplineData 属性 (MFnPluginData)
# 解析流程:
#   writeBinary() → parseBlocks → decompress (zlib) →
#   extract PrimitiveInfos / Positions / WIDTH_CV
# ===========================================================================

class XGenProxy(CurvesProxy):
    """
    XGen 样条线代理

    outSplineData 输出的位置为 Description 局部空间坐标,
    因此 OCurves 写入位置原值, OXform 负责将 Description
    的世界矩阵写入层级, 无需额外矩阵变换.
    """
    def __init__(self, curve_obj, fn_dep_node, need_bake_uv=False, animation=False, bake_mesh=None, uv_set=None):
        super(XGenProxy, self).__init__(curve_obj, fn_dep_node, need_bake_uv, animation, bake_mesh, uv_set)

    # ---- XGen 二进制数据解析 ----

    @staticmethod
    def _parse_blocks(raw_bytes):
        """
        解析 Alembic 插件数据中的块结构
        每个块: [type_code(u32) + padding(4) + data_size(u64) + data...]
        """
        blocks = []
        addr = 0
        max_blocks = 1000
        while addr < len(raw_bytes) - 1:
            type_code = struct.unpack("<I", raw_bytes[addr:addr + 4])[0]
            data_size = struct.unpack("<Q", raw_bytes[addr + 8:addr + 16])[0]
            start = addr + 16
            end = start + data_size
            blocks.append((start, end, type_code))
            addr = end
            if len(blocks) > max_blocks:
                break
        return blocks

    @staticmethod
    def _read_xgen_item(items_dict, raw_items):
        """从 JSON header 中解析数据索引 (group_idx, block_idx)"""
        for entry in raw_items:
            if not isinstance(entry, dict):
                continue
            for key, value in entry.items():
                if isinstance(value, (int, numbers.Integral)):
                    group_idx = value >> 32          # 高 32 位: 数据组索引
                    block_idx = value & 0xFFFFFFFF    # 低 32 位: 块内偏移
                    items_dict.setdefault(key, []).append((group_idx, block_idx))

    def _extract_xgen_data(self):
        """
        从 outSplineData 插件数据中提取:
          - PrimitiveInfos: 每条毛发的 (offset, length)
          - Positions:      CV 位置 (float array) — outSplineData 为 Description 局部空间
          - WIDTH_CV:       CV 宽度 (float array)
        """
        # 强制 XGen 重新计算样条线（解决移动 transform 后导出位置仍为旧位置的问题）
        shape_name = self.fn_dep_node.name()
        cmds.dgdirty(shape_name)
        # cmds.getAttr(shape_name + ".outSplineData")

        # 尝试通过 xgenm API 刷新（更可靠）
        if xg:
            try:
                desc_transform = cmds.listRelatives(shape_name, p=True)[0]
                palette = xg.palette(desc_transform)
                xg.palette(palette, refresh=True)
            except Exception:
                pass

        spline_plug = self.fn_dep_node.findPlug("outSplineData", False)
        data_handle = spline_plug.asMObject()
        plugin_data = om.MFnPluginData(data_handle).data()
        raw_bytes = plugin_data.writeBinary()  # 获取原始二进制数据

        # ---- 顶层块解析 ----
        top_blocks = self._parse_blocks(raw_bytes)
        header_block = top_blocks[0]           # 首个块包含 JSON header
        data_blocks = top_blocks[1:]           # 后续为数据块

        # ---- 读取 JSON header ----
        slice_data = raw_bytes[header_block[0]:header_block[1]]
        header_text = slice_data if isinstance(slice_data, str) else slice_data.decode("utf-8")
        header_info = json.loads(header_text)
        header = header_info["Header"]

        # ---- 提取数据索引 ----
        items = {}
        self._read_xgen_item(items, header_info.get("Items", []))
        self._read_xgen_item(items, header_info.get("RefMeshArray", []))

        # ---- 解压缩与数据提取 ----
        decompress_cache = {}

        def _decompress(group_idx, block_idx):
            """按 (组, 块) 索引取出对应字节数据，自动处理 zlib 解压"""
            if group_idx not in decompress_cache:
                g_start, g_end, _ = data_blocks[group_idx]
                if header["GroupBase64"]:
                    raise RuntimeError("Base64 编码未实现，请联系更新代码")
                if header["GroupDeflate"]:
                    compressed = raw_bytes[g_start + 32:g_end]
                    decompress_cache[group_idx] = zlib.decompress(bytes(compressed))
                else:
                    decompress_cache[group_idx] = raw_bytes[g_start:g_end]
            group_bytes = decompress_cache[group_idx]
            sub_blocks = self._parse_blocks(group_bytes)
            b_start, b_end, _ = sub_blocks[block_idx]
            return group_bytes[b_start:b_end]

        primitives_list = []
        positions_list = []
        widths_list = []

        # PrimitiveInfos: (offset, length) 每条毛发的起始索引和 CV 数量
        for addr in items.get("PrimitiveInfos", []):
            data = _decompress(*addr)
            fmt = "<IQ"
            rec_size = struct.calcsize(fmt)
            records = []
            for off in range(0, len(data), rec_size):
                records.append(struct.unpack_from(fmt, data, off))
            primitives_list.append(records)

        # Positions: 所有 CV 位置 (xyz 交错), float32 array
        for addr in items.get("Positions", []):
            data = _decompress(*addr)
            positions_list.append(array.array("f", data))

        # WIDTH_CV: CV 宽度, float32 array
        for addr in items.get("WIDTH_CV", []):
            data = _decompress(*addr)
            widths_list.append(array.array("f", data))

        return primitives_list, positions_list, widths_list

    # ---- 数据写入 ----

    def write_first_frame(self):
        """写入首帧 (含拓扑 + 宽度信息)"""
        primitives_list, positions_list, widths_list = self._extract_xgen_data()

        # 统计总曲线数和总 CV 数
        total_curves = 0
        total_cvs = 0
        for primitives in primitives_list:
            total_curves += len(primitives)
            for prim in primitives:
                total_cvs += prim[1]  # prim[1] = length (CV 数量)

        if total_curves == 0 or total_cvs == 0:
            return

        degree = self.CURVE_DEGREE
        order = self.CURVE_ORDER

        orders_arr = imath.UnsignedCharArray(total_curves)
        num_vertices_arr = imath.IntArray(total_curves)
        points = imath.V3fArray(total_cvs)
        widths = imath.FloatArray(total_cvs)
        all_knots = []

        if self.need_bake_uv:
            self.hair_root_list = []

        curve_idx = 0
        cv_idx = 0

        for group_idx in range(len(primitives_list)):
            primitives = primitives_list[group_idx]
            pos_data = positions_list[group_idx]
            width_data = widths_list[group_idx]

            for prim in primitives:
                offset = prim[0]          # 在 pos_data 中的起始索引
                length = int(prim[1])     # 该曲线的 CV 数量

                if length < 2:
                    continue

                for k in range(length):
                    start = (offset + k) * 3
                    points[cv_idx].x = pos_data[start]
                    points[cv_idx].y = pos_data[start + 1]
                    points[cv_idx].z = pos_data[start + 2]
                    widths[cv_idx] = width_data[offset + k]

                    if k == 0 and self.need_bake_uv:
                        self.hair_root_list.append(om.MPoint(points[cv_idx]))

                    cv_idx += 1

                orders_arr[curve_idx] = order
                num_vertices_arr[curve_idx] = length
                all_knots.extend(_build_knots(length, degree))
                curve_idx += 1

        samp = self.first_sample
        samp.setBasis(abcGeom.BasisType.kBsplineBasis)
        samp.setWrap(abcGeom.CurvePeriodicity.kNonPeriodic)
        samp.setType(abcGeom.CurveType.kCubic)
        samp.setCurvesNumVertices(num_vertices_arr)
        samp.setPositions(points)
        samp.setOrders(orders_arr)
        samp.setKnots(_list_to_imath_array(all_knots, imath.FloatArray))

        # OFloatGeomParamSample: 创建逐顶点 (kVertexScope) 宽度参数
        # 然后通过 setWidths() 附加到曲线采样
        width_sample = abcGeom.OFloatGeomParamSample(widths, abcGeom.GeometryScope.kVertexScope)
        samp.setWidths(width_sample)

        self.schema.set(samp)

    def write_frame(self):
        """写入后续帧 (仅更新位置和宽度)"""
        primitives_list, positions_list, _ = self._extract_xgen_data()

        total_cvs = 0
        for primitives in primitives_list:
            for prim in primitives:
                total_cvs += prim[1]

        if total_cvs == 0:
            return

        # 复用首帧的拓扑信息
        samp = abcGeom.OCurvesSchemaSample()
        samp.setBasis(self.first_sample.getBasis())
        samp.setWrap(self.first_sample.getWrap())
        samp.setType(self.first_sample.getType())
        samp.setCurvesNumVertices(self.first_sample.getCurvesNumVertices())
        samp.setKnots(self.first_sample.getKnots())
        samp.setOrders(self.first_sample.getOrders())
        samp.setWidths(self.first_sample.getWidths())

        points = imath.V3fArray(total_cvs)
        cv_idx = 0

        for group_idx in range(len(primitives_list)):
            primitives = primitives_list[group_idx]
            pos_data = positions_list[group_idx]

            for prim in primitives:
                offset = prim[0]
                length = int(prim[1])

                if length < 2:
                    continue

                for k in range(length):
                    start = (offset + k) * 3
                    points[cv_idx].x = pos_data[start]
                    points[cv_idx].y = pos_data[start + 1]
                    points[cv_idx].z = pos_data[start + 2]
                    cv_idx += 1

        samp.setPositions(points)
        self.schema.set(samp)


# ===========================================================================
# 导出主流程
# ===========================================================================

class ExportCancelledError(Exception):
    pass


def _collect_xgen_hierarchy(job):
    """
    收集 XGen 分组的变换/形状节点以及对应导引线

    Returns:
        dict: {group_name: {
            'xgen':  {'transform': str, 'shape': str},
            'guide': str (guide 节点名)
        }}
    """
    job_dict = {}
    bd_childrens = cmds.listRelatives(job, c=1, type='transform') or []
    xgen_nodes = [n for n in bd_childrens if cmds.nodeType(n) == "transform"]
    for xgen in xgen_nodes:
        is_export = cmds.getAttr('{}.IsExport'.format(xgen))
        if not is_export:
            continue

        xgen_shapes = cmds.listRelatives(xgen, c=1) or []
        if not xgen_shapes:
            continue

        xgen_shape = xgen_shapes[0]
        group_name = cmds.getAttr('{}.GroupName'.format(xgen))
        xgen_animation = cmds.getAttr('{}.SplineAnimaiton'.format(xgen))
        guide_animation = cmds.getAttr('{}.GuideAnimation'.format(xgen))
        guide_conns = cmds.listConnections(xgen + '.GuideGroupName') or []
        if not guide_conns:
            continue

        guide = guide_conns[0]
        job_dict[group_name] = {
            'xgen': {'transform': xgen, 'shape': xgen_shape, 'animation': xgen_animation},
            'guide': {'transform': guide, 'animation': guide_animation},
        }
    
    # 计算groom_group_id，因为之前的资产导出是根据GroupName字符串排序，为了兼容
    for index, group_name in enumerate(sorted(job_dict)):
        job_dict[group_name]['xgen']['groom_group_id'] = index
        job_dict[group_name]['guide']['groom_group_id'] = index
    
    # 为后面导出的abc大纲节点排序，与资产顺序不一致则无法导入UE
    job_dict_sorted = OrderedDict(
        sorted(job_dict.items(), key=lambda x: int(x[0]))
    )
    
    return job_dict_sorted


def _find_bake_mesh(fn_dep_node):
    """
    在给定变换节点下查找第一个 Mesh，用于毛发根部 UV 烘焙

    Returns:
        (MFnMesh or None, str or None): (mesh_fn, current_uv_set_name)
    """
    it_dag = om.MItDag()
    # MItDag.reset(object, traversal_mode, filter_type): 以深度优先遍历该节点下的物体，只过滤 Mesh
    it_dag.reset(fn_dep_node.object(), om.MItDag.kDepthFirst, om.MFn.kMesh)
    while not it_dag.isDone():
        mesh_path = om.MDagPath.getAPathTo(it_dag.currentItem())
        mesh_fn = om.MFnMesh(mesh_path)
        uv_set = mesh_fn.currentUVSetName()
        return mesh_fn, uv_set
    return None, None


def _create_proxies(project, archive, job_name, job_dict, time_sampling, static):
    """
    为所有分组创建 CurvesProxy / XGenProxy，写入元数据

    Args:
        archive: abc.OArchive — Alembic 归档
        job_name: str — 原始 job 变换节点名 (用于 Hair01 过滤)
        job_dict: _collect_xgen_hierarchy 返回的分组字典
        time_sampling: abcA.TimeSampling — 导引线使用的时间采样 (独立于 XGen 毛发)

    Returns:
        list[CurvesProxy]
    """
    proxies = []
    if 'SSDSY_CS' in project:
        # 财神项目 非 static 模式下跳过 Hair01 xgen, 仅保留其他分组
        skip_condition = (not static and 'Hair01' in job_name)
    else:
        # 非 static 模式下跳过所有xgen
        skip_condition = (not static)

    for group_name, group_info in job_dict.items():
        for object_type, value in group_info.items():
            # ---- 创建选择 / DAG 路径 ----
            sel = om.MSelectionList()
            # XGen: 用 shape 节点; 导引线: 直接用 transform
            sel.add(value['shape'] if object_type == 'xgen' else value['transform'])
            dag_path = sel.getDagPath(0)
            fn_dep_node = om.MFnDependencyNode(dag_path.node())

            # ---- 查找用于 UV 烘焙的 Mesh ----
            bake_mesh, uv_set = _find_bake_mesh(fn_dep_node)

            # ---- 创建 Alembic 对象与代理 ----
            if object_type == 'xgen':
                if skip_condition:
                    continue
                # OXform / OCurves 在 Alembic 归档中创建层级:
                #   |-- <transform>  (含 Description 的世界矩阵)
                #        |-- <shape>
                # outSplineData 的位置为 Description 局部空间, 因此
                # OXform 写入世界矩阵, OCurves 写入位置原值, 两者
                # 共同确定最终世界坐标.
                xform = abcGeom.OXform(archive.getTop(), str(value['transform']))

                # 获取 XGen description 的世界矩阵并写入 OXform
                sel_xform = om.MSelectionList()
                sel_xform.add(str(value['transform']))
                xform_dag_path = sel_xform.getDagPath(0)
                world_matrix = xform_dag_path.inclusiveMatrix()       # om.MMatrix

                xform_schema = xform.getSchema()
                xform_sample = abcGeom.XformSample()
                m44 = imath.M44d(
                    world_matrix[0],  world_matrix[1],  world_matrix[2],  world_matrix[3],
                    world_matrix[4],  world_matrix[5],  world_matrix[6],  world_matrix[7],
                    world_matrix[8],  world_matrix[9],  world_matrix[10], world_matrix[11],
                    world_matrix[12], world_matrix[13], world_matrix[14], world_matrix[15],
                )
                xform_sample.addOp(
                    abcGeom.XformOp(abcGeom.XformOperationType.kMatrixOperation, 0),
                    m44,
                )
                xform_schema.set(xform_sample)

                curve_obj = abcGeom.OCurves(xform, str(value['shape']))
                proxy = XGenProxy(curve_obj, fn_dep_node, True, value['animation'], bake_mesh, uv_set)
                proxy.write_group_id(value['groom_group_id'])           # groom_group_id
                proxy.write_group_name(group_name)                      # groom_group_name

            else:  # guide
                # 导引线使用独立的时间采样 (可设置不同帧率)
                # archive.addTimeSampling() 注册采样并返回索引
                curve_obj = abcGeom.OCurves(
                    archive.getTop(),
                    str(fn_dep_node.name()),
                    archive.addTimeSampling(time_sampling),
                )
                proxy = CurvesProxy(curve_obj, fn_dep_node, True, value['animation'], bake_mesh, uv_set)
                # ---- 写入自定义属性 ----
                proxy.write_group_id(value['groom_group_id'])           # groom_group_id
                proxy.write_group_name(group_name)                      # groom_group_name
                proxy.write_is_guide(True)                              # groom_guide = 1

            proxies.append(proxy)

    return proxies


def export_xgen(jobs, file_paths, project, 
                start_frame, end_frame, start_expend, end_expend,
                refresh_hair, static):
    """
    XGen 毛发导出入口函数

    Args:
        jobs: list[str] — Maya 场景中的 XGen 变换组节点名
        file_paths: list[str] — 对应每个 job 的输出 .abc 路径
        start_frame / end_frame: 帧范围
        start_expend / end_expend: 起始/结束 额外帧扩展
        guide_animation: 导引线是否逐帧导出
        xgen_animation: XGen 毛发是否逐帧导出
        refresh_hair: 每帧是否强制刷新 (触发 XGen 重新生成)
        static: 是否仅导出静态帧
    """
    cmds.waitCursor(state=True)
    old_cur_time = omAnim.MAnimControl.currentTime()
    progress_bar = mel.eval('$tmp = $gMainProgressBar')
    cmds.progressBar(progress_bar, edit=True, isInterruptable=True, status=u'计算中...')
    try:
        """
        向前拓展为整体的时间轴偏移，向后拓展每帧写入结束帧
        例：
            start_frame=1, end_frame=100, start_expend=5, end_expend=10
            ABC时间轴:
            1     5        6                         105       106~115
            |-----|--------|-------------------------|---------|
            空白       Maya1                      Maya100     Maya100
        """
        # ---- 时间采样设置 ----
        # abcA.TimeSampling(rate, start_time): 创建均匀时间采样
        # spf = 1/fps (秒/帧), 起始时间为 spf * (start_frame + start_expend)
        frame_range = [start_frame, end_frame + end_expend]
        sec = om.MTime(1, om.MTime.kSeconds)
        spf = 1.0 / sec.asUnits(om.MTime.uiUnit())
        time_sampling = abcA.TimeSampling(spf, spf * (start_frame + start_expend))

        # ---- 创建 Alembic 归档 ----
        # abc.OArchive(path): 创建一个用于写入的 Alembic 归档文件
        archive_job = {}
        for job, file_path in zip(jobs, file_paths):
            archive = abc.OArchive(str(file_path))
            archive_job[archive] = job

        # ---- 创建代理对象 ----
        proxy_list = []
        for archive, job in archive_job.items():
            if cmds.progressBar(progress_bar, query=True, isCancelled=True):
                raise ExportCancelledError(u'用户取消导出')

            job_dict = _collect_xgen_hierarchy(job)
            proxies = _create_proxies(
                project, archive, job, job_dict, time_sampling, static
            )
            proxy_list.extend(proxies)

        # ---- 写入帧数据 ----
        for frame in range(frame_range[0], frame_range[1] + 1):
            if cmds.progressBar(progress_bar, query=True, isCancelled=True):
                raise ExportCancelledError(u'用户取消导出')

            if frame > end_frame:
                cmds.currentTime(end_frame, edit=True)
            else:
                cmds.currentTime(frame, edit=True)

            if refresh_hair:
                cmds.refresh(force=True)        # 触发 XGen 重新生成样条线

            for proxy in proxy_list:
                if frame == frame_range[0]:
                    proxy.write_first_frame()
                elif proxy.animation:
                    proxy.write_frame()

        # ---- UV 烘焙 ----
        for proxy in proxy_list:
            proxy.bake_uv()
    
    except ExportCancelledError:
        cmds.warning(u"导出已取消")

    finally:
        omAnim.MAnimControl.setCurrentTime(old_cur_time)
        cmds.progressBar(progress_bar, edit=True, endProgress=True)
        cmds.waitCursor(state=False)


if __name__ == '__main__':
    jobs = [
        'DouZhanLong_ErShiSuiXin_Dyn:DouZhanLong_ErShiSuiXin_Hair01_BD',
        'DouZhanLong_ErShiSuiXin_Dyn:DouZhanLong_ErShiSuiXin_Hair02_BD',
        'DouZhanLong_ErShiSuiXin_Dyn:DouZhanLong_ErShiSuiXin_Hair03_BD',
    ]
    file_paths = [
        'd:/Desktop/DouZhanLong_ErShiSuiXin_Hair01_BD_1-10_hCache.abc',
        'd:/Desktop/DouZhanLong_ErShiSuiXin_Hair02_BD_1-10_hCache.abc',
        'd:/Desktop/DouZhanLong_ErShiSuiXin_Hair03_BD_1-10_hCache.abc',
    ]

    export_xgen(jobs, file_paths, '财神-SSDSY_CS', 
                1, 10, 0, 1,
                1, 0)
