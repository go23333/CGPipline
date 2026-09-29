import unreal
import re
import os

from Qt import QtCore
from Qt import QtWidgets


from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets.line_edit import MLineEdit
from dayu_widgets.label import MLabel
from dayu_widgets import dayu_theme
from dayu_widgets.qt import application



#创建动画序列
# anim_sequence_factory=unreal.AnimSequenceFactory()
# skeletal_mesh_path='/Game/Assets/Cluster/Cluster_CH/QunJi_KaoShengE_CH/SkeletalMesh/dK_QunJi_KaoShengE_BDWQ.dK_QunJi_KaoShengE_BDWQ'
# skeletal_path='/Game/Assets/Cluster/Cluster_CH/QunJi_KaoShengE_CH/SkeletalMesh/dK_QunJi_KaoShengE_BDWQ_Skeleton.dK_QunJi_KaoShengE_BDWQ_Skeleton'
# skeletal_mesh=unreal.EditorAssetLibrary.find_asset_data(skeletal_mesh_path).get_asset()
# skeletal=unreal.EditorAssetLibrary.find_asset_data(skeletal_path).get_asset()
# anim_sequence_factory.preview_skeletal_mesh=skeletal_mesh
# anim_sequence_factory.target_skeleton=skeletal

# as_path='/Game/Assets/Cluster/BP/Ep003_sc003_054/3-3-54_DaoChu/a1.a1'
# as_asset=unreal.EditorAssetLibrary.find_asset_data(as_path).get_asset()


# actors_bind=export_sequence.get_bindings()
# # export_sequence.add_track(unreal.MovieSceneSkeletalAnimationTrack)
# # export_sequence.add_possessable(unreal.MovieSceneSkeletalAnimationTrack)
# actor_bind=actors_bind[0]
# actor_bind:unreal.MovieSceneBindingProxy

# print(actor_bind.get_tracks()[0])




def sequenceCurrentPath(sequence):
    #获取当前关卡序列
    sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    sequence_asset=unreal.EditorAssetLibrary.find_asset_data(sequence.get_path_name()).get_asset()
    #获取关卡序列的路径位置
    sequence_path=sequence_asset.get_path_name()
    #通过关卡序列的路径位置获取当前文件夹路径
    current_path=sequence_path.rsplit('/',2)[0]

    return current_path


#动画序列链接设置
def anim_sequence_export_options():
    anim_sequence_export_options=unreal.AnimSeqExportOption()
    anim_sequence_export_options.export_transforms=1
    anim_sequence_export_options.export_morph_targets=1
    anim_sequence_export_options.export_attribute_curves=1
    anim_sequence_export_options.record_in_world_space=1
    anim_sequence_export_options.evaluate_all_skeletal_mesh_components=0

    return anim_sequence_export_options


def sequenceFbxExportOption():
    fbx_options=unreal.FbxExportOption()

    fbx_options.fbx_export_compatibility=unreal.FbxExportCompatibility.FBX_2013
    fbx_options.force_front_x_axis=0
    fbx_options.vertex_color=0
    fbx_options.level_of_detail=0
    fbx_options.collision=0
    fbx_options.export_source_mesh=0
    fbx_options.export_morph_targets=0
    fbx_options.export_preview_mesh=0
    fbx_options.map_skeletal_motion_to_root=0
    fbx_options.export_local_time=1

    return fbx_options


def sequenceFbxExportparams(fbx_export_path,export_sequence:unreal.LevelSequence):
    sequence_fbx_params=unreal.SequencerExportFBXParams()
    sequence_fbx_params.fbx_file_name=fbx_export_path
    sequence_fbx_params.bindings=export_sequence.get_bindings()
    sequence_fbx_params.tracks=export_sequence.get_tracks()
    sequence_fbx_params.override_options=sequenceFbxExportOption()
    sequence_fbx_params.sequence=export_sequence
    sequence_fbx_params.root_sequence=export_sequence
    sequence_fbx_params.world=unreal.LayersSubsystem().get_world()

    return sequence_fbx_params



#导出基于关卡序列和当前世界的新动画序列，并且获取动画序列对象和其实结束帧
def exportAnimSequence(sequence,export_path):

    #获取当前世界
    world=unreal.LayersSubsystem().get_world()

    #设置导出动画序列字典
    export_folder_anims={}
    actor_binds=sequence.get_bindings()
    for actor_bind in actor_binds:
        actor_bind:unreal.MovieSceneBindingProxy
        
        #判断轨道类型
        if actor_bind.get_possessed_object_class():
            if actor_bind.get_possessed_object_class().get_name()=='SkeletalMeshComponent':
                #获取bind行号
                bind_index=int(actor_bind.get_parent().get_sorting_order())+1
                #获取父级名称
                bind_parent_name=actor_bind.get_parent().get_display_name()
                #获取骨骼名称
                actor_bind_name=actor_bind.get_display_name()
                #新动画序列名称
                new_anim_name=f'AN_{bind_parent_name}_{actor_bind_name}_{bind_index}'
                print(new_anim_name)
                actor_tracks=actor_bind.get_tracks()

                #通过bind获取tracks
                for actor_track in actor_tracks:
                    actor_track:unreal.MovieSceneTrack
                    
                    #通过track获取sections
                    actor_sections=actor_track.get_sections()

                    for actor_section in actor_sections:
                        actor_section:unreal.MovieSceneSkeletalAnimationSection

                        #判断section是否为MovieSceneSkeletalAnimationSection类型
                        if actor_section.get_class().get_name() == 'MovieSceneSkeletalAnimationSection':
                            #获取section中的animation信息
                            anim_seq=actor_section.params.animation
                            anim_seq_name=anim_seq.get_name()
                            anim_seq_path=anim_seq.get_path_name()
                            print(anim_seq_path)
                            actor_section_start=actor_section.get_start_frame()
                            actor_section_end=actor_section.get_end_frame()
                            print(actor_section_start,actor_section_end)
                            #复制动画到导出文件夹
                            new_anim_seq=unreal.EditorAssetLibrary.duplicate_asset(source_asset_path=anim_seq_path,destination_asset_path=export_path+'/'+new_anim_name)
                            print(new_anim_seq.get_name())
                            export_folder_anims[new_anim_seq]=[actor_section_start,actor_section_end]
                            #连接变换到新动画序列
                            unreal.SequencerTools.export_anim_sequence(world=world,sequence=sequence,anim_sequence=new_anim_seq,export_option=anim_sequence_export_options(),binding=actor_bind,create_link=1)
        
    return export_folder_anims
            

#通过动画序列生成新的关卡序列
def animSequenceToLevelSequence(export_folder_anims,base_name,creat_path):

    #判断用于导出的关卡序列是否已存在，因存在的话修改后缀名称后创建
    export_level_sequnce_name=base_name+'_LevelSequence'
    export_level_sequnce_name_i=export_level_sequnce_name

    i=1
    while unreal.EditorAssetLibrary.does_asset_exist(creat_path+'/'+export_level_sequnce_name_i):
        export_level_sequnce_name_i=export_level_sequnce_name+'_'+str(i)
        i+=1

    export_level_sequnce_name=export_level_sequnce_name_i

    #创建新场景序列并打开
    export_level_sequnce=unreal.AssetToolsHelpers.get_asset_tools().create_asset(asset_name=export_level_sequnce_name,package_path=creat_path,asset_class=unreal.LevelSequence,factory=unreal.LevelSequenceFactoryNew())
    export_level_sequnce.set_display_rate((25,1))
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(export_level_sequnce)
    #获取当前打开的关卡序列
    export_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()

    #导入当前动画序列
    for export_folder_anim,start_end in export_folder_anims.items():
        if export_folder_anim.get_class().get_name()=='AnimSequence':
            #将动画序列添加到当前场景序列中
            spawnable_obj=export_sequence.add_spawnable_from_instance(export_folder_anim)
            spawnable_obj.get_tracks()[0].add_section()
            # 添加animation track
            animation_track=spawnable_obj.add_track(unreal.MovieSceneSkeletalAnimationTrack)
            animation_section=animation_track.add_section()
            animation_section:unreal.MovieSceneSkeletalAnimationSection
            animation_section.params.animation=export_folder_anim
            #从第0帧到所获取的源关卡序列结束帧
            animation_section.set_range(0,start_end[1])
            #添加transform track
            transform_track=spawnable_obj.add_track(unreal.MovieSceneTransformTrack)
            transform_track.set_display_name('Transform')
            transform_track.add_section()
    
    return export_sequence




class mw(QtWidgets.QWidget, MFieldMixin):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.ui()

    def ui(self):   
        self.setWindowTitle('群集_通过关卡序列导出FBX文件')
        self.resize(380,150)
        lay=QtWidgets.QVBoxLayout()

        folder_lay=QtWidgets.QVBoxLayout()


        notice_label=MLabel('使用前需手动拖动修改关卡序列中的对象顺序,否则会影响名称生成')

        #只生成关卡序列
        create_seq_btn=MPushButton(text="只创建新关卡序列")
        create_seq_btn.clicked.connect(lambda:self.execute(fbx_export_switch=False))#不启用fbx导出

        #导出文件
        self.flie_export=MLineEdit().save_file(filters=['fbx']).medium()
        self.flie_export.setPlaceholderText(self.tr("选择FBX导出目录"))

        export_fbx_btn=MPushButton(text="创建新关卡序列并导出到FBX")
        export_fbx_btn.clicked.connect(lambda:self.execute(fbx_export_switch=True))#启用fbx导出

        self.error_label=MLabel('')
        self.error_label.setStyleSheet('color: red;')

        folder_lay.addWidget(notice_label)
        folder_lay.addWidget(create_seq_btn)
        folder_lay.addWidget(self.flie_export)
        folder_lay.addWidget(export_fbx_btn)
        folder_lay.addWidget(self.error_label)

        import_lay=QtWidgets.QVBoxLayout()
        


        lay.addLayout(folder_lay)
        lay.addLayout(import_lay)
        self.setLayout(lay)

    def createNewLevelSequence(self):
        #获取当前level sequence
        start_level_sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        #生成动画导出的路径名称
        current_parent_path=sequenceCurrentPath(start_level_sequence)
        #去掉无用字符
        sequence_counts=re.sub(r'[a-zA-Z]','',current_parent_path.split('/')[-1]).split('_')
        #根据当前文件名称生成新关卡序列名称
        if len(sequence_counts)==3:
            item_count=''
            for count in sequence_counts:
                #去除有效数字前的0后转为str累加
                item_count+=str(int(count))+'-'
            item_count=item_count.rsplit('-',1)[0]
            new_seq_name=item_count+'_DaoChu'
        else:
            new_seq_name=current_parent_path.split('/')[-1]+'_DaoChu'

        new_seq_path=current_parent_path+'/'+new_seq_name

        #如果路径不存在就创建导出文件夹
        if not unreal.EditorAssetLibrary.does_directory_exist(new_seq_path):
            unreal.EditorAssetLibrary.make_directory(new_seq_path)

        #导出基于关卡序列和当前世界的新动画序列，并且获取动画序列对象和其实结束帧
        export_anim_seqs_dict=exportAnimSequence(start_level_sequence,new_seq_path)

        #保存动画序列
        unreal.EditorAssetLibrary.save_directory(new_seq_path)

        #基于动画序列生成关卡序列
        export_sequence=animSequenceToLevelSequence(export_anim_seqs_dict,new_seq_name,new_seq_path)

        #保存
        unreal.EditorAssetLibrary.save_directory(new_seq_path)

        return export_sequence
        


    def execute(self,fbx_export_switch:bool):

        #保存所有文件
        unreal.EditorAssetLibrary.save_directory('/Game')

        #规范化路径格式
        fbx_export_path=self.flie_export.text().replace('\\','/')
        fbx_legal=0

        #判断文件夹是否存在，不存在则不运行程序
        if os.path.exists(fbx_export_path.rsplit('/',1)[0]):
            fbx_legal=1

        #判断是否导出FBX文件
        if fbx_export_switch:

            #判断fbx导出输入框是否合法
            if fbx_legal==1:

                #清空错误提示
                self.error_label.setText('')

                #判断fbx后缀是否合法，不合法的话添加后缀
                path_suffix=fbx_export_path.split('.')[-1]
                suffix_name='fbx'
                if str(path_suffix).lower()!=suffix_name.lower():
                    fbx_export_path=fbx_export_path+'.fbx'

                #创建包含新动画的新关卡序列并获取关卡序列名称
                export_sequence=self.createNewLevelSequence()

                #导出FBX
                unreal.SequencerTools.export_level_sequence_fbx(sequenceFbxExportparams(fbx_export_path,export_sequence))   
            
            else:
                self.error_label.setText('路径不合法,请检查路径')

        else:
            #创建包含新动画的新关卡序列
            self.createNewLevelSequence()



def start():
    with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))



if __name__ == "__main__":
    with application() as app:
        global test
        test = mw()
        dayu_theme.apply(test)
        test.show()
        unreal.parent_external_window_to_slate(int(test.winId()))