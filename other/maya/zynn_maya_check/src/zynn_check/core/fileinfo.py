# -*- coding: utf-8 -*-

import os
import re

import maya.cmds as cmds


LENS_NAME_PATTERN = r'Ep[0-9]{3}_sc[0-9]{3}_[0-9]{3}[a-z]?'


class FileInfo(object):
    """
    场景文件信息

    默认取当前场景文件路径（cmds.file 只查询一次），提供文件名/项目/镜头名/
    资产-镜头判别等解析方法，避免各检查重复调用 cmds.file。

    Args:
        file_path (str): 文件路径，None 时取当前场景全路径
    """

    def __init__(self, file_path=None):
        if file_path is None:
            file_path = cmds.file(q=True, sceneName=True) or ''
        self.file_path = file_path

    def get_project(self):
        """
        获取所属项目

        :return: 所属项目
        :rtype: str
        """
        return self.file_path.split('/')[1]

    def get_name(self):
        """
        获取文件名

        :return: 文件名
        :rtype: str
        """
        return os.path.basename(self.file_path)

    def get_folder(self):
        """
        获取所属文件夹

        :return: 所属文件夹
        :rtype: str
        """
        return os.path.dirname(self.file_path)

    def get_stem(self):
        """
        获取文件名（不含后缀）

        :return: 文件名（不含后缀）
        :rtype: str
        """
        return os.path.splitext(self.get_name())[0]

    def get_suffix(self):
        """
        获取文件后缀

        :return: 文件后缀
        :rtype: str
        """
        return os.path.splitext(self.get_name())[1]

    def get_entity_name(self):
        """
        获取 资产/镜头名

        :return: 文件类型
        :rtype: str
        """
        return '_'.join(self.get_stem().split('_')[0: -1])

    def get_type(self):
        """
        获取文件类型

        :return: 文件类型
        :rtype: str
        """
        return self.get_stem().split('_')[-1]

    def get_lens_name(self):
        """
        获取当前场景文件的镜头号

        Returns:
            str: 镜头号，如 'Ep001_sc001_010a'，无匹配返回 None
        """
        lens_names = re.findall(LENS_NAME_PATTERN, self.get_name())
        if not lens_names or len(lens_names) > 1:
            return None
        return lens_names[0]

    def is_shot(self):
        """
        判断是否为镜头文件（文件名命中镜头号规则）

        :return: 是否为镜头文件
        :rtype: bool
        """
        return self.get_lens_name() is not None

    def is_asset(self):
        """
        判断是否为资产文件（非镜头文件）

        :return: 是否为资产文件
        :rtype: bool
        """
        return self.get_lens_name() is None
