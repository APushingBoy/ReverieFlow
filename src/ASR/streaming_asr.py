#!/usr/bin/env python3
"""
流式ASR模块
通过dashscope调用千问的语音识别模型
"""

import os
import threading
import queue
import dashscope
from dashscope.audio.asr import RecognitionCallback, Recognition, RecognitionResult
from typing import Optional, Callable

class StreamingASR:
    """
    流式ASR类
    通过dashscope调用千问的语音识别模型
    """
    
    def __init__(self, api_url: str, api_key: str, model: str = "fun-asr-realtime"):
        """
        初始化流式ASR
        
        Args:
            api_url: WebSocket API URL
            api_key: API密钥
            model: 模型名称
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.recognition = None
        self.is_connected = False
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.result_callback = None
        self.error_callback = None
        self.thread = None
        
        # 设置API密钥
        dashscope.api_key = api_key
        
        # 设置WebSocket API URL
        if api_url:
            dashscope.base_websocket_api_url = api_url
    
    def connect(self) -> bool:
        """
        初始化识别服务
        
        Returns:
            bool: 是否成功初始化
        """
        try:
            # 创建识别回调
            self.callback = Callback(self.result_callback, self.error_callback)
            
            # 初始化识别服务
            self.recognition = Recognition(
                model=self.model,
                format='pcm',
                sample_rate=16000,
                semantic_punctuation_enabled=True,
                callback=self.callback
            )
            
            self.is_connected = True
            return True
        except Exception as e:
            print(f"初始化识别服务失败: {e}")
            if self.error_callback:
                self.error_callback(f"初始化失败: {e}")
            return False
    
    def start(self, result_callback: Callable[[str, bool], None], error_callback: Optional[Callable[[str], None]] = None):
        """
        开始流式识别
        
        Args:
            result_callback: 识别结果回调函数
            error_callback: 错误回调函数
        """
        self.result_callback = result_callback
        self.error_callback = error_callback
        self.is_recording = True
        
        # 更新回调
        if hasattr(self, 'callback'):
            self.callback.result_callback = result_callback
            self.callback.error_callback = error_callback
        
        # 【新增】清空队列，防止上次录音的残留数据
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
                
        # 【新增】启动音频发送异步线程
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._send_thread)
            self.thread.daemon = True # 设置为守护线程
            self.thread.start()
        
        # 启动识别
        if self.recognition:
            self.recognition.start()
    
    def stop(self):
        """
        停止流式识别
        """
        self.is_recording = False
        # 发送结束标志
        self.audio_queue.put(None)
        
        # 【新增】等待发送线程处理完队列中的最后数据并结束
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            self.thread = None
        
        # 停止识别
        if self.recognition:
            self.recognition.stop()
    
    def send_audio(self, audio_data: bytes):
        """
        发送音频数据
        
        Args:
            audio_data: 音频数据
        """
        if self.is_connected and self.is_recording:
            # 【修改】将数据放入队列，而不是直接阻塞发送
            self.audio_queue.put(audio_data)
    
    def _send_thread(self):
        """
        发送音频数据的线程
        """
        while self.is_recording:
            try:
                audio_data = self.audio_queue.get(timeout=1)
                
                # 检查是否是结束标志
                if audio_data is None:
                    break
                
                # 发送音频数据
                if self.recognition and self.is_connected:
                    self.recognition.send_audio_frame(audio_data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"发送音频数据失败: {e}")
                if self.error_callback:
                    self.error_callback(f"发送音频失败: {e}")
                break
    
    def close(self):
        """
        关闭识别服务
        """
        self.is_recording = False
        if self.recognition:
            try:
                self.recognition.stop()
            except Exception as e:
                print(f"停止识别服务失败: {e}")
        self.is_connected = False
    
    def __del__(self):
        """
        析构函数
        """
        self.close()

class Callback(RecognitionCallback):
    """
    识别回调类
    """
    
    def __init__(self, result_callback: Optional[Callable[[str, bool], None]] = None, 
                 error_callback: Optional[Callable[[str], None]] = None):
        """
        初始化回调
        
        Args:
            result_callback: 识别结果回调函数
            error_callback: 错误回调函数
        """
        self.result_callback = result_callback
        self.error_callback = error_callback
        self.accumulated_text = ""  # 累积的文本
        self.last_text = ""  # 用于去重
    
    def on_open(self) -> None:
        """
        连接打开回调
        """
        print('RecognitionCallback open.')
        # 重置累积文本
        self.accumulated_text = ""
        self.last_text = ""
    
    def on_close(self) -> None:
        """
        连接关闭回调
        """
        print('RecognitionCallback close.')
    
    def on_complete(self) -> None:
        """
        识别完成回调
        """
        print('RecognitionCallback completed.')
    
    def on_error(self, message) -> None:
        """
        错误回调
        
        Args:
            message: 错误信息
        """
        print('RecognitionCallback task_id: ', message.request_id)
        print('RecognitionCallback error: ', message.message)
        if self.error_callback:
            self.error_callback(message.message)
    
    def on_event(self, result: RecognitionResult) -> None:
        """
        事件回调
        
        Args:
            result: 识别结果
        """
        sentence = result.get_sentence()
        if 'text' in sentence:
            text = sentence['text']
            is_final = RecognitionResult.is_sentence_end(sentence)
            
            # 去重：只有当文本不同时才处理
            if text != self.last_text:
                if is_final:
                    # 最终结果，直接使用
                    self.accumulated_text = text
                else:
                    # 中间结果，累积显示
                    self.accumulated_text = text
                
                if self.result_callback:
                    self.result_callback(self.accumulated_text, is_final)
                print('RecognitionCallback text: ', self.accumulated_text)
                self.last_text = text
                
            if is_final:
                print(
                    'RecognitionCallback sentence end, request_id:%s, usage:%s'
                    % (result.get_request_id(), result.get_usage(sentence)))

