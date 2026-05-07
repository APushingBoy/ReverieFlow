# ReverieFlow iOS MVP（Voice Input Method）

该目录实现基于 PRD 的 iOS 初版架构，目标是“纯语音输入法”：
- Keyboard Extension 不提供任何键盘按键输入
- 通过 ASR 流式识别 + LLM 润色输出文本
- 最终通过 `textDocumentProxy` 注入当前 App 输入框
- 主 App 负责权限申请与配置管理

## 目录说明

```text
ios/ReverieFlowiOS/
├── project.yml                            # xcodegen 工程配置
├── App/
│   ├── ReverieFlowApp.entitlements        # 主 App App Group
│   └── ReverieFlowKeyboard.entitlements   # 输入法扩展 App Group
├── Sources/
│   ├── MainApp/                           # 主 App：权限、设置、状态查看
│   ├── KeyboardExtension/                 # 输入法扩展：双栏 UI + 注入文本
│   └── Shared/                            # 共享模型、状态机、音频/ASR/润色管线
└── README.md
```

## 与 PRD 对应关系

- 输入法扩展职责：`KeyboardViewController` + `KeyboardRootView`
- 主 App 职责：`MainAppView` + `SettingsView` + `PermissionCenter`
- 状态机：`InputEngineState`
- 数据流：`VoicePipelineCoordinator`
- App Group 通信：`SharedStore` + `ReverieSettings` + `PipelineSnapshot`

## 快速开始

1. 安装 xcodegen
2. 在本目录执行：

```bash
xcodegen generate
```

3. 使用 Xcode 打开 `ReverieFlowiOS.xcodeproj`
4. 在 Signing 中设置 Team 与 App Group：`group.com.reverieflow.ios`
5. 启用 Keyboard Extension，并在系统设置中允许“完全访问”
6. 启动主 App，填写 ASR/LLM API 参数并申请麦克风权限

## 注意事项

- iOS 键盘扩展对后台能力和权限有严格限制，此版本采用轻量本地流程 + 云端服务调用。
- 若需更强稳定性，建议后续引入更可靠的流式协议适配层（例如 Fun-ASR 官方消息格式适配器）。
