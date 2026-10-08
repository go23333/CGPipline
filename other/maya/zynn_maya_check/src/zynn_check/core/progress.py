# -*- coding: utf-8 -*-
"""进度抽象（无头）

内核只依赖这里的抽象，不依赖任何 Maya UI 模块：
    - ``NullProgress``：批量/客户端无头场景，不做任何 UI 操作
Maya 插件的有 UI 实现（主进度条 + 忙光标）在 ``maya_plugin.progress.MayaProgress``。
"""


class Progress(object):

    def begin(self, total_steps):
        """初始化"""
        self._pos = 0.0
        self._inc = round(100.0 / total_steps, 2) if total_steps else 0.0

    def step(self):
        """推进一格"""
        self._pos += self._inc

    def cancelled(self):
        """查询是否取消"""
        return False

    def end(self):
        """结束"""
        pass


class NullProgress(Progress):
    """批量模式：不执行任何 UI 操作，仅记录步进"""
    pass
