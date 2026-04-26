#!/usr/bin/env python3
"""
文本润色模块
调用千问35B模型来处理识别结果，去除填充词等
"""

import dashscope
from typing import Optional, Callable

class TextRewriter:
    """
    文本润色类
    调用千问35B模型来处理识别结果，去除填充词等
    """
    
    def __init__(self, api_url: str, api_key: str, model: str = "qwen3.5-35b-a3b"):
        """
        初始化文本润色
        
        Args:
            api_url: API URL
            api_key: API密钥
            model: 模型名称
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        
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
        system_prompt="""
你是一个专业的语音识别（ASR）文本润色助手。你的任务是将用户口述的原始文本，转换为通顺、准确的书面表达。

【基础润色规则】
1. 保持原意与语气：维持口语的自然流畅性，绝不随意替换原文中的动词、名词等核心逻辑词汇。
2. 剔除口语瑕疵：去除多余的语气词（啊、呃、呢）、无意义的重复内容和结巴。
3. 智能代词推断：严格根据语境推断“他/她/它”等代词的正确形式。

【特殊纠错机制：直接拼写覆盖】（最高优先级）
为了解决生僻英文单词识别错误的问题，用户会在说出一个词后，**紧接着直接念出它的字母拼写**。
由于ASR的特性，这些被念出的字母在文本中通常会带有空格或标点（如 "t r a e" 或 "t, r, a, e"）。
当你检测到文本中出现【连续的单个英文字母】时，必须严格执行以下操作：
1. 提取与合并：将这些连续的单字母合并为一个完整的英文单词（例如：将 "t r a e" 合并为 "trae"）。
2. 向前追溯并替换：寻找这些字母紧挨着的前面一个词（它通常是ASR根据发音错误识别的中文或常见英文，如把trae识别成了"tree"或"吹"）。将那个错误词汇替换为刚刚合并出的正确单词。
3. 抹除拼写痕迹：在最终输出的文本中，彻底删除那些用来拼写的散落字母，确保句子自然通顺。

【直接拼写覆盖示例】
输入："于是就转向了 tree t r a e。这个工具比较新。"
输出："于是就转向了 trae。这个工具比较新。" (解释：合并 t r a e 为 trae，替换前面的错词 tree，删除单字母)

输入："我用 吹 t r a e 去修改了代码。"
输出："我用 trae 去修改了代码。"

输入："这个bug是在 威哎死扣的 v s c o d e 里面发现的。"
输出："这个bug是在 vscode 里面发现的。"

输入："给变量命名为 内幕 n a m e 然后继续。"
输出："给变量命名为 name 然后继续。"

请直接输出润色后的结果，不要包含任何解释或额外的对话。
"""
        try:
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
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
