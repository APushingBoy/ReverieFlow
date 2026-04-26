#!/usr/bin/env python3
"""
主窗口
使用 FluentWindow 框架，包含左侧导航栏
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from qfluentwidgets import FluentWindow, NavigationItemPosition, setTheme, Theme, FluentIcon as FIF
from UI.home_interface import HomeInterface
from UI.setting_interface import SettingInterface


class MainWindow(FluentWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.init_window()
        self.init_navigation()

    def init_window(self):
        """
        初始化窗口
        """
        self.resize(1000, 700)
        self.setMinimumWidth(700)
        self.setWindowTitle("ReverieFlow")
        self.titleBar.iconLabel.hide()

    def init_navigation(self):
        """
        初始化导航栏
        """
        self.home_interface = HomeInterface(self)
        self.setting_interface = SettingInterface(self)

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
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.setCurrentItem("Home")
