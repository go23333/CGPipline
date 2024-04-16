#coding=utf-8


from imp import reload

#导入自定义模块
import lib.mayaLibrary as ML
#导入标准模块
import maya.cmds as cmds

reload(ML)
import lib.pathLibrary as PL

reload(PL)



class ConnectTexturexUI:
    def __init__(self):
        if cmds.window('ConnectTextureTool',ex=1):
            cmds.deleteUI('ConnectTextureTool',window=True)
        self.window = cmds.window('ConnectTextureTool',title=u"贴图连接工具")
        # process Layout
        MainLayout = cmds.columnLayout( adjustableColumn=True ,w=300,h=400,p=self.window)
        # Display SceneName
        SceneNameText = u'场景名称:' + ML.getScenename()
        if ML.getScenename() == '':
            SceneNameText = u'场景名称:当前场景未保存,无法提取场景名'
        cmds.text( label=SceneNameText,al='left',height=40,font='boldLabelFont',p=MainLayout)
        table = cmds.tabLayout()
        # NOTE 自动连接贴图
        autoFindTextureFrame = cmds.frameLayout(u'自动连接贴图',l = u'自动连接贴图',p=table)

        rowlayout_AutoConnectTexture = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=autoFindTextureFrame,height = 20)
        cmds.text(l=u'选择贴图路径: ',p=rowlayout_AutoConnectTexture,al='left')
        self.tf_AutoPickPath = cmds.textField(p=rowlayout_AutoConnectTexture)
        BTN_AutoPickPath = cmds.button(l=u'选择路径',p=rowlayout_AutoConnectTexture,c=self.selectTexturePath)
        # 是否添加前缀
        # 根据项目名称进行判断
        prefixbool = ('_ch' in ML.getScenename().lower())
        self.CB_Addprefix = cmds.checkBox(l=u'是否添加项目名称为前缀:',p = autoFindTextureFrame,v = prefixbool)

        BTN_AutoAssigen = cmds.button(l=u'查找并连接贴图',height = 20,p=autoFindTextureFrame,c=self.ConnectTextures)
        cmds.text(l=u"选中要连接贴图的物体,并指定贴图所在的路径,插件根据\"_材质球名称_\"\n的规则匹配贴图,并赋予材质球.赋予贴图后插件会在材质球名称上加入场景名\n作为前缀,当前加入的前缀名称为{}".format(ML.getScenename()),p=autoFindTextureFrame,font='boldLabelFont')
        
        # NOTE 手动连接贴图
        manualFindTextureFrame = cmds.frameLayout(u'手动连接贴图',l = u'手动连接贴图',p=table)
        self.manualTextWidth = 60
        self.manualitemHeight = 30 
        #baseColor
        rowlayout_baseColor = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='BaseColor:  ',p=rowlayout_baseColor,width=self.manualTextWidth,al='left')
        self.tf_baseColorPath = cmds.textField(p=rowlayout_baseColor)
        BTN_baseColor = cmds.button(l=u'指定贴图路径',p=rowlayout_baseColor,c = self.selectTexturePathManualBasecolor)


        #roughness
        rowlayout_roughness = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Roughness:  ',p=rowlayout_roughness,width=self.manualTextWidth,al='left')
        self.tf_roughnessPath = cmds.textField(p=rowlayout_roughness)
        BTN_roughness = cmds.button(l=u'指定贴图路径',p=rowlayout_roughness,c = lambda *args:self.selectTexturePathManualOther(self.tf_roughnessPath))

        
        #metallic
        rowlayout_metallic = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Metallic:  ',p=rowlayout_metallic,width=self.manualTextWidth,al='left')
        self.tf_metallicPath = cmds.textField(p=rowlayout_metallic)
        BTN_metallic = cmds.button(l=u'指定贴图路径',p=rowlayout_metallic,c = lambda *args:self.selectTexturePathManualOther(self.tf_metallicPath))


        #AO
        rowlayout_AO = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Occlusion:  ',p=rowlayout_AO,width=self.manualTextWidth,al='left')
        self.tf_AOPath = cmds.textField(p=rowlayout_AO)
        BTN_AO = cmds.button(l=u'指定贴图路径',p=rowlayout_AO,c = lambda *args:self.selectTexturePathManualOther(self.tf_AOPath))


        #anisotropy
        rowlayout_anisotropy = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Anisotropy:  ',p=rowlayout_anisotropy,width=self.manualTextWidth,al='left')
        self.tf_anisotropyPath = cmds.textField(p=rowlayout_anisotropy)
        BTN_anisotropy = cmds.button(l=u'指定贴图路径',p=rowlayout_anisotropy,c = lambda *args:self.selectTexturePathManualOther(self.tf_anisotropyPath))


        #Emissive
        rowlayout_Emissive = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Emissive:  ',p=rowlayout_Emissive,width=self.manualTextWidth,al='left')
        self.tf_EmissivePath = cmds.textField(p=rowlayout_Emissive)
        BTN_Emissive = cmds.button(l=u'指定贴图路径',p=rowlayout_Emissive,c = lambda *args:self.selectTexturePathManualOther(self.tf_EmissivePath))


        #mask
        rowlayout_mask = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Mask:  ',p=rowlayout_mask,width=self.manualTextWidth,al='left')
        self.tf_maskPath = cmds.textField(p=rowlayout_mask)
        BTN_bmask = cmds.button(l=u'指定贴图路径',p=rowlayout_mask,c = lambda *args:self.selectTexturePathManualOther(self.tf_maskPath))


        #cavity
        rowlayout_cavity = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Cavity:  ',p=rowlayout_cavity,width=self.manualTextWidth,al='left')
        self.tf_cavityPath = cmds.textField(p=rowlayout_cavity)
        BTN_cavity = cmds.button(l=u'指定贴图路径',p=rowlayout_cavity,c = lambda *args:self.selectTexturePathManualOther(self.tf_cavityPath))


        #Normal
        rowlayout_Normal = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Normal:  ',p=rowlayout_Normal,width=self.manualTextWidth,al='left')
        self.tf_NormalPath = cmds.textField(p=rowlayout_Normal)
        BTN_Normal  = cmds.button(l=u'指定贴图路径',p=rowlayout_Normal,c = lambda *args:self.selectTexturePathManualOther(self.tf_NormalPath))


        #ARMS
        rowlayout_ARMS = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='ARMS:  ',p=rowlayout_ARMS,width=self.manualTextWidth,al='left')
        self.tf_ARMSPath = cmds.textField(p=rowlayout_ARMS)
        BTN_ARMS  = cmds.button(l=u'指定贴图路径',p=rowlayout_ARMS,c = lambda *args:self.selectTexturePathManualOther(self.tf_ARMSPath))

        
        #Opacity
        rowlayout_Opacity = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Opacity:  ',p=rowlayout_Opacity,width=self.manualTextWidth,al='left')
        self.tf_OpacityPath = cmds.textField(p=rowlayout_Opacity)
        BTN_Opacity  = cmds.button(l=u'指定贴图路径',p=rowlayout_Opacity,c = lambda *args:self.selectTexturePathManualOther(self.tf_OpacityPath))
        
        
        #Specular
        rowlayout_Specular = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=2,p=manualFindTextureFrame,height=self.manualitemHeight)
        cmds.text(l='Specular:  ',p=rowlayout_Specular,width=self.manualTextWidth,al='left')
        self.tf_SpecularPath = cmds.textField(p=rowlayout_Specular)
        BTN_Specular  = cmds.button(l=u'指定贴图路径',p=rowlayout_Specular,c = lambda *args:self.selectTexturePathManualOther(self.tf_SpecularPath))


        # button
        BTN_manualAssigen = cmds.button(l=u'创建赋予材质球并连接贴图',height = 80,p=manualFindTextureFrame,c=self.CreateAssignMaterial)
        self.MTFdic = {
                        'BaseColor':self.tf_baseColorPath,
                        'ARMS':self.tf_ARMSPath,
                        'Normal':self.tf_NormalPath,
                        'Anisotropy':self.tf_anisotropyPath,
                        'Mask':self.tf_maskPath,
                        'Opacity':self.tf_OpacityPath,
                        'Emissive':self.tf_EmissivePath,
                        'Occlusion':self.tf_AOPath,
                        'Roughness':self.tf_roughnessPath,
                        'Cavity':self.tf_cavityPath,
                        'Metallic':self.tf_metallicPath,
                        'Specular':self.tf_SpecularPath
                        }
    def CreateAssignMaterial(self,arg):
        # 创建并赋予选择物体材质
        sl = cmds.ls(selection=True)[0]
        material = ML.createRSMaterial()
        sg = cmds.sets(empty=True, renderable=True, noSurfaceShader=True)
        cmds.connectAttr( material+".outColor", sg+".surfaceShader", f=True)
        cmds.sets(sl,e=True, forceElement= sg)
        for key in self.MTFdic.keys():
            Path = cmds.textField(self.MTFdic[key],text=1,q=1)
            if not PL.isPath(Path):
                Path = []
            else:
                Path = [Path]
            ML.connectMaterial(material,Path,key)
        self.clearManualText()
    def show(self):
        cmds.showWindow(self.window)
    def selectTexturePath(self,arg):
        path = ML.fileDialog(u'选择贴图路径',3,self.tf_AutoPickPath)
        #cmds.textField(,text=path,e=1)
    def selectTexturePathManualBasecolor(self,arg):
        self.clearManualText()
        FilePath = ML.fileDialog(u'选择贴图路径',1)
        if FilePath == '':
            return False
        #检测其他贴图是否存在
        Paths = PL.getOtherChannelTexture(FilePath,'BaseColor')
        #判定是不是UDIM
        if PL.IsUDIMFormate(FilePath) and PL.calUDIMCount(FilePath) > 1:
            FilePath = FilePath .replace(PL.IsUDIMFormate(FilePath),'.<UDIM>.')
            for key in Paths.keys():
                Paths[key] = Paths[key].replace(PL.IsUDIMFormate(Paths[key]),'.<UDIM>.')
        cmds.textField(self.tf_baseColorPath,text=FilePath,e=1)
        #填充到列表中
        cmds.textField(self.tf_roughnessPath,text=Paths['Roughness'],e=1)
        cmds.textField(self.tf_metallicPath,text=Paths['Metallic'],e=1)
        cmds.textField(self.tf_AOPath,text=Paths['Occlusion'],e=1)
        cmds.textField(self.tf_anisotropyPath,text=Paths['Anisotropy'],e=1)
        cmds.textField(self.tf_EmissivePath,text=Paths['Emissive'],e=1)
        cmds.textField(self.tf_maskPath,text=Paths['Mask'],e=1)
        cmds.textField(self.tf_cavityPath,text=Paths['Cavity'],e=1)
        cmds.textField(self.tf_NormalPath,text=Paths['Normal'],e=1)
        cmds.textField(self.tf_ARMSPath,text=Paths['ARMS'],e=1)
        cmds.textField(self.tf_ARMSPath,text=Paths['Opacity'],e=1)
        cmds.textField(self.tf_SpecularPath,text=Paths['Specular'],e=1)

    def clearManualText(self):
        cmds.textField(self.tf_roughnessPath,text='',e=1)
        cmds.textField(self.tf_metallicPath,text='',e=1)
        cmds.textField(self.tf_AOPath,text='',e=1)
        cmds.textField(self.tf_anisotropyPath,text='',e=1)
        cmds.textField(self.tf_EmissivePath,text='',e=1)
        cmds.textField(self.tf_maskPath,text='',e=1)
        cmds.textField(self.tf_cavityPath,text='',e=1)
        cmds.textField(self.tf_NormalPath,text='',e=1)
        cmds.textField(self.tf_ARMSPath,text='',e=1)
        cmds.textField(self.tf_OpacityPath,text='',e=1)
        cmds.textField(self.tf_SpecularPath,text='',e=1)
    
    def selectTexturePathManualOther(self,Des):
        FilePath = ML.fileDialog(u'选择贴图路径',1,Des)
    def ConnectTextures(self,arg):
        path = cmds.textField(self.tf_AutoPickPath,text=1,q=1)
        if not PL.isPath(path):
                cmds.warning(u'路径不合法')
                return False
        path = PL.normailizePath(path)
        PassWords = ['kouqiang','yanqiu','boliti','jiemao','YanJian']
        slTransformNodes = ML.filterNode(ML.getSelectNodes(),'transform')
        if slTransformNodes == []:
            cmds.warning(u'没有选择任何物体')
            return False
        shapes = ML.getshapes(slTransformNodes)
        materials = ML.getMaterials(shapes)
        max = len(materials)
        cur = 0
        ML.progressWidow(title=u'贴图连接中',currentamout=cur)
        for material in materials:
            #删除原有连接的节点
            ML.DelAllInputConnections(material)
            # 规范化命名
            if ML.getScenename() not in material and cmds.checkBox(self.CB_Addprefix,q=1,v=1):
                try:
                    cmds.rename(material,ML.getScenename() + '_' + material)
                    material = ML.getScenename() + '_' + material
                except:
                    pass
            # 查找关键词
            for PassWord in PassWords:
                if PassWord in str(material).lower():
                    continue
            if 'skin' in str(material).lower():
                keyWord = str(material).replace(ML.getScenename() +'_Skin_','')
                keyWord = '_' + keyWord + '_'
                pass
            else:
                # 正常贴图查找
                keyWord = str(material)
                if ML.getScenename() != '':
                    keyWord = keyWord.replace(ML.getScenename() + '_','')
                keyWord = '_' + keyWord + '_'

            TexturePaths = PL.getFilesByKeyWords(path,keyWord)
            #判断是否是RSMaterial
            if cmds.nodeType(material) != 'RedshiftMaterial':
                sgs = cmds.listConnections(material,type='shadingEngine')
                cmds.delete(material)
                material = ML.createRSMaterial(str(material))
                for sg in sgs:
                    cmds.connectAttr(material+'.outColor',sg+'.surfaceShader')
            #提取并连接不同贴图
            ARMSTextures = PL.keyFilter(TexturePaths,'_ARMS')
            ML.connectMaterial(material,ARMSTextures,'ARMS')
            BaseColorTextures = PL.keyFilter(TexturePaths,'_BaseColor')
            ML.connectMaterial(material,BaseColorTextures,'BaseColor')
            NormalTextures = PL.keyFilter(TexturePaths,'_Normal')
            ML.connectMaterial(material,NormalTextures,'Normal')
            AnisotropyTextures = PL.keyFilter(TexturePaths,'_Anisotropy')
            ML.connectMaterial(material,AnisotropyTextures,'Anisotropy')
            MaskTextures = PL.keyFilter(TexturePaths,'_Mask')
            ML.connectMaterial(material,MaskTextures,'Mask')
            OpacityTextures = PL.keyFilter(TexturePaths,'_Opacity')
            ML.connectMaterial(material,OpacityTextures,'Opacity')
            EmissiveTextures = PL.keyFilter(TexturePaths,'_Emissive')
            ML.connectMaterial(material,EmissiveTextures,'Emissive')
            #Occlusion
            OcclusionTextures = PL.keyFilter(TexturePaths,'_Occlusion')
            ML.connectMaterial(material,OcclusionTextures,'Occlusion')
            #Rougness
            RougnessTextures = PL.keyFilter(TexturePaths,'_Roughness')
            ML.connectMaterial(material,RougnessTextures,'Roughness')
            #Cavity
            CavityTextures = PL.keyFilter(TexturePaths,'_Cavity')
            ML.connectMaterial(material,CavityTextures,'Cavity')
            #Metallic
            CavityTextures = PL.keyFilter(TexturePaths,'_Metallic')
            ML.connectMaterial(material,CavityTextures,'Metallic')
            #Specular
            CavityTextures = PL.keyFilter(TexturePaths,'_Specular')
            ML.connectMaterial(material,CavityTextures,'Specular')
            cur = cur+1
            ML.updateProgress(cur,max)
        ML.deleteUnusedNode()
                    


def ConnectTextureMain():
    UI = ConnectTexturexUI()
    UI.show()

