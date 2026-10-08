# -*- coding: utf-8 -*-

try:
    from PySide6 import QtCore, QtWidgets
    from shiboken6 import wrapInstance
    IS_PYSIDE_6 = True
except ImportError:
    from PySide2 import QtCore, QtWidgets
    from shiboken2 import wrapInstance
    IS_PYSIDE_6 = False

from functools import partial

import maya.mel as mel
import maya.cmds as cmds
import maya.OpenMayaUI as omui

from zynn_check.__version__ import __version__
from zynn_check.core import environment as env
from zynn_check.core.config import STAGES
from zynn_check.core.engine import Engine
from .progress import MayaProgress


class UI(QtWidgets.QMainWindow):
    """主检查窗口类"""
    qmwInstance = None
    version = __version__

    def __init__(self, parent=None, stage_name='model'):
        """
        初始化主窗口，根据环节名称创建对应的引擎和UI组件

        Args:
            parent (QWidget): 父窗口对象，默认为None
            stage_name (str): 环节名称，如 'model' / 'shading'
        """
        super(UI, self).__init__(parent)
        self.stage_name = stage_name
        # 未登记的环节名不做加工，保持原样显示
        label = STAGES.get(stage_name)
        title = u"{}检查".format(label) if label else stage_name
        self.setWindowTitle(u"{} {}".format(title, self.version))
        self.resize(1200, 900)

        self.engine = Engine(stage_name=stage_name, progress=MayaProgress())
        self._error_cache = {}
        self.diagnostics = {}
        self.checked_nodes = []
        self.commandsList = self.engine.commandsList
        self.categoryLayout = {}
        self.categoryWidget = {}
        self.categoryButton = {}
        self.categoryHeader = {}
        self.categoryCollapse = {}
        self.commandWidget = {}
        self.commandLayout = {}
        self.commandLabel = {}
        self.commandCheckBox = {}
        self.commandRunButton = {}
        self.error_info_button = {}
        self.fix_button = {}

        mainWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(mainWidget)
        mainLayout = QtWidgets.QVBoxLayout(mainWidget)
        report = self.buildReportUI()
        checks = self.buildChecksList()
        left = QtWidgets.QWidget()
        right = QtWidgets.QWidget()
        splitter = QtWidgets.QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(right)
        left.setLayout(checks)
        right.setLayout(report)
        mainLayout.addWidget(splitter)

        self.loadSettings()
        self.createReport()

    def buildReportUI(self):
        """
        构建右侧报告区域UI

        创建报告输出控件及相关按钮布局。

        Returns:
            QVBoxLayout: 报告区域的垂直布局
        """
        report = QtWidgets.QVBoxLayout()

        self.reportOutputUI = QtWidgets.QTextEdit()
        self.reportOutputUI.setReadOnly(True)
        self.reportOutputUI.setMinimumWidth(600)

        runAllCheckedButton = QtWidgets.QPushButton(u"运行检查")
        runAllCheckedButton.setFixedWidth(300)

        clearButton = QtWidgets.QPushButton(u"清除")
        clearButton.setFixedWidth(150)

        runLayout = QtWidgets.QHBoxLayout()
        runLayout.addStretch()
        runLayout.addWidget(clearButton)
        runLayout.addWidget(runAllCheckedButton)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.reportOutputUI)
        splitter.setSizes([0, 1])
        report.addWidget(splitter)
        report.addLayout(runLayout)
        runAllCheckedButton.clicked.connect(self.sanityCheckChecked)
        clearButton.clicked.connect(self.clearReport)
        return report

    def buildChecksList(self):
        """
        构建左侧检查列表区域UI

        创建分类标题、命令复选框、运行按钮及底部批量操作按钮。

        Returns:
            QVBoxLayout: 检查列表区域的垂直布局
        """
        checkLayout = QtWidgets.QVBoxLayout()
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)

        contentWidget = QtWidgets.QWidget()
        checks = QtWidgets.QVBoxLayout(contentWidget)

        category = self.getCategories(self.commandsList)
        for obj in category:
            self.categoryWidget[obj] = QtWidgets.QWidget()
            self.categoryLayout[obj] = QtWidgets.QVBoxLayout()
            self.categoryHeader[obj] = QtWidgets.QHBoxLayout()
            self.categoryButton[obj] = QtWidgets.QPushButton(obj)
            self.categoryCollapse[obj] = QtWidgets.QPushButton(u'\u2193')
            self.categoryCollapse[obj].clicked.connect(
                partial(self.toggleUI, obj))
            self.categoryCollapse[obj].setMaximumWidth(30)
            self.categoryButton[obj].setStyleSheet(
                """background-color: grey;
                text-transform: uppercase;
                color: #000000;
                font-size: 18px;""")
            self.categoryButton[obj].clicked.connect(
                partial(self.checkCategory, obj))
            self.categoryHeader[obj].addWidget(self.categoryButton[obj])
            self.categoryHeader[obj].addWidget(self.categoryCollapse[obj])
            self.categoryWidget[obj].setLayout(self.categoryLayout[obj])
            checks.addLayout(self.categoryHeader[obj])
            checks.addWidget(self.categoryWidget[obj])

        for name in sorted(self.commandsList.keys()):
            label = self.commandsList[name]['label']
            category = self.commandsList[name]['category']

            self.commandWidget[name] = QtWidgets.QWidget()
            self.commandWidget[name].setMaximumHeight(40)
            self.commandLayout[name] = QtWidgets.QHBoxLayout()

            self.categoryLayout[category].addWidget(self.commandWidget[name])
            self.commandWidget[name].setLayout(self.commandLayout[name])

            self.commandLayout[name].setSpacing(4)
            self.commandLayout[name].setContentsMargins(0, 0, 0, 0)
            self.commandWidget[name].setStyleSheet('padding: 0px; margin: 0px;')
            self.commandLabel[name] = QtWidgets.QLabel(label)
            self.commandLabel[name].setMinimumWidth(180)
            check_cls = self.engine._check_registry.get(name)
            requires = getattr(check_cls, 'requires', None)
            if requires:
                labels = u"、".join(self._get_check_label(r) for r in requires)
                self.commandLabel[name].setToolTip(u"依赖: {}".format(labels))
            self.commandCheckBox[name] = QtWidgets.QCheckBox()

            self.commandCheckBox[name].setChecked(False)
            self.commandCheckBox[name].setMaximumWidth(20)

            self.commandRunButton[name] = QtWidgets.QPushButton(u"运行")
            self.commandRunButton[name].setMaximumWidth(40)

            self.commandRunButton[name].clicked.connect(
                partial(self.oneOfs, name))

            self.error_info_button[name] = QtWidgets.QPushButton(u"详情")
            self.error_info_button[name].setEnabled(False)
            self.error_info_button[name].setMaximumWidth(40)

            self.error_info_button[name].clicked.connect(
                partial(self._show_detail, name))

            check_cls = self.engine._check_registry.get(name)
            if check_cls is not None and hasattr(check_cls, 'fix'):
                self.fix_button[name] = QtWidgets.QPushButton(u"修复")
                self.fix_button[name].setEnabled(False)
                self.fix_button[name].setMaximumWidth(40)
                self.fix_button[name].clicked.connect(
                    partial(self._run_fix, name))

            self.commandLayout[name].addWidget(self.commandLabel[name])
            self.commandLayout[name].addWidget(self.commandCheckBox[name])
            self.commandLayout[name].addWidget(self.commandRunButton[name])
            self.commandLayout[name].addWidget(self.error_info_button[name])
            if name in self.fix_button:
                self.commandLayout[name].addWidget(self.fix_button[name])
            else:
                self.commandLayout[name].addSpacerItem(
                    QtWidgets.QSpacerItem(44, 0, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))

        checks.addStretch()

        scrollArea.setWidget(contentWidget)

        checkButtonsLayout = QtWidgets.QHBoxLayout()

        uncheckAllButton = QtWidgets.QPushButton(u"取消选择")
        uncheckAllButton.clicked.connect(self.uncheckAll)

        invertCheckButton = QtWidgets.QPushButton(u"反选")
        invertCheckButton.clicked.connect(self.invertCheck)

        failedCheckButton = QtWidgets.QPushButton(u"检查失败项")
        failedCheckButton.clicked.connect(self.selectFailed)

        checkAllButton = QtWidgets.QPushButton(u"选择全部")
        checkAllButton.clicked.connect(self.checkAll)

        checkButtonsLayout.addWidget(uncheckAllButton)
        checkButtonsLayout.addWidget(invertCheckButton)
        checkButtonsLayout.addWidget(failedCheckButton)
        checkButtonsLayout.addWidget(checkAllButton)

        checkLayout.addWidget(scrollArea)
        checkLayout.addLayout(checkButtonsLayout)

        return checkLayout

    def getCategories(self, commands):
        """
        获取所有命令的唯一分类列表

        Args:
            commands (dict): 命令字典

        Returns:
            list: 排序后的分类名称列表
        """
        allCategories = set()
        for command in commands.values():
            allCategories.add(command['category'])
        categories = list(allCategories)
        categories.sort()
        return categories

    def _get_check_label(self, name):
        """
        获取检查的 label 名称

        Args:
            name (str): 检查命令名

        Returns:
            str: label 名称
        """
        info = self.engine._check_registry.get(name)
        if info is not None:
            return getattr(info, 'label', name)
        return name

    def checkState(self, name):
        """
        获取指定命令的复选框状态

        Args:
            name (str): 命令名称

        Returns:
            Qt.CheckState: 复选框状态
        """
        return self.commandCheckBox[name].checkState()

    def checkAll(self):
        """
        勾选所有命令的复选框
        """
        for command in self.commandsList:
            self.commandCheckBox[command].setChecked(True)

    def toggleUI(self, category):
        """
        切换分类面板的折叠/展开状态

        Args:
            category (str): 分类名称
        """
        state = self.categoryWidget[category].isVisible()
        buttonLabel = u"\u21B5" if state else u"\u2193"
        self.categoryCollapse[category].setText(buttonLabel)
        self.categoryWidget[category].setVisible(not state)

    def uncheckAll(self):
        """
        取消所有命令的勾选
        """
        for name in self.commandsList:
            self.commandCheckBox[name].setChecked(False)

    def invertCheck(self):
        """
        反选所有命令的复选框状态
        """
        for name in self.commandsList.keys():
            self.commandCheckBox[name].setChecked(
                not self.commandCheckBox[name].isChecked())

    def clearReport(self):
        """
        清除报告内容
        """
        self.diagnostics = {}
        self.checked_nodes = []
        for command in self.commandsList.keys():
            self.error_info_button[command].setEnabled(False)
            if command in self.fix_button:
                self.fix_button[command].setEnabled(False)
            self.commandLabel[command].setStyleSheet('background-color: none;')
        self._error_cache.clear()
        self.reportOutputUI.clear()

    def checkCategory(self, category):
        """
        切换分类下所有命令的勾选状态

        若分类中有未勾选的命令则全部勾选，否则全部取消勾选。

        Args:
            category (str): 分类名称
        """
        uncheckedCategoryButtons = []
        categoryButtons = []
        for name in self.commandsList.keys():
            if self.commandsList[name]['category'] == category:
                categoryButtons.append(name)
                if self.commandCheckBox[name].isChecked():
                    uncheckedCategoryButtons.append(name)

        for cat in categoryButtons:
            checked = len(uncheckedCategoryButtons) != len(categoryButtons)
            self.commandCheckBox[cat].setChecked(checked)

    def oneOfs(self, command):
        """
        对全场景执行单条命令检查

        Args:
            command (str): 命令名称
        """
        newDiagnostics, _ = self.engine.command_to_run([command])
        self.diagnostics.update(newDiagnostics)
        self.createReport()

    def sanityCheckChecked(self):
        """
        对全场景执行已勾选的检查
        """
        checkedCommands = []
        for name in self.commandsList:
            if self.commandCheckBox[name].isChecked():
                checkedCommands.append(name)

        if not checkedCommands:
            cmds.warning(u"至少选择一个检查命令以运行")
            return

        diagnostics, checked_nodes = self.engine.command_to_run(checkedCommands)
        self.diagnostics = diagnostics
        self.checked_nodes = checked_nodes
        self.createReport()

        result = self.engine.validation(diagnostics)
        if result:
            QtWidgets.QMessageBox.information(
                self,
                u"检查通过",
                u"检查已通过，请及时上传。"
            )

    def createReport(self):
        """
        生成HTML格式的检查报告

        报告包含已检查节点、各命令通过/失败状态及错误详情。
        """
        diagnostics = self.diagnostics
        nodes = self.checked_nodes
        name = u"全局"
        self.reportOutputUI.clear()
        lastState = None
        html = "<h2>{}</h2>".format(name)
        html += u"&#10752; 已检查节点: {}<br><br>".format(len(nodes))

        if len(diagnostics) == 0:
            html += u"{} - 没有检查运行。".format(name)
            self.reportOutputUI.setHtml(html)
            return

        cmds.waitCursor(state=True)
        progress_bar = mel.eval('$tmp = $gMainProgressBar')
        step_ref = [0.00, round(100.00 / len(self.commandsList.keys()), 2)]
        cmds.progressBar(progress_bar, edit=True, beginProgress=True, isInterruptable=True,
                         minValue=0, maxValue=100, status=u"生成报告中...")

        for error in sorted(self.commandsList.keys()):
            if cmds.progressBar(progress_bar, query=True, isCancelled=True):
                break

            if error not in diagnostics:
                self._error_cache.pop(error, None)
                self.error_info_button[error].setEnabled(False)
                if error in self.fix_button:
                    self.fix_button[error].setEnabled(False)
                self.commandLabel[error].setStyleSheet('background-color: none;')
                continue

            diag = diagnostics[error]
            status = diag.get('status')
            label = self.commandsList[error]['label']
            parsedErrors = self.engine.parse_errors(diag)

            if status == 'blocked':
                self._error_cache.pop(error, None)
                self.error_info_button[error].setEnabled(False)
                if error in self.fix_button:
                    self.fix_button[error].setEnabled(False)
                self.commandLabel[error].setStyleSheet(
                    'background-color: #777a3a;')
                blocked_by = u"、".join(
                    self._get_check_label(b) for b in (diag.get('blocked_by') or []))
                html += u"&#10752; {}<font color=#c8b900> [ 待定 ]</font>" \
                        u" - 依赖 [{}] 未通过<br>".format(label, blocked_by)
                if lastState is not None and lastState != 'blocked':
                    html += "<br>"
                lastState = 'blocked'
                step_ref[0] += step_ref[1]
                cmds.progressBar(progress_bar, edit=True, step=step_ref[0])
                continue

            failed = status == 'failed' or len(parsedErrors) != 0
            if failed:
                self._error_cache[error] = diag
                self.error_info_button[error].setEnabled(True)
                if error in self.fix_button:
                    self.fix_button[error].setEnabled(True)
                self.commandLabel[error].setStyleSheet(
                    'background-color: #664444;')
            else:
                self._error_cache.pop(error, None)
                self.error_info_button[error].setEnabled(False)
                if error in self.fix_button:
                    self.fix_button[error].setEnabled(False)
                self.commandLabel[error].setStyleSheet(
                    'background-color: #446644;')

            state = 'failed' if failed else 'passed'
            if lastState is not None and lastState != state:
                html += "<br>"
            lastState = state
            if failed:
                error_text = u" [ 失败 ]"
                if diag.get('error'):
                    error_text = u" [ 失败 ] ({})".format(diag['error'])
                html += u"&#10752; {}<font color=#9c4f4f>{}</font><br>".format(
                    label, error_text)
            else:
                html += u"{}<font color=#64a65a> [ 成功 ]</font><br>".format(label)

            if failed:
                store = {}
                for item in parsedErrors:
                    nodePath = item.get('node') if isinstance(item, dict) else item
                    nameKey = nodePath.split('.')[0]
                    store[nameKey] = store.get(nameKey, 0) + 1

                for nodeKey in store:
                    html += u"&#9492;&#9472; {} - <font color=#9c4f4f>{} {}</font><br>".format(
                        nodeKey, store[nodeKey], u"问题")

            step_ref[0] += step_ref[1]
            cmds.progressBar(progress_bar, edit=True, step=step_ref[0])

        cmds.progressBar(progress_bar, edit=True, endProgress=True)
        cmds.waitCursor(state=False)
        self.reportOutputUI.insertHtml(html)

    def selectErrorNodes(self, errors):
        """
        在Maya场景中选中指定错误节点

        Args:
            errors (dict): 错误诊断数据
        """
        cmds.select(self.engine.get_selectable(self.engine.parse_errors(errors)))

    def _on_select_error_nodes(self, cmd):
        """
        从缓存中选择指定命令的错误节点

        Args:
            cmd (str): 命令名称
        """
        if cmd not in self._error_cache:
            return
        cmds.select(self.engine.get_selectable(
            self.engine.parse_errors(self._error_cache[cmd])))

    def _show_detail(self, cmd):
        """
        显示指定命令的错误详情对话框

        Args:
            cmd (str): 命令名称
        """
        if cmd not in self._error_cache:
            return
        diagnostics = self._error_cache[cmd]
        label = self.commandsList[cmd]['label']
        dialog = ErrorDetailDialog(self, self.engine, cmd, label, diagnostics)
        dialog.show()

    def _run_fix(self, name):
        """
        执行指定命令的修复函数

        Args:
            name (str): 命令名称
        """
        registry = self.engine._check_registry
        check_cls = registry.get(name)
        if check_cls is None or not hasattr(check_cls, 'fix'):
            return
        if self.engine.context is None or name not in self.engine.context['results']:
            return
        instance = check_cls(self.engine.context)
        instance.fix()
        self.oneOfs(name)

    def selectFailed(self):
        """
        勾选所有检查失败的命令
        """
        for name in self.commandsList.keys():
            diag = self.diagnostics.get(name)
            failed = diag is not None and diag.get('status') == 'failed'
            self.commandCheckBox[name].setChecked(failed)

    def saveSettings(self):
        """
        保存当前检查设置到optionVars
        """
        checked_commands = {}
        for name in self.commandsList:
            checked_commands[name] = self.commandCheckBox[name].isChecked()
        self.engine.save_preferences(checked_commands)

    def loadSettings(self):
        """
        从optionVars加载之前保存的检查设置

        按住Shift键启动可跳过加载，使用默认设置。
        """
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            return

        settings = self.engine.load_preferences()
        if settings and 'commands' in settings:
            for name in settings['commands']:
                try:
                    self.commandCheckBox[name].setChecked(settings['commands'][name])
                except:
                    continue

    def closeEvent(self, event):
        """
        窗口关闭时自动保存设置并调用父类关闭事件

        Args:
            event (QCloseEvent): 关闭事件对象
        """
        self.saveSettings()
        super(UI, self).closeEvent(event)


class ErrorDetailDialog(QtWidgets.QDialog):
    SELECT_ALL_THRESHOLD = 100000
    _COMPONENT_MAP = {
        'edge': u"边",
        'vertex': u"顶点",
        'face': u"面",
        'uv': u"UV",
    }

    def __init__(self, parent, engine, cmd_name, label, diagnostics):
        super(ErrorDetailDialog, self).__init__(parent)
        self.engine = engine
        self.cmd_name = cmd_name
        self.label = label
        self.diagnostics = diagnostics
        self._errors = self.engine.parse_errors(self.diagnostics)
        self._build_groups()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setWindowTitle(u"错误详情 - {}".format(label))
        self.resize(700, 400)
        self._build_ui()
        self._populate_table()

    def _build_groups(self):
        result_type = self.diagnostics.get('result_type', 'node')
        suffix = self._COMPONENT_MAP.get(result_type)
        if suffix:
            buckets = {}
            for error in self._errors:
                node = error.split('.')[0]
                buckets.setdefault(node, []).append(error)
            self._groups = [
                (u"{} ({} {})".format(node, len(errors), suffix), errors)
                for node, errors in buckets.items()
            ]
        elif result_type == 'node':
            self._groups = [(item.get('node', ''), [item]) for item in self._errors]
        else:
            self._groups = [(error, [error]) for error in self._errors]

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.header_label = QtWidgets.QLabel(u"检查项: {}  |  错误数量: {} (共 {} 组)".format(
            self.label, len(self._errors), len(self._groups)))
        layout.addWidget(self.header_label)

        self.table = QtWidgets.QTableWidget()
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)

        btn_layout = QtWidgets.QHBoxLayout()
        self.refresh_btn = QtWidgets.QPushButton(u"刷新")
        self.refresh_btn.clicked.connect(self._refresh)
        btn_layout.addWidget(self.refresh_btn)

        self.select_all_btn = QtWidgets.QPushButton(u"选择全部")
        self.select_all_btn.clicked.connect(self._select_all)
        btn_layout.addWidget(self.select_all_btn)

        btn_layout.addStretch()

        info = self.engine._check_registry.get(self.cmd_name)
        if info is not None and hasattr(info, 'fix'):
            self.fix_btn = QtWidgets.QPushButton(u"修复选中的节点")
            self.fix_btn.clicked.connect(self._fix_selected)
            btn_layout.addWidget(self.fix_btn)
        layout.addLayout(btn_layout)

    def _populate_table(self):
        """将错误分组数据填充到表格中"""
        is_node = self.diagnostics.get('result_type', 'node') == 'node'
        has_message = is_node and any(
            any(e.get('text') for e in errors) for _, errors in self._groups)
        if has_message:
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels([u"序号", u"节点", u"错误信息"])
            self.table.horizontalHeader().setSectionResizeMode(
                1, QtWidgets.QHeaderView.Interactive)
            self.table.horizontalHeader().setSectionResizeMode(
                2, QtWidgets.QHeaderView.Stretch)
        else:
            self.table.setColumnCount(2)
            if is_node:
                self.table.setHorizontalHeaderLabels([u"序号", u"节点"])
            else:
                self.table.setHorizontalHeaderLabels([u"序号", u"错误对象"])
            self.table.horizontalHeader().setSectionResizeMode(
                1, QtWidgets.QHeaderView.Stretch)

        self.table.setRowCount(len(self._groups))
        for i, (display_text, errors) in enumerate(self._groups):
            num_item = QtWidgets.QTableWidgetItem(str(i + 1))
            self.table.setItem(i, 0, num_item)

            if is_node:
                node_item = QtWidgets.QTableWidgetItem(display_text)
                self.table.setItem(i, 1, node_item)
                if has_message:
                    text_item = QtWidgets.QTableWidgetItem(
                        errors[0].get('text', '') if errors else u'')
                    self.table.setItem(i, 2, text_item)
            else:
                error_item = QtWidgets.QTableWidgetItem(display_text)
                self.table.setItem(i, 1, error_item)

    def _on_selection_changed(self):
        """表格选中项变化时在Maya场景中高亮对应错误对象"""
        rows = set()
        for item in self.table.selectedItems():
            rows.add(item.row())
        if not rows:
            return
        all_errors = []
        for r in sorted(rows):
            all_errors.extend(self._groups[r][1])
        count = len(all_errors)
        if count >= self.SELECT_ALL_THRESHOLD:
            reply = QtWidgets.QMessageBox.question(
                self,
                u"确认选择",
                u"数据过大（{}条），选择会造成卡顿，是否继续？".format(count),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return
        try:
            cmds.select(self.engine.get_selectable(all_errors))
        except (TypeError, ValueError):
            pass

    def _select_all(self):
        """选择表格中所有错误对象并在Maya场景中高亮"""
        all_errors = [e for _, errors in self._groups for e in errors]
        count = len(all_errors)
        if count >= self.SELECT_ALL_THRESHOLD:
            reply = QtWidgets.QMessageBox.question(
                self,
                u"确认选择全部",
                u"数据过大（{}条），选择全部会造成卡顿，是否继续？".format(count),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if reply != QtWidgets.QMessageBox.Yes:
                return
        if count:
            try:
                cmds.select(self.engine.get_selectable(all_errors))
            except TypeError:
                pass
            self.table.selectAll()

    def _fix_selected(self):
        """修复表格中选中行对应的错误"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        if not selected_rows:
            return

        errors = []
        for r in sorted(selected_rows):
            errors.extend(self._groups[r][1])

        check_cls = self.engine._check_registry.get(self.cmd_name)
        if check_cls is None or not hasattr(check_cls, 'fix'):
            return
        if self.engine.context is None or self.cmd_name not in self.engine.context['results']:
            return
        instance = check_cls(self.engine.context)

        result_type = self.diagnostics.get('result_type', 'node')
        if result_type == 'node':
            instance.fix(self.engine.get_selectable(errors))
        elif result_type == 'text':
            instance.fix(errors)
        else:
            instance.fix(self._filter_diagnostics(errors))

        self._refresh()

    def _filter_diagnostics(self, errors):
        """根据选中路径过滤组件类型诊断，返回完整字典"""
        type_mapping = {
            'uv': ".map[{}]",
            'vertex': ".vtx[{}]",
            'edge': ".e[{}]",
            'face': ".f[{}]",
        }
        result_type = self.diagnostics['result_type']
        selected_set = set(errors)
        filtered_uuids = {}
        for uuid, indices in self.diagnostics['uuids'].items():
            nodeName = cmds.ls(uuid)
            if not nodeName:
                continue
            prefix = nodeName[0]
            f_indices = [i for i in indices
                         if prefix + type_mapping[result_type].format(i) in selected_set]
            if f_indices:
                filtered_uuids[uuid] = f_indices
        return {'result_type': result_type, 'uuids': filtered_uuids}

    def _refresh(self):
        """重新运行检查并刷新对话框数据"""
        parent_ui = self.parent()
        if parent_ui is None:
            return
        parent_ui.oneOfs(self.cmd_name)

        new_diag = parent_ui._error_cache.get(self.cmd_name)
        if new_diag is None:
            new_diag = {'result_type': self.diagnostics.get('result_type', 'node'), 'uuids': {}}
        self.diagnostics = new_diag
        self._errors = self.engine.parse_errors(self.diagnostics)
        self._build_groups()
        self._populate_table()
        self.header_label.setText(u"检查项: {}  |  错误数量: {} (共 {} 组)".format(
            self.label, len(self._errors), len(self._groups)))


def show_UI(stage='model'):
    """
    显示检查窗口的主入口函数

    根据环节名称创建或激活对应的检查窗口。窗口实例作为父窗口的属性缓存，
    确保多次调用不会重复创建窗口。

    Args:
        stage (str): 环节名称，可选 'model' 或 'shading'，默认为 'model'
    """
    ptr = omui.MQtUtil.mainWindow()
    parent = wrapInstance(int(ptr), QtWidgets.QWidget)

    WINDOW_NAME = '{}Check'.format(stage.title())

    if hasattr(parent, WINDOW_NAME) and getattr(parent, WINDOW_NAME) is not None:
        getattr(parent, WINDOW_NAME).raise_()
        getattr(parent, WINDOW_NAME).showNormal()
    else:
        window = UI(parent, stage_name=stage)
        setattr(parent, WINDOW_NAME, window)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        window.destroyed.connect(lambda: setattr(parent, WINDOW_NAME, None))
        window.show()


if __name__ == '__main__':
    show_UI()
