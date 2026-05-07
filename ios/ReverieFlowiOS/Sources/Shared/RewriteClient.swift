import Foundation

protocol RewriteClientProtocol {
    func rewrite(text: String, settings: ReverieSettings) async throws -> String
}

enum RewriteError: Error {
    case invalidEndpoint
    case invalidResponse
}

final class QwenRewriteClient: RewriteClientProtocol {
    func rewrite(text: String, settings: ReverieSettings) async throws -> String {
        guard let url = URL(string: settings.llmEndpoint) else {
            throw RewriteError.invalidEndpoint
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 20
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(settings.llmApiKey)", forHTTPHeaderField: "Authorization")

        let prompt = "请将以下口语文本润色为书面语，保留原意：\n\(text)"
        let body: [String: Any] = [
            "model": settings.llmModel,
            "input": [
                "messages": [
                    ["role": "system", "content": "你是中文语音转书面语助手。"],
                    ["role": "user", "content": prompt]
                ]
            ],
            "parameters": [
                "temperature": 0.3
            ]
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              (200..<300).contains(httpResponse.statusCode) else {
            throw RewriteError.invalidResponse
        }

        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let output = json["output"] as? [String: Any],
              let choices = output["choices"] as? [[String: Any]],
              let first = choices.first,
              let message = first["message"] as? [String: Any],
              let content = message["content"] as? String else {
            throw RewriteError.invalidResponse
        }

        return content
    }
}
