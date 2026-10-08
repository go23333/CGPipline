# -*- coding: utf-8 -*-

"""
配置类变量
"""

# ----- 环节 -----

# 环节名称：环节 -> 界面显示名
#
# 顺序不要依赖这里的书写顺序：Python 2.7（Maya2018 的 mayapy）下 dict 无序，
# 实测会变成 shading-half / rig-half / animation / ... 这种乱序。
# 界面与清单的顺序一律取下面的 STAGE_ORDER。
STAGES = {
    'model-all': u"模型---全流程",
    'model-half': u"模型---半流程",
    'shading-all': u"材质---全流程",
    'shading-half': u"材质---半流程",
    'rig-all': u"绑定---全流程",
    'rig-half': u"绑定---半流程",
    'layout': u"Layout",
    'animation': u"动画",
}

# 环节顺序：界面下拉框顺序，也是清单(checks_meta.json)里 __stages__ 的顺序
#
# 内核把这张表按本顺序发给客户端，客户端不再自带环节表。
# 必须与 STAGES 的键完全一致：构建清单时校验，不一致会直接报错中止。
STAGE_ORDER = (
    'model-all',
    'model-half',
    'shading-all',
    'shading-half',
    'rig-all',
    'rig-half',
    'layout',
    'animation',
)

# 环节流程分类：环节 -> 所属分类
# 分类名只用于继承（检查里写 'model' 就同时作用于 model-all / model-half），
# 不会向下展开：get_commands_list('model') 不含只声明 'model-all' 的检查。
# 值必须带尾逗号，('model') 是字符串不是元组。
STAGE_GROUPS = {
    'model-all': ('model',),
    'model-half': ('model',),
    'shading-all': ('shading',),
    'shading-half': ('shading',),
    'rig-all': ('rig',),
    'rig-half': ('rig',),
}

# 文件后缀
FILE_SUFFIX = {
    'model': '_Mo.mb',
    'model-all': '_Mo.mb',
    'model-half': '_Mo.mb',
    'shading': '_Shade.mb',
    'shading-all': '_Shade.mb',
    'shading-half': '_Shade.mb',
    'rig': '_CH.mb',
    'rig-all': '_CH.mb',
    'rig-half': '_CH.mb',
    'layout': '_ly.mb',
    'animation': '_an.mb',
}

# ----- Maya 环境 -----

# 支持的 Maya 版本
SUPPORTED_MAYA_VERSIONS = ('2018', '2023')

# ----- 默认节点白名单 -----

# Maya 默认相机
DEFAULT_CAMERA_SHAPES = ('perspShape', 'frontShape', 'topShape', 'sideShape')
DEFAULT_CAMERA_TRANSFORMS = ('persp', 'front', 'top', 'side')
DEFAULT_CAMERA_LONG_TRANSFORMS = ('|persp', '|front', '|top', '|side')

# Maya 默认材质球
DEFAULT_MATERIALS = ('lambert1', 'particleCloud1', 'standardSurface1')

# Maya 默认着色组
DEFAULT_SHADING_GROUPS = ('initialShadingGroup', 'initialParticleSE')

# 锁定/解锁相机属性时需跳过的属性
AI_CAMERA_ATTRS = (u'aiFiltermap', u'aiMesh')

# ----- 贴图目录 -----

# 允许的贴图路径
# 必须带尾逗号：写成 ('//192.168.3.248/texiaosucai') 是字符串，
# general.py 里 "any(allowed in path for allowed in ...)" 会被逐字符遍历，
# 于是 '/' 命中任何路径，检查等于失效。
ALLOWED_TEXTURE_DIRS = ('//192.168.3.248/texiaosucai',)
