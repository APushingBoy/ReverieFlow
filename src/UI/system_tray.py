#!/usr/bin/env python3
"""
系统托盘管理器
提供托盘图标、右键菜单、主窗口显示/隐藏控制
"""

import sys
import os

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal


class SystemTrayManager(QObject):
    """
    系统托盘管理器
    """

    show_main_window = pyqtSignal()
    toggle_recording = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)
        self._setup_tray()

    def _setup_tray(self):
        """
        初始化托盘图标和菜单
        """
        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            self.tray_icon.setIcon(app.style().standardIcon(
                app.style().SP_ComputerIcon
            ))

        self.tray_icon.setToolTip("ReverieFlow - 语音识别与文本润色")

        tray_menu = QMenu()

        show_action = QAction("显示主窗口", tray_menu)
        show_action.triggered.connect(self.show_main_window.emit)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        record_action = QAction("开始/停止录音 (Ctrl+Win)", tray_menu)
        record_action.triggered.connect(self.toggle_recording.emit)
        tray_menu.addAction(record_action)

        tray_menu.addSeparator()

        quit_action = QAction("退出", tray_menu)
        quit_action.triggered.connect(self.quit_app.emit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        """
        托盘图标点击事件
        """
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_main_window.emit()

    def show(self):
        """
        显示托盘图标
        """
        self.tray_icon.show()

    def hide(self):
        """
        隐藏托盘图标
        """
        self.tray_icon.hide()

    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.Information):
        """
        显示托盘通知消息

        Args:
            title: 消息标题
            message: 消息内容
            icon: 消息图标类型
        """
        self.tray_icon.showMessage(title, message, icon, 3000)
