#!/usr/bin/env python3
"""
设置页界面
用于配置 API Key、模型选择等
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QDialog, QTextEdit
from qfluentwidgets import (
    SettingCardGroup,
    SettingCard,
    PushSettingCard,
    HyperlinkCard,
    InfoBar,
    InfoBarPosition,
    FluentIcon as FIF,
    ScrollArea,
    ComboBox,
    PushButton
)
from Utils.config_manager import ConfigManager, DEFAULT_REWRITE_SYSTEM_PROMPT


class ApiKeyCard(SettingCard):
    """
    带 API Key 输入框的设置卡片，支持明文/星号切换
    """

    text_changed = pyqtSignal(str)

    def __init__(self, icon, title, content, parent=None):
        super().__init__(icon, title, content, parent)
        self._real_text = ""
        self._placeholder = content
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(content)
        self.line_edit.setMinimumWidth(280)
        self.line_edit.setAlignment(Qt.AlignRight)
        self.line_edit.setEchoMode(QLineEdit.Password)
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.line_edit.focusInEvent = self._on_focus_in
        self.line_edit.focusOutEvent = self._on_focus_out

        self.hBoxLayout.addWidget(self.line_edit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def _on_text_changed(self, text):
        if self.line_edit.echoMode() == QLineEdit.Normal:
            self._real_text = text
        self.text_changed.emit(text)

    def _on_focus_in(self, event):
        self.line_edit.setEchoMode(QLineEdit.Normal)
        self.line_edit.setText(self._real_text)
        QLineEdit.focusInEvent(self.line_edit, event)

    def _on_focus_out(self, event):
        if self.line_edit.echoMode() == QLineEdit.Normal:
            self._real_text = self.line_edit.text()
            self.line_edit.setEchoMode(QLineEdit.Password)
            self.line_edit.setText(self._mask_text(self._real_text))
        QLineEdit.focusOutEvent(self.line_edit, event)

    def _mask_text(self, text):
        if not text or len(text) <= 8:
            return text
        return text[:4] + "*" * (len(text) - 8) + text[-4:]

    def setText(self, text):
        self._real_text = text
        self.line_edit.setText(self._mask_text(text))

    def text(self):
        return self._real_text


class LineEditCard(SettingCard):
    """
    带输入框的设置卡片
    """

    text_changed = pyqtSignal(str)

    def __init__(self, icon, title, content, parent=None):
        super().__init__(icon, title, content, parent)
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(content)
        self.line_edit.setMinimumWidth(280)
        self.line_edit.setAlignment(Qt.AlignRight)
        self.line_edit.textChanged.connect(self.text_changed.emit)

        self.hBoxLayout.addWidget(self.line_edit, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class ComboBoxSettingCard(SettingCard):
    """
    带下拉框的设置卡片
    """

    currentIndexChanged = pyqtSignal(int)

    def __init__(self, icon, title, content, options, parent=None):
        super().__init__(icon, title, content, parent)
        self.comboBox = ComboBox()
        self.comboBox.setMinimumWidth(180)
        for option in options:
            self.comboBox.addItem(option)
        self.comboBox.currentIndexChanged.connect(self.currentIndexChanged.emit)

        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class SettingInterface(ScrollArea):
    """
    设置页界面类
    """

    settings_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingInterface")
        self.config = ConfigManager()
        self.view = QWidget(self)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background-color: transparent; border: none;")
        self.view.setStyleSheet("background-color: transparent; border: none;")
        self.rewrite_system_prompt = ""
        self.rewrite_system_prompt_changed = False
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """
        初始化UI
        """
        self.layout = QVBoxLayout(self.view)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("设置")
        title.setObjectName("TitleLabel")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.layout.addWidget(title)

        self.layout.addSpacing(20)

        asr_group = SettingCardGroup("语音识别 (ASR)", self)

        self.asr_api_key_card = ApiKeyCard(FIF.CERTIFICATE, "API Key", "请输入 ASR API Key", asr_group)
        asr_group.addSettingCard(self.asr_api_key_card)

        self.asr_api_url_card = LineEditCard(FIF.LINK, "API URL", "ASR WebSocket 地址", asr_group)
        asr_group.addSettingCard(self.asr_api_url_card)

        self.asr_model_card = LineEditCard(FIF.ROBOT, "模型", "ASR 模型名称", asr_group)
        asr_group.addSettingCard(self.asr_model_card)

        self.layout.addWidget(asr_group)

        rewrite_group = SettingCardGroup("文本润色", self)

        self.rewrite_api_key_card = ApiKeyCard(FIF.CERTIFICATE, "API Key", "请输入文本润色 API Key", rewrite_group)
        rewrite_group.addSettingCard(self.rewrite_api_key_card)

        self.rewrite_api_url_card = LineEditCard(FIF.LINK, "API URL", "文本润色 API 地址", rewrite_group)
        rewrite_group.addSettingCard(self.rewrite_api_url_card)

        self.rewrite_model_card = LineEditCard(FIF.ROBOT, "模型", "文本润色模型名称", rewrite_group)
        rewrite_group.addSettingCard(self.rewrite_model_card)

        self.system_prompt_card = PushSettingCard(
            "编辑",
            FIF.ROBOT,
            "系统提示词",
            "自定义润色模型的 system prompt",
            rewrite_group
        )
        self.system_prompt_card.clicked.connect(self._open_system_prompt_dialog)
        rewrite_group.addSettingCard(self.system_prompt_card)

        self.layout.addWidget(rewrite_group)

        ui_group = SettingCardGroup("界面与行为", self)

        self.startup_behavior_card = ComboBoxSettingCard(
            FIF.POWER_BUTTON,
            "启动时行为",
            "选择程序启动时的显示方式",
            ["显示主窗口", "仅显示托盘图标"],
            parent=ui_group
        )
        ui_group.addSettingCard(self.startup_behavior_card)

        self.close_behavior_card = ComboBoxSettingCard(
            FIF.CLOSE,
            "关闭按钮行为",
            "选择点击关闭按钮时的操作",
            ["最小化到托盘", "退出程序"],
            parent=ui_group
        )
        ui_group.addSettingCard(self.close_behavior_card)

        self.layout.addWidget(ui_group)

        self.layout.addStretch()

        self.save_button = PushSettingCard(
            "保存设置",
            FIF.SAVE,
            "保存",
            "保存当前设置",
            self
        )
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_button)

        self.layout.addSpacing(20)

        about_group = SettingCardGroup("关于", self)

        about_card = SettingCard(
            FIF.INFO,
            "ReverieFlow",
            f"版本 v0.2.3  |  开发者: Homie",
            about_group
        )
        about_group.addSettingCard(about_card)

        github_card = HyperlinkCard(
            "https://github.com/APushingBoy/ReverieFlow",
            "访问 GitHub 仓库",
            FIF.GITHUB,
            "开源地址",
            "在 GitHub 上查看源代码",
            about_group
        )
        about_group.addSettingCard(github_card)

        self.layout.addWidget(about_group)

    def load_settings(self):
        """
        从配置管理器加载设置
        """
        self.asr_api_key_card.setText(self.config.get("asr", "api_key", ""))
        self.asr_api_url_card.line_edit.setText(self.config.get("asr", "api_url", ""))
        self.asr_model_card.line_edit.setText(self.config.get("asr", "model", ""))

        self.rewrite_api_key_card.setText(self.config.get("rewrite", "api_key", ""))
        self.rewrite_api_url_card.line_edit.setText(self.config.get("rewrite", "api_url", ""))
        self.rewrite_model_card.line_edit.setText(self.config.get("rewrite", "model", ""))
        self.rewrite_system_prompt = self.config.get_rewrite_system_prompt()
        self.rewrite_system_prompt_changed = False

        startup = self.config.get("ui", "startup_behavior", "show")
        self.startup_behavior_card.comboBox.setCurrentIndex(0 if startup == "show" else 1)

        close = self.config.get("ui", "close_behavior", "minimize")
        self.close_behavior_card.comboBox.setCurrentIndex(0 if close == "minimize" else 1)

    def save_settings(self):
        """
        保存设置到配置管理器
        """
        self.config.set("asr", "api_key", self.asr_api_key_card.text())
        self.config.set("asr", "api_url", self.asr_api_url_card.line_edit.text())
        self.config.set("asr", "model", self.asr_model_card.line_edit.text())

        self.config.set("rewrite", "api_key", self.rewrite_api_key_card.text())
        self.config.set("rewrite", "api_url", self.rewrite_api_url_card.line_edit.text())
        self.config.set("rewrite", "model", self.rewrite_model_card.line_edit.text())
        if self.rewrite_system_prompt_changed:
            self.config.save_rewrite_system_prompt(self.rewrite_system_prompt)

        self.config.set("ui", "startup_behavior", "show" if self.startup_behavior_card.comboBox.currentIndex() == 0 else "tray")
        self.config.set("ui", "close_behavior", "minimize" if self.close_behavior_card.comboBox.currentIndex() == 0 else "quit")

        self.config.save()
        self.settings_saved.emit()

        InfoBar.success(
            "保存成功",
            "设置已保存到 config.json",
            parent=self,
            position=InfoBarPosition.BOTTOM
        )

    def _open_system_prompt_dialog(self):
        """
        打开系统提示词编辑对话框
        """
        try:
            self._show_system_prompt_dialog()
        except Exception as e:
            InfoBar.error(
                "打开失败",
                f"系统提示词编辑器打开失败: {e}",
                parent=self,
                position=InfoBarPosition.TOP
            )

    def _show_system_prompt_dialog(self):
        """
        显示系统提示词编辑对话框
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑系统提示词")
        dialog.resize(720, 520)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        tip_label = QLabel("修改后点击“保存设置”才会写入 config.json")
        tip_label.setStyleSheet("font-size: 13px; color: gray;")
        layout.addWidget(tip_label)

        prompt_edit = QTextEdit(dialog)
        prompt_edit.setPlainText(self.rewrite_system_prompt)
        prompt_edit.setAcceptRichText(False)

        prompt_palette = prompt_edit.palette()
        prompt_palette.setColor(QPalette.Base, QColor("#ffffff"))
        prompt_palette.setColor(QPalette.Text, QColor("#202020"))
        prompt_palette.setColor(QPalette.Highlight, QColor("#0078d4"))
        prompt_palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        prompt_edit.setPalette(prompt_palette)
        prompt_edit.viewport().setPalette(prompt_palette)
        prompt_edit.viewport().setAutoFillBackground(True)
        prompt_edit.viewport().setStyleSheet(
            "background-color: #ffffff;"
            "color: #202020;"
        )
        prompt_edit.setStyleSheet(
            "QTextEdit {"
            "background-color: #ffffff;"
            "color: #202020;"
            "border: 1px solid #d0d0d0;"
            "border-radius: 4px;"
            "padding: 8px;"
            "selection-background-color: #0078d4;"
            "selection-color: #ffffff;"
            "}"
            "QTextEdit QWidget {"
            "background-color: #ffffff;"
            "color: #202020;"
            "}"
        )
        layout.addWidget(prompt_edit)

        button_layout = QHBoxLayout()
        reset_button = PushButton("恢复默认")
        cancel_button = PushButton("取消")
        ok_button = PushButton("确定")

        reset_button.clicked.connect(lambda: prompt_edit.setPlainText(DEFAULT_REWRITE_SYSTEM_PROMPT))
        cancel_button.clicked.connect(dialog.reject)
        ok_button.clicked.connect(dialog.accept)

        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        if dialog.exec_() == QDialog.Accepted:
            prompt = prompt_edit.toPlainText().strip()
            self.rewrite_system_prompt = prompt or DEFAULT_REWRITE_SYSTEM_PROMPT
            self.rewrite_system_prompt_changed = True
