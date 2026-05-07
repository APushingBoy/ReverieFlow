import SwiftUI

struct SettingsView: View {
    @State private var settings: ReverieSettings
    private let onSave: (ReverieSettings) -> Void

    init(settings: ReverieSettings, onSave: @escaping (ReverieSettings) -> Void) {
        _settings = State(initialValue: settings)
        self.onSave = onSave
    }

    var body: some View {
        Section("API 配置") {
            TextField("ASR API Key", text: $settings.asrApiKey)
                .textInputAutocapitalization(.never)
            TextField("ASR Endpoint", text: $settings.asrEndpoint)
                .textInputAutocapitalization(.never)
            TextField("ASR Model", text: $settings.asrModel)
                .textInputAutocapitalization(.never)

            TextField("LLM API Key", text: $settings.llmApiKey)
                .textInputAutocapitalization(.never)
            TextField("LLM Endpoint", text: $settings.llmEndpoint)
                .textInputAutocapitalization(.never)
            TextField("LLM Model", text: $settings.llmModel)
                .textInputAutocapitalization(.never)
        }

        Section("润色策略") {
            Toggle("自动润色", isOn: $settings.autoRewrite)
            Picker("润色时机", selection: $settings.rewriteMode) {
                Text("实时润色").tag(RewriteMode.realtime)
                Text("停止后润色").tag(RewriteMode.afterStop)
            }
            Picker("润色强度", selection: $settings.rewriteStrength) {
                Text("轻").tag(RewriteStrength.light)
                Text("中").tag(RewriteStrength.medium)
                Text("强").tag(RewriteStrength.strong)
            }
        }

        Section("输入行为") {
            Toggle("自动写入输入框", isOn: $settings.autoInsert)
            Toggle("覆盖原输入", isOn: $settings.overwriteInput)
            HStack {
                Text("写入延迟")
                Spacer()
                Text("\(settings.insertDelay, specifier: "%.1f") 秒")
            }
            Slider(value: $settings.insertDelay, in: 0...2, step: 0.1)

            HStack {
                Text("自动停止延迟")
                Spacer()
                Text("\(settings.autoStopDelay, specifier: "%.1f") 秒")
            }
            Slider(value: $settings.autoStopDelay, in: 0...10, step: 0.5)
        }

        Section {
            Button("保存设置") {
                onSave(settings)
            }
        }
    }
}
