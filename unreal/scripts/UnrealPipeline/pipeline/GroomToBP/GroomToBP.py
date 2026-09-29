import unreal
from importlib import reload

import UnrealPipeline.core.Config as UC
reload(UC)

from Qt import QtCore
from Qt import QtWidgets

from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.label import MLabel
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application


def createGroomComponent(bp_path):
    groom_path = UC.globalConfig.get().AssetPath + 'Character/' + bp_path.split('/')[5] + '/Groom/ChaiFen/'
    asset_paths = unreal.EditorAssetLibrary.list_assets(groom_path)

    blueprint_asset=unreal.EditorAssetLibrary.find_asset_data(bp_path).get_asset()

    for asset_path in asset_paths:
        groom_asset = unreal.EditorAssetLibrary.find_asset_data(asset_path).get_asset()
        if groom_asset.get_class().get_name() == 'GroomAsset':
            subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
            root_data_handle = subsystem.k2_gather_subobject_data_for_blueprint(blueprint_asset)[0]

            sub_handle, fail_reason = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(
                        parent_handle=root_data_handle,
                        new_class=unreal.GroomComponent,
                        blueprint_context=blueprint_asset
                    ))

            subobject_data = subsystem.k2_find_subobject_data_from_handle(sub_handle)
            subobject = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(subobject_data)
            subobject.groom_asset=groom_asset


# main_bp_path='/Game/AAI/Reference/BP/BP_Character.BP_Character'
# bp_path_c='/Game/AAI/Reference/Character/DouZhanLong_ErShiSui/DouZhanLong_ErShiSui_AAI_BP.DouZhanLong_ErShiSui_AAI_BP_C'
# blueprint_class = unreal.load_object(None, bp_path_c)

# editor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
# blueprint_asset_c=unreal.EditorAssetLibrary.find_asset_data(bp_path_c).get_asset()
# main_bp=unreal.EditorAssetLibrary.find_asset_data(main_bp_path).get_asset()

# components=[]

# graphs=unreal.Kismet2Library.get_all_graphs(blueprint_class)
# print(main_bp.get_all_graphs())

# cdo = unreal.get_default_object(blueprint_class)
# old_groom = cdo.get_editor_property('Groom毛发')
# old_groom[None]=None
# print(cdo.get_class())
# for i in range(3):
#     groom_component=unreal.GroomComponent()
#     components.append(groom_component)
# print(components)
# print(cdo.set_editor_property('Components',components))
# print(cdo.get_editor_property('Components'))
# print(cdo.get_editor_property('是否隐藏'))

# sub_handle, fail_reason = subsystem.add_new_subobject(unreal.AddNewSubobjectParams(
#             parent_handle=root_data_handle,
#             new_class=unreal.GroomComponent,
#             blueprint_context=blueprint_asset
#         ))

# subobject_data = subsystem.k2_find_subobject_data_from_handle(sub_handle)


def groomComponentToWroldSpace(bp_path):

    blueprint_asset=unreal.EditorAssetLibrary.find_asset_data(bp_path).get_asset()

    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    component_data_handles = subsystem.k2_gather_subobject_data_for_blueprint(blueprint_asset)

    #获取骨骼组件
    joint_component_data = subsystem.k2_find_subobject_data_from_handle(component_data_handles[1])
    joint_component = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(joint_component_data)

    root_name = 'Group'
    for component_data_handle in component_data_handles:
        subobject_data = subsystem.k2_find_subobject_data_from_handle(component_data_handle)
        component = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(subobject_data)

        if component.get_class().get_name() == 'GroomComponent':
            component_name = component.get_name()

            if '__' in component_name:
                #通过Groom组件名称获取骨骼名称
                bone_name=component_name.split('__')[-1].split('_GEN_VARIABLE')[0]     
                #获取骨骼与艮骨骼的相对坐标
                bone_transform = joint_component.get_delta_transform_from_ref_pose(bone_name,root_name)
                root_transform = joint_component.get_delta_transform_from_ref_pose('Group')
                root_rotation = root_transform.rotation.euler()

                bone_transform:unreal.Transform
                new_location = bone_transform.translation           #位置
                new_rotation = bone_transform.rotation.euler()      #旋转
                #通过相加清除根变换使骨骼旋转值归正
                new_rotation = unreal.Rotator(new_rotation.x+root_rotation.x,new_rotation.y+root_rotation.y,new_rotation.z+root_rotation.z)
                #赋予参数
                component.set_editor_property('relative_location',new_location)
                component.set_editor_property('relative_rotation',new_rotation)

            # print(bone_name)
            



class GroomToBpWindow(QtWidgets.QWidget, MFieldMixin):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.uii()

    def uii(self):   
        self.setWindowTitle('角色BPGroom组件创建工具')
        self.resize(300,160)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()

        #导入文件
        create_component_btn=MPushButton(text="为选中角色蓝图创建Groom组件")
        create_component_btn.clicked.connect(self.createComponent)
        correct_coord_btn=MPushButton(text="为选中角色蓝图归正坐标")
        correct_coord_btn.clicked.connect(self.correctCoord)
        
 

        hint_label = MLabel("Groom组件设置好骨骼对象后需将骨骼名称以'__XX'\n的形式作为后缀,为Groom组件重命名.\n如Groom__Head_M")    #关卡创建开关

        folder_lay.addWidget(create_component_btn)
        folder_lay.addWidget(correct_coord_btn)
        folder_lay.addWidget(hint_label)        

        lay.addLayout(folder_lay)
        self.setLayout(lay)

    def createComponent(self):
        sel_asset = unreal.EditorUtilityLibrary.get_selected_assets()[0]
        if sel_asset.get_class().get_name()=='Blueprint':
            bp_path = sel_asset.get_path_name()
            createGroomComponent(bp_path)

    def correctCoord(self):
        sel_asset = unreal.EditorUtilityLibrary.get_selected_assets()[0]
        if sel_asset.get_class().get_name()=='Blueprint':
            bp_path = sel_asset.get_path_name()
            groomComponentToWroldSpace(bp_path)




def start():
    with application() as app:
        global test
        test = GroomToBpWindow()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":

    start()


