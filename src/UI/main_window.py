#!/usr/bin/env python3
"""
主窗口类
实现参考Voxt的UI界面
"""

import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QComboBox, QStatusBar, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon

from Audio.audio_capture import AudioCapture
from ASR.streaming_asr import StreamingASR
from TextProcessing.text_rewriter import TextRewriter
from Utils.config_manager import ConfigManager
from Utils.logger import logger

class MainWindow(QMainWindow):
    """
    主窗口类
    """
    
    # 定义信号
    update_text_signal = pyqtSignal(str, bool)
    update_status_signal = pyqtSignal(str)
    
    def __init__(self):
        """
        初始化主窗口
        """
        super().__init__()
        
        # 加载配置
        self.config = ConfigManager()
        
        # 初始化组件
        self.audio_capture = AudioCapture(
            sample_rate=self.config.get_int("SAMPLE_RATE", 16000),
            channels=self.config.get_int("CHANNELS", 1),
            chunk_size=self.config.get_int("CHUNK_SIZE", 1024)
        )
        
        self.streaming_asr = StreamingASR(
            api_url=self.config.get("ASR_API_URL", "wss://dashscope.aliyuncs.com/api-ws/v1/inference"),
            api_key=self.config.get("ASR_API_KEY", ""),
            model=self.config.get("ASR_MODEL", "fun-asr-realtime")
        )
        
        self.text_rewriter = TextRewriter(
            api_url=self.config.get("REWRITE_API_URL", "https://dashscope.aliyuncs.com/api/v1"),
            api_key=self.config.get("REWRITE_API_KEY", ""),
            model=self.config.get("REWRITE_MODEL", "qwen3.5-35b-a3b")
        )
        
        # 状态变量
        self.is_recording = False
        self.recognized_text = ""
        self.rewritten_text = ""
        
        # 初始化UI
        self.init_ui()
        
        # 连接信号
        self.update_text_signal.connect(self._update_text)
        self.update_status_signal.connect(self.statusBar().showMessage)
        
        # 加载设备列表
        self.load_devices()
    
    def init_ui(self):
        """
        初始化UI
        """
        # 设置窗口标题和大小
        self.setWindowTitle(self.config.get("APP_NAME", "ReverieFlow"))
        self.setGeometry(100, 100, 
                        self.config.get_int("WINDOW_WIDTH", 800),
                        self.config.get_int("WINDOW_HEIGHT", 600))
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 设备选择布局
        device_layout = QHBoxLayout()
        device_label = QLabel("音频设备:")
        self.device_combo = QComboBox()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_combo)
        device_layout.addStretch()
        main_layout.addLayout(device_layout)
        
        # 文本显示区域
        splitter = QSplitter(Qt.Vertical)
        
        # 原始识别文本
        original_group = QWidget()
        original_layout = QVBoxLayout(original_group)
        original_label = QLabel("原始识别结果:")
        self.original_text = QTextEdit()
        self.original_text.setReadOnly(True)
        original_layout.addWidget(original_label)
        original_layout.addWidget(self.original_text)
        splitter.addWidget(original_group)
        
        # 润色后文本
        rewritten_group = QWidget()
        rewritten_layout = QVBoxLayout(rewritten_group)
        rewritten_label = QLabel("润色后结果:")
        self.rewritten_text_edit = QTextEdit()
        self.rewritten_text_edit.setReadOnly(True)
        rewritten_layout.addWidget(rewritten_label)
        rewritten_layout.addWidget(self.rewritten_text_edit)
        splitter.addWidget(rewritten_group)
        
        # 设置分割器比例
        splitter.setSizes([300, 300])
        main_layout.addWidget(splitter)
        
        # 控制按钮布局
        control_layout = QHBoxLayout()
        
        self.record_button = QPushButton("开始录音")
        self.record_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; }")
        self.record_button.clicked.connect(self.toggle_recording)
        
        self.rewrite_button = QPushButton("润色文本")
        self.rewrite_button.setEnabled(False)
        self.rewrite_button.clicked.connect(self.rewrite_text)
        
        control_layout.addWidget(self.record_button)
        control_layout.addWidget(self.rewrite_button)
        control_layout.addStretch()
        
        main_layout.addLayout(control_layout)
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def load_devices(self):
        """
        加载音频设备列表
        """
        devices = self.audio_capture.get_devices()
        for device in devices:
            self.device_combo.addItem(device["name"], device["index"])
    
    def toggle_recording(self):
        """
        切换录音状态
        """
        if not self.is_recording:
            # 开始录音
            self.start_recording()
        else:
            # 停止录音
            self.stop_recording()
    
    def start_recording(self):
        """
        开始录音
        """
        try:
            logger.info("开始录音")
            
            # 选择设备
            device_index = self.device_combo.currentData()
            if device_index is not None:
                logger.info(f"选择音频设备: {device_index}")
                if not self.audio_capture.set_device(device_index):
                    logger.error("设置音频设备失败")
                    QMessageBox.warning(self, "设备错误", "无法设置音频设备")
                    return
            
            # 连接ASR服务
            logger.info("连接到ASR服务")
            if not self.streaming_asr.connect():
                logger.error("连接ASR服务失败")
                QMessageBox.warning(self, "连接失败", "无法连接到ASR服务，请检查网络和API配置")
                return
            
            # 开始捕获音频
            logger.info("启动音频捕获")
            if not self.audio_capture.start(callback=self.audio_callback):
                logger.error("启动音频捕获失败")
                QMessageBox.warning(self, "启动失败", "无法启动音频捕获，请检查麦克风权限")
                return
            
            # 开始ASR
            self.streaming_asr.start(
                result_callback=self.asr_result_callback,
                error_callback=self.asr_error_callback
            )
            
            # 更新UI
            self.is_recording = True
            self.record_button.setText("停止录音")
            self.record_button.setStyleSheet("QPushButton { background-color: #4ecdc4; color: white; font-weight: bold; }")
            self.status_bar.showMessage("录音中...")
            self.original_text.clear()
            self.rewritten_text_edit.clear()
            self.recognized_text = ""
            self.rewritten_text = ""

            # 【新增】用于保存已经确定下来的历史句子
            self.history_text = "" 
            
            logger.info("录音已启动")
        except Exception as e:
            logger.error("启动录音失败", exception=e)
            QMessageBox.critical(self, "错误", f"启动录音失败: {e}")
    
    def stop_recording(self):
        """
        停止录音
        """
        try:
            logger.info("停止录音")
            
            # 停止音频捕获
            self.audio_capture.stop()
            logger.info("音频捕获已停止")
            
            # 停止ASR
            self.streaming_asr.stop()
            logger.info("ASR已停止")
            
            # 关闭ASR连接
            self.streaming_asr.close()
            logger.info("ASR连接已关闭")
            
            # 更新UI
            self.is_recording = False
            self.record_button.setText("开始录音")
            self.record_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; }")
            self.status_bar.showMessage("录音已停止")
            self.rewrite_button.setEnabled(True)
            
            logger.info("录音已停止")
        except Exception as e:
            logger.error("停止录音失败", exception=e)
            QMessageBox.critical(self, "错误", f"停止录音失败: {e}")
    
    def audio_callback(self, audio_data):
        """
        音频数据回调
        """
        if self.is_recording:
            self.streaming_asr.send_audio(audio_data)
    
    def asr_result_callback(self, text, is_final):
        """
        ASR结果回调
        """
        # 通过信号更新UI
        self.update_text_signal.emit(text, is_final)
    
    def asr_error_callback(self, error):
        """
        ASR错误回调
        """
        # 通过信号更新UI
        self.update_status_signal.emit(f"错误: {error}")
    
    def _update_text(self, text, is_final):
            """
            更新文本的槽函数
            """
            if is_final:
                # 最终结果：追加到历史记录中，并加上换行符
                self.history_text += text
                self.recognized_text = self.history_text
                self.original_text.setText(self.history_text)
                
                # 让文本框自动滚动到底部
                scrollbar = self.original_text.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
            else:
                # 中间结果：显示 历史记录 + 当前正在说的半句话
                current_display = self.history_text + text
                self.original_text.setText(current_display)
    
    def rewrite_text(self):
        """
        润色文本
        """
        if not self.recognized_text:
            logger.warning("没有可润色的文本")
            QMessageBox.warning(self, "警告", "没有可润色的文本")
            return
        
        logger.info("开始润色文本")
        self.status_bar.showMessage("正在润色文本...")
        
        # 调用润色API
        try:
            rewritten = self.text_rewriter.rewrite(self.recognized_text)
            
            if rewritten:
                self.rewritten_text = rewritten
                self.rewritten_text_edit.setText(self.rewritten_text)
                self.status_bar.showMessage("润色完成")
                logger.info("文本润色成功")
            else:
                logger.warning("润色失败，请检查API配置")
                QMessageBox.warning(self, "警告", "润色失败，请检查API配置")
                self.status_bar.showMessage("润色失败")
        except Exception as e:
            logger.error("润色文本失败", exception=e)
            QMessageBox.critical(self, "错误", f"润色文本失败: {e}")
            self.status_bar.showMessage("润色失败")
    
    def closeEvent(self, event):
        """
        关闭窗口事件
        """
        # 停止录音
        if self.is_recording:
            self.stop_recording()
        
        # 关闭音频捕获
        if hasattr(self, 'audio_capture'):
            del self.audio_capture
        
        # 关闭ASR连接
        if hasattr(self, 'streaming_asr'):
            del self.streaming_asr
        
        event.accept()
