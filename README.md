# ReverieFlow

## 项目简介
ReverieFlow 是一个语音识别和文本处理工具，支持实时语音识别、智能文本润色，以及全局快捷键快速录入。

## 为什么叫 ReverieFlow
只是因为我比较喜欢 Reverie 这个词，因为"Ripples of past reverie"，往昔的涟漪。

## 功能特性
- **流式 ASR 识别**：支持实时语音识别，说话时即时显示结果
- **文本润色**：对识别结果进行智能润色，提升文本质量
- **全局快捷键**：按下 `Ctrl + Win` 即可快速开始/停止录音，无需打开主界面
- **悬浮窗口**：快捷键模式下，屏幕底部显示悬浮窗口，实时展示识别结果
- **自动粘贴**：润色完成后自动粘贴到当前光标活跃的文本框，或复制到剪贴板
- **音频设备选择**：支持选择当前实际连接的麦克风设备，自动过滤已断开设备
- **GUI 设置页**：通过图形界面配置 ASR API、文本润色 API 等，无需手动编辑配置文件

## 快捷键说明

| 快捷键 | 功能 |
|---|---|
| `Ctrl + Win` | 开始/停止语音识别 |

**快捷键模式流程：**
1. 按下 `Ctrl + Win` 开始录音，屏幕底部出现悬浮窗口
2. 说话时，识别结果实时显示在悬浮窗口中
3. 再次按下 `Ctrl + Win` 停止录音，自动触发文本润色
4. 润色完成后，结果自动粘贴到当前活跃的文本框
5. 如无活跃文本框，则复制到剪贴板并提示

## 环境配置
1. 安装依赖：`pip install -r requirements.txt`
2. 运行程序：`python main.py`
3. 首次运行后，通过主界面左侧导航栏的"设置"页配置 API Key 等参数

## 项目结构
```
ReverieFlow/
├── main.py                          # 应用入口
├── config.json                      # 配置文件（自动生成，勿提交）
├── requirements.txt                 # 依赖列表
├── .gitignore
├── CHANGELOG.md                     # 版本更新日志
└── src/
    ├── UI/
    │   ├── main_app.py              # 主窗口（FluentWindow）
    │   ├── home_interface.py        # 首页界面
    │   ├── setting_interface.py     # 设置页
    │   └── overlay_widget.py        # 悬浮提示窗口
    ├── Audio/
    │   └── audio_capture.py         # 音频捕获与设备管理
    ├── ASR/
    │   └── streaming_asr.py         # 流式语音识别
    ├── TextProcessing/
    │   ├── text_post_processor.py   # 文本后处理
    │   └── text_rewriter.py         # 文本润色
    └── Utils/
        ├── config_manager.py        # JSON 配置管理
        └── logger.py                # 日志工具
```

## 依赖库
| 库 | 用途 |
|---|---|
| PyQt5 | GUI 框架 |
| qfluentwidgets | Fluent Design UI 组件库 |
| pyaudio | 音频捕获 |
| soundcard | 获取当前活动的音频输入设备 |
| sounddevice | 获取正确编码的设备名 |
| websockets | ASR WebSocket 通信 |
| pynput | 全局快捷键监听 |
| pyperclip | 剪贴板操作 |
| pyautogui | 模拟键盘粘贴操作 |
| httpx | HTTP 请求（文本润色 API） |

## 未来计划
- 加入对本地大模型的支持
- 提供更多语音识别和文本处理功能
- 支持自定义快捷键组合
- 提供更多主题和界面自定义选项
