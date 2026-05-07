import SwiftUI

struct KeyboardRootView: View {
    @ObservedObject var viewModel: KeyboardViewModel

    var body: some View {
        HStack(spacing: 8) {
            VStack(alignment: .leading, spacing: 4) {
                Text("Raw ASR")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                ScrollView {
                    Text(viewModel.rawText.isEmpty ? "等待语音输入..." : viewModel.rawText)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .font(.system(size: 13))
                }
            }
            .padding(8)
            .background(Color(.secondarySystemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 8))

            VStack(spacing: 10) {
                Button(action: viewModel.toggleRecording) {
                    Image(systemName: viewModel.state == .idle ? "mic.fill" : "stop.fill")
                        .font(.title2)
                        .foregroundStyle(.white)
                        .frame(width: 44, height: 44)
                        .background(viewModel.state == .idle ? .blue : .red)
                        .clipShape(Circle())
                }

                Button(action: viewModel.rewriteNow) {
                    Image(systemName: "wand.and.stars")
                        .font(.title3)
                        .frame(width: 36, height: 36)
                }
                .buttonStyle(.bordered)

                Text(viewModel.state.rawValue)
                    .font(.caption2)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
            }
            .frame(width: 72)

            VStack(alignment: .leading, spacing: 4) {
                Text("Polished")
                    .font(.caption)
                    .foregroundStyle(.secondary)
                ScrollView {
                    Text(viewModel.polishedText.isEmpty ? "润色结果将在这里显示" : viewModel.polishedText)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .font(.system(size: 13))
                }
            }
            .padding(8)
            .background(Color(.secondarySystemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 8))
        }
        .padding(8)
        .background(Color(.systemBackground))
    }
}
