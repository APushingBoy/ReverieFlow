#!/usr/bin/env python3
"""
ReverieFlow - Windows 语音识别客户端
基于 Fluent Design 的全新界面
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from qfluentwidgets import setTheme, Theme

# 设置高 DPI 缩放
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

app = QApplication(sys.argv)

# 设置主题（跟随系统）
setTheme(Theme.AUTO)

from UI.main_app import MainWindow

if __name__ == "__main__":
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())
