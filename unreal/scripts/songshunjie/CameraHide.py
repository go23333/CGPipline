import unreal

from Qt import QtCore
from Qt import QtWidgets

from dayu_widgets.field_mixin import MFieldMixin
from dayu_widgets.push_button import MPushButton
from dayu_widgets import MRadioButton, dayu_theme
from dayu_widgets.qt import application


print('Hide actor')


class mw(QtWidgets.QWidget, MFieldMixin):

    #功能开关
    hide_switch=1

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.uii()

    def uii(self):   
        self.setWindowTitle('为镜头隐藏actor')
        self.resize(260,120)
        lay=QtWidgets.QVBoxLayout()

        radio_lay=QtWidgets.QHBoxLayout()
        execute_lay=QtWidgets.QVBoxLayout()

        #创建功能切换按钮
        radio_hide=MRadioButton("隐藏")
        radio_hide.clicked.connect(self.switchoverHide)
        radio_hide.setChecked(True)
        radio_show=MRadioButton("显示")
        radio_show.clicked.connect(self.switchoverShow)

        radio_lay.addWidget(radio_hide)
        radio_lay.addWidget(radio_show)

        #执行按钮
        create_base_folder=MPushButton(text="执行")
        create_base_folder.clicked.connect(self.execute)
        execute_lay.addWidget(create_base_folder)
 

        
        lay.addLayout(radio_lay)
        lay.addLayout(execute_lay)
        
        self.setLayout(lay)

    def switchoverHide(self):
        self.hide_switch=1

    def switchoverShow(self):
        self.hide_switch=0
    

    def execute(self):

        #获取当前选择的actor
        actors=unreal.EditorActorSubsystem().get_selected_level_actors()

        #判断是否选择了actor
        if actors:

            if self.hide_switch==1:
                for actor in actors:
                    
                    #获取当前关卡序列
                    sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
                    #关闭当前关卡序列的锁定
                    unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(0)
                    #添加actor到关卡序列中
                    actor_bind=sequence.add_possessable(actor)

                    hidden_track=''
                    actor_bind_traks=actor_bind.get_tracks()
                    for actor_bind_trak in actor_bind_traks:
                        if actor_bind_trak.get_class().get_name()=='MovieSceneVisibilityTrack':
                            hidden_track=actor_bind_trak
                            hidden_section=hidden_track.get_sections()[0]
                            hidden_key=hidden_section.get_all_channels()[0]
                            # print(hidden_section[0])
                            break
                    
                    if not hidden_track:
                        #创建可视性track
                        hidden_track=actor_bind.add_track(unreal.MovieSceneVisibilityTrack)
                        hidden_track.set_property_name_and_path('ActorHidden', 'ActorHidden')
                        #创建bool选项框
                        hidden_section=hidden_track.add_section()
                        #设置起始帧
                        hidden_section.set_start_frame_seconds(0)
                        #设置可视性选项框去√
                        hidden_key=hidden_section.get_all_channels()[0]
                    hidden_key.add_key(unreal.FrameNumber(0),False)
            if self.hide_switch==0:
                for actor in actors:
                    actor:unreal.Actor
                    #获取当前关卡序列
                    sequence=unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
                    #关闭当前关卡序列的锁定
                    unreal.LevelSequenceEditorBlueprintLibrary.set_lock_level_sequence(0)
                    actors_bind=sequence.get_possessables()
                    #遍历所有轨道
                    for actor_bind in actors_bind:
                        actor_bind:unreal.MovieSceneBindingProxy
                        #对比actor名称
                        if actor_bind.get_name()==actor.get_actor_label():
                            #获取所有track
                            actor_bind_traks=actor_bind.get_tracks()
                            for actor_bind_trak in actor_bind_traks:
                                #判断是否含有可视性开关
                                if actor_bind_trak.get_class().get_name()=='MovieSceneVisibilityTrack':
                                    #删除可视性开关轨道
                                    actor_bind.remove_track(actor_bind_trak)



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




