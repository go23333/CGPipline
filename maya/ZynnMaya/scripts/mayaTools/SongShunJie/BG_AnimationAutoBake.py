# #coding=utf-8

from maya import cmds,mel
import time
import os
import tempfile

import json

def openJson():
    temp_path = tempfile.gettempdir()
    # temp_path=temp_path.replace('\\','/')
    json_path = os.path.join(temp_path,'mayajson.json')
    # json_path = 'D:/Documents/maya/scripts/mayajson.json'
    if os.path.exists(json_path):
        with open(json_path,'r') as js_file:
            json_data=json.load(js_file)
        if json_data :
            return json_data

# def start():
#     maya_dict=openJson()
#     maya_path=maya_dict['maya_path']
#     fbx_export_path=maya_dict['fbx_export_path']
#     start_endK_d=maya_dict['frame']
#     offset_franme=maya_dict['offset_frame']
#     start_frame=int(start_endK_d['frame'][0])#获取关键帧起始信息
#     end_frame=int(start_endK_d['frame'][1])
#     print(start_frame,end_frame)




def execute():
    maya_dict=openJson()
    maya_path=maya_dict['maya_path']
    fbx_export_path=maya_dict['fbx_export_path']
    start_endK_d=maya_dict['frame']
    offset_franme=maya_dict['offset_frame']
        
    export_fail_list=[]
    

    #print(cmds.file(q=1,sn=1))
    cmds.file(modified=0)
    cmds.file(maya_path,o=1)
    time.sleep(5)
    #将帧速率设置为25
    cmds.currentUnit( time='pal' )

    

    start_frame=start_endK_d[0]#获取关键帧起始信息
    end_frame=start_endK_d[1]
    
    #获取偏移值
    start_offset=int(offset_franme[0])
    end_offset=int(offset_franme[1])
    
    start_key=start_frame
    end_key=end_frame+start_offset+end_offset
    
    #设置时间轴范围    
    cmds.playbackOptions( minTime=start_key, maxTime=end_key )

    #获取全部名称空间名
    space_names=cmds.namespaceInfo( lon=True )
    for space_name in space_names:
        print('')
        if cmds.objExists(space_name+':Root_M'):
            #选择所有对应名称空间的对象
            #cmds.select(space_name+':*',hi=1)
            #将所有对象放入列表
            #frame_list=cmds.ls(sl=1)
            #偏移关键帧
            #start_offset=int(cmds.textFieldGrp('start_offset',text=1,q=1))
            #cmds.keyframe( frame_list,relative=True,timeChange=start_offset)
            
            print('ch',space_name)
            cmds.select(space_name+':DeformationSystem')
            #cmds.pickWalk(space_name+':DeformationSystem', direction='down')
            
            try:
                #cmds.select(space_name+':Geometry',add=1)
                select_obj=bake(start_offset,end_offset,start_frame,end_frame)
                exportFBX(fbx_export_path,space_name,select_obj,start_key,end_key)
                print('ch',space_name)
            except:
                export_fail_list.append(maya_path+'  :  '+space_name)
                print('!!!!!!!!!!!!'+space_name+' export fail')
            
        elif cmds.objExists(space_name+':*_GuGe_G'):

            print('pro',space_name)
            cmds.select(space_name+':*_GuGe_G')
            
            try:
                # cmds.select(space_name+':*_Pro_Mo',add=1)
                select_obj=bake(start_offset,end_offset,start_frame,end_frame)
                exportFBX(fbx_export_path,space_name,select_obj,start_key,end_key)
                print('pro',space_name)
            except:
                export_fail_list.append(maya_path+'  :  '+space_name)
                print('!!!!!!!!!!!!'+space_name+' export fail')

    for export_fail in export_fail_list:
        print(export_fail)
def bake(start_offset,end_offset,start_frame,end_frame):
    
    obj=cmds.ls(sl=1)

    #导入选定对象引用并删除选定对象的名称空间
    path_reference=cmds.referenceQuery(obj[0], f=True )
    cmds.file(path_reference, ir=1)
    # cmds.parent(obj,world=True)#解除组
    obj_namespace=str(obj[0]).split(':',1)[0]+':'
    cmds.select(obj)
    cmds.namespace(removeNamespace = obj_namespace, mergeNamespaceWithParent = True)
    obj_new=cmds.ls(sl=1)
    
    #选择需要烘焙的对象
    cmds.select(obj_new,hi=1)
    
    #烘焙
    obj_bake_l=[]
    obj_list=cmds.ls(sl=1)
    i=0
    while i<len(obj_list):
        obj_bake_l.append(str(obj_list[i]))
        i+=1
    obj_bake_a=str(obj_bake_l)[2:-2]
    obj_bake=obj_bake_a.replace("'",'"')
    
    #设置烘焙起始结束帧
    print(start_frame,end_frame)
    mel.eval('''bakeResults -simulation true -t "%s:%s" -sampleBy 1 -oversamplingRate 1 -disableImplicitControl true -preserveOutsideKeys true -sparseAnimCurveBake false -removeBakedAttributeFromLayer false -removeBakedAnimFromLayer false -bakeOnOverrideLayer false -minimizeRotation true -controlPoints false -shape true {"%s"}'''%(start_frame,end_frame,obj_bake))
    
    
    #选择所有烘焙的对象
    cmds.select(obj_new,hi=1)
    #将所有对象放入列表
    frame_list=cmds.ls(sl=1)
    #偏移关键帧
    cmds.keyframe( frame_list,relative=True,timeChange=start_offset)
    
    #烘焙前后帧
    #cmds.bakeResults( frame_list, t=(start,end+end_offset+start_offset), simulation=True )
    if start_offset!=0:
        cmds.bakeResults( frame_list, t=(start_frame,start_frame+start_offset+1), simulation=True,preserveOutsideKeys=True )
    if end_offset!=0:
        cmds.bakeResults( frame_list, t=(end_frame,end_frame+start_offset+end_offset), simulation=True,preserveOutsideKeys=True )

    
    #选择所有需要导出的对象
    # cmds.select(obj_new,hi=1)

    return obj_new


    
def exportFBX(fbx_export_path,space_name,select_obj,start_key,end_key):    
    
    #获取文件路径并创建新路径
    dir_path = fbx_export_path
    sc_folder = str(cmds.file(q=1,sn=1)).rsplit('_',1)[0].rsplit('/',1)[-1]
    sc_name = sc_folder.split('_')[1]
    text_path_old=dir_path+'/'+sc_name+'/'+sc_folder
    save_file_name='/'+str(cmds.file(q=1,sn=1)).rsplit('_',1)[0].rsplit('/',1)[-1]+'_an_'+space_name#创建文件名
    export_path=text_path_old+save_file_name
    print(export_path)
    #导出fbx
    cmds.select(select_obj)
    cmds.FBXResetExport()
    mel.eval('FBXExportFileVersion -v FBX201300')
    mel.eval('FBXExportSmoothingGroups -v true')
    mel.eval('FBXExportInputConnections -v false')
    mel.eval('FBXExportUpAxis y')
    mel.eval('FBXExportSmoothMesh -v true')
    #mel.eval('FBXExportSplitAnimationIntoTakes -v \"Take_001 " %s %s'%(start,end+start_offset+end_offset))
    #mel.eval('FBXExportSplitAnimationIntoTakes -c ')
    
    
    
    #创建对应FBX文件夹
    if not os.path.exists(export_path.rsplit('/',1)[0]):
        os.makedirs(export_path.rsplit('/',1)[0])
    
    if os.path.exists(export_path+'.fbx'):
        os.remove(export_path+'.fbx')
        print('delete '+export_path+'.fbx')
    
    #设置时间轴范围    
    cmds.playbackOptions( minTime=start_key, maxTime=end_key )
    #导出
    mel.eval('FBXExport -f "%s" -s'%(export_path))
    
    #eval('file -force -options "" -typ "FBX export" -pr -es "%s.fbx"'%(export_path))
    
    #ExportFbx(export_path)
    
    #创建收纳组
    try:
        cmds.select(select_obj)
        cmds.pickWalk( direction='up' )
        cmds.pickWalk( direction='up' )
        cmds.pickWalk( direction='up' )
        cmds.rename('Group_'+space_name.split(':',1)[0])
    except:
        pass             


    
    
import maya.standalone as standalone
standalone.initialize()

execute()




# ma_path=openJson()[0]
# cmds.file(modified=0)
# cmds.file(ma_path,o=1)
# print(ma_path)
# print(cmds.file(q=1,sn=1))




