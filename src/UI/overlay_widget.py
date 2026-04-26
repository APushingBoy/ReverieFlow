#!/usr/bin/env python3
"""
悬浮提示窗口
用于显示实时识别结果和润色结果
"""

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtGui import QColor, QPalette


class OverlayWidget(QWidget):
    """
    悬浮提示窗口
    显示在屏幕底部居中位置
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 8, 12, 8)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(
            "background-color: rgba(30, 30, 30, 220);"
            "color: white;"
            "border-radius: 8px;"
            "padding: 8px 16px;"
            "font-size: 14px;"
        )
        self.label.setMinimumWidth(200)
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.resize(200, 40)
        self.hide()

    def show_text(self, text: str, processing: bool = False):
        """
        显示文本

        Args:
            text: 要显示的文本
            processing: 是否为处理中状态（灰色显示）
        """
        self.label.setText(text)
        if processing:
            self.label.setStyleSheet(
                "background-color: rgba(30, 30, 30, 220);"
                "color: gray;"
                "border-radius: 8px;"
                "padding: 8px 16px;"
                "font-size: 14px;"
            )
        else:
            self.label.setStyleSheet(
                "background-color: rgba(30, 30, 30, 220);"
                "color: white;"
                "border-radius: 8px;"
                "padding: 8px 16px;"
                "font-size: 14px;"
            )
        self.adjust_size()
        self.show()
        self.move_to_bottom_center()

    def show_waiting(self):
        """
        显示等待状态：正在等待说话
        """
        self.label.setText("正在等待说话…")
        self.label.setStyleSheet(
            "background-color: rgba(30, 30, 30, 220);"
            "color: gray;"
            "border-radius: 8px;"
            "padding: 8px 16px;"
            "font-size: 14px;"
        )
        self.adjust_size()
        self.show()
        self.move_to_bottom_center()

    def adjust_size(self):
        """
        根据内容调整窗口大小
        """
        from PyQt5.QtGui import QFontMetrics

        screen = QApplication.primaryScreen().availableGeometry()
        max_width = screen.width() // 3

        fm = QFontMetrics(self.label.font())
        text_width = fm.horizontalAdvance(self.label.text()) + 32
        desired_width = min(text_width, max_width)
        desired_width = max(desired_width, 200)

        self.setFixedWidth(desired_width)
        self.label.setFixedWidth(desired_width)
        self.label.adjustSize()

        h = self.label.height() + 16
        h = max(h, 40)
        self.resize(desired_width, h)

    def move_to_bottom_center(self):
        """
        移动到屏幕底部居中
        """
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.x() + (screen.width() - self.width()) // 2
        y = screen.y() + screen.height() - self.height() - 60
        self.move(x, y)

    def hide_after(self, delay_ms: int = 500):
        """
        延迟隐藏
        """
        QTimer.singleShot(delay_ms, self.hide)
