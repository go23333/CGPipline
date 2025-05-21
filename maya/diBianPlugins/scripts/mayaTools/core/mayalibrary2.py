#coding=utf-8
import pymel.core as pm
import maya.cmds as cmds
import xgenm as xg
import xgenm.xgGlobal as xgg


# 确保需要的插件已经打开
pm.loadPlugin( 'fbxmaya.mll' )


#------------------------------Groom---------------------------------#
GROOM_GROUP_ID_NAME = 'groom_group_id'
GROOM_GUIDE_NAME = 'groom_guide'
GROOM_ID_NAME = "groom_id"
GROOM_GUIDE_WEIGHTS_NAME = "groom_guide_weights"
GROOM_CLOSEST_GUIDES_NAME = "groom_closest_guides"



def add_groom_group_id(node,value):
    cmds.addAttr(node, longName=GROOM_GROUP_ID_NAME, attributeType='short', defaultValue=value, keyable=True)
    cmds.addAttr(node, longName='{}_AbcGeomScope'.format(GROOM_GROUP_ID_NAME), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(node, GROOM_GROUP_ID_NAME), 'con', type='string')


def set_groom_guide(node):
    cmds.addAttr(node, longName=GROOM_GUIDE_NAME, attributeType='short', defaultValue=1, keyable=True)
    cmds.addAttr(node, longName='riCurves', attributeType='bool', defaultValue=1, keyable=True)
    cmds.addAttr(node, longName='{}_AbcGeomScope'.format(GROOM_GUIDE_NAME), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(node, GROOM_GUIDE_NAME), 'con', type='string')

def add_groom_guide_weights(node,value):
    cmds.addAttr(node, longName=GROOM_GUIDE_WEIGHTS_NAME, attributeType='float', defaultValue=value, keyable=True)
    cmds.addAttr(node, longName='{}_AbcGeomScope'.format(GROOM_GUIDE_WEIGHTS_NAME), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(node, GROOM_GUIDE_WEIGHTS_NAME), 'uni', type='string')

def add_groom_closest_guides(node,value):
    cmds.addAttr(node, longName=GROOM_CLOSEST_GUIDES_NAME, attributeType='short', defaultValue=value, keyable=True)
    cmds.addAttr(node, longName='{}_AbcGeomScope'.format(GROOM_CLOSEST_GUIDES_NAME), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(node, GROOM_CLOSEST_GUIDES_NAME), 'uni', type='string')


def add_groom_id(node,value):
    cmds.addAttr(node, longName=GROOM_ID_NAME, attributeType='short', defaultValue=value, keyable=True)
    cmds.addAttr(node, longName='{}_AbcGeomScope'.format(GROOM_ID_NAME), dataType='string', keyable=True)
    cmds.setAttr('{}.{}_AbcGeomScope'.format(node, GROOM_ID_NAME), 'uni', type='string')

def get_all_uv_meshs():
    patches = []
    palettes = xg.palettes()
    for palette in palettes:
        patches.extend(xg.palettePatches(palette))
    patches = set(patches)
    meshs = []
    for patche in patches:
        xgmSubdPatch = cmds.listRelatives(patche,type="xgmSubdPatch")[0]
        mesh_transform = cmds.listConnections(xgmSubdPatch,d=0,type="mesh")[0]
        if mesh_transform not in meshs:
            meshs.append(mesh_transform)
    return meshs

def importgroomabc(filepath):
    newnodes = cmds.file(filepath, i=True,rnn=True)
    return newnodes

def exportxgenABC(filepath,nodes,start_frame=0, end_frame=0):
    command = ( ' -file '+ filepath+
                ' -df "ogawa" -fr '+ str(start_frame)+
                ' '+ str(end_frame)+ ' -step 1  -wfw'
    )
    nodecommand = ''
    for node in nodes:
        nodecommand = nodecommand + " -obj " + node
    command = nodecommand + command
    print(cmds.xgmSplineCache(export=True, j=command))

def exportABC_gromm(objects,path,sFrame=0,eFrane=0):
    cmds.loadPlugin( 'AbcExport.mll' )
    cmds.loadPlugin( 'AbcImport.mll' )
    command = "-frameRange " + str(sFrame) + " " + str(eFrane) +" -attr groom_group_id -attr groom_guide -attr groom_id -attr groom_guide_weights -attr groom_closest_guides -uvWrite -writeFaceSets -dataFormat ogawa -root " + objects + " -file " + path
    cmds.AbcExport ( j = command )

def convert_all_descriptions_to_interactive_groom():
    interactives = []
    descriptions = xg.descriptions()
    for description in descriptions:
        interactive_shape = cmds.xgmGroomConvert(description)
        interactives.append(cmds.listRelatives(interactive_shape,ap=1,type='transform')[0])
    return interactives

def convert_interactive_groom_to_curve(temp_abc_path=r"d:\temp.abc"):
    #获取所有交互式毛发
    grooms = cmds.ls(typ="xgmSplineDescription")
    exportxgenABC(temp_abc_path,grooms)
    #删除交互式
    # for groom in grooms:
    #     cmds.delete(cmds.listRelatives(groom,typ='transform',ap=1))
    newnodes = importgroomabc(temp_abc_path)
    curveNodes = []
    for node in newnodes:
        if cmds.nodeType(node) == 'transform' and cmds.listRelatives(node,type = 'nurbsCurve'):
            curveNodes.append(node)
    return curveNodes


#------------------------------fbx---------------------------------#
def export_fbx(obj,path,op=""):
    current_select = cmds.ls(sl=1)
    cmds.select(cl=1)
    cmds.select(obj)
    pm.mel.FBXExport(f=path,pr=1,op=op,s=1)
    cmds.select(cl=1)
    cmds.select(current_select)

def import_fbx(path,rpr):
    pm.mel.FBXImport(f=path,ignoreVersion=1,mergeNamespacesOnClash=0,rpr=rpr, pr=1)

#------------------------------fun---------------------------------#
def rename_conflicting_nodes():
    '''
    检查当前场景是否存在命名冲突,如果存在就重新命名
    '''
    all_nodes = cmds.ls()
    name_dict = {}
    renamed_count = 0
    for node in all_nodes:
        base_name = node.split('|')[-1].split(':')[-1]
        if cmds.objectType(node, isAType='shape'):
            continue  
        if base_name not in name_dict:
            name_dict[base_name] = 1
        else:
            name_dict[base_name] += 1
            new_name = "{0}_{1}".format(base_name,name_dict[base_name])
            try:
                renamed_node = cmds.rename(node, new_name)
                print(u"rename:{0} -> {1}".format(node,renamed_node))
                renamed_count += 1
                new_base_name = renamed_node.split('|')[-1].split(':')[-1]
                name_dict[new_base_name] = 1
            except Exception as e:
                pass
                print(u"can't rename node {0}:{1}".format(node,str(e)))
    print(u"well done {0}".format(renamed_count))


def delete_empty_groups():
    """
    删除场景中所有空组（不包含任何子对象的变换节点）
    """
    # 获取场景中所有的组（变换节点）
    all_transforms = cmds.ls(type='transform')
    
    empty_groups = []
    deleted_count = 0
    
    for group in all_transforms:
        # 检查是否是组节点（排除相机、灯光等特殊节点）
        if cmds.nodeType(group) == 'transform':
            # 获取组下的所有子对象（排除内部形状节点）
            children = cmds.listRelatives(group, children=True, fullPath=True) or []
            shapes = cmds.listRelatives(group, shapes=True, fullPath=True) or []
            
            # 计算有效子对象数量（排除形状节点）
            valid_children = [child for child in children if child not in shapes]
            
            # 如果没有有效子对象，则认为是空组
            if not valid_children:
                empty_groups.append(group)
    
    if not empty_groups:
        print("there is no empyt group in the scene")
        return
    
    # 删除空组（从最底层的组开始删除，避免层级依赖问题）
    empty_groups.sort(key=lambda x: len(x.split('|')), reverse=True)
    
    for group in empty_groups:
        try:
            print("delte empty group:{0}".format(group))
            cmds.delete(group)
            deleted_count += 1
        except Exception as e:
            print("can't delete group:{0}: {1}".format(group,str(e)))
    print("ok,totaly delte {0} groups".format(deleted_count))


if __name__ == '__main__':
    for obj in cmds.ls(sl=1):
        set_groom_guide(obj)


    # from mayaTools import reloadModule
    # reloadModule()
    # print("#########################################")
    # #convert_all_descriptions_to_interactive_groom()
    # curves = convert_interactive_groom_to_curve()
    # curves_export_group = cmds.createNode('transform', name="curves_export_group")
    # for curve in curves:
    #     cmds.parent(curve,curves_export_group)
    # #exportABC_gromm(curves_export_group,r"d:\Desktop\abc_test.abc")
    # #cmds.delete(curves_export_group)
    # print("#########################################")
    


