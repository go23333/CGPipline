# -*-coding:utf-8 -*-

from __future__ import unicode_literals, print_function, division

if False:
    from typing import *
import maya.cmds as cmds  # 导入Maya的命令库

def main(source_attr, target_obj, attr=None,new=True,disconnect=False,pz=True):
    if len(attr.split('.'))==2:
        connections = cmds.listConnections('{}.{}'.format(target_obj, attr.split('.')[0]), plugs=True,connections=True)  # 获取目标对象的动态数组属性列表
    if len(attr.split('.'))==1:
        connections = cmds.listConnections('{}.{}'.format(target_obj,attr), plugs=True, connections=True)# 获取目标对象的动态数组属性列表

    if not connections:
        next_index = 0
    else:

        indices = [int(conn.split('[')[-1].split(']')[0]) for conn in connections if '[' in conn]#它的作用是从connections列表中解析出每个连接字符串中的索引值，并将这些索引值以整数形式存储在新的列表indices中。
        if new :
            next_index = max(indices) + 1
        else:
            next_index = max(indices)
    if disconnect == False:
        if len(attr.split('.'))==2:

            attr_sp=attr.split('.')
            target_attr = '{}.{}[{}].{}'.format(target_obj,attr_sp[0],next_index,attr_sp[1])
            cmds.connectAttr(source_attr, target_attr, force=True)  # 使用force=True确保即使存在现有的连接，也会强制执行新的连接

        else:

            target_attr = '{}.{}[{}]'.format(target_obj, attr,next_index)
            cmds.connectAttr(source_attr, target_attr, force=True)  # 使用force=True确保即使存在现有的连接，也会强制执行新的连接

    elif disconnect == True:#需要查找物体跟他动态连接到哪一个属性，而不是默认最大的属性

        if len(attr.split('.')) == 2:
            attr_sp = attr.split('.')
            connections_to_check = cmds.listConnections('{}.{}[*].{}'.format(target_obj, attr_sp[0], attr_sp[1]),source=True, destination=False, plugs=True,connections=True) or []
            try:
                if cmds.getAttr(source_attr.split('.')[0] + '.colliderType') == 'infinitePlane':
                    pass
                else:
                    target_attr = '{}.{}[{}].{}'.format(target_obj, attr_sp[0], next_index,attr_sp[1])  # 这个是新的子属性（每次都会自动添加一个新的），我下面直接用它进行连接，好让断开的属性值归默认
            except ValueError:
                target_attr = '{}.{}[{}].{}'.format(target_obj, attr_sp[0], next_index, attr_sp[1])#这个是新的子属性（每次都会自动添加一个新的），我下面直接用它进行连接，好让断开的属性值归默认
        else:
            connections_to_check = cmds.listConnections('{}.{}[*]'.format(target_obj, attr), source=True,
                                                        destination=False, plugs=True, connections=True) or []
            target_attr = '{}.{}[{}]'.format(target_obj, attr, next_index)

        for conn in connections_to_check:
            if conn == source_attr or conn == source_attr[:-3]:
                pp_index=connections_to_check.index(conn)


                if pz==True:
                    try :
                        if cmds.getAttr(source_attr.split('.')[0] + '.colliderType'):
                            if cmds.getAttr(source_attr.split('.')[0] + '.colliderType') != 'infinitePlane' :
                                default_val = cmds.getAttr(target_attr)
                                print('最新的属性值', default_val)
                                cmds.disconnectAttr(source_attr, connections_to_check[pp_index-1])
                                cmds.connectAttr(target_attr, connections_to_check[pp_index-1], force=True)
                                cmds.disconnectAttr(target_attr, connections_to_check[pp_index-1])
                            elif cmds.getAttr(source_attr.split('.')[0] + '.colliderType') == 'infinitePlane':
                                infi=connections_to_check[pp_index-1].split('.')
                                cmds.removeMultiInstance('{}.{}'.format(infi[0],infi[1]), b=1)#删除多实例，指定删除谁，比如'boneDynamicsNode1.infinitePlaneCollider[0]'，b的意思是直接断开连接并且删除
                    except ValueError:
                        default_val = cmds.getAttr(target_attr)
                        print('最新的属性值', default_val)
                        cmds.disconnectAttr(source_attr, connections_to_check[pp_index - 1])
                        cmds.connectAttr(target_attr, connections_to_check[pp_index - 1], force=True)
                        cmds.disconnectAttr(target_attr, connections_to_check[pp_index - 1])
                else:
                    cmds.disconnectAttr(source_attr, connections_to_check[pp_index-1])

                print("已断开连接 {} 和 {}".format(source_attr,connections_to_check[pp_index-1]))
                break  # 找到并断开连接后，退出循环
        else:

            print("未找到 {} 与 {}.{} 之间的连接".format(source_attr,target_obj,attr))


















