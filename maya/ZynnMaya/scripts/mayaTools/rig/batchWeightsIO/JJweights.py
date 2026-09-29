# coding:utf-8
import maya.cmds as cmds
import json,sys,os,glob
user_documents_path = os.path.join(os.path.expanduser("~"))
JJ_weights_path = os.path.join(user_documents_path, "maya", "scripts").replace("\\", "/") + "/RigTools/JJ_weights"
if JJ_weights_path not in sys.path:
    sys.path.insert(0, JJ_weights_path)

def Clean_up_folders():
    # 清理文件夹
    folder_path = JJ_weights_path+"/skin"
    xml_files = glob.glob(os.path.join(folder_path, "*.xml"))
    txt_files = glob.glob(os.path.join(folder_path, "*.json"))
    all_files = xml_files + txt_files
    if len(all_files) > 200:
        for file_path in all_files:
            os.remove(file_path)



def get_select_obj():
    # 获取选择
    transformList = []
    select_obj = cmds.ls(sl=True)
    if select_obj:
        if len(select_obj) == 1:
            # 获取单个对象的所有子孙对象
            children = cmds.listRelatives(select_obj[0], children=True, allDescendents=True, type="transform") or [None]
            if children[0] != None:
                select_obj = children if children else select_obj
            else:
                select_obj = select_obj
        for each in select_obj:
            my_sel = cmds.listRelatives(each, shapes=True)
            if my_sel:
                shape_history = cmds.listHistory(my_sel, levels=5)
                skin_clus = cmds.ls(shape_history, typ="skinCluster")
                if skin_clus:
                    transformList.append(each)
    return transformList
    
                    

def Export_weights():
    # 导出权重
    Clean_up_folders() #清理文件夹
    skin_path = JJ_weights_path + "/skin"
    obj_list = get_select_obj()
    for each in obj_list:
        my_sel = cmds.listRelatives(each, shapes=True)
        shape_history = cmds.listHistory(my_sel, levels=5)
        skin_clus = cmds.ls(shape_history, typ="skinCluster")
        joints_influence = cmds.ls(shape_history, typ="joint")
        # 处理命名空间
        Re_each = each.split(':')[-1] if ':' in each else each
        # 保存关节影响列表
        folder_path = skin_path + "/"
        file_path = folder_path + Re_each + ".json"
        with open(file_path, "w") as f:
            for obj in joints_influence:
                f.write(obj + "\n")
        # 导出皮肤权重
        if skin_clus:
            cmds.deformerWeights(Re_each + "_sknCls.xml", deformer=skin_clus[0], ex=True, path=folder_path)  



                    
     
def Import_weights():
    # 选择模型导入权重
    skin_path = JJ_weights_path + "/skin"
    select_obj = cmds.ls(sl=True)
    if select_obj:
        if len(select_obj) == 1:
            children = cmds.listRelatives(select_obj[0], children=True, allDescendents=True, type="transform")
            select_obj = children if children else select_obj
    for each in select_obj:   
        name_obj = each.split(':')[-1] if ':' in each else each
        folder_path = skin_path + "/"
        file_path = folder_path + name_obj + ".json"
        # 读取关节名称
        if  os.path.exists(file_path):
            with open(file_path, 'r') as f:
                joint_names = f.read().splitlines()
            joint_list = cmds.ls(joint_names)
            # ----
            shape_history = cmds.listHistory(each, levels=5)
            skin_clus = cmds.ls(shape_history, typ="skinCluster")
            if skin_clus:
                cmds.delete(skin_clus)
            new_skin = cmds.skinCluster(joint_list, each, tsb=True)  #joint_list=骨骼列表/each=网格
            cmds.deformerWeights(name_obj + "_sknCls.xml", path=folder_path, im=True, method="index", deformer=new_skin[0])
            cmds.skinCluster(new_skin, edit=True, fnw=True)
        cmds.select(cl=True)
        
                    
def Export_solo():
    skin_path = JJ_weights_path + "/skin"
    each = select_obj = cmds.ls(sl=True)[0]
    if cmds.nodeType(each) == "skinCluster":
        skin_clus = each
        joints_influence = cmds.skinCluster(skin_clus, query=True, influence=True)
        # 处理命名空间
        Re_each = "test"
        # 保存关节影响列表
        folder_path = skin_path + "/"
        file_path = folder_path + Re_each + ".json"
        with open(file_path, "w") as f:
            for obj in joints_influence:
                f.write(obj + "\n")
        # 导出皮肤权重
        if skin_clus:
            cmds.deformerWeights(Re_each + "_sknCls.xml", deformer=skin_clus, ex=True, path=folder_path)  
    else:
        cmds.warning("请选择skinCluster节点导出权重")
    
def Import_solo():
    skin_path = JJ_weights_path + "/skin"
    each = select_obj = cmds.ls(sl=True)[0]
    name_obj = "test"
    folder_path = skin_path + "/"
    file_path = folder_path + name_obj + ".json"
    # 读取关节名称
    if  os.path.exists(file_path):
        with open(file_path, 'r') as f:
            joint_names = f.read().splitlines()
        joint_list = cmds.ls(joint_names)
        # ----
        shape_history = cmds.listHistory(each, levels=5)
        skin_clus = cmds.ls(shape_history, typ="skinCluster")
        if skin_clus:
            cmds.delete(skin_clus)
        new_skin = cmds.skinCluster(joint_list, each, tsb=True)  #joint_list=骨骼列表/each=网格
        cmds.deformerWeights(name_obj + "_sknCls.xml", path=folder_path, im=True, method="index", deformer=new_skin[0])
        cmds.skinCluster(new_skin, edit=True, fnw=True)
    cmds.select(cl=True)       
                    
                    
def UI_JJweights():
    if cmds.window("Win_JJweights", exists=True):
        cmds.deleteUI("Win_JJweights", window=True)
    # 创建 UI
    Win_JJweights = cmds.window("Win_JJweights", title="JJweights_LHJ", widthHeight=(205, 120), mnb=False, mxb=False, sizeable=False)
    cmds.showWindow(Win_JJweights)
    mainLayoutA = cmds.columnLayout("Layout",width=100)
    cmds.separator(w=200, h=10, style="in", parent=mainLayoutA) 
    cmds.rowColumnLayout(numberOfColumns=10,parent=mainLayoutA) 
    cmds.button(label="导出权重",width=200,command=lambda x:Export_weights())
    cmds.separator(w=200, h=10, style="in", parent=mainLayoutA)
    cmds.rowColumnLayout(numberOfColumns=10,parent=mainLayoutA) 
    cmds.button(label="导入权重",width=200,command=lambda x:Import_weights())
    cmds.separator(w=200, h=10, style="in", parent=mainLayoutA)
    cmds.rowColumnLayout(numberOfColumns=10,parent=mainLayoutA) 
    cmds.button(label="单独导出",width=98,command=lambda x:Export_solo())
    cmds.separator(w=4) # 空格
    cmds.button(label="单独导入",width=98,command=lambda x:Import_solo())


if __name__ == "__main__":
    UI_JJweights()
                    

           