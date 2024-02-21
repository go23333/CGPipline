#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
# version: 3.10.13
##################################################################
import bpy

import json


def getAllMaterials():
    materials = []
    # 遍历当前场景中的所有物体
    for obj in bpy.context.scene.objects:
        # 检查物体是否有材质
        if obj.material_slots:
            # 遍历该物体的所有材质槽
            for slot in obj.material_slots:
                if slot.material not in materials:
                    materials.append(slot.material)
    return materials


def createMaterialNode(materila,data):
    materila.use_nodes = True
    nodes = materila.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    # 连接漫反射节点到材质输出节点
    links = materila.node_tree.links
    links.new(bsdf.outputs[0], node_output.inputs[0])

    useUDIM = data["fUDIM"]

    if data["baseColorPath"] != None:
        baseColorNode = nodes.new(type="ShaderNodeTexImage")
        image = bpy.data.images.load(data["baseColorPath"])
        if useUDIM:
            image.source = "TILED"
        baseColorNode.image = image
        links.new(baseColorNode.outputs[0],bsdf.inputs[0])

    if data["roughnessPath"] != None:
        roughnessNode = nodes.new(type="ShaderNodeTexImage")
        image = bpy.data.images.load(data["roughnessPath"])
        image.colorspace_settings.name = 'Non-Color'
        if useUDIM:
            image.source = "TILED"
        roughnessNode.image = image
        splitXYZNode = nodes.new(type="ShaderNodeSeparateXYZ")
        links.new(roughnessNode.outputs[0],splitXYZNode.inputs[0])
        links.new(splitXYZNode.outputs[1],bsdf.inputs[2])
   
    if data["normalPath"] != None:
        normalNode = nodes.new(type="ShaderNodeTexImage")
        image = bpy.data.images.load(data["normalPath"])
        image.colorspace_settings.name = 'Non-Color'
        if useUDIM:
            image.source = "TILED"
        normalNode.image = image
        normalMapNode = nodes.new(type="ShaderNodeNormalMap")
        links.new(normalNode.outputs[0],normalMapNode.inputs[1])
        links.new(normalMapNode.outputs[0],bsdf.inputs[5])
    
    if data["metallicPath"] != None:
        metallicNode = nodes.new(type="ShaderNodeTexImage")
        image = bpy.data.images.load(data["metallicPath"])
        image.colorspace_settings.name = 'Non-Color'
        if useUDIM:
            image.source = "TILED"
        metallicNode.image = image
        splitXYZNode = nodes.new(type="ShaderNodeSeparateXYZ")
        links.new(metallicNode.outputs[0],splitXYZNode.inputs[0])
        links.new(splitXYZNode.outputs[2],bsdf.inputs[1])

def read_some_data(context, filepath, use_some_setting):

    jsonpath = filepath.replace('.fbx','.json')
    #导入fbx文件
    bpy.ops.import_scene.fbx(filepath=filepath)

    #读取材质信息
    with open(jsonpath,'r',encoding="utf-8") as file:
        jsonstring  = file.read()
    datas = json.loads(jsonstring)
    for material in getAllMaterials():
        for data in datas:
            if material.name == data["materialName"]:
                createMaterialNode(material,data)
    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportSomeData(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Some Data"

    # ImportHelper mix-in class uses this.
    filename_ext = ".fbx"

    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ('OPT_A', "First Option", "Description one"),
            ('OPT_B', "Second Option", "Description two"),
        ),
        default='OPT_A',
    )

    def execute(self, context):
        return read_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu.
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Custom Import")


# Register and add to the "file selector" menu (required to use F3 search "Text Import Operator" for quick access).
def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')


