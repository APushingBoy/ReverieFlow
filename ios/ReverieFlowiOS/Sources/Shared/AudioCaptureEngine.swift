import AVFoundation

final class AudioCaptureEngine {
    private let engine = AVAudioEngine()
    private(set) var isRunning = false

    func start(onPCMBuffer: @escaping (Data) -> Void) throws {
        guard !isRunning else { return }

        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        inputNode.removeTap(onBus: 0)
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: format) { buffer, _ in
            guard let channelData = buffer.floatChannelData?.pointee else { return }
            let frameLength = Int(buffer.frameLength)
            let pcm = Self.floatToInt16PCM(channelData: channelData, frameLength: frameLength)
            onPCMBuffer(pcm)
        }

        engine.prepare()
        try engine.start()
        isRunning = true
    }

    func stop() {
        guard isRunning else { return }
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
        isRunning = false
    }

    private static func floatToInt16PCM(channelData: UnsafePointer<Float>, frameLength: Int) -> Data {
        var pcm = [Int16](repeating: 0, count: frameLength)
        for index in 0..<frameLength {
            let sample = max(-1.0, min(1.0, channelData[index]))
            pcm[index] = Int16(sample * Float(Int16.max))
        }
        return Data(bytes: pcm, count: pcm.count * MemoryLayout<Int16>.size)
    }
}
