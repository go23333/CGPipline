# -*- coding: utf-8 -*-
"""
zynn_check 外部批处理调用接口

供外部进程在 mayapy 中加载 zynn_check 后，
以批处理方式检查 Maya 文件。

stdout 协议：
    START <file>
    RESULT <file> <result_json_path>
"""

import os
import io
import sys
import json
import argparse


COMPONENT_FORMAT = {
    'uv': '.map[{}]',
    'vertex': '.vtx[{}]',
    'edge': '.e[{}]',
    'face': '.f[{}]',
}


def to_unicode(value):
    """
    将 Py2 下的 bytes / Exception / 容器数据转换为可序列化的数据
    """
    if isinstance(value, Exception):
        try:
            return str(value)
        except Exception:
            return repr(value)

    if isinstance(value, bytes):
        return value.decode('utf-8', 'replace')

    if isinstance(value, dict):
        return {
            to_unicode(key): to_unicode(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [to_unicode(item) for item in value]

    return value


def print_event(message):
    """输出批处理事件"""
    print(message)
    sys.stdout.flush()


def open_file(cmds, file_path):
    """打开 Maya 文件。"""
    cmds.file(new=True, force=True)
    cmds.file(file_path, open=True, force=True, ignoreVersion=True)


def _resolve_node_name(cmds, node):
    """将uuid转为节点名"""
    node = to_unicode(node)
    if cmds is None:
        return node
    try:
        names = cmds.ls(node)
        if names:
            return to_unicode(names[0])
    except Exception:
        pass
    return node


def get_detail_list(diagnostic, cmds=None):
    """
    将 Engine 返回的诊断结果转换成明细列表

    Args:
        diagnostic (dict): 诊断结果
        cmds: maya.cmds 模块
    """
    if not diagnostic:
        return []

    result_type = diagnostic.get('result_type', 'node')
    values = diagnostic.get('uuids') or []

    # 普通文本
    if result_type == 'text':
        return [to_unicode(value) for value in values]

    # 节点
    if result_type == 'node':
        if isinstance(values, dict):
            return [
                {
                    u'node': _resolve_node_name(cmds, node),
                    u'text': to_unicode(text or u'')
                }
                for node, text in values.items()
            ]

        return [
            _resolve_node_name(cmds, value)
            for value in values
        ]

    # 组件
    if isinstance(values, dict):
        component_format = COMPONENT_FORMAT.get(result_type)
        details = []

        for node, indices in values.items():
            node = _resolve_node_name(cmds, node)

            for index in indices:
                if component_format:
                    details.append(node + component_format.format(index))
                else:
                    details.append(node)

        return details

    return [
        to_unicode(value)
        for value in values
    ]


def create_result(file_path, stage):
    """创建单个文件的检查结果"""
    return {
        'file': file_path,
        'stage': stage,
        'status': 'error',
        'open_error': None,
        'summary': {
            'passed': 0,
            'failed': 0,
            'blocked': 0,
            'total': 0,
        },
        'diagnostics': {},
        'details': {},
        'fix': {},
        'saved': False,
    }


def check_file(cmds, manifest, file_path):
    """检查 Maya 文件"""
    stage = manifest['stage']
    commands = manifest.get('commands')

    result = create_result(file_path, stage)

    # 打开文件
    try:
        open_file(cmds, file_path)
    except Exception as exc:
        result['open_error'] = str(exc)
        return result

    # 执行检查
    try:
        from zynn_check.core.engine import Engine

        engine = Engine(stage_name=stage)

        if not commands:
            commands = list(engine.commandsList.keys())

        fix_enabled = bool(manifest.get('fix'))
        fix_results = {}

        if fix_enabled:
            diagnostics, _, fix_results = engine.command_to_run_fix(commands)
        else:
            diagnostics, _ = engine.command_to_run(commands)

        # 至少一项修复成功时，就地保存修复后的文件
        if fix_enabled and any(status == 'fixed' for status in fix_results.values()):
            cmds.file(save=True)
            result['saved'] = True

        result['fix'] = fix_results

        # 统计检查结果
        statuses = [diagnostic.get('status') for diagnostic in diagnostics.values()]

        result['summary'] = {
            'passed': statuses.count('passed'),
            'failed': statuses.count('failed'),
            'blocked': statuses.count('blocked'),
            'total': len(statuses),
        }

        if result['summary']['failed']:
            result['status'] = 'failed'
        else:
            result['status'] = 'passed'

        result['diagnostics'] = diagnostics

        # 整理明细
        for command, diagnostic in diagnostics.items():
            result['details'][command] = get_detail_list(diagnostic, cmds)

    except Exception as exc:
        result['status'] = 'error'
        result['open_error'] = 'check error: ' + str(exc)

    return result


def write_result(result_dir, file_index, result):
    """保存检查结果 JSON"""
    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)

    file_name = 'result_{}.json'.format(file_index)
    result_path = os.path.join(result_dir, file_name)

    try:
        result = to_unicode(result)
        content = json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as exc:
        content = json.dumps(
            {
                'file': result.get('file', ''),
                'stage': result.get('stage', ''),
                'status': 'error',
                'open_error': 'result serialize failed: {0}'.format(exc),
                'summary': {},
                'diagnostics': {},
                'details': {},
            },
            ensure_ascii=False
        )

    with open(result_path, 'wb') as stream:
        stream.write(content.encode('utf-8'))

    return result_path


def format_detail(detail):
    """格式化单条检查明细"""
    if isinstance(detail, dict):
        node = to_unicode(detail.get('node', ''))
        text = to_unicode(detail.get('text') or '')

        if text:
            return u'{} - {}'.format(node, text)

        return node

    return to_unicode(detail)


def print_result(result):
    """输出详细检查结果"""
    summary = result.get('summary') or {}

    print_event(
        u'SUMMARY {} status={} passed={} failed={} '
        u'blocked={} total={}'.format(
            result.get('file', ''),
            result.get('status', ''),
            summary.get('passed', 0),
            summary.get('failed', 0),
            summary.get('blocked', 0),
            summary.get('total', 0)
        )
    )

    if result.get('open_error'):
        print_event(u'OPEN_ERROR: {}'.format(result['open_error']))

    details = result.get('details') or {}
    for command in sorted(details.keys()):
        entries = details[command]

        if not entries:
            print_event(u'PASS {}'.format(command))
            continue

        text = u', '.join(format_detail(entry) for entry in entries)
        print_event(u'FAIL {}: {}'.format(command, text))


def run_batch(cmds, manifest_path, verbose=False):
    """执行文件检查"""
    with io.open(manifest_path, 'r', encoding='utf-8') as stream:
        manifest = json.load(stream)

    file_path = manifest['file']
    print_event('START ' + file_path)

    result = check_file(cmds, manifest, file_path)
    result_path = write_result(manifest['result_dir'], 0, result)
    print_event('RESULT {} {}'.format(file_path, result_path))

    if verbose:
        print_result(result)


def parse_args(argv):
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='zynn_check batch interface (mayapy)'
    )

    parser.add_argument(
        '--manifest',
        default=None,
        help='manifest json 路径'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='每个文件额外输出检查摘要与明细'
    )

    return parser.parse_args(argv)


def main(argv=None):
    """批处理入口：由引导脚本在 maya 初始化后调用"""
    import maya.cmds as cmds

    args = parse_args(argv)
    if not args.manifest:
        raise RuntimeError('--manifest is required')

    run_batch(cmds, args.manifest, args.verbose)
