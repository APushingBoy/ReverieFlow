import SwiftUI

@main
struct ReverieFlowApp: App {
    @StateObject private var store = SharedStore()

    var body: some Scene {
        WindowGroup {
            MainAppView()
                .environmentObject(store)
                .onOpenURL { url in
                    guard url.absoluteString == AppGroup.commandURLScheme else { return }
                    Task {
                        await PermissionCenter.requestMicrophonePermissionIfNeeded()
                    }
                }
        }
    }
}
