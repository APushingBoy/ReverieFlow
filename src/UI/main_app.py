#!/usr/bin/env python3
"""
主窗口
使用 FluentWindow 框架，包含左侧导航栏和系统托盘
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSystemTrayIcon
from qfluentwidgets import FluentWindow, NavigationItemPosition, setTheme, Theme, FluentIcon as FIF
from UI.home_interface import HomeInterface
from UI.setting_interface import SettingInterface
from UI.system_tray import SystemTrayManager
from Utils.config_manager import ConfigManager


class MainWindow(FluentWindow):
    """
    主窗口类
    """

    APP_VERSION = "v0.2.3"

    def __init__(self, show_on_start=True):
        super().__init__()
        self.config = ConfigManager()
        self.tray_manager = None
        self.init_window()
        self.init_navigation()
        self.init_system_tray()

        if not show_on_start:
            self.hide()

    def init_window(self):
        """
        初始化窗口
        """
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        width = screen.width() // 2
        height = screen.height() // 2
        self.resize(width, height)
        self.setMinimumWidth(700)
        self.setWindowTitle(f"ReverieFlow {self.APP_VERSION}")
        self.titleBar.iconLabel.hide()

        icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        x = screen.x() + (screen.width() - width) // 2
        y = screen.y() + (screen.height() - height) // 2
        self.move(x, y)

    def init_navigation(self):
        """
        初始化导航栏
        """
        self.home_interface = HomeInterface(self)
        self.setting_interface = SettingInterface(self)
        self.setting_interface.settings_saved.connect(self._on_settings_saved)

        self.addSubInterface(
            self.home_interface,
            FIF.HOME,
            "首页",
            position=NavigationItemPosition.TOP
        )

        self.addSubInterface(
            self.setting_interface,
            FIF.SETTING,
            "设置",
            position=NavigationItemPosition.TOP
        )

        self.navigationInterface.setCurrentItem("Home")
        self.navigationInterface.setExpandWidth(200)

    def init_system_tray(self):
        """
        初始化系统托盘
        """
        self.tray_manager = SystemTrayManager(self)
        self.tray_manager.show_main_window.connect(self._on_show_main_window)
        self.tray_manager.toggle_recording.connect(self._on_toggle_recording)
        self.tray_manager.quit_app.connect(self._on_quit_app)
        self.tray_manager.show()

    def _on_show_main_window(self):
        """
        显示主窗口
        """
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _on_toggle_recording(self):
        """
        切换录音状态
        """
        self.home_interface._toggle_recording()

    def _on_quit_app(self):
        """
        退出应用（托盘右键菜单触发，强制退出）
        """
        self.home_interface.hotkey_listener.stop()
        self.home_interface.engine.cleanup()
        self.tray_manager.hide()
        from PyQt5.QtWidgets import QApplication
        QApplication.instance().quit()

    def _on_settings_saved(self):
        """
        设置保存后刷新运行中的配置快照
        """
        self.config = ConfigManager()
        self.home_interface.reload_config()

    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        close_behavior = self.config.get("ui", "close_behavior", "minimize")

        if close_behavior == "minimize":
            event.ignore()
            self.hide()
            self.tray_manager.show_message(
                "ReverieFlow",
                "已最小化到托盘，按 Ctrl+Win 可快速录音",
                QSystemTrayIcon.Information
            )
        else:
            self.home_interface.hotkey_listener.stop()
            self.home_interface.engine.cleanup()
            self.tray_manager.hide()
            event.accept()
