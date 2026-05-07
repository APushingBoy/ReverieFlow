import Foundation

enum InputEngineState: String, Codable {
    case idle = "IDLE"
    case requestMicPermission = "REQUEST_MIC_PERMISSION"
    case recording = "RECORDING"
    case streamingASR = "STREAMING_ASR"
    case streamingRewrite = "STREAMING_REWRITE"
    case finalizing = "FINALIZING"
    case insertText = "INSERT_TEXT"
}

enum RewriteMode: String, Codable, CaseIterable {
    case realtime
    case afterStop
}

enum RewriteStrength: String, Codable, CaseIterable {
    case light
    case medium
    case strong
}

struct ReverieSettings: Codable {
    var asrApiKey: String = ""
    var llmApiKey: String = ""
    var asrEndpoint: String = "wss://dashscope.aliyuncs.com/api-ws/v1/inference"
    var llmEndpoint: String = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    var asrModel: String = "fun-asr-realtime"
    var llmModel: String = "qwen-plus"

    var autoRewrite: Bool = true
    var rewriteMode: RewriteMode = .realtime
    var rewriteStrength: RewriteStrength = .medium

    var autoInsert: Bool = true
    var insertDelay: Double = 0.2
    var autoStopDelay: Double = 1.0
    var keepSession: Bool = false
    var overwriteInput: Bool = false
}

struct PipelineSnapshot: Codable {
    var state: InputEngineState = .idle
    var rawText: String = ""
    var polishedText: String = ""
    var updatedAt: Date = .now
}
