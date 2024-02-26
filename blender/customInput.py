#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2024.2
# Email  : 978654313@qq.com
# version: 3.10.13
##################################################################
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


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

    if data["normalPath"] != None:
        normalNode = nodes.new(type="ShaderNodeTexImage")
        bpy.ops.image.open(filepath=data["normalPath"], relative_path=True, show_multiview=False)
        image = bpy.data.images.load(data["normalPath"],check_existing=True)
        image.colorspace_settings.name = 'Non-Color'
        if useUDIM:
            image.source = "TILED"
        normalNode.image = image
        normalMapNode = nodes.new(type="ShaderNodeNormalMap")
        links.new(normalNode.outputs[0],normalMapNode.inputs[1])
        links.new(normalMapNode.outputs[0],bsdf.inputs[5])


        texCoordNode = nodes.new(type="ShaderNodeTexCoord")
        mapNode = nodes.new(type="ShaderNodeMapping")
        mapNode.inputs[3].default_value[0] = data["normalTiling"][0]
        mapNode.inputs[3].default_value[1] = data["normalTiling"][1]
        links.new(texCoordNode.outputs[2],mapNode.inputs[0])
        links.new(mapNode.outputs[0],normalNode.inputs[0])

    # 当类型为PBR模式时
    if data["type"] == "PBR":
        if data["baseColorPath"] != None:
            baseColorNode = nodes.new(type="ShaderNodeTexImage")
            bpy.ops.image.open(filepath=data["baseColorPath"], relative_path=True, show_multiview=False)
            image = bpy.data.images.load(data["baseColorPath"],check_existing=True)
            if useUDIM:
                image.source = "TILED"
            baseColorNode.image = image
            links.new(baseColorNode.outputs[0],bsdf.inputs[0])


            texCoordNode = nodes.new(type="ShaderNodeTexCoord")
            mapNode = nodes.new(type="ShaderNodeMapping")
            mapNode.inputs[3].default_value[0] = data["baseColorTiling"][0]
            mapNode.inputs[3].default_value[1] = data["baseColorTiling"][1]
            links.new(texCoordNode.outputs[2],mapNode.inputs[0])
            links.new(mapNode.outputs[0],baseColorNode.inputs[0])


        if data["roughnessPath"] != None:
            roughnessNode = nodes.new(type="ShaderNodeTexImage")
            bpy.ops.image.open(filepath=data["roughnessPath"], relative_path=True, show_multiview=False)
            image = bpy.data.images.load(data["roughnessPath"],check_existing=True)
            image.colorspace_settings.name = 'Non-Color'
            if useUDIM:
                image.source = "TILED"
            roughnessNode.image = image
            splitXYZNode = nodes.new(type="ShaderNodeSeparateXYZ")
            links.new(roughnessNode.outputs[0],splitXYZNode.inputs[0])
            links.new(splitXYZNode.outputs[1],bsdf.inputs[2])
            

            texCoordNode = nodes.new(type="ShaderNodeTexCoord")
            mapNode = nodes.new(type="ShaderNodeMapping")
            mapNode.inputs[3].default_value[0] = data["roughnessTiling"][0]
            mapNode.inputs[3].default_value[1] = data["roughnessTiling"][1]
            links.new(texCoordNode.outputs[2],mapNode.inputs[0])
            links.new(mapNode.outputs[0],roughnessNode.inputs[0])

        
        if data["metallicPath"] != None:
            metallicNode = nodes.new(type="ShaderNodeTexImage")
            bpy.ops.image.open(filepath=data["metallicPath"], relative_path=True, show_multiview=False)
            image = bpy.data.images.load(data["metallicPath"],check_existing=True)
            image.colorspace_settings.name = 'Non-Color'
            if useUDIM:
                image.source = "TILED"
            metallicNode.image = image
            splitXYZNode = nodes.new(type="ShaderNodeSeparateXYZ")
            links.new(metallicNode.outputs[0],splitXYZNode.inputs[0])
            links.new(splitXYZNode.outputs[2],bsdf.inputs[1])


            texCoordNode = nodes.new(type="ShaderNodeTexCoord")
            mapNode = nodes.new(type="ShaderNodeMapping")
            mapNode.inputs[3].default_value[0] = data["metallicTiling"][0]
            mapNode.inputs[3].default_value[1] = data["metallicTiling"][1]
            links.new(texCoordNode.outputs[2],mapNode.inputs[0])
            links.new(mapNode.outputs[0],metallicNode.inputs[0])

    # 当类型为传统模式时
    elif data["type"] == "legacy":
        if data["diffusePath"] != None:
            diffuseNode = nodes.new(type="ShaderNodeTexImage")
            bpy.ops.image.open(filepath=data["diffusePath"], relative_path=True, show_multiview=False)
            image = bpy.data.images.load(data["diffusePath"],check_existing=True)
            if useUDIM:
                image.source = "TILED"
            diffuseNode.image = image
            links.new(diffuseNode.outputs[0],bsdf.inputs[0])


            texCoordNode = nodes.new(type="ShaderNodeTexCoord")
            mapNode = nodes.new(type="ShaderNodeMapping")
            mapNode.inputs[3].default_value[0] = data["diffuseTiling"][0]
            mapNode.inputs[3].default_value[1] = data["diffuseTiling"][1]
            links.new(texCoordNode.outputs[2],mapNode.inputs[0])
            links.new(mapNode.outputs[0],diffuseNode.inputs[0])

        if data["glossinessPath"] != None:
            glossinessNode = nodes.new(type = "ShaderNodeTexImage")
            bpy.ops.image.open(filepath=data["glossinessPath"], relative_path=True, show_multiview=False)
            image = bpy.data.images.load(data["glossinessPath"],check_existing=True)
            image.colorspace_settings.name = 'Non-Color'
            if useUDIM:
                image.source = "TILED"
            glossinessNode.image = image
            invertColorNode = nodes.new(type = "ShaderNodeInvert")
            links.new(glossinessNode.outputs[0],invertColorNode.inputs[1])
            links.new(invertColorNode.outputs[0],bsdf.inputs[2])


            texCoordNode = nodes.new(type="ShaderNodeTexCoord")
            mapNode = nodes.new(type="ShaderNodeMapping")
            mapNode.inputs[3].default_value[0] = data["glossinessTiling"][0]
            mapNode.inputs[3].default_value[1] = data["glossinessTiling"][1]
            links.new(texCoordNode.outputs[2],mapNode.inputs[0])
            links.new(mapNode.outputs[0],glossinessNode.inputs[0])


        if data["f0Path"] != None:
            f0Node = nodes.new(type = "ShaderNodeTexImage")
            image = bpy.data.images.load(data["f0Path"],check_existing=True)
            image.colorspace_settings.name = 'Non-Color'
            if useUDIM:
                image.source = "TILED"
            f0Node.image = image
            links.new(f0Node.outputs[0],bsdf.inputs[1])


            texCoordNode = nodes.new(type="ShaderNodeTexCoord")
            mapNode = nodes.new(type="ShaderNodeMapping")
            mapNode.inputs[3].default_value[0] = data["f0Tiling"][0]
            mapNode.inputs[3].default_value[1] = data["f0Tiling"][1]
            links.new(texCoordNode.outputs[2],mapNode.inputs[0])
            links.new(mapNode.outputs[0],f0Node.inputs[0])


        if data["reflectColorPath"] != None:
            reflectColorNode = nodes.new(type = "ShaderNodeTexImage")
            image = bpy.data.images.load(data["reflectColorPath"],check_existing=True)
            if useUDIM:
                image.source = "TILED"
            reflectColorNode.image = image

            texCoordNode = nodes.new(type="ShaderNodeTexCoord")
            mapNode = nodes.new(type="ShaderNodeMapping")
            mapNode.inputs[3].default_value[0] = data["reflectColorTiling"][0]
            mapNode.inputs[3].default_value[1] = data["reflectColorTiling"][1]
            links.new(texCoordNode.outputs[2],mapNode.inputs[0])
            links.new(mapNode.outputs[0],reflectColorNode.inputs[0])

        
        if data["f0Path"] != None and data["reflectColorPath"] != None:
            colorMixNode = nodes.new(type = "ShaderNodeMixRGB")
            links.new(f0Node.outputs[0],colorMixNode.inputs[0])
            links.new(diffuseNode.outputs[0],colorMixNode.inputs[1])
            links.new(reflectColorNode.outputs[0],colorMixNode.inputs[2])
            links.new(colorMixNode.outputs[0],bsdf.inputs[0])


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



