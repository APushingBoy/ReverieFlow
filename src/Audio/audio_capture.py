#!/usr/bin/env python3
"""
音频捕获模块
用于从麦克风捕获音频数据
"""

import pyaudio
import sounddevice as sd
import soundcard as sc
import numpy as np
import threading
import queue
from typing import Optional, Callable

class AudioCapture:
    """
    音频捕获类
    用于从麦克风捕获音频数据并提供给ASR模块
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.pa = pyaudio.PyAudio()
        self.stream = None
        self.queue = queue.Queue()
        self.is_recording = False
        self.callback = None
        self.thread = None
        # 【新增】保存设备索引
        self.device_index = None 
    
    def start(self, callback: Optional[Callable[[bytes], None]] = None) -> bool:
        """
        开始捕获音频
        """
        try:
            self.callback = callback
            self.is_recording = True
            
            # 构建打开流的参数
            stream_kwargs = {
                'format': pyaudio.paInt16,
                'channels': self.channels,
                'rate': self.sample_rate,
                'input': True,
                'frames_per_buffer': self.chunk_size,
                'stream_callback': self._audio_callback
            }
            
            # 如果指定了设备，则添加设备索引参数
            if self.device_index is not None:
                stream_kwargs['input_device_index'] = self.device_index
                
            # 打开音频流
            self.stream = self.pa.open(**stream_kwargs)
            
            # 开始流
            self.stream.start_stream()
            return True
        except Exception as e:
            print(f"音频捕获启动失败: {e}")
            return False
    
    def stop(self):
        """
        停止捕获音频
        """
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """
        音频流回调函数
        
        Args:
            in_data: 音频数据
            frame_count: 帧数
            time_info: 时间信息
            status: 状态
            
        Returns:
            tuple: (数据, 状态)
        """
        if self.is_recording:
            # 只调用回调函数，不将数据放入队列
            # 避免音频数据被重复处理
            if self.callback:
                self.callback(in_data)
        
        return (None, pyaudio.paContinue)
    
    def get_audio_data(self, block: bool = True, timeout: Optional[float] = None) -> Optional[bytes]:
        """
        获取音频数据
        
        Args:
            block: 是否阻塞
            timeout: 超时时间
            
        Returns:
            bytes: 音频数据
        """
        try:
            return self.queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
    
    def get_devices(self) -> list:
        """
        获取当前实际可用的音频输入设备
        使用 soundcard 获取当前活动的设备（过滤掉已断开/未连接的设备）
        使用 sounddevice 获取正确的设备名（处理 Windows Unicode 编码）
        使用 pyaudio 进行实际的音频捕获

        Returns:
            list: 设备列表
        """
        # 获取当前活动的麦克风设备名（soundcard 只返回实际连接的设备）
        try:
            active_mics = sc.all_microphones()
            active_names = {mic.name for mic in active_mics}
        except Exception:
            active_names = None

        devices = []
        seen_names = set()
        sd_devices = sd.query_devices()
        for i in range(self.pa.get_device_count()):
            info = self.pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                try:
                    if i < len(sd_devices):
                        name = sd_devices[i]['name']
                    else:
                        name = info['name']
                except Exception:
                    name = info['name']

                # 如果 soundcard 可用，只保留活动设备
                if active_names is not None and name not in active_names:
                    continue

                # 按设备名去重，保留第一个出现的
                if name not in seen_names:
                    seen_names.add(name)
                    devices.append({
                        'index': i,
                        'name': name,
                        'channels': info['maxInputChannels']
                    })
        return devices
    
    def set_device(self, device_index: int) -> bool:
        """
        设置音频输入设备（仅记录索引，在start时生效）
        """
        self.device_index = device_index
        return True
    
    def __del__(self):
        """
        析构函数
        """
        self.stop()
        if self.pa:
            self.pa.terminate()
