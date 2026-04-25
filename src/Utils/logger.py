#!/usr/bin/env python3
"""
日志管理模块
用于记录应用运行状态和错误信息
"""

import logging
import os
from datetime import datetime

class Logger:
    """
    日志管理类
    用于记录应用运行状态和错误信息
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志目录
        """
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建日志文件
        log_file = os.path.join(self.log_dir, f"ReverieFlow_{datetime.now().strftime('%Y%m%d')}.log")
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("ReverieFlow")
    
    def info(self, message: str):
        """
        记录信息日志
        
        Args:
            message: 日志消息
        """
        self.logger.info(message)
    
    def warning(self, message: str):
        """
        记录警告日志
        
        Args:
            message: 日志消息
        """
        self.logger.warning(message)
    
    def error(self, message: str, exception: Exception = None):
        """
        记录错误日志
        
        Args:
            message: 日志消息
            exception: 异常对象
        """
        if exception:
            self.logger.error(message, exc_info=exception)
        else:
            self.logger.error(message)
    
    def debug(self, message: str):
        """
        记录调试日志
        
        Args:
            message: 日志消息
        """
        self.logger.debug(message)

# 创建全局日志实例
logger = Logger()
