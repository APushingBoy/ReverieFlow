#!/usr/bin/env python3
"""
配置管理模块
用于加载和管理应用配置，基于 JSON 格式
配置文件存储在软件同级目录，支持便携使用（Portable）
"""

import os
import json
import copy
import sys
from pathlib import Path


DEFAULT_REWRITE_SYSTEM_PROMPT = """
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
""".strip()


DEFAULT_CONFIG = {
    "asr": {
        "api_key": "",
        "api_url": "wss://dashscope.aliyuncs.com/api-ws/v1/inference",
        "model": "fun-asr-realtime"
    },
    "rewrite": {
        "api_key": "",
        "api_url": "https://dashscope.aliyuncs.com/api/v1",
        "model": "qwen3.5-35b-a3b",
        "system_prompt": DEFAULT_REWRITE_SYSTEM_PROMPT
    },
    "audio": {
        "sample_rate": 16000,
        "channels": 1,
        "chunk_size": 1024
    },
    "ui": {
        "app_name": "ReverieFlow",
        "window_width": 800,
        "window_height": 600
    }
}


class ConfigManager:
    """
    配置管理类
    用于管理 config.json 的创建、读取和写入
    """

    def __init__(self, config_file: str = None):
        """
        初始化配置管理器

        Args:
            config_file: 配置文件路径，如果不指定则自动选择
        """
        if config_file:
            self.config_path = Path(config_file)
        else:
            self.config_path = self._resolve_config_path()

        self.config = {}
        self._load_or_create()

    def _resolve_config_path(self) -> Path:
        """
        解析配置文件路径
        使用软件同级目录，支持便携使用（Portable）

        Returns:
            Path: 配置文件路径
        """
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent / "config.json"
        return Path(__file__).resolve().parent.parent.parent / "config.json"

    def _load_or_create(self):
        """
        加载配置文件，如果不存在则创建默认配置
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.config = self._merge_with_defaults(loaded)
            except (json.JSONDecodeError, IOError):
                self.config = copy.deepcopy(DEFAULT_CONFIG)
                self.save()
        else:
            self.config = copy.deepcopy(DEFAULT_CONFIG)
            self.save()

    def _merge_with_defaults(self, loaded: dict) -> dict:
        """
        将加载的配置与默认配置合并，确保新字段不会缺失

        Args:
            loaded: 从文件加载的配置

        Returns:
            dict: 合并后的配置
        """
        merged = copy.deepcopy(DEFAULT_CONFIG)
        for section, values in loaded.items():
            if section in merged and isinstance(values, dict) and isinstance(merged[section], dict):
                merged[section].update(values)
            else:
                merged[section] = values
        return merged

    def get(self, section: str, key: str, default: str = "") -> str:
        """
        获取配置值

        Args:
            section: 配置分组名
            key: 配置键
            default: 默认值

        Returns:
            str: 配置值
        """
        try:
            return str(self.config.get(section, {}).get(key, default))
        except Exception:
            return str(default)

    def get_int(self, section: str, key: str, default: int = 0) -> int:
        """
        获取整数类型的配置值

        Args:
            section: 配置分组名
            key: 配置键
            default: 默认值

        Returns:
            int: 配置值
        """
        try:
            return int(self.config.get(section, {}).get(key, default))
        except (ValueError, TypeError):
            return default

    def get_bool(self, section: str, key: str, default: bool = False) -> bool:
        """
        获取布尔类型的配置值

        Args:
            section: 配置分组名
            key: 配置键
            default: 默认值

        Returns:
            bool: 配置值
        """
        try:
            value = self.config.get(section, {}).get(key, str(default))
            if isinstance(value, bool):
                return value
            return str(value).lower() in ("true", "1", "yes", "y")
        except Exception:
            return default

    def set(self, section: str, key: str, value):
        """
        设置配置值

        Args:
            section: 配置分组名
            key: 配置键
            value: 配置值
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value

    def get_section(self, section: str) -> dict:
        """
        获取整个分组的配置

        Args:
            section: 配置分组名

        Returns:
            dict: 该分组的配置字典
        """
        return self.config.get(section, {}).copy()

    def get_all(self) -> dict:
        """
        获取完整配置

        Returns:
            dict: 完整配置字典的深拷贝
        """
        return json.loads(json.dumps(self.config))

    def save(self):
        """
        保存配置到 JSON 文件
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"保存配置文件失败: {e}")

    def __repr__(self) -> str:
        return f"ConfigManager(path={self.config_path})"
