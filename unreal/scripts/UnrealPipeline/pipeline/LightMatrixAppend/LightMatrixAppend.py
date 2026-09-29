import unreal

from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


from dayu_widgets.push_button import MPushButton
from dayu_widgets.button_group import MRadioButtonGroup
from dayu_widgets.label import MLabel

from dayu_widgets import dayu_theme
from dayu_widgets.qt import application



actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
unreal_editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)


def create_actor_with_label(actor_class, label, location, rotation):
    """生成 Actor 并设置标签、位置与旋转"""
    world = unreal.EditorLevelLibrary.get_editor_world()
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, location, rotation)
    actor.set_actor_label(label)
    return actor

def set_root_component_world_rotation(actor, pitch, yaw, roll):
    """设置 Actor 根组件的相对旋转"""
    root = actor.root_component
    if root:
        rot = unreal.Rotator(pitch, yaw, roll)
        root.set_world_rotation(rot,sweep=True,teleport=False)


def create_spot_light(parent, relative_location, relative_rotation, label,
                      source_radius, attenuation_radius, intensity,
                      lighting_channels, **kwargs):
    """创建聚光源并附加到父 Actor,设置全部属性"""
    spot_light = create_actor_with_label(unreal.SpotLight, label, unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    spot_light.attach_to_actor(parent,socket_name='',location_rule=unreal.AttachmentRule.KEEP_RELATIVE,rotation_rule=unreal.AttachmentRule.KEEP_RELATIVE,scale_rule=unreal.AttachmentRule.KEEP_RELATIVE)
    spot_light.set_actor_relative_location(relative_location,sweep=True,teleport=False)
    root = spot_light.root_component
    root.set_world_rotation(relative_rotation,sweep=True,teleport=False)

    light_comp = spot_light.light_component
    if not light_comp:
        light_comp = spot_light.get_component_by_class(unreal.SpotLightComponent)

    # 基本参数
    light_comp.set_editor_property("source_radius", source_radius)
    light_comp.set_editor_property("attenuation_radius", attenuation_radius)
    light_comp.set_editor_property("intensity", intensity)
    light_comp.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    light_comp.set_editor_property("lighting_channels", lighting_channels)
    
    # 其他参数
    light_comp.set_editor_property("allow_mega_lights", kwargs.get("b_allow_mega_lights", False))
    light_comp.set_editor_property("affect_translucent_lighting", kwargs.get("b_affect_translucent_lighting", False))
    light_comp.set_editor_property("cast_raytraced_shadow", kwargs.get("cast_raytraced_shadow", unreal.CastRayTracedShadow.ENABLED))
    light_comp.set_editor_property("indirect_lighting_intensity", kwargs.get("indirect_lighting_intensity", 0.0))
    light_comp.set_editor_property("volumetric_scattering_intensity", kwargs.get("volumetric_scattering_intensity", 0.0))
    light_comp.set_editor_property("samples_per_pixel", kwargs.get("samples_per_pixel", 4))
    light_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    
    return spot_light


def create_rect_light(parent, relative_location, relative_rotation, label,
                      source_width, source_height, attenuation_radius, intensity,
                      lighting_channels, light_color=None, **kwargs):
    """创建矩形光源并附加到父 Actor,设置全部属性"""
    # 生成光源（先在世界原点生成，之后附加并设置相对变换）
    rect_light = create_actor_with_label(unreal.RectLight, label, unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    
    # 附加到父 Actor（保持相对变换）
    rect_light.attach_to_actor(parent,socket_name='',location_rule=unreal.AttachmentRule.KEEP_RELATIVE,rotation_rule=unreal.AttachmentRule.KEEP_RELATIVE,scale_rule=unreal.AttachmentRule.KEEP_RELATIVE)
    
    # 设置相对位置与旋转
    rect_light.set_actor_relative_location(relative_location,sweep=True,teleport=False)
    root = rect_light.root_component
    root.set_world_rotation(relative_rotation,sweep=True,teleport=False)
    
    # 获取光源组件
    light_comp = rect_light.light_component  # rect_light 自动拥有 LightComponent0
    if not light_comp:
        light_comp = rect_light.get_component_by_class(unreal.RectLightComponent)
    
    # 基本参数
    light_comp.set_editor_property("source_width", source_width)
    light_comp.set_editor_property("source_height", source_height)
    light_comp.set_editor_property("intensity", intensity)
    light_comp.set_editor_property("attenuation_radius", attenuation_radius)
    light_comp.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    
    # 光照通道
    light_comp.set_editor_property("lighting_channels", lighting_channels)
    
    # 其他常用参数（根据 T3D 设置）
    light_comp.set_editor_property("allow_mega_lights", kwargs.get("b_allow_mega_lights", False))
    light_comp.set_editor_property("affect_translucent_lighting", kwargs.get("b_affect_translucent_lighting", False))
    light_comp.set_editor_property("cast_raytraced_shadow", kwargs.get("cast_raytraced_shadow", unreal.CastRayTracedShadow.ENABLED))
    light_comp.set_editor_property("indirect_lighting_intensity", kwargs.get("indirect_lighting_intensity", 0.0))
    light_comp.set_editor_property("volumetric_scattering_intensity", kwargs.get("volumetric_scattering_intensity", 0.0))
    light_comp.set_editor_property("samples_per_pixel", kwargs.get("samples_per_pixel", 4))
    if light_color:
        light_comp.set_editor_property("light_color", light_color)
    
    # 移动性
    light_comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
    
    return rect_light


def createChLight(character_actor=None,socket_name=None):
    # ---------- 1. 创建根容器 Actor_5 (LIG) ----------
    ch_name= character_actor.get_actor_label()
    actor_5 = create_actor_with_label(unreal.Actor, ch_name+"_"+str(socket_name)+"_LIG", unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    actor_5.root_component.set_absolute(new_absolute_rotation=True)   #设置旋转为绝对旋转
    # 设置 DefaultSceneRoot 的相对旋转
    set_root_component_world_rotation(actor_5, 90.0, 0.000000, -90.000000)
    
    # ---------- 2. 创建子容器 Actor_7 (SHANG) 和 Actor_6 (XIA)，并附加到 Actor_5 ----------
    actor_7 = create_actor_with_label(unreal.Actor, "SHANG", unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    actor_7.attach_to_actor(actor_5,socket_name='',location_rule=unreal.AttachmentRule.KEEP_RELATIVE,rotation_rule=unreal.AttachmentRule.KEEP_RELATIVE,scale_rule=unreal.AttachmentRule.KEEP_RELATIVE)
    set_root_component_world_rotation(actor_7, 0.000000, 0.000000, 0.000000)
    
    # actor_6 = create_actor_with_label(unreal.Actor, "XIA", unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    # actor_6.attach_to_actor(actor_5,socket_name='',location_rule=unreal.AttachmentRule.KEEP_RELATIVE,rotation_rule=unreal.AttachmentRule.KEEP_RELATIVE,scale_rule=unreal.AttachmentRule.KEEP_RELATIVE)
    # set_root_component_world_rotation(actor_6, 0.000000, 0.000000, 0.000000)
    
    # ---------- 3. 定义光源通用参数 ----------
    lighting_channels = unreal.LightingChannels(channel0=False, channel1=True, channel2=False)
    common_kwargs = {
        "b_allow_mega_lights": False,
        "b_affect_translucent_lighting": False,
        "cast_raytraced_shadow": unreal.CastRayTracedShadow.ENABLED,
        "indirect_lighting_intensity": 0.0,
        "volumetric_scattering_intensity": 0.0,
        "samples_per_pixel": 4
    }
    
    # 定义所有矩形光源数据: (父Actor, 相对位置, 相对旋转, 标签, 宽, 高, 强度, 额外参数)
    # 注意：所有旋转值均按 T3D 中的 Pitch, Yaw, Roll 顺序传入
    lights_data = [
        # 上层光源（父为 SHANG）
        (actor_7, (156.016079, -0.000007, 141.251435), (0.000010, -30.000000, 180.000000), "DING_0", 100, 100, 5.0),
        (actor_7, (110.320025, 110.320040, 141.251426), (0.000007, -30.000000, -135.00000), "DING_45", 100, 100, 5.0),
        (actor_7, (-0.000018, 156.016103, 141.251407), (0.000000, -30.000000, -90.0000), "DING_90", 100, 100, 5.0),
        (actor_7, (-110.320065, 110.320050, 141.251388), (0.000009, -30.00000, -45.00000), "DING_135", 100, 100, 5.0),
        (actor_7, (-156.016129, 0.000007, 141.251380), (0.000000, -30.000000, -0.000000), "DING_180", 100, 100, 5.0),
        (actor_7, (-110.320075, -110.320040, 141.251388), (0.000000, -30.0000, 45.0000), "DING_225", 100, 100, 5.0),
        (actor_7, (-0.000032, -156.016104, 141.251407), (0.0000, -30.000000, 90.00000), "DING_270", 100, 100, 5.0),
        (actor_7, (110.320015, -110.320050, 141.251426), (0.00000, -30.00000, 135.00000), "DING_315", 100, 100, 5.0),
        (actor_7, (81.537887, -0.000007, 184.251421), (0.000000, -60.000010, 180.000000), "DING_DIN", 100, 100, 5.0),
        
        # # 下层光源（父为 XIA）
        # (actor_6, (150.000000, 0.000000, -60.000000), (-0.00000, 30.000, 180.000000), "DI_0", 150, 150, 2.0),
        # (actor_6, (143.418765, 121.888490, -59.999983), (-0.00000, 30.0000, -135.00000), "DI_45", 150, 150, 5.0),
        # (actor_6, (-121.888487, 143.418751, -60.000021), (-0.00000, 30.00000, -45.00000), "DI_135", 150, 150, 5.0),
        # (actor_6, (-143.418741, -121.888497, -60.000025), (0.00000, 30.00000, 45.00000), "DI_225", 150, 150, 5.0),
        # (actor_6, (121.888507, -143.418751, -59.999979), (0.00000, 30.00000, 135.00000), "DI_315", 150, 150, 5.0),
        # (actor_6, (0.000000, -0.000000, -72.000000), (0.000000, 90.000000, 0.000000), "DI_ZHEN", 200, 200, 0.0),
    ]
    
    attenuation_radius = 1000  # 设置一个足够大的衰减半径，确保光照范围覆盖角色
    # 批量生成光
    for data in lights_data:
        parent, loc, rot, label, w, h, intens = data[:7]
        # 构造 Rotator 和 Vector
        rel_loc = unreal.Vector(*loc)
        rel_rot = unreal.Rotator(rot[0], rot[1], rot[2])
        create_rect_light(parent, rel_loc, rel_rot, label, w, h, attenuation_radius, intens, lighting_channels, **common_kwargs)
    
    # 刷新视口
    unreal.EditorLevelLibrary.editor_invalidate_viewports()
    unreal.SystemLibrary.print_string(None, "所有 Actor 创建完成！", text_color=[0,255,0,255])

    lightToCharacter(character_actor, actor_5,socket_name)
    #保存所有文件
    unreal.EditorAssetLibrary.save_directory('/Game')


def lightToCharacter(character_actor, light_actor, socket_name):
    # #在大纲将灯光绑定到角色上
    # base_bones = ['pelvis','Root_M','root']
    # socket_name = ''
    # skeletal_mesh_comp = character_actor.get_component_by_class(unreal.SkeletalMeshComponent)
    # bone_num = skeletal_mesh_comp.get_num_bones()
    # #判断基础骨骼名称
    # for index in range(bone_num):
    #     bone_name = skeletal_mesh_comp.get_bone_name(index)
    #     if bone_name in base_bones:
    #         socket_name = bone_name
    #         break
    
    socket = unreal.Name(socket_name)

    light_actor.attach_to_actor(parent_actor=character_actor,socket_name=socket,location_rule=unreal.AttachmentRule.KEEP_RELATIVE,rotation_rule=unreal.AttachmentRule.KEEP_WORLD,scale_rule=unreal.AttachmentRule.KEEP_RELATIVE)

    #在灯光关卡序列中将灯光绑定到角色
    current_world = unreal.LevelEditorSubsystem().get_current_level().get_world()
    current_world_split = current_world.get_path_name().split('/')
    root_path = current_world.get_path_name().rsplit('/', 1)[0]
    lt_seq_path = f'{root_path}/Light/{current_world_split[5]}_lt'
    if not unreal.EditorAssetLibrary.does_asset_exist(lt_seq_path):
        lt_seq_path = f'{root_path}/Lighting/{current_world_split[5]}_lt'
    render_seq_path = f'{root_path}/{current_world_split[5]}_Render'
    
    if unreal.EditorAssetLibrary.does_asset_exist(render_seq_path) and unreal.EditorAssetLibrary.does_asset_exist(lt_seq_path):
        render_seq = unreal.EditorAssetLibrary.load_asset(render_seq_path)
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(render_seq)
        #从总关卡序列获取lt子关卡序列
        current_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        sub_sequence_tracks = current_sequence.get_tracks()
        lt_sub_sequence = None
        for sub_sequence_track in sub_sequence_tracks:
            try:
                sub_sequence_section = sub_sequence_track.get_sections()[0]
                sub_sequence = sub_sequence_section.get_sequence()
                if '_lt' in sub_sequence.get_name():
                    lt_sub_sequence = sub_sequence
                    break
            except:
                pass
        
        lt_seq = unreal.EditorAssetLibrary.load_asset(lt_seq_path)
        ch_bind = lt_seq.add_possessable(character_actor)
        light_bind = lt_seq.add_possessable(light_actor)

        attach_track = light_bind.add_track(unreal.MovieScene3DAttachTrack)
        attach_section = attach_track.add_section()

        attach_section.set_start_frame_bounded(False)
        attach_section.set_end_frame_bounded(False)

        # 使用 MovieSceneSequenceExtensions 来获取正确的 ID
        # ch_bind_id = unreal.MovieSceneBindingExtensions.get_id(ch_bind)
        ch_bind_id = current_sequence.get_portable_binding_id(destination_sequence=lt_sub_sequence, binding=ch_bind)

        # 创建一个 MovieSceneObjectBindingID 并设置其 Guid
        # constraint_binding_id = unreal.MovieSceneObjectBindingID()
        # constraint_binding_id.set_editor_property('guid', ch_bind_id)

        # 将约束 ID 应用到附加片段上
        attach_section.set_editor_property('constraint_binding_id', ch_bind_id)

        # 指定要附加到的骨骼名称
        attach_section.set_editor_property('attach_socket_name', socket_name)

        unreal.EditorAssetLibrary.save_directory('/Game')



def createLevelLight():
    # ---------- 1. 创建根容器 lightRoot ----------
    light_root = create_actor_with_label(unreal.Actor, "lightRoot", unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    set_root_component_world_rotation(light_root, -0.000000, -90.000000, 90.000000)

    # ---------- 2. 创建 SHANG 和 XIA 并附加到 lightRoot ----------
    shang = create_actor_with_label(unreal.Actor, "SHANG", unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    shang.attach_to_actor(light_root,socket_name='',location_rule=unreal.AttachmentRule.KEEP_RELATIVE,rotation_rule=unreal.AttachmentRule.KEEP_RELATIVE,scale_rule=unreal.AttachmentRule.KEEP_RELATIVE)
    set_root_component_world_rotation(shang, 0.000000, 0.000000, 0.0)

    xia = create_actor_with_label(unreal.Actor, "XIA", unreal.Vector(0,0,0), unreal.Rotator(0,0,0))
    xia.attach_to_actor(light_root,socket_name='',location_rule=unreal.AttachmentRule.KEEP_RELATIVE,rotation_rule=unreal.AttachmentRule.KEEP_RELATIVE,scale_rule=unreal.AttachmentRule.KEEP_RELATIVE)
    set_root_component_world_rotation(xia, 0.000000, 0.000000, 0.0)

    # ---------- 3. 定义光源通用参数 ----------
    lighting_channels = unreal.LightingChannels(channel0=False, channel1=True, channel2=False)
    common_kwargs = {
        "b_allow_mega_lights": False,
        "b_affect_translucent_lighting": False,
        "cast_raytraced_shadow": unreal.CastRayTracedShadow.ENABLED,
        "indirect_lighting_intensity": 0.0,
        "volumetric_scattering_intensity": 0.0,
        "samples_per_pixel": 4
    }

    # ---------- 4. 创建上层聚光源（挂载于 SHANG） ----------
    spotlights_data = [
        # (相对位置, 相对旋转, 标签, 半径, 衰减半径, 强度)
        ((2039.808810, -14.478147, 2330.570231), (0.000000, -30.00000, -180.000000), "D_0", 350, 8500, 400.0),
        ((1655.867098, 881.395435, 2330.570164), (0.00000, -30.00000, -135.000000), "D_45", 350, 8500, 400.0),
        ((750.901024, 1243.385931, 2330.570008), (0.0000, -30.000000, -90.00000), "D_90", 350, 8500, 400.0),
        ((-144.972558, 859.444220, 2330.569851), (0.00000, -30.000000, -45.000000), "D_135", 350, 8500, 400.0),
        ((-506.963056, -45.521855, 2330.569786), (0.000000, -30.000000, -0.000000), "D_180", 350, 8500, 400.0),
        ((-123.021342, -941.395438, 2330.569853), (0.000000, -30.000000, 45.000000), "D_225", 350, 8500, 400.0),
        ((781.944732, -1303.385935, 2330.570009), (0.000000, -30.000000, 90.000000), "D_270", 350, 8500, 400.0),
        ((1677.818316, -919.444221, 2330.570165), (0.000000, -30.000000, 135.000000), "D_315", 350, 8500, 400.0),
        ((1743.676735, -14.478147, 2626.872535), (0.000000, -45.000000, 180.000000), "D_DIN", 350, 8500, 400.0)
    ]

    for loc, rot, label, radius, atten_rad, intens in spotlights_data:
        rel_loc = unreal.Vector(*loc)
        rel_rot = unreal.Rotator(rot[0], rot[1], rot[2])
        create_spot_light(shang, rel_loc, rel_rot, label, radius, atten_rad, intens,
                          lighting_channels, **common_kwargs)

    # ---------- 5. 创建下层矩形光源（挂载于 XIA） ----------
    # 定义暖色 (R=216, G=225, B=255)
    warm_color = unreal.Color(216, 225, 255, 255)

    rectlights_data = [
        # (相对位置, 相对旋转, 标签, 宽, 高, 衰减半径, 强度, 颜色)
        ((1492.821759, 697.793992, 1270.897196), (0.000000, 30.000000, -135.000000), "B_45", 300, 300, 4500, 50.0, warm_color),
        ((38.629071, 696.398697, 1270.896942), (0.000000, 30.000000, -45.000000), "B_135", 300, 300, 4500, 200.0, None),
        ((40.024366, -757.793991, 1270.896941), (0.000000, 30.000000, 45.000000), "B_225", 300, 300, 4500, 200.0, None),
        ((1494.217054, -756.398697, 1270.897199), (0.000000, 30.000000, 135.000000), "B_315", 300, 300, 4500, 200.0, None),
        ((1794.692574, -29.013377, 1270.897247), (0.000000, 30.000000, -180.000000), "B_0", 300, 300, 4500, 50.0, warm_color)
    ]

    for loc, rot, label, w, h, atten_rad, intens, color in rectlights_data:
        rel_loc = unreal.Vector(*loc)
        rel_rot = unreal.Rotator(rot[0], rot[1], rot[2])
        create_rect_light(xia, rel_loc, rel_rot, label, w, h, atten_rad, intens,
                          lighting_channels, light_color=color, **common_kwargs)

    # 刷新视口
    unreal.EditorLevelLibrary.editor_invalidate_viewports()
    unreal.SystemLibrary.print_string(None, "所有灯光 Actor 创建完成！", text_color=[0,255,0,255])





class LightMatrixWin(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.uii()

    def uii(self):   
        self.setWindowTitle('灯光矩阵添加工具')
        self.resize(300,120)
        lay=QtWidgets.QVBoxLayout()

        self.model_radio_group = MRadioButtonGroup()
        self.model_radio_group.set_button_list(['道具使用root骨骼','道具使用foll骨骼'])
        self.model_radio_group.set_dayu_checked(0)

        ch_add_btn = MPushButton('为选中的对象添加灯光矩阵')
        ch_add_btn.clicked.connect(self.addChLight)

        scence_add_btn = MPushButton('为场景添加多人灯光矩阵')
        scence_add_btn.clicked.connect(self.addLevelLight)

        lay.addWidget(self.model_radio_group)
        lay.addWidget(ch_add_btn)
        lay.addWidget(scence_add_btn)
        self.setLayout(lay)


    def addChLight(self):
        base_bones = ['pelvis','Root_M','root']
        foll_bone_basesname = 'foll_'

        if actor_subsystem.get_selected_level_actors():
            character_actors = actor_subsystem.get_selected_level_actors()
            for character_actor in character_actors:
                if character_actor.get_component_by_class().get_class().get_name() == "SkeletalMeshComponent":
                    #在大纲将灯光绑定到角色上
                    socket_names = []
                    skeletal_mesh_comp = character_actor.get_component_by_class(unreal.SkeletalMeshComponent)
                    bone_num = skeletal_mesh_comp.get_num_bones()
                    #判断基础骨骼名称
                    for index in range(bone_num):
                        bone_name = skeletal_mesh_comp.get_bone_name(index)
                        if bone_name in base_bones:
                            socket_names.append(bone_name)
                        elif foll_bone_basesname in str(bone_name):
                            socket_names.append(bone_name)

                    new_socket_names = []
                    if socket_names:
                        #根据选项过滤骨骼，避免添加灯光
                        if self.model_radio_group.get_dayu_checked()==1:    #root 0,foll 1
                            if 'root' in socket_names:
                                socket_names.remove('root')
                                break
                            new_socket_names = socket_names
                        elif self.model_radio_group.get_dayu_checked()==0:
                            for socket_name in socket_names:
                                if foll_bone_basesname not in str(socket_name):
                                    new_socket_names.append(socket_name)

                        print(new_socket_names)
                        for socket_name in new_socket_names:
                            createChLight(character_actor,socket_name)
    
    def addLevelLight(self):
        createLevelLight()







    

def start():
    with application() as app:
        global test
        test = LightMatrixWin()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))


if __name__ == "__main__":
   
   start()





