#!/usr/bin/env python3
"""
ReverieFlow - Windows 语音识别客户端
基于 Fluent Design 的全新界面
"""

import sys
import os

# 获取基础路径（兼容开发环境和打包后的环境）
if getattr(sys, 'frozen', False):
    # 打包后的环境
    base_path = sys._MEIPASS
else:
    # 开发环境
    base_path = os.path.dirname(os.path.abspath(__file__))

# 添加src目录到Python路径
sys.path.append(os.path.join(base_path, 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from qfluentwidgets import setTheme, Theme

# 设置高 DPI 缩放
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

app = QApplication(sys.argv)

# 设置主题（跟随系统）
setTheme(Theme.AUTO)

from UI.main_app import MainWindow
from Utils.config_manager import ConfigManager

if __name__ == "__main__":
    config = ConfigManager()
    show_on_start = config.get("ui", "startup_behavior", "show") == "show"

    # 创建主窗口
    window = MainWindow(show_on_start=show_on_start)
    if show_on_start:
        window.show()

    # 运行应用
    sys.exit(app.exec_())
