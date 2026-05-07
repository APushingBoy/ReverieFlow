# main 分支功能分析

## 1. 技术栈与形态
- 平台：Windows 桌面工具（Python）
- UI 框架：PyQt5 + qfluentwidgets
- 音频采集：pyaudio / soundcard / sounddevice
- 云服务：Fun-ASR（流式）+ Qwen（文本润色）
- 自动输入：pyautogui 模拟粘贴 + pyperclip

## 2. 核心用户路径
1. 用户通过主界面或全局快捷键启动录音
2. 音频流式发送至 ASR，实时显示识别文本
3. 停止后触发文本润色
4. 将润色结果自动写入当前焦点输入框（失败则复制剪贴板）

## 3. 模块职责
- `src/UI/home_interface.py`：工作台、录音控制、结果展示、快捷键
- `src/Audio/audio_capture.py`：音频设备选择与采集
- `src/ASR/streaming_asr.py`：流式识别连接与事件回调
- `src/TextProcessing/text_rewriter.py`：调用 LLM 进行文本润色
- `src/UI/setting_interface.py`：API、模型和行为设置
- `src/UI/system_tray.py`：系统托盘与后台驻留

## 4. 现状结论
- `main` 已实现完整桌面 MVP，优势是“快捷键触发 + 悬浮反馈 + 自动粘贴”链路完整。
- 架构面向桌面系统，不可直接复用于 iOS 输入法扩展，需要拆分为“主 App + Keyboard Extension + App Group”模式。
