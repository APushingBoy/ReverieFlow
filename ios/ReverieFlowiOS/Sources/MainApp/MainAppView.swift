import SwiftUI

struct MainAppView: View {
    @EnvironmentObject private var store: SharedStore

    var body: some View {
        NavigationStack {
            Form {
                Section("权限") {
                    HStack {
                        Text("麦克风")
                        Spacer()
                        Text(PermissionCenter.microphoneAuthorized() ? "已授权" : "未授权")
                            .foregroundStyle(PermissionCenter.microphoneAuthorized() ? .green : .orange)
                    }

                    Button("申请麦克风权限") {
                        Task {
                            _ = await PermissionCenter.requestMicrophonePermissionIfNeeded()
                        }
                    }
                }

                Section("输入法扩展") {
                    Text("请在系统设置 > 键盘中启用 ReverieFlow Keyboard，并打开“允许完全访问”。")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                SettingsView(settings: store.settings) { updated in
                    store.saveSettings(updated)
                }

                Section("运行快照") {
                    LabeledContent("状态", value: store.snapshot.state.rawValue)
                    LabeledContent("Raw", value: store.snapshot.rawText)
                    LabeledContent("Polished", value: store.snapshot.polishedText)
                }
            }
            .navigationTitle("ReverieFlow 控制中心")
        }
    }
}
