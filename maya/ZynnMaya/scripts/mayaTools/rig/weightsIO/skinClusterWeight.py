# -*- coding: utf-8 -*-
import maya.cmds as mc
import re,os

from mayaTools.rig.weightsIO.shared_ch.mayaPrint import MayaPrint
from mayaTools.rig.weightsIO.shared_ch.searchByName import Matching
from mayaTools.rig.weightsIO.shared_ch.fileDialog import FDialog

class SkinWeightImExport(Matching,FDialog):
    def __init__(self):
        MayaPrint.__init__(self)
        self.swPath = None
        self.mayaVersion = mc.about(f=True)
        self.userName = os.environ['USERNAME']

    @staticmethod
    def changListToStr(list_):
        result = ''
        if type(list_)==list and len(list_)>=1:
            for i in range(len(list_)):
                if i== len(list_)-1:
                    result += '%s'%(list_[i])
                else:
                    result += '%s;'%(list_[i])
        elif list_ is None or list_==[]:
            result = ''
        return result

    def loadSelectedIntoButtonGrp(self,buttonGrp):
        objs = mc.ls(sl=True)
        if len(objs) > 0:
            mc.textFieldButtonGrp(buttonGrp,e=True,tx=self.changListToStr(objs) )
        else:
            mc.textFieldButtonGrp(buttonGrp,e=True,tx="" )
        return True

    def swReturnPath(self,fileName,fileType):
        self.swPath = fileName

    def searchSkinCluster(self,mod=""):
        if mod=="":
            selObjs = mc.ls(sl=True,ap=1,fl=True)
            if 0==len(selObjs):
                self.mayaError("No object or points selected!")
                return
            mod = selObjs[0]
            shape = self.searchControlShape(mod)
            if shape==None or not mc.objExists(mod):
                self.mayaWarning( "No controlPoint object" )
                return
        skinNode = self.findRelatedSkinCluster(mod)
        if None==skinNode:
            self.mayaWarning( "Can't fint skinCluster: %s"%mod )
            return
        return skinNode

    def moveWeightOnFollow(self,addInfo = "L_mothConner_jnt",W01=0.5):
        slVertex = mc.ls(sl=True,fl=True)
        aJot = "jawRot_jnt"
        bJot = "jaw_jnt"
        for vtx in slVertex:
            valus = mc.skinPercent( 'skinCluster1', vtx, query=True, value=True )
            trans = mc.skinPercent( 'skinCluster1', vtx, query=True, t=None)
            idxA = trans.index(aJot)
            idxB = trans.index(bJot)
            idxAdd = trans.index(addInfo)
            if valus[idxAdd] ==0.0:
                #add info value =  (av + bv) -abs(av-bv)
                valus[idxAdd] = (valus[idxA]+valus[idxB])-abs(valus[idxA]-valus[idxB])
                if valus[idxA]>valus[idxB]:
                    valus[idxA] = abs(valus[idxA]-valus[idxB])
                    valus[idxB] = 0.0
                elif valus[idxA]<valus[idxB]:
                    valus[idxB] = abs(valus[idxA]-valus[idxB])
                    valus[idxA] = 0.0
                else:
                    valus[idxA] = 0.0
                    valus[idxB] = 0.0
                transformValue = []
                for idx in range( len(valus) ):
                    transformValue.append( (trans[idx] , valus[idx]) )
                mc.skinPercent( 'skinCluster1', vtx, transformValue=transformValue )

    def splitWeight(self,*pointName,**flags):
            """can form proportion split skin weight.
            flag:
            replaceStr default ["L_","R_"]
            proportion defalut [1,1]"""
            #--------------------------------------
            defineFlags = { "replaceStr":(["L_","R_"],list),"proportion":([1,1],list) }
            flagDirect = self.funtionFlag(defineFlags,**flags)
            ##read from flagDirect
            replaceStr = flagDirect[ "replaceStr" ]
            proportion = flagDirect[ "proportion" ]
            #--------------------------------------

            if pointName==():
                    pointName=mc.filterExpand(sm=31)
            if pointName==None:
                    self.mayaWarning("Nothing input or no poly vertex selected.")
                    return

            #funtion main
            valueList,transList = [],[]
            for ver in pointName:
                    #get skincluster node name
                    mc.select(ver)
                    skNode = self.searchSkinCluster()
                    if skNode==False:
                            self.mayaWarning("Can not find skinCluster node.%s"%(ver))
                            continue
                    allWeightJoints = mc.skinCluster(skNode,q=True,wi=True)
                    #get weith and inf name list
                    valueList = mc.skinPercent(skNode,ver,v=True,q=True,ib=01e-013)
                    transList = mc.skinPercent(skNode,ver,t=None,q=True,ib=01e-013)
                    #first must lock all joint weight
                    for jnt in allWeightJoints:
                            mc.setAttr("%s.liw"%(jnt),1)
                    for inf in transList:
                            if re.search(replaceStr[0],inf)!=None:
                                    targetInf = re.sub(replaceStr[0],replaceStr[1],inf)
                                    if mc.objExists(targetInf) and mc.objExists(inf):
                                            #combin the weight
                                            cobinWeit = mc.skinPercent(skNode,ver,t=inf,q=True)
                                            cobinWeit+=mc.skinPercent(skNode,ver,t=targetInf,q=True)
                                            sum = proportion[0]+proportion[1]
                                            average= float(cobinWeit)/sum
                                            #unlock
                                            mc.setAttr("%s.liw"%(inf),0)
                                            mc.setAttr("%s.liw"%(targetInf),0)
                                            #set weight
                                            va = average*proportion[0]
                                            vb = average*proportion[1]
                                            mc.skinPercent(skNode,ver,tv=[inf,va])
                                            mc.skinPercent(skNode,ver,tv=[targetInf,vb])
                                            print(skNode,ver,inf,va)
                                            print(skNode,ver,targetInf,vb)
            mc.select(pointName)
    #import point joint weight
    def importPointJointWeight(self,fileName,pointJoint,mod=None):
        "Import point joint skin weight "
        if mod==None:
            sels = mc.ls(sl=True,ap=1)
            if sels==[]:
                self.mayaWarning("No one mesh input or selected")
                return
            mod = sels[0]
        skinCluster = self.searchSkinCluster(mod)
        #mc.skinPercent("skinCluster1","head_geo.vtx[920]",tv=["Mouth_C_All_jnt",1]
        #24:  1 0.9991 3 0.0009
        self.fileName = fileName
        #if self.checkSkJoint(fileName)==False:
        #    return
        #deel with input joint name
        pointJoints = []
        if type(pointJoint)==str or type(pointJoint)==unicode:
            pointJoints = [pointJoint]
        elif type(pointJoint)==list:
            pointJoints = pointJoint
        else:
            raise TypeError("pointJoint must a list .")
        #check joints is inf if not add it
        infs = mc.skinCluster(skinCluster,q=True,inf=True)
        for jot in pointJoints:
            if jot not in infs:
                mc.skinCluster(skinCluster,e=True,ai=jot,lw=True,wt=0)
        #
        rFile = open(self.fileName,'r')#read weight file
        self.jntNumDit = {}
        #=========================================================================
        vertexCount = mc.polyEvaluate(mod,v=True)-1
        amount = 0
        mc.progressWindow(title='Impoting Weight V1.1 ...',progress=amount,max=vertexCount,
                                status='Progress: -/-',
                                isInterruptable=True )

        #=========================================================================
        for line in rFile:
            if mc.progressWindow( query=True, isCancelled=True ):
                break
            if re.search("^#|^\n|^\r|^ ",line)!=None:
                continue
            line = re.sub('\n|\r','',line)
            if(line[0:8] == 'deformer'):
                #read inf joint name
                lineList = line.split(' ',2)#lineList[0] demomer lineList[1] jointNumber lineList[2] jointName
                self.jntNumDit[lineList[1]]=lineList[2]
            else:#0:  8 0.962239 9 0.0377611
                #cmds.skinPercent( 'skinCluster1', 'pPlane1.vtx[100]', transformValue=[('joint1', 0.2), ('joint3', 0.8)])
                strA = line.split(':  ',1)#vertexWeight[0] vertex number
                vertex = strA[0]
                if int(vertex)>vertexCount:
                    break
                transformValue = strA[1].split(' ')
                #--------------------------------
                total = 0.0
                #get the joint name
                for i in range(0,len(transformValue),2):
                    for jnt in pointJoints:
                        transformValueList = []
                        vWet = float("%0.5f"%(float(transformValue[i+1])))#round(float(transformValue[i+1]),5)
                        if self.jntNumDit[transformValue[i]]== jnt:
                            vertexName = '%s.vtx[%s]'%(mod,vertex)
                            transformValueList.append((self.jntNumDit[transformValue[i]],vWet))
                            mc.skinPercent(skinCluster,vertexName,tv=transformValueList)
                #--------------------------------
                amount+=1
                mc.progressWindow( edit=True, progress=amount,status=('Progress: %s/%s'%(amount,vertexCount)))
        rFile.close()
        mc.progressWindow(endProgress=True)
        self.mayaPrint(' Rewrite skinCluster weight from %s\n' %(self.fileName))

    #import selected points skin weight
    def importSelPointsWeight(self):
            mc.ls(sl=True,fl=True)

    def exportSkinWeight(self,mod,fileName=None):
        """mod : alist of one geo or vertexs
        export skin cluster weight
        """
        print(mod)
        shape = self.searchControlShape(mod)
        objType = mc.objectType(shape)
        if "mesh"==objType:
            #Mesh skin weight export
            polygon = mc.filterExpand(mod,sm=12)
            vertice = mc.filterExpand(mod,sm=31)
            if None!=polygon:
                #Export mesh object skin weight
                self.exportMeshSkinWeight(polygon[0],fileName)
            elif None!=vertice:
                #Export polygon vertexs skin weight
                self.exportMeshSelPointWeight(vertice,fileName)
        elif "nurbsCurve"==objType:
            self.exportCurveSkinWeight(mod[0],fileName)
        elif "nurbsSurface"==objType:
            self.exporpSufsSkinWeight(mod[0],fileName)
        elif "lattice"==objType:
            self.exportLatticeSkinWeight(mod[0],fileName)

    def exportMeshSkinWeight(self,mod,fileName=None):
        "----export selected mesh skinCluster weight----"
        if fileName==None:
            fileName = self.fileDialog(m=1,ft="*.w")
            if fileName==[] or fileName==None:
                return False
        else:
            fileName = [fileName]
        skinCluster = self.searchSkinCluster(mod)
        if None==skinCluster:
            return
        fileName = re.sub( '\.w$','',fileName[0] )
        wFile = open(fileName+'.w','w')#weight File
        wFile.write( '#Mesh skinWeight file <%s> CreateBy:%s written by Maya %s\n\n' %(skinCluster,self.userName,self.mayaVersion) )
        #get inf joint
        skinJoints = mc.skinCluster(skinCluster,q=True,inf=True)
        #deformer 0 Bip01
        self.jntNumDit = {}
        for i,joint in enumerate(skinJoints):
            wFile.write('%s %s %s\n' %('deformer',i,joint))
            self.jntNumDit[joint]=i
        wFile.write('\n')
        #0:  0 0.167997 3 0.0455759 5 0.163311 6 0.169825 7 0.113641 31 0.169825 32 0.169825
        number = mc.polyEvaluate(mod,v=True)
        #wFile.write('#mesh %d'%number)
        for i in range(number):
            wFile.write('%s: '%(i))
            infJnt = mc.skinPercent(skinCluster,'%s.vtx[%s]' %(mod,i),ignoreBelow=0.00001,query=True,t=None)#per mod inf joint list
            jntWet = mc.skinPercent(skinCluster,'%s.vtx[%s]' %(mod,i),ignoreBelow=0.00001,query=True,v=True)#per joint weight
            totalWeight = 0.0
            for n,jnt in enumerate(infJnt):
                #round the weight
                toStr = "%0.5f"%(jntWet[n])
                rWeit = float(toStr)#round(jntWet[n],5)
                if n==len(infJnt)-1:
                    wFile.write(' %s %0.5f' %(self.jntNumDit[jnt],(1.0-totalWeight)))
                else:
                    totalWeight += rWeit
                    wFile.write(' %s %s' %(self.jntNumDit[jnt],toStr))
            wFile.write('\n')
        wFile.close()
        self.mayaPrint(' %s.w\n' %(fileName))

    def exportMeshSelPointWeight(self,points,fileName=None):
        "----export selected vertexs skinCluster weight----"
        if type(points)==str:
            points = self.changeStrToList(points)
        #write weight file
        skinCluster = self.searchSkinCluster(points)
        if skinCluster==None:
            return
        if points==None or points==[]:
            self.mayaWarning('No vertex selected...')
            return
        #--------file dialog --------------
        if fileName==None:
            swPath = self.fileDialog(m=1,ft="*.evw")
            if swPath==[] or swPath==None:
                return False
        eswFile = re.sub('\.evw$','',swPath[0])
        wFile = open(eswFile+'.evw','w')#weight File
        wFile.write('#mesh skin weight file, written by Maya %s\n\n' %(self.mayaVersion,))
        skinJoints = mc.skinCluster(skinCluster,q=True,inf=True)
        #deformer 0 Bip01
        jntNumDit = {}
        for i,joint in enumerate(skinJoints):
            wFile.write('%s %s %s\n' %('deformer',i,joint))
            jntNumDit[joint]=i
        wFile.write('\n')
        #0:  0 0.167997 3 0.0455759 5 0.163311 6 0.169825 7 0.113641 31 0.169825 32 0.169825
        for x in points:
            reSpStr = re.split('\[|\]',x)
            wFile.write('%s: '%(reSpStr[1]))
            infJnt = mc.skinPercent(skinCluster,x,ignoreBelow=0.00001,query=True,t=None)
            jntWet = mc.skinPercent(skinCluster,x,ignoreBelow=0.00001,query=True,v=True)
            for n,jnt in enumerate(infJnt):
                wFile.write(' %s %s' %(jntNumDit[jnt],jntWet[n]))
            wFile.write('\n')
        wFile.close()
        self.mayaPrint('Write SkinWeight by selected vertex <%s.evw>.'%(eswFile))

    def exportCurveSkinWeight(self,mod,fileName=None):
        "----export nurbsCurve skinCluster weight----"
        if fileName==None:
            fileName = self.fileDialog(m=1,ft="*.w")
            if fileName==[] or fileName==None:
                return False
        else:
            fileName = [fileName]
        skinCluster = self.searchSkinCluster(mod)
        if skinCluster==None:
            return
        fileName = re.sub( '\.w$','',fileName[0] )
        wFile = open(fileName+'.w','w')#weight File
        wFile.write('#NurbsCurve skinWeight file <%s> CreateBy:%s written by Maya %s\n\n' %(skinCluster,self.userName,self.mayaVersion) )
        #get inf joint
        skinJoints = mc.skinCluster(skinCluster,q=True,inf=True)
        #deformer 0 Bip01
        self.jntNumDit = {}
        for i,joint in enumerate(skinJoints):
            wFile.write('%s %s %s\n' %('deformer',i,joint))
            self.jntNumDit[joint]=i
        wFile.write('\n')
        #0:  0 0.167997 3 0.0455759 5 0.163311 6 0.169825 7 0.113641 31 0.169825 32 0.169825
        shape = self.searchControlShape(mod)
        number = mc.getAttr("%s.degree"%shape)+mc.getAttr("%s.spans"%shape)
        #wFile.write('#nurbsCurve %d'%number)
        for i in range(number):
            wFile.write('%s: '%(i))
            infJnt = mc.skinPercent(skinCluster,'%s.cv[%s]' %(mod,i),ignoreBelow=0.00001,query=True,t=None)#per mod inf joint list
            jntWet = mc.skinPercent(skinCluster,'%s.cv[%s]' %(mod,i),ignoreBelow=0.00001,query=True,v=True)#per joint weight
            totalWeight = 0.0
            for n,jnt in enumerate(infJnt):
                #round the weight
                toStr = "%0.5f"%(jntWet[n])
                rWeit = float(toStr)#round(jntWet[n],5)
                if n==len(infJnt)-1:
                    wFile.write(' %s %0.5f' %(self.jntNumDit[jnt],(1.0-totalWeight)))
                else:
                    totalWeight += rWeit
                    wFile.write(' %s %s' %(self.jntNumDit[jnt],toStr))
            wFile.write('\n')
        wFile.close()
        self.mayaPrint(' %s.w\n' %(fileName))

    def exportLatticeSkinWeight(self,mod,fileName=None):
        "----export lattice skinCluster weight----"
        if fileName==None:
            fileName = self.fileDialog(m=1,ft="*.w")
            if fileName==[] or fileName==None:
                return False
        else:
            fileName = [fileName]
        skinCluster = self.searchSkinCluster(mod)
        if skinCluster==None:
            return
        fileName = re.sub( '\.w$','',fileName[0] )
        wFile = open(fileName+'.w','w')#weight File
        wFile.write('#Lattice skinWeight file <%s> CreateBy:%s written by Maya %s\n\n' %(skinCluster,self.userName,self.mayaVersion) )
        #get inf joint
        skinJoints = mc.skinCluster(skinCluster,q=True,inf=True)
        #deformer 0 Bip01
        self.jntNumDit = {}
        for i,joint in enumerate(skinJoints):
            wFile.write('%s %s %s\n' %('deformer',i,joint))
            self.jntNumDit[joint]=i
        wFile.write('\n')
        #0:  0 0.167997 3 0.0455759 5 0.163311 6 0.169825 7 0.113641 31 0.169825 32 0.169825
        shape = self.searchControlShape(mod)
        sds = mc.getAttr("%s.sDivisions"%shape)
        tds = mc.getAttr("%s.tDivisions"%shape)
        uds = mc.getAttr("%s.uDivisions"%shape)
        #wFile.write('#nurbsCurve %d'%number)
        for sd in range(sds):
            for td in range(tds):
                for ud in range(uds):
                    wFile.write('[%d][%d][%d]: '%(sd,td,ud))
                    infJnt = mc.skinPercent(skinCluster,'%s.pt[%d][%d][%d]'%(mod,sd,td,ud),ignoreBelow=0.00001,query=True,t=None)#per mod inf joint list
                    jntWet = mc.skinPercent(skinCluster,'%s.pt[%d][%d][%d]'%(mod,sd,td,ud),ignoreBelow=0.00001,query=True,v=True)#per joint weight
                    totalWeight = 0.0
                    for n,jnt in enumerate(infJnt):
                        #round the weight
                        toStr = "%0.5f"%(jntWet[n])
                        rWeit = float(toStr)#round(jntWet[n],5)
                        if n==len(infJnt)-1:
                            wFile.write(' %s %0.5f' %(self.jntNumDit[jnt],(1.0-totalWeight)))
                        else:
                            totalWeight += rWeit
                            wFile.write(' %s %s' %(self.jntNumDit[jnt],toStr))
                    wFile.write('\n')
        wFile.close()
        self.mayaPrint(' %s.w\n' %(fileName))

    def exporpSufsSkinWeight(self,mod,fileName=None):
        "----export nurbsSurface skinCluster weight----"
        if fileName==None:
            fileName = self.fileDialog(m=1,ft="*.w")
            if fileName==[] or fileName==None:
                return False
        else:
            fileName = [fileName]
        skinCluster = self.searchSkinCluster(mod)
        if skinCluster==None:
            return
        fileName = re.sub( '\.w$','',fileName[0] )
        wFile = open(fileName+'.w','w')#weight File
        wFile.write('#NurbsSurface skinWeight file <%s> CreateBy:%s written by Maya %s\n\n' %(skinCluster,self.userName,self.mayaVersion) )
        #get inf joint
        skinJoints = mc.skinCluster(skinCluster,q=True,inf=True)
        #deformer 0 Bip01
        self.jntNumDit = {}
        for i,joint in enumerate(skinJoints):
            wFile.write('%s %s %s\n' %('deformer',i,joint))
            self.jntNumDit[joint]=i
        wFile.write('\n')
        #0:  0 0.167997 3 0.0455759 5 0.163311 6 0.169825 7 0.113641 31 0.169825 32 0.169825
        shape = self.searchControlShape(mod)
        numberU = mc.getAttr("%s.su"%shape)+mc.getAttr("%s.du"%shape)
        numberV = mc.getAttr("%s.sv"%shape)+mc.getAttr("%s.dv"%shape)
        #wFile.write('#nurbsCurve %d'%number)
        for u in range(numberU):
            for v in range(numberV):
                wFile.write('[%s][%s]: '%(u,v))
                infJnt = mc.skinPercent(skinCluster,'%s.cv[%s][%s]'%(mod,u,v),ignoreBelow=0.00001,query=True,t=None)#per mod inf joint list
                jntWet = mc.skinPercent(skinCluster,'%s.cv[%s][%s]'%(mod,u,v),ignoreBelow=0.00001,query=True,v=True)#per joint weight
                totalWeight = 0.0
                for n,jnt in enumerate(infJnt):
                    #round the weight
                    toStr = "%0.5f"%(jntWet[n])
                    rWeit = float(toStr)#round(jntWet[n],5)
                    if n==len(infJnt)-1:
                        wFile.write(' %s %0.5f' %(self.jntNumDit[jnt],(1.0-totalWeight)))
                    else:
                        totalWeight += rWeit
                        wFile.write(' %s %s' %(self.jntNumDit[jnt],toStr))
                wFile.write('\n')
        wFile.close()
        self.mayaPrint(' %s.w\n' %(fileName))

    def importSkinWeight(self,fileName,mod,subs={}):
        "import SkinWeight "
        if self.checkSkJoint(fileName,subs)==False:
            return
        skinCluster = self.searchSkinCluster(mod)
        shape = self.searchControlShape(mod)
        if skinCluster==None and shape!=None:
            skinCluster = mc.skinCluster(self.getInfsFrom_w(fileName,subs),mod,sm=0,tsb=True)
        objType = mc.objectType(shape)
        #Edit inf joints
        curtInfs = mc.skinCluster(skinCluster,q=True,inf=True)
        wetsInfs = self.getInfsFrom_w(fileName,subs)
        for inf in curtInfs:
            if inf in wetsInfs:
                wetsInfs.remove(inf)
        if len(wetsInfs)>0:
            mc.skinCluster(skinCluster,e=True,dr=4,lw=False,wt=0,ai=wetsInfs)
        #unlock all inf
        curtInfs = mc.skinCluster(skinCluster,q=True,inf=True)
        for jot in curtInfs:
            mc.setAttr("%s.liw"%(jot),0)
        shape = self.searchControlShape(mod)
        objType = mc.objectType(shape)
        if "mesh"==objType:
            self.importMeshSkinWeight(fileName,mod,subs)
        elif "nurbsCurve"==objType:
            self.importCurveSkinWeight(fileName,mod)
        elif "nurbsSurface"==objType:
            self.importSufsSkinWeight(fileName,mod)
        elif "lattice"==objType:
            self.importLatticeSkinWeight(fileName,mod)
        self.mayaPrint( ' Rewrite <%s> skinCluster weight from %s.' %(mod,fileName) )

    def importMeshSkinWeight(self,fileName,mod,subs={}):
        #reading weights
        rFile = open(fileName,'r')#read weight file
        self.jntNumDit = {}
        #=========================================================================
        skinCluster = self.searchSkinCluster(mod)
        vertexCount = mc.polyEvaluate(mod,v=True)-1
        amount = 0
        mc.progressWindow(title="MDL:%s"%(mod),progress=amount,max=vertexCount,
                                status='Import weight: -/-',
                                isInterruptable=True )
        #=========================================================================
        for line in rFile:
            if mc.progressWindow( query=True, isCancelled=True ):
                break
            if re.search("^#|^\n|^\r|^ ",line)!=None:
                continue
            line = re.sub('\n|\r','',line)
            if(line[0:8] == 'deformer'):
                #read inf joint name
                lineList = line.split(' ',2)#lineList[0] demomer lineList[1] jointNumber lineList[2] jointName
                jotName = self.getSubName(lineList[2],subs)
                self.jntNumDit[lineList[1]] = jotName
            else:#0:  8 0.962239 9 0.0377611
                #cmds.skinPercent( 'skinCluster1', 'pPlane1.vtx[100]', transformValue=[('joint1', 0.2), ('joint3', 0.8)])
                strA = line.split(':  ',1)#vertexWeight[0] vertex number
                vertex = strA[0]
                weights = strA[1].split(' ')
                weightsList = []
                #--------------------------------
                total = 0.0
                for i in range(0,len(weights),2):
                    #vWet = float("%0.5f"%(float(weights[i+1])))#
                    vWet = round(eval(weights[i+1]),5)
                    #vWet = eval(weights[i+1])
                    if i ==(len(weights)-2):#(len(weights)-2) the last joint,if i is the end joint set the value = 1-others, for keep value sum equal 1.
                        weightsList.append((self.jntNumDit[weights[i]],1.0-total))
                    else:#else get the value form text.
                        total += vWet
                        weightsList.append((self.jntNumDit[weights[i]],vWet))
                #print '%s.vtx[%s]'%(mod,vertex),weightsList
                mc.skinPercent(skinCluster,'%s.vtx[%s]'%(mod,vertex),transformValue=weightsList)
                #--------------------------------
                amount+=1
                mc.progressWindow( edit=True, progress=amount,status=('Import weight: %s/%s'%(amount,vertexCount)))
        mc.progressWindow(endProgress=True)
        rFile.close()

    def importCurveSkinWeight(self,fileName,mod):
        "import nurbs curve skin weight"
        #reading weights
        rFile = open(fileName,'r')#read weight file
        self.jntNumDit = {}
        #=========================================================================
        skinCluster = self.searchSkinCluster(mod)
        shape = self.searchControlShape(mod)
        number = mc.getAttr("%s.degree"%shape)+mc.getAttr("%s.spans"%shape)
        amount = 0
        mc.progressWindow(title="MDL:%s"%(mod),progress=amount,max=number,
                                status='Import weight: -/-',
                                isInterruptable=True )
        #=========================================================================
        for line in rFile:
            if mc.progressWindow( query=True, isCancelled=True ):
                break
            if re.search("^#|^\n|^\r|^ ",line)!=None:
                continue
            line = re.sub('\n|\r','',line)
            if(line[0:8] == 'deformer'):
                #read inf joint name
                lineList = line.split(' ',2)#lineList[0] demomer lineList[1] jointNumber lineList[2] jointName
                self.jntNumDit[lineList[1]]=lineList[2]
            else:#0:  8 0.962239 9 0.0377611
                #cmds.skinPercent( 'skinCluster1', 'pPlane1.vtx[100]', transformValue=[('joint1', 0.2), ('joint3', 0.8)])
                strA = line.split(':  ',1)#vertexWeight[0] vertex number
                vertex = strA[0]
                weights = strA[1].split(' ')
                weightsList = []
                #--------------------------------
                total = 0.0
                for i in range(0,len(weights),2):
                    #vWet = float("%0.5f"%(float(weights[i+1])))#
                    vWet = round(eval(weights[i+1]),5)
                    #vWet = eval(weights[i+1])
                    if i ==(len(weights)-2):#(len(weights)-2) the last joint,if i is the end joint set the value = 1-others, for keep value sum equal 1.
                        weightsList.append((self.jntNumDit[weights[i]],1.0-total))
                    else:#else get the value form text.
                        total += vWet
                        weightsList.append((self.jntNumDit[weights[i]],vWet))
                #print '%s.vtx[%s]'%(mod,vertex),weightsList
                mc.skinPercent(skinCluster,'%s.cv[%s]'%(mod,vertex),transformValue=weightsList)
                #--------------------------------
                amount+=1
                mc.progressWindow( edit=True, progress=amount,status=('Import weight: %s/%s'%(amount,number)))
        rFile.close()
        mc.progressWindow(endProgress=True)

    def importSufsSkinWeight(self,fileName,mod):
        "import nurbs curve skin weight"
        #reading weights
        rFile = open(fileName,'r')#read weight file
        self.jntNumDit = {}
        #=========================================================================
        skinCluster = self.searchSkinCluster(mod)
        shape = self.searchControlShape(mod)
        numberU = mc.getAttr("%s.su"%shape)+mc.getAttr("%s.du"%shape)
        numberV = mc.getAttr("%s.sv"%shape)+mc.getAttr("%s.dv"%shape)
        amount = 0
        mc.progressWindow(title="MDL:%s"%(mod),progress=amount,max=numberU*numberV,
                                status='Import weight: -/-',
                                isInterruptable=True )
        #=========================================================================
        for line in rFile:
            if mc.progressWindow( query=True, isCancelled=True ):
                break
            if re.search("^#|^\n|^\r|^ ",line)!=None:
                continue
            line = re.sub('\n|\r','',line)
            if(line[0:8] == 'deformer'):
                #read inf joint name
                lineList = line.split(' ',2)#lineList[0] demomer lineList[1] jointNumber lineList[2] jointName
                self.jntNumDit[lineList[1]]=lineList[2]
            else:#0:  8 0.962239 9 0.0377611
                #cmds.skinPercent( 'skinCluster1', 'pPlane1.vtx[100]', transformValue=[('joint1', 0.2), ('joint3', 0.8)])
                strA = line.split(':  ',1)#vertexWeight[0] vertex number
                vertex = strA[0]
                weights = strA[1].split(' ')
                weightsList = []
                #--------------------------------
                total = 0.0
                for i in range(0,len(weights),2):
                    #vWet = float("%0.5f"%(float(weights[i+1])))#
                    vWet = round(eval(weights[i+1]),5)
                    #vWet = eval(weights[i+1])
                    if i ==(len(weights)-2):#(len(weights)-2) the last joint,if i is the end joint set the value = 1-others, for keep value sum equal 1.
                        weightsList.append((self.jntNumDit[weights[i]],1.0-total))
                    else:#else get the value form text.
                        total += vWet
                        weightsList.append((self.jntNumDit[weights[i]],vWet))
                #print '%s.vtx[%s]'%(mod,vertex),weightsList
                mc.skinPercent(skinCluster,'%s.cv%s'%(mod,vertex),transformValue=weightsList)
                #--------------------------------
                amount+=1
                mc.progressWindow( edit=True, progress=amount,status=('Import weight: %s/%s'%(amount,numberU*numberV)))
        rFile.close()
        mc.progressWindow(endProgress=True)

    def importLatticeSkinWeight(self,fileName,mod):
        "import nurbs curve skin weight"
        #reading weights
        rFile = open(fileName,'r')#read weight file
        self.jntNumDit = {}
        #=========================================================================
        skinCluster = self.searchSkinCluster(mod)
        shape = self.searchControlShape(mod)
        sds = mc.getAttr("%s.sDivisions"%shape)
        tds = mc.getAttr("%s.tDivisions"%shape)
        uds = mc.getAttr("%s.uDivisions"%shape)
        number = sds*tds*uds
        amount = 0
        mc.progressWindow(title="MDL:%s"%(mod),progress=amount,max=number,
                                status='Import weight: -/-',
                                isInterruptable=True )
        #=========================================================================
        for line in rFile:
            if mc.progressWindow( query=True, isCancelled=True ):
                break
            if re.search("^#|^\n|^\r|^ ",line)!=None:
                continue
            line = re.sub('\n|\r','',line)
            if(line[0:8] == 'deformer'):
                #read inf joint name
                lineList = line.split(' ',2)#lineList[0] demomer lineList[1] jointNumber lineList[2] jointName
                self.jntNumDit[lineList[1]]=lineList[2]
            else:#0:  8 0.962239 9 0.0377611
                #cmds.skinPercent( 'skinCluster1', 'pPlane1.vtx[100]', transformValue=[('joint1', 0.2), ('joint3', 0.8)])
                strA = line.split(':  ',1)#vertexWeight[0] vertex number
                vertex = strA[0]
                weights = strA[1].split(' ')
                weightsList = []
                #--------------------------------
                total = 0.0
                for i in range(0,len(weights),2):
                    #vWet = float("%0.5f"%(float(weights[i+1])))#
                    vWet = round(eval(weights[i+1]),5)
                    #vWet = eval(weights[i+1])
                    if i ==(len(weights)-2):#(len(weights)-2) the last joint,if i is the end joint set the value = 1-others, for keep value sum equal 1.
                        weightsList.append((self.jntNumDit[weights[i]],1.0-total))
                    else:#else get the value form text.
                        total += vWet
                        weightsList.append((self.jntNumDit[weights[i]],vWet))
                #print '%s.vtx[%s]'%(mod,vertex),weightsList
                mc.skinPercent(skinCluster,'%s.pt%s'%(mod,vertex),transformValue=weightsList)
                #--------------------------------
                amount+=1
                mc.progressWindow( edit=True, progress=amount,status=('Import weight: %s/%s'%(amount,number)))
        rFile.close()
        mc.progressWindow(endProgress=True)

    def batchExportSkinWeight(self):
        "batch Export SkinWeight in folder"
        suptObjs = []
        #get poly curve surface
        filGeos = mc.filterExpand(sm=[9,10,12])
        if filGeos!=None:
            suptObjs.extend( filGeos )
        #get lattice object
        sels = mc.ls(sl=True)
        for x in sels:
            shape = self.searchControlShape(x)
            if shape==None:
                continue
            objType = mc.objectType(shape)
            if ("lattice"==objType) and (x not in suptObjs):
                suptObjs.append(x)
        #empty list return
        if len(suptObjs)==[]:
            self.mayaWarning( "None support objects selected." )
            return False
        selFolder = self.fileDialog(m=4,okc="Select")
        if selFolder==None or selFolder==[]:
            return False
        for geo in suptObjs:
            try:
                self.exportSkinWeight( [geo],"%s/%s"%(selFolder[0],geo) )
            except:
                self.mayaWarning( "%s: export skin weight Failure."%geo )

    def batchImportSkinWeight(self,path=None):
        "batch Import SkinWeight from folder"
        selFolder = [path]
        if path==None:
            selFolder = self.fileDialog(m=4,okc="Select")
            if selFolder==[] or selFolder==None:
                return False
        allFiles = os.listdir( selFolder[0] )
        for f in allFiles:
            fileName = os.path.join(selFolder[0],f )
            if os.path.isfile(fileName) and re.search("\.w$|\.evw$",f)!=None:
                name = os.path.splitext(f)
                if mc.objExists(name[0]):
                    skined = self.searchSkinCluster(name[0])
                    if skined==None:
                        mc.skinCluster(self.getInfsFrom_w(fileName),name[0],sm=0,tsb=True)
                    mc.select(name[0])
                    mc.refresh(f=True)
                    try:
                        self.importSkinWeight(fileName,name[0])
                    except:
                        self.mayaWarning( "%s: import skin weight Failure."%name[0] )

    def importSeldPntWet(self):#import selected point weight
            pass

    def getSubName(self,oriName,subsDirt=dict()):
        "replace oriName from subsDirt"
        if subsDirt=={}:
            return oriName
        if oriName in subsDirt:
            return subsDirt[ oriName ]
        else:
            return oriName

    def getInfsFrom_w(self,fileName,subs={}):
        if self.checkSkJoint(fileName,subs)==False:
            return
        infJnts = []
        rFile = open(self.fileName,'r')
        #---------------------------------------------------------------------------------
        for idx,line in enumerate(rFile):
            if(line[0:8] == 'deformer'):
                #read inf joint name
                line = re.sub('\n|\r','',line)
                #lineList[0] demomer lineList[1] jointNumber lineList[2] jointName
                lineList = line.split(' ',2)
                jotName = self.getSubName(lineList[2],subs)
                infJnts.append( jotName )
            elif idx>10:
                break
            else:
                continue
        rFile.close()
        return infJnts

    def selInfluenceJoint(self,fileName,printer=True):
        infs = self.getInfsFrom_w(fileName)
        mc.select(infs)
        if printer==True:
            self.mayaPrint(' %s'%(infs))
        return infs

    def checkSkJoint(self,fileName,subs={}):
        lostSkJoint = []#will be return lost skin joint name
        self.fileName = fileName
        self.infJnt = []
        rFile = open(self.fileName,'r')
        #---------------------------------------------------------------------------------
        for idx,line in enumerate(rFile):
            if(line[0:8] == 'deformer'):
                #read inf joint name
                line = re.sub('\n|\r','',line)
                lineList = line.split(' ',2)#lineList[0] demomer lineList[1] jointNumber lineList[2] jointName
                jotName = self.getSubName(lineList[2],subs)
                if mc.objExists(jotName)==0:
                    lostSkJoint.append(jotName)
                else:
                    self.infJnt.append(jotName)
            elif idx>10:
                break
            else:
                continue
        rFile.close()
        if lostSkJoint==[]:
            return True
        else:
            self.mayaWarning("Lost skinJoint:%s"%(lostSkJoint))
            return False

    def holdAllInfJoint(self):
        mod = mc.ls(sl=True,ap=1)[0]
        skinCluster = self.searchSkinCluster()#return skincluster node name
        if skinCluster==0:
            self.mayaWaring("Can't find skinCluster deformer.")
            return 0
        skinJoints = mc.skinCluster(skinCluster,q=True,inf=True)
        for jot in skinJoints:
            mc.setAttr("%s.liw"%(jot),1)
        self.mayaPrint("Hold all the inf joint.")

    def unHoldAllInfJoint(self):
        mod = mc.ls(sl=True,ap=1)[0]
        skinCluster = self.searchSkinCluster()#return skincluster node name
        if skinCluster==0:
            self.mayaWaring("Can't find skinCluster deformer.")
            return 0
        skinJoints = mc.skinCluster(skinCluster,q=True,inf=True)
        for jot in skinJoints:
            mc.setAttr("%s.liw"%(jot),0)
        self.mayaPrint("unHold all the inf joint.")

    def editSelInfJointHold(self,hold):
        slJots = mc.ls(sl=True,ap=True,type="joint")
        for jot in slJots:
            if mc.objExists("%s.liw"%jot):
                mc.setAttr("%s.liw"%(jot),hold)
                self.mayaPrint("setAttr %s.liw %d;"%(jot,hold),addResult=False)

    def resetSelectSkinPose(self):
        for obj in mc.ls(sl=True):
            skinNode = self.findRelatedSkinCluster(obj)
            if skinNode!=None:
                sk_mx = "%s.matrix"%skinNode
                mx_mi = mc.getAttr(sk_mx,mi=True)
                infs = mc.listConnections(sk_mx,s=True,d=False,scn=True)
                if infs!=None:
                    for idx in mx_mi:
                        inf = mc.listConnections("%s[%d]"%(sk_mx,idx),s=True,d=False,scn=True)
                        if inf==None:
                            continue
                        matrix = mc.getAttr("%s.worldInverseMatrix[0]"%inf[0])
                        mc.setAttr("%s.pm[%d]"%(skinNode,idx),matrix,type="matrix")
    #tools cmd
    def importPointJointWeightTool(self):
        """
        """
        def setIPJWPath():
            path = self.fileDialog(m=0)
            if path!=None:
                mc.textFieldButtonGrp(skWt_tfbg,e=True,text=path[0])
        def doImport():
            mesh = mc.textFieldButtonGrp(skms_tfbg,q=True,text=True)
            if mesh=="" or not mc.objExists(mesh):
                self.mayaWarning("No one mesh loaded.")
                return
            infs = mc.textFieldButtonGrp(skIf_tfbg,q=True,text=True)
            if infs=="":
                self.mayaWarning("No one inf joint loaded.")
                return
            path = mc.textFieldButtonGrp(skWt_tfbg,q=True,text=True)
            if path=="":
                self.mayaWarning("No path loaded.")
                return
            for jot in re.split(";",infs):
                self.importPointJointWeight(path,jot,mesh)
        winName = 'zch_exportskw_win'
        if mc.window( winName,ex=True):
            mc.deleteUI( winName )
        mc.window(winName,t='SkinCluster Weight Tool',)
        gFACWin_RootLayout = mc.columnLayout(adj=1)
        mc.frameLayout(label="mportPointJointWeight...",collapsable=1)
        mc.columnLayout(adj=1)
        skms_tfbg = mc.textFieldButtonGrp(label="Skined Mesh:",buttonLabel="<< Load",bc=lambda *args:self.loadSelectedIntoButtonGrp(skms_tfbg) )
        skIf_tfbg = mc.textFieldButtonGrp(label="Which Joint:",buttonLabel="<< Load",bc=lambda *args:self.loadSelectedIntoButtonGrp(skIf_tfbg) )
        skWt_tfbg = mc.textFieldButtonGrp(label="Weight File Paht:",buttonLabel="Select",bc=lambda *args:setIPJWPath() )
        mc.button(label="Apply",c=lambda *args:doImport() )
        #------------------------------------------------------------------------
        mc.showWindow(winName)




SkinWeight = SkinWeightImExport()


def win():
    winName = "zch_skinWeight_win"
    impStr = "import %s as skWeight\nskWeight"%( __name__ )
    #------------------------------
    if mc.window( winName,ex=True):
        mc.deleteUI( winName )
    timeStamp = "2010-2015"
    showHelpCmd = "import maya.cmds;maya.cmds.showHelp('http://blog.sina.com.cn/u/2364869810\',absolute=True)"

    mc.window(winName,t="SkinCluster Weight Tool",menuBar=True)
    #Menu
    theMenu = mc.menu(label="Edit",tearOff=False,allowOptionBoxes=True)
    mc.menuItem( label="Save Seting" ,tearOff=False )
    mc.menuItem( label="Reset Seting" ,tearOff=False)
    mc.menuItem( divider=True)
    mc.radioMenuItemCollection()
    mc.menuItem( label="As Tool" ,rb=True,en=0)
    mc.menuItem( label="As Action" ,rb=True,en=0)
    mc.setParent(menu=True)
    mc.menu(label="Help",tearOff=False,allowOptionBoxes=True)
    mc.menuItem(label="Help On This Tool ...",tearOff=False,c=showHelpCmd)
    mc.setParent(menu=True)
    #skinWeight layout
    rootLaytou = mc.columnLayout(adj=1)
    mc.separator(style="single",h=5)
    mc.text(label=u"首先选择模型顶点")
    mc.separator(style="none",h=3)
    #mc.textFieldButtonGrp( buttonLabel="<< Load" ,text="load severl poly vertex")
    mc.textFieldGrp("splWet_searchFor_tfg",label=u"查找:",text="L_")
    mc.textFieldGrp("splWet_replaceWith_tfg",label=u"替换为:",text="R_")
    mc.floatFieldGrp("splWet_proportion_ffg",numberOfFields=2 ,label=u"比例:",value=[1.0,1.0,0,0])
    mc.button(label=u"分离选择的顶点皮肤权重",h=30,c="%s.splitWeightCmd()"%( impStr ) )
    mc.separator(style="single",h=5)
    mc.button(label='Hold All Inf Joint',c='%s.SkinWeight.holdAllInfJoint()'%(impStr) )
    mc.button(label='Unhold All In Joint',c='%s.SkinWeight.unHoldAllInfJoint()'%(impStr) )
    mc.separator(style="single",h=5)
    mc.button(label='Select Skin Joint',c='%s.selectSkinJoint()'%(impStr) )
    mc.button(label='Reset Select Skined Pose',c='%s.SkinWeight.resetSelectSkinPose()'%(impStr) )
    mc.button(label='Get Inf Joint(from .w file)',c='%s.selFunFileDialog()'%(impStr) )
    mc.button(label='Import Point Joint Weight',c='%s.SkinWeight.importPointJointWeightTool()'%(impStr) )
    mc.separator(style="single",h=5)
    mc.button(label='Export SkinWeight',c='%s.exportSkinClusterWeight()'%(impStr ) )
    mc.button(label='Import SkinWeight',c='%s.imFileDialog()'%(impStr ) )
    mc.button(label='Batch Export SkinWeight',c='%s.SkinWeight.batchExportSkinWeight()'%(impStr ) )
    mc.button(label='Batch Import SkinWeight',c='%s.SkinWeight.batchImportSkinWeight()'%(impStr ) )
    #mc.textImageButton(label="http://blog.sina.com.cn/u/2364869810")
    thisLayout = mc.frameLayout(lv=0,bs="etchedOut")
    mc.iconTextButton(label="Copyright (C) %s Rigging TD | ChunHai Zhao"%timeStamp,style='textOnly',image="blendShape.png",h=22,al="center",c=showHelpCmd )
    mc.setParent("..")
    mc.showWindow(winName)

def splitWeightWin():
    winName = "zch_splitWeight_win"
    impStr = "import %s as skWeight\nskWeight"%( __name__ )
    #------------------------------
    if mc.window( winName,ex=True):
        mc.deleteUI( winName )
    mc.window(winName,t="SplitWeight V12/08/22")
    #skinWeight
    rootLaytou = mc.columnLayout(adj=1)
    mc.separator(style="none",h=5)
    mc.text(label="First Select The Poly Vertex")
    mc.separator(style="single",h=5)
    #mc.textFieldButtonGrp( buttonLabel="<< Load" ,text="load severl poly vertex")
    mc.textFieldGrp("splWet_searchFor_tfg",label="Search for:",text="L_")
    mc.textFieldGrp("splWet_replaceWith_tfg",label="Replace with:",text="R_")
    mc.floatFieldGrp("splWet_proportion_ffg",numberOfFields=2 ,label="Proportion:",value=[1.0,1.0,0,0])
    mc.button(label="Split Seleced Vertex Skin Weight",h=30,c="%s.splitWeightCmd()"%( impStr ) )
    mc.separator(style="single",h=5)
    mc.text(label="(author) |Zhao ChunHai",en=0)
    mc.separator(style="single",h=5)
    mc.showWindow(winName)
    
def splitWeightCmd():
    searchFor = mc.textFieldGrp("splWet_searchFor_tfg",  q=True,text=True)
    replaceWith = mc.textFieldGrp("splWet_replaceWith_tfg",q=True,text=True)
    v1 = mc.floatFieldGrp("splWet_proportion_ffg",q=True,v1=True)
    v2 = mc.floatFieldGrp("splWet_proportion_ffg",q=True,v2=True)
    SkinWeight.splitWeight( replaceStr=[searchFor,replaceWith],proportion=[v1,v2] )
    
#----------------------------------------------------------------------------------------------------
def exportSkinClusterWeight():
    skinNode = SkinWeight.searchSkinCluster()
    if None==skinNode:
        return
    mod = mc.ls(sl=True,fl=True)
    if len(mod)>0:
        SkinWeight.exportSkinWeight( mod )
    
def selectSkinJoint():
        mod = mc.ls(sl=True,ap=1)[0]
        skinCluster = SkinWeight.searchSkinCluster()#return skincluster node name
        if skinCluster==0:
                return 0
        skinJoints = mc.skinCluster(skinCluster,q=True,inf=True)
        mc.select(skinJoints)
#-------------------------------------------------------------------------------------------------
def importFileName(fileName,fileType):
        sl = mc.ls(sl=True,ap=True)
        if(len(sl)!=1):
                return
        mod = sl[0]
        SkinWeight.importSkinWeight(fileName,mod)
def imFileDialog():
        if SkinWeight.searchSkinCluster()==0:
                return False
        setPath = mc.fileDialog2(fm=1, okc='Import Weight', fileFilter="*.w *.evw")
        if setPath is not None:
            importFileName(setPath[0], ".w")
        return  True
#---------------------------------------------------------------------------------------------------
def selectFunFileName(fileName,fileType):
        SkinWeight.selInfluenceJoint(fileName)
def selFunFileDialog():
        if SkinWeight.mayaVersion < '2011':
                mc.fileBrowserDialog(m=0,fc=selectFunFileName,an='Get',om='Import')
        elif SkinWeight.mayaVersion >='2011':
                setPath = mc.fileDialog2(fm=1,okc='Select File',fileFilter="*.w")
                if setPath is not None:
                        selectFunFileName(setPath[0],".w")
                else:
                        return
#----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    from mayaTools import reloadModule
    reloadModule()
    win()
