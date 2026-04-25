#!/usr/bin/env python3
"""
文本后处理模块
用于检测和修正识别结果中的重复词语
"""

import re
from typing import Optional

class TextPostProcessor:
    """
    文本后处理类
    用于检测和修正识别结果中的重复词语
    """
    
    def __init__(self):
        """
        初始化文本后处理
        """
        # 叠词检测正则表达式
        # 匹配连续重复的词语或短语
        self.word_pattern = re.compile(r'(\b\w+\b)(\s+\1)+\b')
        # 匹配连续重复的字符
        self.char_pattern = re.compile(r'(.)\1{2,}')
    
    def process(self, text: str) -> str:
        """
        处理文本，去除重复词语
        
        Args:
            text: 原始文本
            
        Returns:
            str: 处理后的文本
        """
        if not text:
            return text
        
        # 处理连续重复的词语
        text = self._remove_repeated_words(text)
        
        # 处理连续重复的字符
        text = self._remove_repeated_chars(text)
        
        return text
    
    def _remove_repeated_words(self, text: str) -> str:
        """
        去除连续重复的词语
        
        Args:
            text: 原始文本
            
        Returns:
            str: 处理后的文本
        """
        def replace_repeated_words(match):
            # 只保留一个重复的词语
            return match.group(1)
        
        return self.word_pattern.sub(replace_repeated_words, text)
    
    def _remove_repeated_chars(self, text: str) -> str:
        """
        去除连续重复的字符（重复3次以上）
        
        Args:
            text: 原始文本
            
        Returns:
            str: 处理后的文本
        """
        def replace_repeated_chars(match):
            # 只保留一个重复的字符
            return match.group(1)
        
        return self.char_pattern.sub(replace_repeated_chars, text)
    
    def batch_process(self, texts: list) -> list:
        """
        批量处理文本
        
        Args:
            texts: 原始文本列表
            
        Returns:
            list: 处理后的文本列表
        """
        return [self.process(text) for text in texts]
