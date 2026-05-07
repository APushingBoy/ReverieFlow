import Foundation

@MainActor
final class VoicePipelineCoordinator: ObservableObject {
    @Published private(set) var state: InputEngineState = .idle
    @Published private(set) var rawText: String = ""
    @Published private(set) var polishedText: String = ""

    private let audioEngine = AudioCaptureEngine()
    private let asrClient: ASRClientProtocol
    private let rewriteClient: RewriteClientProtocol

    private var finalizedSegments: [String] = []
    private var settings: ReverieSettings = .init()
    private var onFinalOutput: ((String) -> Void)?
    private var snapshotCallback: ((PipelineSnapshot) -> Void)?

    init(
        asrClient: ASRClientProtocol = FunASRWebSocketClient(),
        rewriteClient: RewriteClientProtocol = QwenRewriteClient()
    ) {
        self.asrClient = asrClient
        self.rewriteClient = rewriteClient

        self.asrClient.onPartialText = { [weak self] text in
            Task { @MainActor in
                self?.state = .streamingASR
                self?.rawText = text
                self?.emitSnapshot()
            }
        }

        self.asrClient.onFinalText = { [weak self] text in
            Task { @MainActor in
                self?.appendFinalSegment(text)
            }
        }
    }

    func bindSnapshot(_ callback: @escaping (PipelineSnapshot) -> Void) {
        snapshotCallback = callback
        emitSnapshot()
    }

    func start(settings: ReverieSettings, onFinalOutput: @escaping (String) -> Void) async {
        guard state == .idle else { return }

        self.settings = settings
        self.onFinalOutput = onFinalOutput
        self.finalizedSegments = []
        self.rawText = ""
        self.polishedText = ""

        state = .recording
        emitSnapshot()

        do {
            try await asrClient.connect(settings: settings)
            try audioEngine.start { [weak self] chunk in
                guard let self else { return }
                Task {
                    try? await self.asrClient.sendAudioChunk(chunk)
                }
            }
        } catch {
            state = .idle
            emitSnapshot()
        }
    }

    func stop() async {
        guard state != .idle else { return }

        state = .finalizing
        emitSnapshot()

        audioEngine.stop()
        await asrClient.finish()

        let fullRaw = finalizedSegments.joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines)
        rawText = fullRaw

        if settings.autoRewrite {
            state = .streamingRewrite
            emitSnapshot()
            polishedText = (try? await rewriteClient.rewrite(text: fullRaw, settings: settings)) ?? fullRaw
        } else {
            polishedText = fullRaw
        }

        state = .insertText
        emitSnapshot()

        if settings.autoInsert {
            let output = polishedText
            if settings.insertDelay > 0 {
                try? await Task.sleep(for: .seconds(settings.insertDelay))
            }
            onFinalOutput?(output)
        }

        state = .idle
        emitSnapshot()
    }

    func rewriteNow() async {
        guard !rawText.isEmpty else { return }
        state = .streamingRewrite
        emitSnapshot()
        polishedText = (try? await rewriteClient.rewrite(text: rawText, settings: settings)) ?? rawText
        state = .recording
        emitSnapshot()
    }

    private func appendFinalSegment(_ text: String) {
        finalizedSegments.append(text)
        rawText = finalizedSegments.joined(separator: " ")
        emitSnapshot()

        guard settings.autoRewrite, settings.rewriteMode == .realtime else { return }

        Task {
            state = .streamingRewrite
            emitSnapshot()
            polishedText = (try? await rewriteClient.rewrite(text: rawText, settings: settings)) ?? rawText
            state = .recording
            emitSnapshot()
        }
    }

    private func emitSnapshot() {
        snapshotCallback?(PipelineSnapshot(
            state: state,
            rawText: rawText,
            polishedText: polishedText,
            updatedAt: .now
        ))
    }
}
