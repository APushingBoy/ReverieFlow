#!/usr/bin/env python3
"""
首页界面
包含录音、识别、展示润色结果等功能
支持全局快捷键 Ctrl+Win 快速启动
"""

import sys
import os
import threading

from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox

from qfluentwidgets import PushButton, TextEdit, InfoBar, InfoBarPosition

from Utils.config_manager import ConfigManager
from Audio.audio_capture import AudioCapture
from ASR.streaming_asr import StreamingASR
from TextProcessing.text_rewriter import TextRewriter
from UI.overlay_widget import OverlayWidget
from pynput import keyboard


class EngineController(QObject):
    """
    核心引擎控制器
    管理音频捕获、流式识别、文本润色的生命周期
    """

    asr_result = pyqtSignal(str, bool)
    asr_error = pyqtSignal(str)
    rewrite_result = pyqtSignal(str)
    rewrite_error = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.audio_capture = None
        self.streaming_asr = None
        self.text_rewriter = None
        self.is_recording = False
        self.history_text = ""

    def init_engines(self):
        """
        从配置初始化所有引擎
        """
        self.audio_capture = AudioCapture(
            sample_rate=self.config.get_int("audio", "sample_rate", 16000),
            channels=self.config.get_int("audio", "channels", 1),
            chunk_size=self.config.get_int("audio", "chunk_size", 1024)
        )

        self.streaming_asr = StreamingASR(
            api_url=self.config.get("asr", "api_url", "wss://dashscope.aliyuncs.com/api-ws/v1/inference"),
            api_key=self.config.get("asr", "api_key", ""),
            model=self.config.get("asr", "model", "fun-asr-realtime")
        )

        self.text_rewriter = TextRewriter(
            api_url=self.config.get("rewrite", "api_url", "https://dashscope.aliyuncs.com/api/v1"),
            api_key=self.config.get("rewrite", "api_key", ""),
            model=self.config.get("rewrite", "model", "qwen3.5-35b-a3b")
        )

    def get_devices(self) -> list:
        """
        获取可用音频设备列表
        """
        if self.audio_capture:
            return self.audio_capture.get_devices()
        return []

    def start_recording(self, device_index=None):
        """
        开始录音识别
        """
        if self.is_recording:
            return

        if not self.audio_capture:
            self.init_engines()

        if not self.streaming_asr.api_key:
            self.asr_error.emit("未配置 ASR API Key，请前往设置页配置")
            return

        try:
            self.history_text = ""

            if device_index is not None:
                self.audio_capture.set_device(device_index)

            if not self.streaming_asr.connect():
                self.asr_error.emit("连接 ASR 服务失败")
                return

            if not self.audio_capture.start(callback=self._audio_callback):
                self.asr_error.emit("启动音频捕获失败")
                return

            self.streaming_asr.start(
                result_callback=self._asr_result_callback,
                error_callback=self._asr_error_callback
            )

            self.is_recording = True
            self.status_changed.emit("录音中...")
            self.asr_result.emit("", True)
        except Exception as e:
            self.asr_error.emit(f"启动录音失败: {e}")

    def stop_recording(self):
        """
        停止录音识别
        """
        if not self.is_recording:
            return

        try:
            self.audio_capture.stop()
            self.streaming_asr.stop()
            self.streaming_asr.close()

            self.is_recording = False
            self.status_changed.emit("录音已停止")
        except Exception as e:
            self.asr_error.emit(f"停止录音失败: {e}")

    def cancel_recording(self):
        """
        取消录音识别（不触发后续润色操作）
        """
        if not self.is_recording:
            return

        try:
            self.audio_capture.stop()
            self.streaming_asr.stop()
            self.streaming_asr.close()

            self.is_recording = False
            self.history_text = ""
            self.status_changed.emit("录音已取消")
        except Exception as e:
            self.asr_error.emit(f"取消录音失败: {e}")

    def rewrite_text(self, text: str):
        """
        润色文本
        """
        if not text:
            self.rewrite_error.emit("没有可润色的文本")
            return

        if not self.text_rewriter:
            self.init_engines()

        if not self.text_rewriter.api_key:
            self.rewrite_error.emit("未配置文本润色 API Key，请前往设置页配置")
            return

        try:
            self.status_changed.emit("正在润色文本...")
            result = self.text_rewriter.rewrite(text)
            if result:
                self.rewrite_result.emit(result)
                self.status_changed.emit("润色完成")
            else:
                self.rewrite_error.emit("润色失败，请检查 API 配置")
                self.status_changed.emit("润色失败")
        except Exception as e:
            self.rewrite_error.emit(f"润色文本失败: {e}")
            self.status_changed.emit("润色失败")

    def _audio_callback(self, audio_data):
        """
        音频数据回调
        """
        if self.is_recording:
            self.streaming_asr.send_audio(audio_data)

    def _asr_result_callback(self, text, is_final):
        """
        ASR 结果回调
        """
        self.asr_result.emit(text, is_final)

    def _asr_error_callback(self, error):
        """
        ASR 错误回调
        """
        self.asr_error.emit(error)

    def cleanup(self):
        """
        清理资源
        """
        if self.is_recording:
            self.stop_recording()
        if self.audio_capture:
            del self.audio_capture
            self.audio_capture = None
        if self.streaming_asr:
            del self.streaming_asr
            self.streaming_asr = None


class HotkeyListener:
    """
    全局快捷键监听器
    监听 Ctrl+Win 组合键
    """

    def __init__(self, callback):
        self.callback = callback
        self.listener = None
        self._ctrl_pressed = False
        self._win_pressed = False

    def start(self):
        """
        启动快捷键监听
        """
        # from pynput import keyboard
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()

    def stop(self):
        """
        停止快捷键监听
        """
        if self.listener:
            self.listener.stop()

    def _on_press(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self._ctrl_pressed = True
            elif key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                self._win_pressed = True

            if self._ctrl_pressed and self._win_pressed:
                self.callback()
                self._ctrl_pressed = False
                self._win_pressed = False
        except Exception:
            pass

    def _on_release(self, key):
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self._ctrl_pressed = False
            elif key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                self._win_pressed = False
        except Exception:
            pass


class EscKeyListener:
    """
    ESC 键全局监听器
    用于在录音过程中按 ESC 取消录音
    """

    def __init__(self, callback):
        self.callback = callback
        self.listener = None

    def start(self):
        """
        启动快捷键监听
        """
        self.listener = keyboard.Listener(
            on_press=self._on_press
        )
        self.listener.start()

    def stop(self):
        """
        停止快捷键监听
        """
        if self.listener:
            self.listener.stop()

    def _on_press(self, key):
        try:
            if key == keyboard.Key.esc:
                self.callback()
        except Exception:
            pass


class HomeInterface(QWidget):
    """
    首页界面类
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HomeInterface")
        self.engine = EngineController(self)
        self.overlay = OverlayWidget()
        self.hotkey_listener = HotkeyListener(self._toggle_recording)
        self.esc_key_listener = EscKeyListener(self._on_esc_pressed)
        self._pending_rewrite_text = ""
        self._use_overlay = False
        self._devices_loaded = False
        self.init_ui()
        self._connect_signals()
        self.hotkey_listener.start()
        self.esc_key_listener.start()

    def init_ui(self):
        """
        初始化UI
        """
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("ReverieFlow")
        title.setObjectName("TitleLabel")
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.layout.addWidget(title)

        subtitle = QLabel("语音识别与文本润色工具")
        subtitle.setStyleSheet("font-size: 14px; color: gray;")
        self.layout.addWidget(subtitle)

        self.layout.addSpacing(15)

        device_layout = QHBoxLayout()
        device_label = QLabel("音频设备:")
        device_label.setStyleSheet("font-size: 14px;")
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(250)
        self.device_combo.mousePressEvent = self._on_device_combo_clicked
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)
        device_layout.addStretch()
        self.layout.addLayout(device_layout)

        self.layout.addSpacing(10)

        control_layout = QHBoxLayout()
        self.record_button = PushButton("开始录音")
        self.record_button.setFixedWidth(160)
        self.record_button.setObjectName("RecordButton")

        self.rewrite_button = PushButton("润色文本")
        self.rewrite_button.setFixedWidth(160)
        self.rewrite_button.setEnabled(False)

        control_layout.addWidget(self.record_button)
        control_layout.addWidget(self.rewrite_button)
        control_layout.addStretch()
        self.layout.addLayout(control_layout)

        self.layout.addSpacing(10)

        original_label = QLabel("原始识别结果:")
        original_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.layout.addWidget(original_label)

        self.original_text = TextEdit()
        self.original_text.setReadOnly(True)
        self.original_text.setPlaceholderText("识别结果将显示在这里...")
        self.layout.addWidget(self.original_text)

        rewritten_label = QLabel("润色后结果:")
        rewritten_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.layout.addWidget(rewritten_label)

        self.rewritten_text_edit = TextEdit()
        self.rewritten_text_edit.setReadOnly(True)
        self.rewritten_text_edit.setPlaceholderText("润色结果将显示在这里...")
        self.layout.addWidget(self.rewritten_text_edit)

    def _connect_signals(self):
        """
        连接信号与槽
        """
        self.record_button.clicked.connect(self._on_record_clicked)
        self.rewrite_button.clicked.connect(self._on_rewrite_clicked)

        self.engine.asr_result.connect(self._on_asr_result)
        self.engine.asr_error.connect(self._on_asr_error)
        self.engine.rewrite_result.connect(self._on_rewrite_result)
        self.engine.rewrite_error.connect(self._on_rewrite_error)
        self.engine.status_changed.connect(self._on_status_changed)

    def _load_devices(self):
        """
        加载音频设备列表（延迟初始化）
        """
        if self._devices_loaded:
            return

        try:
            if not self.engine.audio_capture:
                self.engine.init_engines()
            devices = self.engine.get_devices()
            self.device_combo.clear()
            for device in devices:
                self.device_combo.addItem(device["name"], device["index"])
        except Exception:
            self.device_combo.addItem("默认设备", None)

        self._devices_loaded = True

    def _on_device_combo_clicked(self, event):
        """
        设备下拉框点击事件（延迟加载设备）
        """
        self._load_devices()
        QComboBox.mousePressEvent(self.device_combo, event)

    def _toggle_recording(self):
        """
        切换录音状态（快捷键触发）
        """
        if not self._devices_loaded:
            self._load_devices()

        if not self.engine.is_recording:
            self._use_overlay = True
            device_index = self.device_combo.currentData()
            self.engine.start_recording(device_index)
        else:
            self.engine.stop_recording()

    def _on_record_clicked(self):
        """
        录音按钮点击事件
        """
        if not self._devices_loaded:
            self._load_devices()

        if not self.engine.is_recording:
            device_index = self.device_combo.currentData()
            self.engine.start_recording(device_index)
        else:
            self.engine.stop_recording()

    def _on_esc_pressed(self):
        """
        ESC 键按下事件：取消录音
        """
        if self.engine.is_recording:
            self.engine.cancel_recording()

    def _on_rewrite_clicked(self):
        """
        润色按钮点击事件
        """
        text = self.engine.history_text
        if text:
            self.engine.rewrite_text(text)

    def _on_asr_result(self, text: str, is_final: bool):
        """
        ASR 结果处理
        """
        if is_final:
            self.engine.history_text += text
            display_text = self.engine.history_text
        else:
            display_text = self.engine.history_text + text

        self.original_text.setText(display_text)
        scrollbar = self.original_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        if self._use_overlay:
            if not display_text:
                self.overlay.show_waiting()
            else:
                self.overlay.show_text(display_text, processing=False)

    def _on_asr_error(self, error: str):
        """
        ASR 错误处理
        """
        InfoBar.error("错误", error, parent=self, position=InfoBarPosition.TOP)

    def _on_rewrite_result(self, text: str):
        """
        润色结果处理
        """
        self.rewritten_text_edit.setText(text)
        if self._use_overlay:
            self.overlay.show_text(text, processing=False)
            QTimer.singleShot(500, lambda: self._paste_or_copy(text))

    def _paste_or_copy(self, text: str):
        """
        粘贴到活跃文本框或复制到剪贴板
        """
        import pyperclip
        import pyautogui

        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')

        self.overlay.show_text("已复制到剪贴板", processing=False)
        self.overlay.hide_after(1500)

    def _on_rewrite_error(self, error: str):
        """
        润色错误处理
        """
        InfoBar.error("润色失败", error, parent=self, position=InfoBarPosition.TOP)
        self.overlay.hide()

    def _on_status_changed(self, status: str):
        """
        状态变更处理
        """
        if status == "录音中...":
            self.record_button.setText("停止录音")
            self.original_text.clear()
            self.rewritten_text_edit.clear()
            self.rewrite_button.setEnabled(False)
        elif status == "录音已停止":
            self.record_button.setText("开始录音")
            self.rewrite_button.setEnabled(True)

            if self._use_overlay:
                text = self.engine.history_text
                if text:
                    self.overlay.show_text(text, processing=True)
                    self.engine.rewrite_text(text)
            self._use_overlay = False
        elif status == "录音已取消":
            self.record_button.setText("开始录音")
            self.rewrite_button.setEnabled(True)
            self.original_text.clear()
            self.rewritten_text_edit.clear()

            if self._use_overlay:
                self.overlay.clear()
                self.overlay.hide()
            self._use_overlay = False
        elif status == "正在润色文本...":
            if self._use_overlay:
                self.overlay.show_text(self.engine.history_text, processing=True)
        elif status == "润色完成":
            pass
        elif status == "润色失败":
            if self._use_overlay:
                self.overlay.hide()
            self._use_overlay = False
        else:
            self.record_button.setText("开始录音")

    def show_info(self, title: str, content: str, is_error: bool = False):
        """
        显示信息提示
        """
        if is_error:
            InfoBar.error(title, content, parent=self, position=InfoBarPosition.TOP)
        else:
            InfoBar.info(title, content, parent=self, position=InfoBarPosition.TOP)

    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        self.hotkey_listener.stop()
        self.esc_key_listener.stop()
        self.engine.cleanup()
        self.overlay.close()
        super().closeEvent(event)
