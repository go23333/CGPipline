#coding=utf-8
#auther=zcx
#data=20220721

from imp import reload

#导入自定义模块
import lib.mayaLibrary as ML
#导入标准模块
import maya.cmds as cmds

reload(ML)
import lib.pathLibrary as PL

reload(PL)


class xgentoolsUI:
    def __init__(self):
        if cmds.window('xgentool',ex=1):
            cmds.deleteUI('xgentool',window=True)
        self.window = cmds.window('xgentool',title=u"Xgen工具",widthHeight=[400,250])
        # process Layout
        MainLayout = cmds.columnLayout( p=self.window,adjustableColumn=True)

        
        frame_xgen_exprort = cmds.frameLayout('xgenexport',l=u'Xgen批量导出工具',cll=1,cl=0,w=400,p=MainLayout)
        cmds.separator()
        BTN_conver_to_interactive = cmds.button(l=u'将选中转换为交互式',p=frame_xgen_exprort,c = self.convert_to_interactive)
        cmds.separator()
        rowlayout_FileName = cmds.rowLayout(numberOfColumns= 2,adjustableColumn=2,p=frame_xgen_exprort,height = 20)
        cmds.text(l=u'输入导出文件名称: ',p=rowlayout_FileName,al='left')
        self.tf_file_name = cmds.textField(p=rowlayout_FileName)
        rowlayout_Path = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=frame_xgen_exprort,height = 20)
        cmds.text(l=u'选择导出路径: ',p=rowlayout_Path,al='left')
        self.tf_export_path = cmds.textField(p=rowlayout_Path,cc = lambda *arg:self.recorrectPath(self.tf_export_path))
        BTN_PickPath = cmds.button(l=u'选择路径',p=rowlayout_Path,c=lambda *arg: ML.fileDialog(u'选择贴图路径',3,self.tf_export_path))
        BTN_export_groom = cmds.button(l=u'导出选中的交互式毛发',p=frame_xgen_exprort,c = self.export_groom)
    def convert_to_interactive(self,arg):
        cmds.xgmGroomConvert(prefix="")
    def export_groom(self,arg):
        #临时目录
        tempabc = r"d:\temp.abc"
        # 第一次导出
        SLobjects = ML.getSelectNodes(True)
        ML.exportxgenABC(tempabc,SLobjects,0,0)
        # 反倒入回maya
        newnodes = ML.importgroomabc(tempabc)
        crvenodes = []
        for node in newnodes:
           if cmds.nodeType(node) == 'transform' and cmds.listRelatives(node,type = 'nurbsCurve'):
                crvenodes.append(node)
        # 添加ID信息
        attr_name = 'groom_group_id'
        for groom_group_id, group_name in enumerate(crvenodes):

            # 获取xgGroom下的曲线
            curves = cmds.listRelatives(group_name, ad=True, type='nurbsCurve')

            # 用组id标记组
            cmds.addAttr(group_name, longName=attr_name, attributeType='short', defaultValue=groom_group_id, keyable=True)

            # 添加属性范围
            # 强制Maya的alembic将数据导出为GeometryScope::kConstantScope
            cmds.addAttr(group_name, longName='{}_AbcGeomScope'.format(attr_name), dataType='string', keyable=True)
            cmds.setAttr('{}.{}_AbcGeomScope'.format(group_name, attr_name), 'con', type='string')
        # 导出Groom曲线
        # 将要导出的曲线添加到新的组中,同时将曲线节点新的名字保存在一个列表中
        curgroup = cmds.createNode( 'transform', n='forcurexportgroup' )
        newnamenodes = []
        for crvenode in crvenodes:
            newnamenodes.append(cmds.parent(crvenode,curgroup))
        path = cmds.textField(self.tf_export_path,q=1,text=1)
        filename = cmds.textField(self.tf_file_name,q=1,text=1)+'.abc'
        ML.exportABC_gromm(curgroup,0,0,path+filename)
        # 删除多余节点
        fordeletelist = newnodes+newnamenodes
        fordeletelist.append(curgroup)
        for node in fordeletelist:
            try:
                cmds.delete(node)
            except:
                pass
    def recorrectPath(self,target):
        path = cmds.textField(target,text=1,q=1)
        cmds.textField(target,text=PL.normailizePath(path),e=1)
    def show(self):
        cmds.showWindow(self.window)
def xgentoolsMain():
    UI = xgentoolsUI()
    UI.show()