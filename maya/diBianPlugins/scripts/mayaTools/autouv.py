#encoding=utf-8


#导入标准模块


import math
from imp import reload

#导入自定义模块
import lib.mayaLibrary as ML
import maya.cmds as cmds

reload(ML)
import lib.pathLibrary as PL

reload(PL)

import lib.callThirdpart as CT

reload(CT)


cmds.loadPlugin( 'objExport.mll' )


class autunuvUI:
    def __init__(self):
        if cmds.window('autounwarrpUV',ex=1):
            cmds.deleteUI('autounwarrpUV',window=True)
        self.window = cmds.window('autounwarrpUV',title=u"UV辅助展开工具")
        # process Layout

        MainLayout = cmds.columnLayout( p=self.window,adjustableColumn=True)
        self.MainLayout = MainLayout
        cmds.helpLine(p = MainLayout )
        cmds.separator(p = MainLayout )


        currentheight = cmds.columnLayout(MainLayout,q=1,height=1)
        scrollmain = cmds.scrollLayout( p=MainLayout,childResizable=True,height = currentheight)
        self.scrollmain = scrollmain
        Framemain = cmds.columnLayout( p=scrollmain,adjustableColumn=True,columnOffset=['left',0],height = 1000)

        self.OM_Res = cmds.optionMenu(p = Framemain,label=u'分辨率',annotation=u'Resolution of texture, to give right amount of island gaps to prevent bleeds.')
        cmds.menuItem( label='512' )
        cmds.menuItem( label='1024' )
        cmds.menuItem( label='2048' )
        cmds.menuItem( label='4096' )
        cmds.menuItem( label='8192' )
        cmds.optionMenu(self.OM_Res,e=1,sl=2)

        self.CB_Sperate = cmds.checkBox(p = Framemain,l=u'分离硬边',annotation='Guarantees that all hard edges are separated. Useful for lightmapping and Normalmapping')

        rowlayout_Aspect = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=3,p=Framemain,height = 40)
        cmds.text(l=u'比例:')
        self.FF_Aspect = cmds.floatField(p = rowlayout_Aspect,value=1,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_Aspect,self.FS_Aspect,0),annotation='Aspect ratio of pixels. For non square textures.')
        self.FS_Aspect = cmds.floatSlider(p = rowlayout_Aspect,value=1,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_Aspect,self.FS_Aspect,1),annotation='Aspect ratio of pixels. For non square textures.')

        self.cb_normals = cmds.checkBox(p = Framemain,l=u'使用法线',annotation=u'使用模型法线帮助分类多边形',value=False)

        rowlayout_UDIM = cmds.rowLayout(numberOfColumns= 2,adjustableColumn=3,p=Framemain,height = 40)
        cmds.text(l=u'UDIM:')
        self.FF_UDIM = cmds.intField(p = rowlayout_UDIM,value=1,annotation='Split the model in to multople UDIMs')



        self.cb_Overlap = cmds.checkBox(p = Framemain,l=u'重叠相同的部分',value=False,annotation='Overlap identtical parts to take up the same texture space.')
        self.cb_mirror = cmds.checkBox(p = Framemain,l=u'重叠镜像的部分',value=False,annotation='verlap mirrored parts to take up the same texture space.')
        self.cb_worldspace = cmds.checkBox(p = Framemain,l=u'缩放uv空间到世界空间',value=False,annotation='Scales the UVs to match their real world scale going beyound the zero to one range.')
        
        self.OM_density = cmds.optionMenu(p = Framemain,label=u'贴图密度:',annotation=u'If worldspace is enabled, this value sets the number of pixels per unit.')
        cmds.menuItem( label='512' )
        cmds.menuItem( label='1024' )
        cmds.menuItem( label='2048' )
        cmds.menuItem( label='4096' )
        cmds.menuItem( label='8192' )
        cmds.optionMenu(self.OM_density,e=1,sl=2)


        cmds.text(l=u'缝合方向:',p =Framemain,align = 'left')
        d_lay = cmds.rowLayout(numberOfColumns= 6,p=Framemain,height = 40,annotation = 'Sets a pointy in space that seams are directed towards. By default the center of the model.')
        cmds.text(l=u'X:',p =d_lay )
        self.dx = cmds.floatField(p = d_lay,value=0.0,annotation = 'Sets a pointy in space that seams are directed towards. By default the center of the model.')
        cmds.text(l=u'Y:',p =d_lay )
        self.dy = cmds.floatField(p = d_lay,value=0.0,annotation = 'Sets a pointy in space that seams are directed towards. By default the center of the model.')
        cmds.text(l=u'Z:',p =d_lay )
        self.dz = cmds.floatField(p = d_lay,value=0.0,annotation = 'Sets a pointy in space that seams are directed towards. By default the center of the model.')
        


        # NOTE 高级模式
        cmds.separator(p=Framemain)
        self.CB_Debug = cmds.checkBox(p = Framemain,l=u'激活debug模式',cc=self.expenddebugMenu)


        rowlayout_debug = cmds.columnLayout(p=Framemain,height = 1,adjustableColumn=True)
        cmds.separator(p=rowlayout_debug)
        self.rowlayout_debug = rowlayout_debug



        cmds.checkBox(p = rowlayout_debug,l=u'抑制验证性错误',value=False,annotation = 'Faulty geometry errors will not be printed to standard out.')
        cmds.checkBox(p = rowlayout_debug,l=u'四边形',value=True,annotation = 'Searches the model for triangle pairs that make good quads. Improves the use of patches.')
        cmds.checkBox(p = rowlayout_debug,l=u'顶点焊接',value=True,annotation = 'Merges duplicate vertices, Does not efect the out put polygon or vertext data.')
        cmds.checkBox(p = rowlayout_debug,l=u'平坦的软表面',value=True,annotation = 'Detects flat areas of soft surfaces in order to minimize their distortion.')
        cmds.checkBox(p = rowlayout_debug,l=u'锥体',value=True,annotation = 'Searches the model for sharp Cones.')


        rowlayout_Cone_Ratio = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=3,p=rowlayout_debug,height = 40)
        cmds.text(l=u'椎体半径',annotation = 'The minimum ratio of a triangle used in a cone.')
        self.FF_CR = cmds.floatField(p = rowlayout_Cone_Ratio,value=0.5,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_CR,self.FS_CR,0),annotation = 'The minimum ratio of a triangle used in a cone.')
        self.FS_CR = cmds.floatSlider(p = rowlayout_Cone_Ratio,value=0.5,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_CR,self.FS_CR,1),annotation = 'The minimum ratio of a triangle used in a cone.')

        self.strips = cmds.checkBox(p = rowlayout_debug,l=u'栅格',value = True,annotation = 'Searches the model for grids of quads.')
        self.patches = cmds.checkBox(p = rowlayout_debug,l=u'补丁',value = True,annotation = 'Searches the model for strips of quads.')
        self.planes = cmds.checkBox(p = rowlayout_debug,l=u'平面',value = True,annotation = 'Searches the model for grids of quads.')


        rowlayout_Flatness = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=3,p=rowlayout_debug,height = 40)
        cmds.text(l=u'平面化程度:',annotation = 'Minimum normal dot product between two flat polygons.')
        self.FF_Flatness= cmds.floatField(p = rowlayout_Flatness,value=0.9,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_Flatness,self.FS_Flatness,0),annotation = 'Minimum normal dot product between two flat polygons.')
        self.FS_Flatness = cmds.floatSlider(p = rowlayout_Flatness,value=0.9,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_Flatness,self.FS_Flatness,1),annotation = 'Minimum normal dot product between two flat polygons.')


        self.CB_merge = cmds.checkBox(p = rowlayout_debug,l=u'合并',value = True,annotation='Merges polygons using unfolding.')

        rowlayout_MergeLimit = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=3,p=rowlayout_debug,height = 40)
        cmds.text(l=u'合并限制:',annotation = 'Limit the angle of polygons beeing merged.')
        self.FF_MergeLimit= cmds.floatField(p = rowlayout_MergeLimit,value=0.0,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_MergeLimit,self.FS_MergeLimit,0),annotation = 'Limit the angle of polygons beeing merged.')
        self.FS_MergeLimit = cmds.floatSlider(p = rowlayout_MergeLimit,value=0.0,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_MergeLimit,self.FS_MergeLimit,1),annotation = 'Limit the angle of polygons beeing merged.')

        self.presmooth = cmds.checkBox(p = rowlayout_debug,l=u'预光滑',value = True,annotation = ' Soften the mesh before atempting to cut and project.')
        self.softunfold = cmds.checkBox(p = rowlayout_debug,l=u'软展开',value = True,annotation = ' Atempt to unfold soft surfaces.')
        self.tubes = cmds.checkBox(p = rowlayout_debug,l=u'管状',value = True,annotation = 'Find tube shaped geometry and unwrap it using cylindrical projection.')
        self.junctions = cmds.checkBox(p = rowlayout_debug,l=u'连接处',value = True,annotation = 'Find and handle Junctions between tubes.')
        self.extraprdenarypoint = cmds.checkBox(p = rowlayout_debug,l=u'额外普通点',value = False,annotation = 'Using vertices not sharded by 4 quads as starting points for cutting.')
        self.anglebasedflatening = cmds.checkBox(p = rowlayout_debug,l=u'基于角度展平',value = True,annotation = 'Using angle based flattening to handle smooth surfaces.')
        self.smooth = cmds.checkBox(p = rowlayout_debug,l=u'平滑',value = True,annotation = 'Cut and project smooth surfaces.')
        self.repairsmooth = cmds.checkBox(p = rowlayout_debug,l=u'修复平滑',value = True,annotation = 'Attaches small islands to larger islands on smooth surfaces.')
        self.repair = cmds.checkBox(p = rowlayout_debug,l=u'修复',value = True,annotation = 'Repair edges to make then straight.')
        self.suqres = cmds.checkBox(p = rowlayout_debug,l=u'四边化',value = True,annotation = 'Finds various individual polygons that hare right angles.')
        self.relax = cmds.checkBox(p = rowlayout_debug,l=u'松弛',value = True,annotation = 'Relax all smooth polygons to minimize distortion.')
        

        rowlayout_Relaxation_iterations = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=3,p=rowlayout_debug,height = 40)
        cmds.text(l=u'松弛迭代次数:',annotation = 'The number of iteration loops when relaxing.')
        self.FF_Relaxation_iterations= cmds.intField(p = rowlayout_Relaxation_iterations,value=50,cc=lambda *arg:self.updateintfieldandSlider(self.FF_Relaxation_iterations,self.FS_Relaxation_iterations,0),annotation = 'The number of iteration loops when relaxing.')
        self.FS_Relaxation_iterations = cmds.intSlider(p = rowlayout_Relaxation_iterations,value=50,cc=lambda *arg:self.updateintfieldandSlider(self.FF_Relaxation_iterations,self.FS_Relaxation_iterations,1),annotation = 'The number of iteration loops when relaxing.')



        rowlayout_Expand = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=3,p=rowlayout_debug,height = 40)
        cmds.text(l=u'扩大:',annotation = 'Expand soft surfaces to make more use of texture space. Experimental, off by default')
        self.FF_Expand= cmds.floatField(p = rowlayout_Expand,value=0.25,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_Expand,self.FS_Expand,0),annotation = 'Expand soft surfaces to make more use of texture space. Experimental, off by default')
        self.FS_Expand = cmds.floatSlider(p = rowlayout_Expand,value=0.25,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_Expand,self.FS_Expand,1),annotation = 'Expand soft surfaces to make more use of texture space. Experimental, off by default')

        self.cut = cmds.checkBox(p = rowlayout_debug,l=u'切开',value = True,annotation = 'Cut down awkward shapes in order to optimize layout coverage.')
        self.stretch = cmds.checkBox(p = rowlayout_debug,l=u'拉伸',value = True,annotation = 'Stretch any island that is too wide to fit in the image.')
        self.match = cmds.checkBox(p = rowlayout_debug,l=u'匹配',value = True,annotation = 'Match individual tirangles for better packing.')
        self.Packing = cmds.checkBox(p = rowlayout_debug,l=u'排布',value = True,annotation = 'Pack islands in to a rectangle')

        self.Rasterization_resolution = cmds.optionMenu(p = rowlayout_debug,label=u'光栅化分辨率',annotation=u'Resolution of packing rasterization.')
        cmds.menuItem( label='8' )
        cmds.menuItem( label='16' )
        cmds.menuItem( label='32' )
        cmds.menuItem( label='64' )
        cmds.menuItem( label='128' )
        cmds.menuItem( label='256' )
        cmds.optionMenu(self.Rasterization_resolution,e=1,sl=4)


        
        rowlayout_Packing_iterations = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=3,p=rowlayout_debug,height = 40)
        cmds.text(l=u'排布迭代次数:',annotation = 'How many times the packer will pack the islands in order to find the optimal island spaceing.')
        self.FF_Packing_iterations= cmds.intField(p = rowlayout_Packing_iterations,value=4,cc=lambda *arg:self.updateintfieldandSlider(self.FF_Packing_iterations,self.FS_Packing_iterations,0),annotation = 'How many times the packer will pack the islands in order to find the optimal island spaceing.')
        self.FS_Packing_iterations = cmds.intSlider(p = rowlayout_Packing_iterations,value=4,cc=lambda *arg:self.updateintfieldandSlider(self.FF_Packing_iterations,self.FS_Packing_iterations,1),annotation = 'How many times the packer will pack the islands in order to find the optimal island spaceing.')

        rowlayout_ScaleToFit = cmds.rowLayout(numberOfColumns= 3,adjustableColumn=3,p=rowlayout_debug,height = 40)
        cmds.text(l=u'缩放适应:',annotation = 'Scales islands to fit cavites.')
        self.FF_ScaleToFit = cmds.floatField(p = rowlayout_ScaleToFit,value=0.5,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_ScaleToFit,self.FS_ScaleToFit,0),annotation = 'Scales islands to fit cavites.')
        self.FS_ScaleToFit = cmds.floatSlider(p = rowlayout_ScaleToFit,value=0.5,cc=lambda *arg:self.updatefloatfieldandSlider(self.FF_ScaleToFit,self.FS_ScaleToFit,1),annotation = 'Scales islands to fit cavites.')

        self.validate = cmds.checkBox(p = rowlayout_debug,l=u'验证',annotation = 'Validate geometry after each stage and print out any issues found (For debugging only).')


        cmds.separator(p=Framemain)
        BTN_PickPath = cmds.button(l=u'执行',p=Framemain,c=self.excuteunwarping)



    def show(self):
        cmds.showWindow(self.window)
    def expenddebugMenu(self,*arg):
        if cmds.checkBox(self.CB_Debug,q=1,value=1):
            cmds.columnLayout(self.rowlayout_debug,e=1,height = 720)
        else:
            cmds.columnLayout(self.rowlayout_debug,e=1,height = 1)
    def updatefloatfieldandSlider(self,field,slider,direction):
        '''direction 0:field to slider
                     1:slider to field '''
        if direction == 0:
            cmds.floatSlider(slider,e = 1,value=cmds.floatField(field,q=1,value=1))
        elif direction == 1:
            cmds.floatField(field,e = 1,value=cmds.floatSlider(slider,q=1,value=1))
    def updateintfieldandSlider(self,field,slider,direction):
        '''direction 0:field to slider
                     1:slider to field '''
        if direction == 0:
            cmds.intSlider(slider,e = 1,value=cmds.intField(field,q=1,value=1))
        elif direction == 1:
            cmds.intField(field,e = 1,value=cmds.intSlider(slider,q=1,value=1))
    def excuteunwarping(self,*arg):
        infilepath = r'd:/in.obj'
        outfilepath = r'd:/out.obj'
        ls = ML.getSelectNodes(True)
        if len(ls) == 0:
            cmds.warning(u'请选择一个模型')
            return False
        for object in ls:
            if cmds.listRelatives(object,type='mesh') == None:
                continue
            ML.exportOBJ(object,infilepath)
            cmddictnormal = {
                '-RESOLUTION ':str(math.pow(2,cmds.optionMenu(self.OM_Res,q=1,sl=1)+8)),
                '-SEPARATE ':str(cmds.checkBox(self.CB_Sperate,q=1,v=1)),
                'ASPECT ':str(cmds.floatField(self.FF_Aspect,q=1,v=1)),
                '-NORMALS ':str(cmds.checkBox(self.cb_normals,q=1,v=1)),
                '-UDIMS ':str(cmds.intField(self.FF_UDIM,q=1,v=1)),
                '-OVERLAP ':str(cmds.checkBox(self.cb_Overlap,q=1,v=1)),
                '-MIRROR ':str(cmds.checkBox(self.cb_mirror,q=1,v=1)),
                '-WORLDSCALE ':str(cmds.checkBox(self.cb_worldspace,q=1,v=1)),
                '-DENSITY ':str(math.pow(2,cmds.optionMenu(self.OM_density,q=1,sl=1)+8)),
                '-CENTER ':'{} {} {}'.format(cmds.floatField(self.dx,q=1,v=1),cmds.floatField(self.dy,q=1,v=1),cmds.floatField(self.dz,q=1,v=1))
            }
            CT.callUnWrap(infilepath,outfilepath,cmddictnormal)#调用unwrap
            iportobject = ML.importobjfile(outfilepath)
            cmds.transferAttributes( iportobject, object, transferUVs=2)
            #清除历史
            cmds.delete(object, constructionHistory = True)
            #删除导入的模型
            cmds.delete(iportobject)






def autouvMain():
    UI = autunuvUI()
    UI.show()
