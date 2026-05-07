import Foundation

protocol ASRClientProtocol {
    var onPartialText: ((String) -> Void)? { get set }
    var onFinalText: ((String) -> Void)? { get set }

    func connect(settings: ReverieSettings) async throws
    func sendAudioChunk(_ chunk: Data) async throws
    func finish() async
}

enum ASRError: Error {
    case invalidEndpoint
    case socketClosed
}

final class FunASRWebSocketClient: ASRClientProtocol {
    var onPartialText: ((String) -> Void)?
    var onFinalText: ((String) -> Void)?

    private var task: URLSessionWebSocketTask?

    func connect(settings: ReverieSettings) async throws {
        guard let url = URL(string: settings.asrEndpoint) else {
            throw ASRError.invalidEndpoint
        }

        var request = URLRequest(url: url)
        request.setValue("Bearer \(settings.asrApiKey)", forHTTPHeaderField: "Authorization")

        let session = URLSession(configuration: .default)
        let socket = session.webSocketTask(with: request)
        socket.resume()
        task = socket

        Task { [weak self] in
            await self?.receiveLoop()
        }
    }

    func sendAudioChunk(_ chunk: Data) async throws {
        guard let task else {
            throw ASRError.socketClosed
        }
        try await task.send(.data(chunk))
    }

    func finish() async {
        task?.cancel(with: .normalClosure, reason: nil)
        task = nil
    }

    private func receiveLoop() async {
        guard let task else { return }

        while true {
            do {
                let message = try await task.receive()
                switch message {
                case .string(let text):
                    parseASRMessage(text)
                case .data(let data):
                    if let text = String(data: data, encoding: .utf8) {
                        parseASRMessage(text)
                    }
                @unknown default:
                    break
                }
            } catch {
                break
            }
        }
    }

    private func parseASRMessage(_ text: String) {
        guard let data = text.data(using: .utf8),
              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let payload = json["output"] as? [String: Any],
              let sentence = payload["text"] as? String else {
            return
        }

        let isFinal = (payload["is_final"] as? Bool) ?? false
        if isFinal {
            onFinalText?(sentence)
        } else {
            onPartialText?(sentence)
        }
    }
}
