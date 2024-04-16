#coding=utf-8
# MayaTools_v0.1 author ZCX
# v0.2修复创建RSMesh后无法将Lambert1指定上的错误
# v0.3增加有重命名物体时的提示，添加选择项目的功能
# v0.4防止导出的代理重名导致替换之前导出,防止因为重名导致无法连接代理
# v0.5增加导出导入功能
# v0.6修复一些BUG
# 20220725 增加可以生成简模并设置为代理的功能

import os
import time
from imp import reload

import maya.cmds as cmds
#导入自定义模块
import lib.mayaLibrary as ML

reload(ML)

import lib.callThirdpart as CT
reload(CT)


tempFilePath = r'D:/reduceTempMesh.obj'
resFilePath = r'D:/Results/reduceTempMesh1.obj'

# Functions
def DialogBoxAccept(title,Text):
    cmds.confirmDialog(
    title=title,
    message=Text,
    button=[u'确认',],
    defaultButton=u'确认'
)
def fileDialog(title,defaultPath=r'E:/'):  
    singleFilter =  "Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)"
    return(cmds.fileDialog2(cc=u'取消',cap=title,ds=2,ff=singleFilter,fm=1,okc=u'选择',dir=defaultPath))
def DialogBoxCheck(title,Text):
    resoult = cmds.confirmDialog( title = title, 
                        message=Text, 
                        button=[u'是',u'否'], 
                        defaultButton=u'是', 
                        cancelButton=u'否', 
                        dismissString=u'否' )
    if resoult == u'是':
        return True
    else:
        return False
def getProjectName():
    yPath = r'Y:/'
    projectNames = []
    for folder in os.listdir(yPath):
        if os.path.isdir(yPath + folder):
            projectNames.append(folder)
    return(projectNames)
def getRoattion(object):
    '''[x,y,z]'''
    x = cmds.getAttr(object + '.rotateX')
    y = cmds.getAttr(object + '.rotateY')
    z = cmds.getAttr(object + '.rotateZ')
    return([x,y,z])
def setRotation(object,rotations):
    cmds.setAttr(object + '.rotateX',rotations[0])
    cmds.setAttr(object + '.rotateY',rotations[1])
    cmds.setAttr(object + '.rotateZ',rotations[2])
def getBoudBoxSize(object):
    '''[x,y,z]'''
    x = cmds.getAttr(object + '.boundingBoxSizeX')
    y = cmds.getAttr(object + '.boundingBoxSizeY')
    z = cmds.getAttr(object + '.boundingBoxSizeZ')
    return([x,y,z])
def getMinBoundboxSize(object,angle):
    cmds.setAttr(object+'.rotateY',angle)
    rotations = getRoattion(object)
    cmds.makeIdentity(object,apply=True, t=1, r=1, s=1, n=0)
    boundSizes = getBoudBoxSize(object)
    inversrotations = [-rotations[0],-rotations[1],-rotations[2]]
    setRotation(object,inversrotations)
    cmds.makeIdentity(object,apply=True, t=1, r=1, s=1, n=0)
    #setRotation(object,rotations)
    return(boundSizes)
def CalBoundBoxVolume(sizes):
    return(sizes[0] * sizes[1] * sizes[2])   

def Test_1(arg):
    timeStamp = time.time()
    # Stepping Mode
    # get Selected object
    ls = cmds.ls(selection = True)[0]
    # NOTE freezen object
    cmds.makeIdentity(ls,apply=True, t=1, r=1, s=1, n=0)
    # NOTE define final angle
    outputAngle = 0 
    # NOTE persicion
    step = 0.1
    minXLength = 99999999
    i = 0
    while (i <= 90):
        xlengtn = getMinBoundboxSize(ls,i)[0]
        print(xlengtn)
        print(step)
        if xlengtn < minXLength:
            minXLength = xlengtn
            outputAngle = i
        else:
            step = step * -1.0
            pass
        i = i+step
    cmds.setAttr(ls + '.rotateY',outputAngle)
    print('Spend Time = {}s'.format(time.time()-timeStamp))
def Test():
    timeStamp = time.time()
    # Stepping Mode
    # get Selected object
    ls = cmds.ls(selection = True)[0]
    # NOTE freezen object
    cmds.makeIdentity(ls,apply=True, t=1, r=1, s=1, n=0)
    # NOTE define final angle
    outputAngle = 0 
    # NOTE persicion
    step = 0.01
    minXLength = 99999999
    i = 0
    flag = 0
    while(i <= 360):
        Currentxlength = getMinBoundboxSize(ls,i)[0]
        print(Currentxlength)
        Nextxlength =  getMinBoundboxSize(ls,i+step)[0]
        if Nextxlength > Currentxlength:
            step = step * -1.0
            flag = flag + 1
        if flag > 1:
            break
        i = i+step
    cmds.setAttr(ls + '.rotateY',i)
    print('Spend Time:{}s'.format(time.time()-timeStamp))

def uniformFilePath(originPath,recursionPath,startSuffix=1):
    if os.path.exists(recursionPath):
        TempPath,Extension = os.path.splitext(originPath)
        Newpath = TempPath + '_' + str(startSuffix) + Extension
    else:
        return(recursionPath)
    return(uniformFilePath(originPath,Newpath,startSuffix=startSuffix+1))

def importFile(path):
    path = path.replace('\\','/')
    newGroupName = 'Imported_Moedl'
    cmds.file(path,i=1,gn=newGroupName,gr=True,renameAll=True)
    importedMoedl = cmds.listRelatives(newGroupName)[0]
    cmds.ungroup(newGroupName)
    # 去除大环
    mainGroup = cmds.listRelatives(importedMoedl,type='transform',children=1)
    if '_con_G' in str(mainGroup):
        for subGroup in mainGroup:
            if '_con_G' in str(subGroup):
                cmds.delete(subGroup)
            else:
                importedMoedl = subGroup
    # 解组
    while True:
        if len(cmds.listRelatives(importedMoedl)) != 1 or cmds.listRelatives(importedMoedl,children=1,type='transform') == None:
            break
        ungroupName = importedMoedl
        print(ungroupName)
        importedMoedl = cmds.listRelatives(importedMoedl)[0]
        cmds.ungroup(ungroupName,absolute=1)
    return(importedMoedl)
def recursionRename(nodes,replace):
    if nodes == []:
        return True
    nextNodeList = []
    for node in nodes:
        children = cmds.listRelatives(node,children=1,type='transform')
        cmds.rename(node,node.replace(replace,'',1))
        if not (children == None):
            nextNodeList = nextNodeList + children
    return(recursionRename(nextNodeList,replace))
def myTest(arg):
    seitem = cmds.ls(selection=True)[0]
    rela = cmds.listRelatives(seitem,type='transform')
    if rela != None and len(rela) == 1:
        print('ok')
def importProxyAsMesh(arg):
    selects = cmds.ls(selection = True)
    for select in selects:
        allnodes = getAllConnections(cmds.listRelatives(select),1,[])
        rsProxyMesh = getNodesWithType(allnodes,'RedshiftProxyMesh')[0]
        if not rsProxyMesh:
            cmds.warning(u'警告',u'网格{}不是代理模型'.format(select))
            continue
        cmds.setAttr(rsProxyMesh + '.displayPercent',100.0)
        proxyMBfilePath = cmds.getAttr(rsProxyMesh + '.fileName').replace('.rs','.mb')
        # 判断MB文件是否存在
        if not os.path.exists(proxyMBfilePath):
            if DialogBoxCheck(u'警告',u'代理{}的mb文件不存在是否手动寻找'.format(select)):
                defaultPath = os.path.split(proxyMBfilePath)[0]
                proxyMBfilePath = fileDialog(u'选择代理文件',defaultPath)[0]
                if proxyMBfilePath == '':
                    continue
            else:
                continue
        # 导入代理MB
        importedGroup = importFile(proxyMBfilePath)
        parent = cmds.listRelatives(select,parent=True)[0]
        cmds.parent(importedGroup,parent,relative=1)
        if importedGroup:
            SourceCenterX = cmds.getAttr(select+'.boundingBoxCenterX')
            SourceCenterY = cmds.getAttr(select+'.boundingBoxCenterY')
            SourceCenterZ = cmds.getAttr(select+'.boundingBoxCenterZ')

            TargetCenterX = cmds.getAttr(importedGroup+'.boundingBoxCenterX')
            TargetCenterY = cmds.getAttr(importedGroup+'.boundingBoxCenterY')
            TargetCenterZ = cmds.getAttr(importedGroup+'.boundingBoxCenterZ')

            translatex = cmds.getAttr(importedGroup+'.translateX')
            translatey = cmds.getAttr(importedGroup+'.translateY')
            translatez = cmds.getAttr(importedGroup+'.translateZ')
            cmds.setAttr(importedGroup + '.translateX',translatex + SourceCenterX-TargetCenterX)
            cmds.setAttr(importedGroup + '.translateY',translatey + SourceCenterY-TargetCenterY)
            cmds.setAttr(importedGroup + '.translateZ',translatez + SourceCenterZ-TargetCenterZ)

            xrot = cmds.getAttr(select+'.rotateX')
            yrot = cmds.getAttr(select+'.rotateY')
            zrot = cmds.getAttr(select+'.rotateZ')
            importedX = cmds.getAttr(importedGroup+'.rotateX')
            importedY = cmds.getAttr(importedGroup+'.rotateX')
            importedZ = cmds.getAttr(importedGroup+'.rotateX')
            cmds.setAttr(importedGroup + '.rotateX', xrot+importedX)
            cmds.setAttr(importedGroup + '.rotateY', yrot+importedY)
            cmds.setAttr(importedGroup + '.rotateZ', zrot+importedZ)
        # 获取文件名称
        root,FileName = os.path.split(proxyMBfilePath)
        filter,exten = os.path.splitext(FileName)
        filter = filter+'_'
        recursionRename([importedGroup],filter)
        if cmds.checkBox('CB_DeleteProxyMesh',value=1,q=1):
            #删除代理
            cmds.delete(select)

def getAllConnections(nodes,direction,outPutNodes):
    '''direction=0:front
       direction=1:back '''
    if nodes == [] and outPutNodes!= []:
        return outPutNodes
    destination = 1
    source = 1
    nextNodes = []
    if direction == 0:
        source = 0
    else:
        destination = 0
    for node in nodes:
        if node not in outPutNodes:
            outPutNodes.append(node)
        subnodes = cmds.listConnections(node,d = destination,s = source)
        if subnodes == None:
            continue
        else:
            nextNodes = nextNodes + subnodes
    return(getAllConnections(nextNodes,direction,outPutNodes))

def getNodesWithType(nodes,type):
    result = []
    for node in nodes:
        if cmds.nodeType(node) == type:
            result.append(node)
    if result == []:
        return False
    return result

def setDisplayPercentage(arg):
    selects = cmds.ls(selection = True)
    for select in selects:
        allnodes = getAllConnections(cmds.listRelatives(select),1,[])
        rsProxyMesh = getNodesWithType(allnodes,'RedshiftProxyMesh')[0]
        if not rsProxyMesh:
            cmds.warning(u'警告',u'网格{}不是代理模型'.format(select))
            continue
        value = cmds.intSlider('IS_DisPer',q=1,v=1)
        cmds.setAttr(rsProxyMesh + '.displayPercent',value)


def setDisplayMode(arg):
    selects = cmds.ls(selection = True)
    for select in selects:
        allnodes = getAllConnections(cmds.listRelatives(select),1,[])
        rsProxyMesh = getNodesWithType(allnodes,'RedshiftProxyMesh')[0]
        if not rsProxyMesh:
            cmds.warning(u'警告',u'网格{}不是代理模型'.format(select))
            continue
        value = cmds.optionMenuGrp('DisplayMode',q=1,select=1)
        cmds.setAttr(rsProxyMesh + '.displayMode',value-1)
def aoLayerOverlay(*args):
    # abandoned!
    currentLayer = cmds.editRenderLayerGlobals(q=1,crl=1)
    if DialogBoxCheck(u'警告',u'是否要把层{}的材质覆盖为AO材质'.format(currentLayer)):
        RsAONode = cmds.createNode('RedshiftAmbientOcclusion',n='RSAONODE_')
        cmds.setAttr(RsAONode+'.numSamples',256)
        RsISNode = cmds.createNode('RedshiftIncandescent',n='RSISNODE_')
        RsISSGNode = cmds.createNode('shadingEngine',n=RsISNode+'_SG')
        cmds.connectAttr(RsAONode+'.outColor',RsISNode+'.color')
        cmds.connectAttr(RsISNode+'.outColor',RsISSGNode+'.surfaceShader')
        cmds.connectAttr(RsISSGNode+'.message',currentLayer+'.shadingGroupOverride')
    else:
        cmds.warning(u'操作被取消')

# UICLASS
class UIMAIN:
    def __init__(self):
        if cmds.dockControl('MayaTool',ex = 1):
            cmds.deleteUI('MayaTool')

        self.window = cmds.window('MAYATOOLS',title="MayaTools")
        # process Layout
        MainLayout = cmds.columnLayout( adjustableColumn=True ,w=300,h=400)

        # processing Dock
        cmds.dockControl('MayaTool',area = 'left',content = 'MAYATOOLS',fl = 1,l = 'MayaTools' )
        
        frameProxyTool = cmds.frameLayout('ProxyTool',l=u'RS代理工具',cll=1,cl=0,w=400,p=MainLayout)
        # set textfield sceneName
        scenename = ((cmds.file(q=True, sn=True).split('/')[-1]).split('_')[0])
        if scenename == '':
            scenename = u'当前文件未保存，手动修改场景名称'
        self.ProjectName = cmds.optionMenuGrp('ProjectName', l = u'选择项目:',cw2 = [140,100])
        for item in getProjectName():
            cmds.menuItem(item)
        cmds.textFieldGrp('SceneName',label=u'场景名称:', text=scenename)
        cmds.textFieldGrp('GroupName',label=u'子文件夹名称:', text='' )
        cmds.checkBox('CB_DeleteOriginModel',l=u'导出后删除原模型',value=1)
        cmds.checkBox('CB_CreatLowMesh',l=u'使用减面模型而不是立方体作为代理模型',value=0)
        cmds.button( h=30, l=u'导出', width=50, c = self.makeLowPoly)
        cmds.checkBox('CB_DeleteProxyMesh',l=u'导入后删除代理文件',value=1)

        cmds.button( h=30, l=u'将选中代理导入为实模', width=50, c = importProxyAsMesh)
        cmds.separator()
        cmds.rowLayout(parent = frameProxyTool ,numberOfColumns=3,columnWidth3=(5, 220, 150),adjustableColumn=1, columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)] ,height=50)
        cmds.intField('IF_DisPer',w=2,changeCommand=self.setPerSilder,maxValue=100,minValue=0)
        cmds.intSlider('IS_DisPer',dragCommand=self.setPerField,maxValue=100,minValue=0)
        cmds.button('BU_DisPer',h=30, l=u'设置选中代理的显示百分比', width=50,c=setDisplayPercentage)


        cmds.separator(p=frameProxyTool)


        cmds.columnLayout(p=frameProxyTool,adjustableColumn=True)
        cmds.optionMenuGrp('DisplayMode', l = u'显示模式:',cw2 = [140,100],w=80)
        cmds.menuItem('Bounding Box')
        cmds.menuItem('Preview Mesh')
        cmds.menuItem('Linked Mesh')
        cmds.menuItem('Hide in Viewport')
        cmds.button('BU_DisMode',h=30, l=u'设定显示模式', width=80,c=setDisplayMode)
    def setPerField(self,arg):
        value = cmds.intSlider('IS_DisPer',q=1,v=1)
        cmds.intField('IF_DisPer',v=value,e=1)
    def setPerSilder(self,arg):
        value = cmds.intField('IF_DisPer',q=1,v=1)
        cmds.intSlider('IS_DisPer',v=value,e=1)
    def importmodelFromProxy(self,arg):
        ls = cmds.ls(selection = True)
        for se in ls:
            print(se)
        pass
    def Show(self):
         cmds.showWindow( self.window )
    def makeLowPoly(self,arg):
        slNodes = cmds.ls(selection=True)
        if len(slNodes) == 0:
            cmds.warning(u'请选择一个物体')
        for slNode in slNodes:
            if len(slNode.split('|')) > 1:
                cmds.warning(u'不止一个物体名为：{}请重命名排查后重试'.format(slNode.split('|')[1]))
                break
            # 获取中心位置
            NewBoxPosX = cmds.getAttr(slNode + '.boundingBoxCenterX')
            NewBoxPosY = cmds.getAttr(slNode + '.boundingBoxCenterY')
            NewBoxPosZ = cmds.getAttr(slNode + '.boundingBoxCenterZ')
            # 获取缩放
            getattCommand = slNode + '.boundingBoxSizeX'
            NewBoxSizeX = cmds.getAttr(getattCommand)

            getattCommand = slNode + '.boundingBoxSizeY'
            NewBoxSizeY = cmds.getAttr(getattCommand)

            getattCommand = slNode + '.boundingBoxSizeZ'
            NewBoxSizeZ = cmds.getAttr(getattCommand)


            notbox = cmds.checkBox('CB_CreatLowMesh',value=1,q=1)
            # 移动到零点
            OTrasnlateX = cmds.getAttr(slNode + '.translateX')
            OTrasnlateY = cmds.getAttr(slNode + '.translateY')
            OTrasnlateZ = cmds.getAttr(slNode + '.translateZ')
            # 移动到原点
            cmds.select(slNode)
            cmds.move(OTrasnlateX-NewBoxPosX,OTrasnlateY-NewBoxPosY,OTrasnlateZ-NewBoxPosZ)
            cmds.select( clear=True )

            LowMeshname = str(slNode) + '_LowRSPR'
            if notbox:
                ML.exportOBJ(slNodes,tempFilePath)

                CT.callPolygonCruncher(False,False,tempFilePath,98.0)
                nenode = ML.importobjfile(resFilePath)
                cmds.rename(nenode,LowMeshname)
            else:
                LowMeshname = cmds.polyCube(d = NewBoxSizeZ,h = NewBoxSizeY,w = NewBoxSizeX,name = LowMeshname)[0]
            cmds.select(LowMeshname)
            cmds.move(NewBoxPosX, NewBoxPosY, NewBoxPosZ )
            # 清除选择
            cmds.select( clear=True )
            cmds.select(slNode)
            # 导出并记录路径 
            ProxyFilePath = self.Export_OBJ(str(slNode))
            # 获取原模型父级
            parent = cmds.listRelatives(slNode,parent=True)[0]
            if cmds.checkBox('CB_DeleteOriginModel',value=1,q=1):
                # 删除原模型
                cmds.delete(slNode)
            # 清除选择
            cmds.select( clear=True )
            # 连接代理
            self.ConnectProxy(ProxyFilePath,LowMeshname,notbox)
            # 将代理放入原来的组中
            cmds.parent(LowMeshname,parent,relative=1)
    def ConnectProxy(self,ProxyFilePath,ProxyMeshNode,notbox):
        #清除历史
        cmds.delete(ProxyMeshNode, constructionHistory = True)
        # 获得创建的用于代理的box
        proxyMesh = cmds.ls(ProxyMeshNode)[0]
        # 获取代理的shape
        ProxyShape = cmds.listRelatives(proxyMesh)[0]
        # 用于隐藏原有Mesh
        cmds.setAttr(ProxyShape+ '.intermediateObject',True)
        
        RedshiftProxyMeshName = ProxyMeshNode + '_PRMESH'
        cmds.createNode('RedshiftProxyMesh',name=RedshiftProxyMeshName)
        cmds.connectAttr(ProxyShape + '.outMesh',RedshiftProxyMeshName + '.inMesh')
        ProxyNewMeshname = ProxyMeshNode + '_NEWMESH'
        cmds.createNode('mesh',name=ProxyNewMeshname,p = proxyMesh)
        cmds.connectAttr(RedshiftProxyMeshName + '.outMesh',ProxyNewMeshname + '.inMesh')
        
        
        # cmds.ls返回的是数组
        ls = cmds.ls('initialShadingGroup')[0]
        lambert1 = cmds.ls('lambert1')[0] 
        cmds.select(ProxyNewMeshname)
        cmds.hyperShade(assign=lambert1)
        cmds.select( clear=True )



        RedshiftProxyMeshNode = cmds.ls(RedshiftProxyMeshName)[0]
        cmds.setAttr(RedshiftProxyMeshNode +'.fileName',ProxyFilePath,type = 'string')
        if notbox:
            cmds.setAttr(RedshiftProxyMeshNode + '.displayMode',2)
        else:
            cmds.setAttr(RedshiftProxyMeshNode + '.displayMode',1)
            cmds.setAttr(RedshiftProxyMeshNode + '.displayPercent',50.0)
    def Export_OBJ(self,filename):
        SceneName = cmds.textFieldGrp('SceneName',q= 1,tx = 1)
        FolderName = cmds.textFieldGrp('GroupName',q= 1,tx = 1)
        projectName = cmds.optionMenuGrp('ProjectName',q = 1,v = 1)
        path = 'Y:\\'+ projectName +'\\Reference\\Poxy_rs\\' + SceneName + '\\' + FolderName
        if not os.path.exists(path):
            os.makedirs(path)
        RSpath = path + '\\' + filename + '.rs'
        RSpath = uniformFilePath(RSpath,RSpath)
        cmds.file( RSpath, force=1, type='Redshift Proxy', pr=1, es=1)
        MBPath = path + '\\' + filename + '.mb'
        MBPath = uniformFilePath(MBPath,MBPath)
        cmds.file( MBPath, force=1, type='mayaBinary', pr=1, es=1)
        return (RSpath)
    def DebugPrint(self,Text):
        print('-------------------------------------------------------------------------------')
        print(Text)
        print('-------------------------------------------------------------------------------')


def UIMain():
    ui = UIMAIN()
    ui.Show()


        