#!/usr/bin/env python3
"""
ReverieFlow - Windows 语音识别客户端
参考Voxt项目设计，实现流式ASR和文本润色功能
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from UI.main_window import MainWindow

if __name__ == "__main__":
    # 创建应用实例
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())
