import AVFoundation
import Foundation

@MainActor
final class KeyboardViewModel: ObservableObject {
    @Published var rawText: String = ""
    @Published var polishedText: String = ""
    @Published var state: InputEngineState = .idle

    private let store = SharedStore()
    private let coordinator = VoicePipelineCoordinator()

    private var insertTextAction: ((String) -> Void)?
    private var requestPermissionAction: (() -> Void)?

    var settings: ReverieSettings { store.settings }

    init() {
        coordinator.bindSnapshot { [weak self] snapshot in
            self?.rawText = snapshot.rawText
            self?.polishedText = snapshot.polishedText
            self?.state = snapshot.state
            Task { @MainActor in
                self?.store.saveSnapshot(snapshot)
            }
        }
    }

    func attach(insertText: @escaping (String) -> Void, requestMicPermission: @escaping () -> Void) {
        insertTextAction = insertText
        requestPermissionAction = requestMicPermission
    }

    func toggleRecording() {
        if state == .idle {
            Task {
                await startRecording()
            }
        } else {
            Task {
                await coordinator.stop()
            }
        }
    }

    func rewriteNow() {
        Task {
            await coordinator.rewriteNow()
        }
    }

    private func startRecording() async {
        let permission = AVAudioSession.sharedInstance().recordPermission
        guard permission == .granted else {
            state = .requestMicPermission
            requestPermissionAction?()
            return
        }

        let currentSettings = store.settings
        await coordinator.start(settings: currentSettings) { [weak self] finalText in
            self?.insertTextAction?(finalText)
        }
    }
}
