#!/usr/bin/env python3
"""
文本润色模块
调用千问35B模型来处理识别结果，去除填充词等
"""

import dashscope
from typing import Optional, Callable
from Utils.config_manager import DEFAULT_REWRITE_SYSTEM_PROMPT

class TextRewriter:
    """
    文本润色类
    调用千问35B模型来处理识别结果，去除填充词等
    """
    
    def __init__(
        self,
        api_url: str,
        api_key: str,
        model: str = "qwen3.5-35b-a3b",
        system_prompt: str = DEFAULT_REWRITE_SYSTEM_PROMPT
    ):
        """
        初始化文本润色
        
        Args:
            api_url: API URL
            api_key: API密钥
            model: 模型名称
            system_prompt: 润色系统提示词
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt or DEFAULT_REWRITE_SYSTEM_PROMPT
        
        # 设置API密钥
        dashscope.api_key = api_key
        
        # 设置API URL
        if api_url:
            dashscope.base_http_api_url = api_url
    
    def rewrite(self, text: str, callback: Optional[Callable[[str], None]] = None) -> Optional[str]:
        """
        润色文本
        
        Args:
            text: 原始文本
            callback: 回调函数
            
        Returns:
            str: 润色后的文本
        """
        try:
            dashscope.api_key = self.api_key
            if self.api_url:
                dashscope.base_http_api_url = self.api_url

            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": f"请润色以下文本：\n{text}"
                }
            ]
            
            # 调用千问API
            response = dashscope.MultiModalConversation.call(
                model=self.model,
                messages=messages,
                temperature=0.3,
                enable_thinking=False
            )
            
            # 处理响应
            if response.status_code == 200:
                # print(f'收到了response: {response}')
                rewritten_text = response.output.choices[0].message.content[0]["text"]
                print(f'润色后的文本: {rewritten_text}')
                
                if callback:
                    callback(rewritten_text)
                
                return rewritten_text
            else:
                print(f"润色API请求失败: {response.status_code} - {response.message}")
                return None
        except Exception as e:
            print(f"润色文本失败: {e}")
            return None
    
    def batch_rewrite(self, texts: list, callback: Optional[Callable[[list], None]] = None) -> Optional[list]:
        """
        批量润色文本
        
        Args:
            texts: 原始文本列表
            callback: 回调函数
            
        Returns:
            list: 润色后的文本列表
        """
        rewritten_texts = []
        
        for text in texts:
            rewritten = self.rewrite(text)
            rewritten_texts.append(rewritten if rewritten else text)
        
        if callback:
            callback(rewritten_texts)
        
        return rewritten_texts
