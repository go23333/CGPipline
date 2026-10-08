# -*- coding: utf-8 -*-
"""Maya 插件专属进度实现

基于 Maya 主进度条与忙光标，仅在有 UI 的 Maya 会话中使用。
无头（批量/客户端）场景请使用 ``zynn_check.core.progress.NullProgress``。
"""

import maya.mel as mel
import maya.cmds as cmds

from zynn_check.core.progress import Progress


class MayaProgress(Progress):
    """基于 Maya 主进度条与忙光标的进度实现"""

    def __init__(self):
        self._bar = None

    def begin(self, total_steps):
        super(MayaProgress, self).begin(total_steps)
        cmds.waitCursor(state=True)
        self._bar = mel.eval('$tmp = $gMainProgressBar')
        cmds.progressBar(self._bar, edit=True, beginProgress=True, isInterruptable=True,
                         minValue=0, maxValue=100, status=u"检查中...")

    def step(self):
        super(MayaProgress, self).step()
        cmds.progressBar(self._bar, edit=True, step=self._pos)

    def cancelled(self):
        return cmds.progressBar(self._bar, query=True, isCancelled=True)

    def end(self):
        cmds.progressBar(self._bar, edit=True, endProgress=True)
        cmds.waitCursor(state=False)
