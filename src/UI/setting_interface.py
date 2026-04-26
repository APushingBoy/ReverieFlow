#!/usr/bin/env python3
"""
设置页界面
用于配置 API Key、模型选择等
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit
from qfluentwidgets import (
    SettingCardGroup,
    SettingCard,
    PushSettingCard,
    InfoBar,
    InfoBarPosition,
    FluentIcon as FIF
)
from Utils.config_manager import ConfigManager


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


class SettingInterface(QWidget):
    """
    设置页界面类
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingInterface")
        self.config = ConfigManager()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """
        初始化UI
        """
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("设置")
        title.setObjectName("TitleLabel")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.layout.addWidget(title)

        self.layout.addSpacing(20)

        asr_group = SettingCardGroup("语音识别 (ASR)", self)

        self.asr_api_key_card = LineEditCard(FIF.CERTIFICATE, "API Key", "请输入 ASR API Key", asr_group)
        asr_group.addSettingCard(self.asr_api_key_card)

        self.asr_api_url_card = LineEditCard(FIF.LINK, "API URL", "ASR WebSocket 地址", asr_group)
        asr_group.addSettingCard(self.asr_api_url_card)

        self.asr_model_card = LineEditCard(FIF.ROBOT, "模型", "ASR 模型名称", asr_group)
        asr_group.addSettingCard(self.asr_model_card)

        self.layout.addWidget(asr_group)

        rewrite_group = SettingCardGroup("文本润色", self)

        self.rewrite_api_key_card = LineEditCard(FIF.CERTIFICATE, "API Key", "请输入文本润色 API Key", rewrite_group)
        rewrite_group.addSettingCard(self.rewrite_api_key_card)

        self.rewrite_api_url_card = LineEditCard(FIF.LINK, "API URL", "文本润色 API 地址", rewrite_group)
        rewrite_group.addSettingCard(self.rewrite_api_url_card)

        self.rewrite_model_card = LineEditCard(FIF.ROBOT, "模型", "文本润色模型名称", rewrite_group)
        rewrite_group.addSettingCard(self.rewrite_model_card)

        self.layout.addWidget(rewrite_group)

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

    def load_settings(self):
        """
        从配置管理器加载设置
        """
        self.asr_api_key_card.line_edit.setText(self.config.get("asr", "api_key", ""))
        self.asr_api_url_card.line_edit.setText(self.config.get("asr", "api_url", ""))
        self.asr_model_card.line_edit.setText(self.config.get("asr", "model", ""))

        self.rewrite_api_key_card.line_edit.setText(self.config.get("rewrite", "api_key", ""))
        self.rewrite_api_url_card.line_edit.setText(self.config.get("rewrite", "api_url", ""))
        self.rewrite_model_card.line_edit.setText(self.config.get("rewrite", "model", ""))

    def save_settings(self):
        """
        保存设置到配置管理器
        """
        self.config.set("asr", "api_key", self.asr_api_key_card.line_edit.text())
        self.config.set("asr", "api_url", self.asr_api_url_card.line_edit.text())
        self.config.set("asr", "model", self.asr_model_card.line_edit.text())

        self.config.set("rewrite", "api_key", self.rewrite_api_key_card.line_edit.text())
        self.config.set("rewrite", "api_url", self.rewrite_api_url_card.line_edit.text())
        self.config.set("rewrite", "model", self.rewrite_model_card.line_edit.text())

        self.config.save()

        InfoBar.success(
            "保存成功",
            "设置已保存到 config.json",
            parent=self,
            position=InfoBarPosition.BOTTOM
        )
