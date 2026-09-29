# -*-coding:utf-8 -*-
from maya import cmds

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from mayaTools.rig.freefk import U as objtypes
from mayaTools.rig.freefk import shi as create_control
from mayaTools.rig.freefk import main as nb
from mayaTools.rig.freefk import Y as dyn
from mayaTools.rig.freefk import N as abs_
from mayaTools.rig.freefk import xi as sc
from mayaTools.rig.freefk import qiu as match
from mayaTools.rig.freefk import A as create_suface_v


if not cmds.pluginInfo( 'quatNodes.mll', query=1,l=1):
    cmds.loadPlugin('quatNodes.mll')


def create_follicle(folliclename,u=0.5,v=0):
    follicle_node=recreate_node('follicle')
    follicle_node_uuid=get_uuid(follicle_node)

    follicle_node_trans = cmds.listRelatives(follicle_node, p=True)[0]
    follicle_node_trans_uuid = get_uuid(follicle_node_trans)
    follicle_node_trans=cmds.rename(follicle_node_trans, folliclename)
    follicle_node=cmds.rename(find_uuid(follicle_node_uuid), folliclename+'_real')
    follicle_node=find_uuid(follicle_node_uuid)
    cmds.setAttr(follicle_node_trans+'.parameterU',u)
    cmds.setAttr(follicle_node_trans+'.parameterV',v)
    cmds.connectAttr(follicle_node+'.outRotate',follicle_node_trans+'.rotate')
    cmds.connectAttr(follicle_node+'.outTranslate',follicle_node_trans+'.translate')
    cmds.hide(follicle_node_trans)
    return follicle_node,follicle_node_trans,follicle_node_uuid,follicle_node_trans_uuid
def get_uuid(obj):
    object_uuid = cmds.ls(obj, o=1, uuid=1)[0]
    return object_uuid
def find_uuid(uuid):
    uuid_list = cmds.ls(uuid)[0]
    return uuid_list
all_Nodes=[]
all_attrs=[]
def recreate_node(type,name=None):
    if name:
        node=cmds.createNode(type,name=name)
    else:
        node=cmds.createNode(type)
    all_Nodes.append(node)
    return node
def readd_nb(node,attr):
    attrs=nb.addAttr_nb(node,attr)
    all_attrs.append(attrs)
def connect_SurfacetoFollicle(surf_uuid,follicle_uuid):
    surf=find_uuid(surf_uuid)
    follicle=find_uuid(follicle_uuid)
    cmds.connectAttr(surf+'.local',follicle+'.inputSurface')
    cmds.connectAttr(surf+'.worldMatrix[0]',follicle+'.inputWorldMatrix')


def fuyuan(value,Surface_uuid,bones,bone_uuids,namme):
    global all_Nodes,all_attrs
    Surface_name=find_uuid(Surface_uuid)


    bone_rotall = []
    add_scale =[]
    root_grp=recreate_node('transform',name='ctrl_{}_grp'.format(namme))
    readd_nb(root_grp, [['Scale_minX', 'float', [0.01, 1, 100, True]]
        , ['Scale_minY', 'float', [0.01, 1, 100, True]]
        , ['Scale_minZ', 'float', [0.01, 1, 100, True]]
        , ['Scale_maxX', 'float', [0, 1, 9999, True]]
         , ['Scale_maxY', 'float', [0, 9999, 9999, True]]
         , ['Scale_maxZ', 'float', [0, 9999, 9999, True]]])
    cmds.matchTransform(root_grp, Surface_name, position=True, rotation=True)

    for bname ,pshu in zip(bones,range(len(bone_uuids))):

        readd_nb(bname,[['exc_rotX','float',[-9999,0,9999,True]],
                             ['exc_rotY','float',[-9999,0,9999,True]],
                             ['exc_rotZ','float',[-9999,0,9999,True]],
                             ['exc_ScaleX','float',[-9999,0,9999,True]],
                             ['exc_ScaleY','float',[-9999,0,9999,True]],
                             ['exc_ScaleZ','float',[-9999,0,9999,True]]])
        realrot_=recreate_node('plusMinusAverage',name='realrot_{}'.format(bname))
        realSCale_=recreate_node('plusMinusAverage', name='realSCale_{}'.format(bname))
        cmds.connectAttr(bname+'.exc_rotX',realrot_+'.input3D[0].input3Dx')
        cmds.connectAttr(bname+'.exc_rotY',realrot_+'.input3D[0].input3Dy')
        cmds.connectAttr(bname+'.exc_rotZ',realrot_+'.input3D[0].input3Dz')
        cmds.connectAttr(bname + '.exc_ScaleX', realSCale_ + '.input3D[0].input3Dx')
        cmds.connectAttr(bname + '.exc_ScaleY', realSCale_ + '.input3D[0].input3Dy')
        cmds.connectAttr(bname + '.exc_ScaleZ', realSCale_ + '.input3D[0].input3Dz')
        cmds.connectAttr(realrot_ + '.output3D', bname + '.rotate')
        cmds.connectAttr(realSCale_ + '.output3D', bname + '.scale')
        jishu=100/len(bone_uuids)
        readd_nb(bname,[['bone_position','float',[0,jishu*(pshu+1),100,False]]])
        rotall=recreate_node('plusMinusAverage',name='rotall_{}'.format(bname))
        bone_rotall.append(rotall)
        cmds.connectAttr(rotall + '.output3D', realrot_ + '.input3D[1]')
        add_scale_=recreate_node('plusMinusAverage',name='add_scale_{}'.format(bname))
        add_scale.append(add_scale_)
        clamp_scale = recreate_node('clamp', name='clamp{}'.format(bname))
        cmds.connectAttr(root_grp + '.Scale_maxX', clamp_scale + '.maxR')
        cmds.connectAttr(root_grp + '.Scale_maxY', clamp_scale + '.maxG')
        cmds.connectAttr(root_grp + '.Scale_maxZ', clamp_scale + '.maxB')
        cmds.connectAttr(root_grp + '.Scale_minX', clamp_scale + '.minR')
        cmds.connectAttr(root_grp + '.Scale_minY', clamp_scale + '.minG')
        cmds.connectAttr(root_grp + '.Scale_minZ', clamp_scale + '.minB')

        cmds.connectAttr(add_scale_ + '.output3D', clamp_scale + '.input')
        cmds.connectAttr(clamp_scale + '.output',realSCale_+'.input3D[1]')



    for i in range(value):

        follicle_node,follicle_node_trans,follicle_node_uuid,follicle_node_trans_uuid = create_follicle('follicle_{}_{:03d}'.format(Surface_name,i+1))
        create_control.create_control(namme, side='m', index=i+1, pos=follicle_node, parent=root_grp,
                                      lock_hide=None, rotate_order=0, shape=u'方块', size=5)
        diver_ = create_control.glb_driven()
        ctrl_ = create_control.glb_ctrl()
        zero_ = create_control.glb_zero()
        sub_ = create_control.glb_output()
        subctrl=create_control.glb_sub_ctrl()
        readd_nb(ctrl_, [['scale_minus_one', 'enum', [u'关闭',u'打开']],['follicle_V_value', 'float', [0, 0, 100, True]],['distance', 'float', [0, 0, 9999, True]]])

        sp_value = 1.0 / value
        cmds.setAttr(ctrl_ + '.follicle_V_value', i * sp_value * 100)

        multDoubleLinear001=recreate_node('multDoubleLinear',name='multDoubleLinear_follicle_{}_{}'.format(Surface_name,i+1))
        cmds.setAttr(multDoubleLinear001+'.input2',0.01)
        cmds.connectAttr(ctrl_+'.follicle_V_value',multDoubleLinear001+'.input1')
        cmds.connectAttr(multDoubleLinear001+'.output',follicle_node_trans+'.parameterV')
        connect_SurfacetoFollicle(Surface_uuid,follicle_node_uuid)

        add_ctrl_sub = recreate_node('plusMinusAverage', name='addall{}_to_{}'.format(ctrl_, sub_))
        cmds.connectAttr(ctrl_ + '.rotate', add_ctrl_sub + '.input3D[0]')
        cmds.connectAttr(sub_ + '.rotate', add_ctrl_sub + '.input3D[1]')

        add_ctrl_sub_scale = recreate_node('multiplyDivide', name='ctrlsub_multe{}_to_{}'.format(ctrl_, sub_))
        cmds.connectAttr(ctrl_ + '.scale', add_ctrl_sub_scale + '.input1')
        cmds.connectAttr(sub_ + '.scale', add_ctrl_sub_scale + '.input2')
        outctrlminus = recreate_node('plusMinusAverage', name='{}minus'.format(ctrl_))
        cmds.setAttr(outctrlminus + '.operation', 2)
        cmds.connectAttr(add_ctrl_sub_scale + '.output', outctrlminus + '.input3D[0]')
        cmds.connectAttr(ctrl_ + '.scale_minus_one',outctrlminus + '.input3D[1].input3Dx')
        cmds.connectAttr(ctrl_ + '.scale_minus_one',outctrlminus + '.input3D[1].input3Dy')
        cmds.connectAttr(ctrl_ + '.scale_minus_one',outctrlminus + '.input3D[1].input3Dz')
        for bs, shu in zip(bone_uuids,range(len(bone_uuids))):
            bone_ing=find_uuid(bs)

            addDoubleLinear001 = recreate_node('addDoubleLinear', name='addDoubleLinear{}_{}'.format(ctrl_, bone_ing))
            cmds.connectAttr(ctrl_+'.distance', addDoubleLinear001 + '.input1')
            cmds.setAttr(addDoubleLinear001 + '.input2', 0.01)

            abss=abs_.abs_connect([ctrl_ + '.follicle_V_value',bone_ing+'.bone_position' ], 1,add=False)
            abs_outattr=abss + '.outColorR'
            clamp = recreate_node('clamp', name='clamp_{}_to_{}'.format(ctrl_, bone_ing))
            cmds.connectAttr(addDoubleLinear001+'.output',clamp+'.maxR')
            cmds.setAttr(clamp+'.minR',0.01)
            cmds.connectAttr(abs_outattr,clamp+'.inputR')
            multiplyDivide001=recreate_node('multiplyDivide', name='multiply001{}_to_{}'.format(ctrl_, bone_ing))
            cmds.setAttr(multiplyDivide001+'.operation',2)
            cmds.connectAttr(clamp+'.outputR',multiplyDivide001+'.input1X')
            cmds.connectAttr(addDoubleLinear001+'.output',multiplyDivide001+'.input2X')
            cos_value=sc.scin(multiplyDivide001+'.outputX',None,sin=False,cos=True,valueScale=1)
            ratio_rot=recreate_node('multiplyDivide',name='rottt{}_to_{}'.format(ctrl_,bone_ing))
            cmds.connectAttr(cos_value,ratio_rot+'.input2X')
            cmds.connectAttr(cos_value,ratio_rot+'.input2Y')
            cmds.connectAttr(cos_value,ratio_rot+'.input2Z')
            cmds.connectAttr(add_ctrl_sub + '.output3D', ratio_rot + '.input1')
            dyn.main(ratio_rot + '.output', bone_rotall[shu], attr='input3D', new=True, disconnect=False, pz=False)
            ratio_scale = recreate_node('multiplyDivide', name='scaleee{}_to_{}'.format(ctrl_, bone_ing))
            cmds.connectAttr(cos_value, ratio_scale + '.input2X')
            cmds.connectAttr(cos_value, ratio_scale + '.input2Y')
            cmds.connectAttr(cos_value, ratio_scale + '.input2Z')
            cmds.connectAttr(outctrlminus+'.output3D',ratio_scale+'.input1')
            dyn.main(ratio_scale+'.output', add_scale[shu], attr='input3D', new=True, disconnect=False, pz=False)
        match.match_axes_and_position(diver_,follicle_node_trans,axis_match=['xy','yz'])
        pa = cmds.parentConstraint(follicle_node_trans, diver_, maintainOffset=True)[0]
        cmds.setAttr(pa + '.interpType', 2)
        print(u'打开偏移')
        cmds.parent(follicle_node_trans, zero_)


def delete_all():
    global all_Nodes,all_attrs
    print(u"删除所有")
    print(all_Nodes)
    print(all_attrs)
    for node in all_Nodes:
        try:
            cmds.delete(node)
        except ValueError:
            pass
        except RuntimeError:
            pass
    all_Nodes=[]
    for attr in all_attrs:
        for attr_ in attr:
            if '|' in attr_:
                attr_=attr_.split('|')[-1]
            else:
                pass
            try:
                cmds.deleteAttr(attr_)
            except ValueError:
                pass
            except RuntimeError:
                pass
    all_attrs=[]

def Q_add(Layout,*args):
    for i in args:
        if isinstance(i,QLayout):
            Layout.addLayout(i)
        elif isinstance(i,QWidget):
            Layout.addWidget(i)

    return Layout
def Q_but(tests,result,width=None):
    but=QPushButton(tests)
    if width:
        but.setFixedWidth(width)
    if result :
        but.clicked.connect(result)
    return but
def Q_Label(string,align=u'居中对齐'):
    label=QLabel(string)
    alignment_mapper = {
        u'左对齐': Qt.AlignLeft,
        u'右对齐': Qt.AlignRight,
        u'顶部对齐': Qt.AlignTop,
        u'底部对齐': Qt.AlignBottom,
        u'居中对齐': Qt.AlignCenter,
        u'两端对齐': Qt.AlignJustify,
        u'右上对齐': Qt.AlignRight | Qt.AlignTop,
        u'左下对齐': Qt.AlignLeft | Qt.AlignBottom,
        u'右下对齐': Qt.AlignRight | Qt.AlignBottom,
        u'左上对齐': Qt.AlignLeft | Qt.AlignTop

    }

    alignment_flag = alignment_mapper.get(align, Qt.AlignCenter)  # 默认是居中对齐
    label.setAlignment(alignment_flag)
    return label

def Q_line(placeholder='',connect=None,types=u'编辑完成',align=u'左对齐'):
    line=QLineEdit()
    line.setText(placeholder)
    alignment_mapper = {
        u'左对齐': Qt.AlignLeft,
        u'右对齐': Qt.AlignRight,
        u'顶部对齐': Qt.AlignTop,
        u'底部对齐': Qt.AlignBottom,
        u'居中对齐': Qt.AlignCenter,
        u'两端对齐': Qt.AlignJustify,
        u'右上对齐': Qt.AlignRight | Qt.AlignTop,
        u'左下对齐': Qt.AlignLeft | Qt.AlignBottom,
        u'右下对齐': Qt.AlignRight | Qt.AlignBottom,
        u'左上对齐': Qt.AlignLeft | Qt.AlignTop

    }

    alignment_flag = alignment_mapper.get(align, Qt.AlignCenter)  # 默认是居中对齐
    line.setAlignment(alignment_flag)

    if connect:
        signal_mapper = {
        u'光标变位': line.cursorPositionChanged,
        u'编辑完成': line.editingFinished,
        u'回车按下': line.returnPressed,
        u'选择变化': line.selectionChanged,
        u'文本变化': line.textChanged,
        u'文本编辑': line.textEdited,

        }
        signal_to_connect = signal_mapper.get(types)
        if signal_to_connect:
            signal_to_connect.connect(connect)
        else:
            print("Warning: Unknown signal type '{}'".format(types))
    return line

def Q_Stretch(args,stretch=QVBoxLayout(),scale=None,sort=None):

    Stretch_lay=stretch

    if sort==1 or sort==2:
        Stretch_lay.addStretch()

    for i in args:
        Stretch_lay.addWidget(i)
    if sort==0 or sort==2:
        Stretch_lay.addStretch()
    if scale:
        for s001,s002 in enumerate(scale):
            Stretch_lay.setStretch(s001,s002)

    return Stretch_lay
def Q_slider_with_spinbox(min_value=0, max_value=100, default_value=0, connect=None):

    container = QWidget()
    layout = QHBoxLayout(container)

    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(min_value)
    slider.setMaximum(max_value)
    slider.setValue(default_value)

    spinbox = QDoubleSpinBox()
    spinbox.setMinimum(min_value)
    spinbox.setMaximum(max_value)
    spinbox.setValue(default_value)
    spinbox.setDecimals(0)  # 设置小数点后保留的位数，可根据需要调整

    def update_spinbox(value):
        spinbox.setValue(value)
        if connect:
            connect(value)  # 调用外部传入的回调函数

    slider.valueChanged.connect(update_spinbox)

    def update_slider(value):
        slider.setValue(int(value))  # 假设滑块只接受整数值，可根据需要调整转换逻辑

    spinbox.valueChanged.connect(update_slider)

    layout.addWidget(slider)
    layout.addWidget(spinbox)

    return container,spinbox# endregion
def Q_menu(menu_name='', content=None):
    if content is None:
        content = []
    menu_bar = QMenuBar()
    menu = menu_bar.addMenu(menu_name)
    for item in content:
        if isinstance(item, QAction):
            menu.addAction(item)
        elif isinstance(item, QWidgetAction):
            menu.addAction(item)
        elif isinstance(item, QWidget):
            widget_action = QWidgetAction(menu_bar)
            widget_action.setDefaultWidget(item)
            menu.addAction(widget_action)
    return menu_bar
class class_win(MayaQWidgetDockableMixin,QWidget):
    def __init__(self,parent=None):
        super(class_win,self).__init__(parent)
        self.resize(400,300)
        self.setWindowTitle(u'自由fk')
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.surface_uuid=None
        self.value=0
        self.real_bones=[]
        self.real_bones_uuid = []
        self.name=None

        self.add_surface_text=Q_line(placeholder='')
        self.slider_follicle=Q_slider_with_spinbox(min_value=0, max_value=50, default_value=0,connect=self.ff_create_ctrl)[0]
        self.okk=Q_but(u'创建',result=self.ff_ok)
        self.delete=Q_but(u'删除',result=self.ff_delete)
        self.statistics_bones_text=Q_line(placeholder='')
        self.statistics_bones=Q_but(u'统计骨骼',result=self.ff_statistics_bones)
        self.table_name=Q_Label(u'请输入名字')
        self.rename_ctrl=Q_line('',connect=self.ff_rename)
        self.create_suf=Q_but(u'创建曲面',result=self.ff_create_suf)
        Q_add(
              self.layout(),
              Q_Stretch([self.table_name,self.rename_ctrl],stretch=QHBoxLayout(), scale=[1,2]),
              Q_Stretch([self.statistics_bones_text,self.statistics_bones],stretch=QHBoxLayout(), scale=[3,1]),
              Q_Stretch([self.add_surface_text, self.create_suf], stretch=QHBoxLayout(), scale=[3, 1]),
              self.slider_follicle,Q_Stretch([self.delete,self.okk],stretch=QHBoxLayout(), scale=[3,1])
              )
    def ff_create_suf(self):
        if self.real_bones:
            sufing=create_suface_v.create_flat_surface_from_joint_chain(self.real_bones,self.name)
            self.add_surface_text.setText(sufing)
            surface_uuid = get_uuid(sufing)
            self.surface_uuid = surface_uuid
            Surface_name = find_uuid(self.surface_uuid)

        else:
            print(u'请先加载骨骼')
            self.surface_uuid =None

    def ff_rename(self):
        self.name=self.rename_ctrl.text()
        print(u'当前命名',self.name)
    def ff_ok(self):
        if self.surface_uuid == None or self.value == 0 or self.real_bones == [] or self.name == None:
            print(u'请先完成所有步骤')
        else:
            fuyuan(self.value, self.surface_uuid,self.real_bones,self.real_bones_uuid,self.name)
    def ff_delete(self):
        print(u'删除freefk')
        delete_all()
        cmds.delete(find_uuid(self.surface_uuid))
        self.add_surface_text.setText('')
        self.surface_uuid = None
        self.real_bones = []
        self.real_bones_uuid = []
        self.name = None

    def ff_create_ctrl(self,value):
        self.value=value
        print(self.value)
    def ff_statistics_bones(self):
        wait_select_bones=cmds.ls(sl=True)
        if wait_select_bones:
            self.real_bones=[]
            self.real_bones_uuid=[]
            for bb in wait_select_bones:
                if objtypes.get_object_type(bb)[0] == 'joint':
                    self.real_bones.append(bb)
                    self.real_bones_uuid.append(get_uuid(bb))
            statistics=len(self.real_bones)
            print(u'选中的骨骼有{}个'.format(statistics))
            self.statistics_bones_text.setText(u'选中的骨骼有{}个'.format(statistics))
        else:
            print(u'请选择骨骼')
            self.real_bones = []
            self.real_bones_uuid=[]
            self.statistics_bones_text.setText('')



window=None
def showUI():
    global window
    window=class_win()
    window.show()

if __name__ == '__main__':
    from mayaTools import reloadModule
    reloadModule()
    showUI()
    # from mayaTools.rig.freefk import F
    # F.get_shape(u"方块","dwad")

