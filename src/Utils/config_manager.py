#!/usr/bin/env python3
"""
配置管理模块
用于加载和管理应用配置
"""

import os
from dotenv import load_dotenv

class ConfigManager:
    """
    配置管理类
    用于加载和管理应用配置
    """
    
    def __init__(self, config_file: str = ".env"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """
        加载配置文件
        """
        # 尝试加载.env文件
        load_dotenv(self.config_file)
        
        # 从环境变量加载配置
        self.config = {
            # ASR API 配置
            "ASR_API_KEY": os.getenv("ASR_API_KEY", ""),
            "ASR_API_URL": os.getenv("ASR_API_URL", "wss://api.example.com/asr/stream"),
            "ASR_MODEL": os.getenv("ASR_MODEL", "whisper-1"),
            
            # 文本润色 API 配置
            "REWRITE_API_KEY": os.getenv("REWRITE_API_KEY", ""),
            "REWRITE_API_URL": os.getenv("REWRITE_API_URL", "https://api.example.com/chat/completions"),
            "REWRITE_MODEL": os.getenv("REWRITE_MODEL", "gpt-4o-mini"),
            
            # 音频配置
            "SAMPLE_RATE": os.getenv("SAMPLE_RATE", "16000"),
            "CHANNELS": os.getenv("CHANNELS", "1"),
            "CHUNK_SIZE": os.getenv("CHUNK_SIZE", "1024"),
            
            # UI 配置
            "APP_NAME": os.getenv("APP_NAME", "ReverieFlow"),
            "WINDOW_WIDTH": os.getenv("WINDOW_WIDTH", "800"),
            "WINDOW_HEIGHT": os.getenv("WINDOW_HEIGHT", "600"),
        }
    
    def get(self, key: str, default: str = "") -> str:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            str: 配置值
        """
        return self.config.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        获取整数类型的配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            int: 配置值
        """
        try:
            return int(self.config.get(key, default))
        except ValueError:
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        获取布尔类型的配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            bool: 配置值
        """
        value = self.config.get(key, str(default)).lower()
        return value in ("true", "1", "yes", "y")
    
    def set(self, key: str, value: str):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
    
    def save(self):
        """
        保存配置到文件
        """
        with open(self.config_file, "w", encoding="utf-8") as f:
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")
