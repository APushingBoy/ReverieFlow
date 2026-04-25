# ReverieFlow

## 项目简介
ReverieFlow是一个语音识别和文本处理工具，目前处于开发版本阶段。

## 为什么叫 ReverieFlow
只是因为我比较喜欢 Reverie 这个词，因为“Ripples of past reverie”，往昔的涟漪

## 功能特性
- **流式ASR模式**：支持实时语音识别
- **文本润色**：对识别结果进行智能润色

## 技术现状
- 目前仅支持千问的ASR模型，并通过`dashscope`调用
- 仅支持在.env中填入API KEY来使用
- 目前仅支持API调用大模型
- 没有EXE或其他release版本
- GUI界面较为简陋，后续会逐步完善

## 未来计划
- 加入对本地大模型的支持
- 优化GUI界面
- 提供更多语音识别和文本处理功能

## 环境配置
1. 复制 `.env.example` 文件为 `.env`
2. 填写相关API密钥和配置信息
3. 安装依赖：`pip install -r requirements.txt`

## 运行方式
```bash
python main.py
```
