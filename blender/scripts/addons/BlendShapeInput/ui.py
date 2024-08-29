import bpy
from bpy.types import Panel,Operator,Context
from bpy.props import IntProperty
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty

#
# Add additional functions here
#
TransformMapMayaBlender = {
    "rotateX":"ROT_Y",
    "rotateY":"ROT_X",
    "rotateZ":"ROT_Z",
}


class SimpleMouseOperator(Operator):
    bl_idname = "custom.mouse_position"
    bl_label = "Invoke Mouse Operator"
    filter_glob: StringProperty( default='*.json', options={'HIDDEN'} )
    def readJsonData(self,path):
        import json
        with open(path,'r') as f:
            return(json.loads(f.read()))
    def execute(self, context):
        bsDatas = self.readJsonData(r"d:\Desktop\test.json")
        for obj in context.selected_objects[0].children:
            if obj.name in bsDatas.keys():
                data = bsDatas[obj.name]
                mesh = obj.to_mesh()
                for shapekey in mesh.shape_keys.key_blocks:
                    shapekey.value = 0
                    if shapekey.name in data.keys():
                        perKeyData = data[shapekey.name]
                        value = "var"
                        if perKeyData["attributeName"] in TransformMapMayaBlender.keys():
                            if perKeyData["attributeName"] == "rotateX":
                                if "_L" in perKeyData["boenName"]:
                                    value = "-var"
                            elif perKeyData["attributeName"] == "rotateZ":
                                if "_R" in perKeyData["boenName"]:
                                    value = "-var"


                            fcurve = shapekey.driver_add("value")
                            driver = fcurve.driver
                            driver.type = "SCRIPTED"
                            OldMin = perKeyData["originValueMin"]
                            OldMax = perKeyData["originValueMax"]
                            NewMin = perKeyData["NewValueMin"]
                            NewMax = perKeyData["NewValueMax"]
                            driver.expression = f"(((({value}/3.1415926*180) - {OldMin}) * ({NewMax} - {NewMin})) / ({OldMax} - {OldMin})) + {NewMin}"
                            v = driver.variables.new()
                            v.name = "var"
                            v.type = "TRANSFORMS"
                            t = v.targets[0]
                            t.id = bpy.data.objects["Armature"]
                            t.bone_target = perKeyData["boenName"]
                            t.transform_type = TransformMapMayaBlender[perKeyData["attributeName"]]
                            t.transform_space = "LOCAL_SPACE"
                   

                        
  
                        

        return {'FINISHED'}

class BlendShapeImportPanel(Panel):
    bl_idname = "OBJECT_PT_Blend_Shape_Import"
    bl_label = "导入工具"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Tool"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        layout.label(text="BS导入工具")
        
        row = layout.row()
        row.operator(SimpleMouseOperator.bl_idname,text="test")




def register():
    bpy.utils.register_class(SimpleMouseOperator)
    bpy.utils.register_class(BlendShapeImportPanel)

def unregister():
    bpy.utils.unregister_class(SimpleMouseOperator)
    bpy.utils.unregister_class(BlendShapeImportPanel)
