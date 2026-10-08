# -*- coding: utf-8 -*-

from .registry import CHECK_REGISTRY
from . import report


class Check(object):
    """
    检查基类

    子类通过 @register 类装饰器注册到 CHECK_REGISTRY，元数据以类属性声明。
    引擎实例化检查并注入 context（承载收集数据与结果），run 写 errors，
    errors 通过 property 挂到 context['results'][name]，fix 默认读取本检查的 errors。

    Attributes:
        name (str): 命令唯一标识
        label (str): 显示名称
        category (str): 分类名称
        check_type (str): 检查类型，决定遍历器
        result_type (str): 返回类型，决定错误解析
        stages (list): 所属环节列表
        requires (list): 前置检查名称列表
    """

    name = ''
    label = ''
    category = ''
    check_type = 'transform'
    result_type = 'node'
    stages = []
    requires = []

    def __init__(self, context):
        self.context = context

    @property
    def errors(self):
        return self.context['results'][self.name]

    @property
    def file_info(self):
        """当前场景文件信息（由收集器始终收集）"""
        return self.context.get('file_info')

    def prepare(self):
        """运行前钩子，初始化 errors 容器；需要非 list 容器的检查在此重设"""
        self.context['results'][self.name] = []

    def run(self, *args):
        raise NotImplementedError

    def selectable(self):
        """把本检查的 errors 归一化为 fix 需要的 selectable 形式"""
        wrapped = {'result_type': self.result_type, 'uuids': self.errors}
        if self.result_type == 'node':
            return report.get_selectable(report.parse_errors(wrapped))
        if self.result_type == 'text':
            return report.parse_errors(wrapped)
        return wrapped


def register(cls):
    """
    检查类注册装饰器

    Py2/Py3 兼容的注册方式，将检查类写入 CHECK_REGISTRY（键为 cls.name）。

    Args:
        cls (type): 检查类

    Returns:
        type: 原样返回检查类
    """
    CHECK_REGISTRY[cls.name] = cls
    return cls
