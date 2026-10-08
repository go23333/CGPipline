# -*- coding: utf-8 -*-
"""Maya 插件（免安装交付）

本包只承载 **Maya 内使用的界面与进度实现**，检查规则与引擎全部来自
``zynn_check`` 内核包（仓库 ``src/zynn_check``），与客户端 ``client/`` 共用同一份内核。

上级加载脚本的调用方式：

    import sys
    sys.path.insert(0, r'<仓库根目录>')     # 让 maya_plugin 可导入
    import maya_plugin
    maya_plugin.show('model')               # 或 maya_plugin.show_UI('model')

只要仓库整份 clone 下来，导入本包时会自动把 ``<仓库根>/src``
放到 ``sys.path`` 最前面，因此 Maya 侧无需安装 zynn_check（免安装）。
"""

import os
import sys

__all__ = ['show', 'show_UI']

_BOOTSTRAPPED = False


def _bootstrap():
    """确保 ``import zynn_check`` 指向本仓库的内核

    免安装交付下 ``src/`` 与 ``maya_plugin/`` 永远成对出现，所以**优先**使用
    仓库自带的 ``src/``（放到 sys.path 最前，避免被客户端装进 Maya
    site-packages 的 wheel 抢占，造成插件与内核版本错配）。

    若 ``src/`` 不存在（例如只把 maya_plugin 单独拷到别处），
    则回退为依赖环境中已安装的 zynn_check。
    """
    global _BOOTSTRAPPED

    if _BOOTSTRAPPED:
        return

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(repo_root, 'src')

    if os.path.isdir(os.path.join(src_dir, 'zynn_check')):
        while src_dir in sys.path:
            sys.path.remove(src_dir)
        sys.path.insert(0, src_dir)
        _BOOTSTRAPPED = True
        return

    try:
        import zynn_check  # noqa: F401
    except ImportError:
        raise RuntimeError(
            u'找不到 zynn_check 内核：{} 下没有 zynn_check 包，环境中也没有已安装的 '
            u'zynn_check。请确认仓库已完整 clone（src/ 与 maya_plugin/ 必须同时存在）。'.format(src_dir)
        )

    _BOOTSTRAPPED = True


def show(stage='model'):
    """显示指定环节的检查窗口

    Args:
        stage (str): 环节名称，如 'model' / 'shading' / 'rig' / 'layout' / 'animation'

    Returns:
        UI: 检查主窗口实例
    """
    _bootstrap()

    from .ui import show_UI as _show_UI

    return _show_UI(stage)


# 兼容旧调用名（原先为 zynn_check.core.ui.show_UI）
show_UI = show
