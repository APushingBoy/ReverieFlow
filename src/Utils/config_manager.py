#!/usr/bin/env python3
"""
配置管理模块
用于加载和管理应用配置，基于 JSON 格式
配置文件存储在软件同级目录，支持便携使用（Portable）
"""

import os
import json
from pathlib import Path


DEFAULT_CONFIG = {
    "asr": {
        "api_key": "",
        "api_url": "wss://dashscope.aliyuncs.com/api-ws/v1/inference",
        "model": "fun-asr-realtime"
    },
    "rewrite": {
        "api_key": "",
        "api_url": "https://dashscope.aliyuncs.com/api/v1",
        "model": "qwen3.5-35b-a3b"
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
                self.config = DEFAULT_CONFIG.copy()
                self.save()
        else:
            self.config = DEFAULT_CONFIG.copy()
            self.save()

    def _merge_with_defaults(self, loaded: dict) -> dict:
        """
        将加载的配置与默认配置合并，确保新字段不会缺失

        Args:
            loaded: 从文件加载的配置

        Returns:
            dict: 合并后的配置
        """
        merged = DEFAULT_CONFIG.copy()
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
