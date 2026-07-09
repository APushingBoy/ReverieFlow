# ReverieFlow

## 项目简介
ReverieFlow 是一个语音识别和文本处理工具，支持实时语音识别、智能文本润色，以及全局快捷键快速录入。

当前版本：`v0.2.3`

## 为什么叫 ReverieFlow
只是因为我比较喜欢 Reverie 这个词，因为"Ripples of past reverie"，往昔的涟漪。

## 功能特性
- **流式 ASR 识别**：支持实时语音识别，说话时即时显示结果
- **文本润色**：对识别结果进行智能润色，提升文本质量
- **自定义润色系统提示词**：可在设置页编辑文本润色模型的 system prompt，适配个人口述习惯和专有名词纠错规则
- **全局快捷键**：按下 `Ctrl + Win` 即可快速开始/停止录音，无需打开主界面
- **悬浮窗口**：快捷键模式下，屏幕底部显示悬浮窗口，实时展示识别结果
- **自动粘贴**：润色完成后自动粘贴到当前光标活跃的文本框，或复制到剪贴板
- **音频设备选择**：支持选择当前实际连接的麦克风设备，自动过滤已断开设备
- **系统托盘**：支持最小化到托盘，右键菜单快速操作
- **GUI 设置页**：通过图形界面配置 ASR API、文本润色 API、启动行为等参数
- **设置保存后生效**：保存设置后无需重启，关闭按钮行为立即生效，ASR/音频配置在下一次录音前刷新
- **便携模式**：配置文件存储在软件同级目录，支持 U 盘携带
- **打包支持**：提供独立可执行文件，无需安装 Python 环境
- **取消识别**：录音过程中按下 `ESC` 键即可取消识别，不触发后续润色操作

## v0.2.3 更新重点
- 文本润色支持在设置页自定义 system prompt，默认提示词维护在 `assets/default_rewrite_system_prompt.txt`，用户自定义提示词会保存到 `config.json` 同级目录的 `rewrite_system_prompt.txt`。
- `rewrite_system_prompt.txt` 默认不存在；用户保存自定义提示词后才会创建，恢复默认提示词时会删除该文件。
- 系统提示词编辑窗口使用明确的亮色文本区域样式，避免黑底黑字导致无法阅读。
- 设置保存后刷新运行中的配置快照：关闭按钮行为立即生效，ASR API Key、ASR URL、ASR 模型和音频参数在下一次录音前生效，文本润色配置在下一次润色前生效。
- 打包版 `config.json` 存放在 `ReverieFlow.exe` 同级目录，便携使用时更容易找到和备份。
- 修复默认配置浅拷贝问题，避免嵌套配置被意外污染。
- Windows 程序版本信息更新为 `0.2.3.0`。

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

### 开发环境（uv 推荐）
1. 创建项目本地虚拟环境：`uv venv .venv-build --python 3.12`
2. 安装依赖：`uv pip install --python .\.venv-build\Scripts\python.exe -r requirements.txt`
3. 运行程序：`.\.venv-build\Scripts\python.exe main.py`
4. 首次运行后，通过主界面左侧导航栏的"设置"页配置 API Key、模型和润色系统提示词等参数

也可以先激活环境再运行：

```powershell
.\.venv-build\Scripts\Activate.ps1
python main.py
```

### 开发环境（pip）
如果使用已有 Python 环境，也可以直接安装依赖：

```bash
pip install -r requirements.txt
python main.py
```

### 打包版本
直接运行 `ReverieFlow.exe` 即可，无需安装 Python 环境。打包版会在 `ReverieFlow.exe` 同级目录创建和读取 `config.json`。

#### 打包命令
```bash
pyinstaller ReverieFlow.spec
```

## 项目结构
```
ReverieFlow/
├── main.py                          # 应用入口
├── config.json                      # 配置文件（自动生成，勿提交）
├── rewrite_system_prompt.txt         # 用户自定义润色提示词（修改后自动生成，可选提交）
├── requirements.txt                 # 依赖列表
├── .gitignore
├── ReverieFlow.spec                  # PyInstaller 打包配置
├── version_info.txt                  # Windows 可执行文件版本信息
├── CHANGELOG.md                     # 版本更新日志
├── assets/
│   └── default_rewrite_system_prompt.txt # 默认润色提示词
└── src/
    ├── UI/
    │   ├── main_app.py              # 主窗口（FluentWindow）
    │   ├── home_interface.py        # 首页界面
    │   ├── setting_interface.py     # 设置页
    │   ├── overlay_widget.py        # 悬浮提示窗口
    │   └── system_tray.py           # 系统托盘
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
| PyQt-Fluent-Widgets | Fluent Design UI 组件库 |
| dashscope | ASR 与文本润色模型调用 |
| pyaudio | 音频捕获 |
| soundcard | 获取当前活动的音频输入设备 |
| sounddevice | 获取正确编码的设备名 |
| websocket-client | ASR WebSocket 通信 |
| requests | HTTP 请求 |
| pynput | 全局快捷键监听 |
| pyperclip | 剪贴板操作 |
| pyautogui | 模拟键盘粘贴操作 |
| python-dotenv | 配置辅助 |
| numpy | 音频数据处理辅助 |

## 未来计划
- 加入对本地大模型的支持
- 提供更多语音识别和文本处理功能
- 提供更多主题和界面自定义选项
