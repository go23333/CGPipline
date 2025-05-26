#coding=utf-8
import maya.cmds as cmds

#导入自定义模块
import mayaTools.core.mayaLibrary as ML
import mayaTools.core.pathLibrary as PL

class abcExportToolUI:
    def __init__(self):
        if cmds.window('abcExportToolUI',ex=1):
            cmds.deleteUI('abcExportToolUI',window=True)
        self.window = cmds.window('abcExportToolUI',title=u"ABC导出工具")
        # process Layout
        MainLayout = cmds.columnLayout( adjustableColumn=True ,w=400,h=200,p=self.window)
        rowlayout_AutoConnectTexture = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=MainLayout,height = 40)
        cmds.text(l=u'选择导出路径: ',p=rowlayout_AutoConnectTexture,al='left')
        self.tf_PickPath = cmds.textField(p=rowlayout_AutoConnectTexture,cc = lambda *arg:self.recorrectPath(self.tf_PickPath))
        BTN_PickPath = cmds.button(l=u'选择路径',p=rowlayout_AutoConnectTexture,c=lambda *arg: ML.fileDialog(u'选择贴图路径',3,self.tf_PickPath))

        rowlayout_CharacterName = cmds.rowLayout(numberOfColumns= 4,adjustableColumn=2,p=MainLayout,height = 40)
        cmds.text(l=u'场次前缀: ',p=rowlayout_CharacterName,al='left')
        scenename = ML.getScenename_real()
        if scenename != '':
            try:
                scenename = scenename.split('_')[0] + '_' + scenename.split('_')[1] + '_' + scenename.split('_')[2]
            except:
                scenename = u'未知'
        self.tf_prefix_scene = cmds.textField(p=rowlayout_CharacterName,text=scenename)
        cmds.text(l=u'角色名称: ',p=rowlayout_CharacterName,al='left')
        self.tf_characterName = cmds.textField(p=rowlayout_CharacterName)
        cmds.text(l=u'场次名称是自动生成的,请检查无误后导出,例:Ep019_sc005_019,手动输入角色名称,例:XiaoSe_XinBan_CH',p=MainLayout,al='left',height=50)
        FrameRange_layout = cmds.rowLayout(numberOfColumns= 4,p=MainLayout,height = 40)
        cmds.text(l=u'开始帧: ',p=FrameRange_layout,al='left')
        stratFrame = int(cmds.playbackOptions(min = 1,q=1))
        self.tf_Sframe = cmds.textField(p=FrameRange_layout,text = str(stratFrame))
        cmds.text(l=u'结束帧: ',p=FrameRange_layout,al='left')
        endframe = int(cmds.playbackOptions(max = 1,q=1))
        self.tf_Eframe = cmds.textField(p=FrameRange_layout,text = str(endframe))

        #FrameExpend
        FrameExpend_layout = cmds.rowLayout(numberOfColumns= 4,p=MainLayout,height = 40)
        cmds.text(l=u'帧向前扩展:',p=FrameExpend_layout,al='left')
        self.tf_fForwardExpend = cmds.textField(p=FrameExpend_layout,text = str(0),annotation=u'导出时向前扩展的帧数')
        cmds.text(l=u'帧向后扩展:',p=FrameExpend_layout,al='left')
        self.tf_fBackwardExpend = cmds.textField(p=FrameExpend_layout,text = str(2),annotation=u'导出时向后扩展的帧数')


        cmds.text(l=u'注意导出前请先删除命名空间!',p=MainLayout,al='left',height=50)
        BTN_export = cmds.button(l=u'导出选择的缓存',height = 50,p=MainLayout,c=lambda *arg:self.exportabcCache())
        cmds.helpLine(p = MainLayout )

    def recorrectPath(self,target):
        path = cmds.textField(target,text=1,q=1)
        cmds.textField(target,text=PL.normailizePath(path),e=1)
    def show(self):
        cmds.showWindow(self.window)
    def exportabcCache(self):
        name =  cmds.textField(self.tf_characterName,text=1,q=1)
        perfix = cmds.textField(self.tf_prefix_scene,text=1,q=1)
        path = cmds.textField(self.tf_PickPath,text=1,q=1)
        if not PL.isPath(path):
            cmds.warning(u'当前输入的路径不合法请检查')
            return False
        if name == '':
            cmds.warning(u'未输入角色名称')
            return False
        sl = ML.getSelectNodes()
        if sl == []:
            cmds.warning(u'未选择任何物体')
            return False
        try:
            combinemesh = cmds.polyUnite(sl)
            combinemesh = ML.getSelectNodes()[0]
        except:
            combinemesh = ML.getSelectNodes()[0]
        sgs = ML.getOneMeshSG(cmds.listRelatives(combinemesh,shapes=1))
        sgs = PL.sortByAscll(sgs)
        sortedMaterials = [] #排序完成的材质列表
        for sg in sgs:
            sortedMaterials.append(cmds.ls(cmds.listConnections(sg),materials=1)[0])
        rootpath = PL.normailizePath(path)
        abcPath = rootpath + perfix + '_' + name + '_cache' + '.abc'
        jsonPath = rootpath + perfix + '_' + name + '_cache' + '.json'
        sFrame = str(eval(cmds.textField(self.tf_Sframe,text=1,q=1)) + eval(cmds.textField(self.tf_fForwardExpend,text=1,q=1)))
        eFrame = str(eval(cmds.textField(self.tf_Eframe,text=1,q=1)) + eval(cmds.textField(self.tf_fBackwardExpend,text=1,q=1)))
        ML.exportABC(combinemesh,sFrame,eFrame,abcPath)
        PL.writejson(sortedMaterials,jsonPath)


def showUI():
    UI = abcExportToolUI()#实例化UI
    UI.show()#显示UI
