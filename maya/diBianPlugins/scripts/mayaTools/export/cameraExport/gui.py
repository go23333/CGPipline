#coding=utf-8

#导入标准模块
import maya.cmds as cmds
import pymel.core as pm
#导入自定义模块
import mayaTools.core.mayaLibrary as ML
import mayaTools.core.pathLibrary as PL

class CameraExporertUI:
    def __init__(self):
        if cmds.window('CameraExporertUI',ex=1):
            cmds.deleteUI('CameraExporertUI',window=True)
        self.window = cmds.window('CameraExporertUI',title=u"相机导出工具",widthHeight=[400,250])
        # process Layout
        MainLayout = cmds.columnLayout( p=self.window,adjustableColumn=True)
        rowlayout_PicPath = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=MainLayout,height = 40)
        cmds.text(l=u'选择导出路径: ',p=rowlayout_PicPath,al='left')
        self.camera_fbx_export_path = cmds.textField(p=rowlayout_PicPath,cc = lambda *arg:self.recorrectPath(self.camera_fbx_export_path))
        BTN_PickPath = cmds.button(l=u'选择路径',p=rowlayout_PicPath,c=lambda *arg: ML.fileDialog(u'选择贴图路径',3,self.camera_fbx_export_path))
        self.cb_ScaleTenTimes = cmds.checkBox(l = u'放大10倍', p = MainLayout,v=1)
        cmds.button(l =u'导出选择的相机', p = MainLayout,c = self.btnExportCamera)
        cmds.separator(p = MainLayout,h = 20)

        cmds.text(l = u'相机修复工具集',p = MainLayout,align = 'left')
        cmds.separator(p = MainLayout,h = 5)
        cmds.button(l =u'修复枢轴改变过的相机', p = MainLayout,c = self.fix_pivot_changed_camera)

    def fix_pivot_changed_camera(self,*arg):
        #load Plugin
        cmds.loadPlugin( 'matrixNodes.mll' )
        slnodes = ML.getSelectNodes(1)
        if len(slnodes) > 1:
            cmds.warning(u'请选择单独的相机')
        cameraTransform = slnodes[0]
        cameraShape = cmds.listRelatives(cameraTransform,type='camera')[0]
        cameraName = str(cameraTransform).replace('|','')
        PivotLocalTOWrold = cmds.createNode('pointMatrixMult',n = 'PivotLocalTOWrold')
        # conver to world space
        cmds.connectAttr(cameraTransform+'.rotatePivot',PivotLocalTOWrold+'.inPoint')
        cmds.connectAttr(cameraTransform+'.worldMatrix',PivotLocalTOWrold+'.inMatrix')
        # get Object Center Position
        getCameraCenterPosition = cmds.createNode('plusMinusAverage',n='getCameraCenterPosition')
        cmds.setAttr(getCameraCenterPosition+'.operation',2)
        cmds.connectAttr(PivotLocalTOWrold+'.output',getCameraCenterPosition+'.input3D[0]')
        cmds.connectAttr(cameraTransform+'.rotatePivot',getCameraCenterPosition+'.input3D[1]')
        # get vector
        getVectorCenterTOPivot = cmds.createNode('plusMinusAverage' , n='getVectorCenterTOPivot')
        cmds.setAttr(getVectorCenterTOPivot+'.operation',2)
        cmds.connectAttr(getCameraCenterPosition+'.output3D',getVectorCenterTOPivot+'.input3D[0]')
        cmds.connectAttr(PivotLocalTOWrold+'.output',getVectorCenterTOPivot+'.input3D[1]')
        # ComposeMatrix
        RotateMatrix = cmds.createNode('composeMatrix',n = 'RotateMatrix')
        cmds.connectAttr(cameraTransform+'.rotate',RotateMatrix+'.inputRotate')
        # Rotate Vector
        getRotatedVector = cmds.createNode('pointMatrixMult',n = 'getRotatedVector')
        cmds.connectAttr(RotateMatrix+'.outputMatrix',getRotatedVector+'.inMatrix')
        cmds.connectAttr(getVectorCenterTOPivot+'.output3D',getRotatedVector+'.inPoint')
        cmds.setAttr(getRotatedVector+'.vectorMultiply',True)
        # calc Final Translate
        finalTranslate = cmds.createNode('plusMinusAverage',n = 'finalTranslate')
        cmds.connectAttr(getRotatedVector+'.output',finalTranslate+'.input3D[0]')
        cmds.connectAttr(PivotLocalTOWrold+'.output',finalTranslate+'.input3D[1]')
        # create Newcamera
        newCameraTransform,newCameraShape = cmds.camera()
        cmds.connectAttr(cameraTransform+'.rotate',newCameraTransform+'.rotate')
        cmds.connectAttr(finalTranslate+'.output3D',newCameraTransform+'.translate')
        # sync Shape Attr
        cmds.connectAttr(cameraShape+'.cameraAperture',newCameraTransform+'.cameraAperture')
        cmds.connectAttr(cameraShape+'.centerOfInterest',newCameraTransform+'.centerOfInterest')
        cmds.connectAttr(cameraShape+'.fStop',newCameraTransform+'.fStop')
        cmds.connectAttr(cameraShape+'.focalLength',newCameraTransform+'.focalLength')
        cmds.connectAttr(cameraShape+'.focusDistance',newCameraTransform+'.focusDistance')
        cmds.connectAttr(cameraShape+'.lensSqueezeRatio',newCameraTransform+'.lensSqueezeRatio')
        cmds.connectAttr(cameraShape+'.shutterAngle',newCameraTransform+'.shutterAngle')
        # bake animation
        framerange_transform = ML.getKeyFrameRange(cameraTransform)
        framerange_shape = ML.getKeyFrameRange(cameraShape)
        framerange = (1.0,max(framerange_transform[1],framerange_shape[1]))
        PMCameraTransform = pm.PyNode(newCameraTransform)
        PMCameraShape = pm.PyNode(newCameraShape)
        pm.animation.bakeResults(PMCameraTransform,t=framerange,simulation=True)
        pm.animation.bakeResults(PMCameraShape,t=framerange)
        # delete Origin Camera
        cmds.delete(cameraTransform)
        # rename newCamera
        cmds.rename(newCameraTransform,cameraName)

    def recorrectPath(self,target):
        path = cmds.textField(target,text=1,q=1)
        cmds.textField(target,text=PL.normailizePath(path),e=1)
    def btnExportCamera(self,*arg):
        slnodes = ML.getSelectNodes(False)
        pm.select(clear=1)
        nslnodes = []
        for slnode in slnodes:
            if cmds.listRelatives(slnode,s=1) == None:
                nslnodes = nslnodes +ML.recursionGroup([],slnode)
            else:
                nslnodes.append(slnode)
                pass
                #camera
        slnodes = nslnodes
        nslnodes = []
        # 删除命名空间
        cmds.namespace( set=':' ) # 设定当前命名
        for slnode in slnodes:
            namesplit = slnode.split(':')
            if len(namesplit) >= 2:
                nslnodes.append(namesplit[1])
                cmds.namespace( rm=namesplit[0],mnr=1)
            else:
                nslnodes.append(slnode)
        slnodes = nslnodes
        # 设置帧率
        try:
            cmds.currentUnit(t='25fps')
        except:
            pass
        # 计算最大帧数并设置最大动画帧数
        cameraNodes = ML.getNodesRelativesByType(slnodes,'camera') #获取相机节点
        ranges = ()
        tandc = cameraNodes + slnodes #附加相机节点列表和Transform节点列表
        for node in tandc:
            ranges = ranges + ML.getKeyFrameRange(node)
        ML.setFrameRange(1,max(ranges))
        #遍历所有节点
        for slnode in slnodes:
            if cmds.checkBox(self.cb_ScaleTenTimes,q=1,v=1):
                ML.scaleFrameValue(slnode+'.translateX',10)
                ML.scaleFrameValue(slnode+'.translateY',10)
                ML.scaleFrameValue(slnode+'.translateZ',10)
            fbxExportPath = cmds.textField(self.camera_fbx_export_path,q=1,text=1) + str(slnode) + '.fbx'
            ML.export_fbx_without_dialog(slnode,fbxExportPath)
            # NOTE 还原缩放
            if cmds.checkBox(self.cb_ScaleTenTimes,q=1,v=1):
                ML.scaleFrameValue(slnode+'.translateX',0.1)
                ML.scaleFrameValue(slnode+'.translateY',0.1)
                ML.scaleFrameValue(slnode+'.translateZ',0.1)
    def show(self):
        cmds.showWindow(self.window)
def showUI():
    UI = CameraExporertUI()
    UI.show()

if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
    showUI()