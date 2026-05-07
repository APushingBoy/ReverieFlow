import Foundation
import SwiftUI

@MainActor
final class SharedStore: ObservableObject {
    @Published var settings: ReverieSettings
    @Published var snapshot: PipelineSnapshot

    private let defaults: UserDefaults
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    init() {
        defaults = UserDefaults(suiteName: AppGroup.suiteName) ?? .standard
        settings = Self.loadValue(for: SharedKeys.settings, defaults: defaults) ?? ReverieSettings()
        snapshot = Self.loadValue(for: SharedKeys.pipelineSnapshot, defaults: defaults) ?? PipelineSnapshot()
    }

    func saveSettings(_ settings: ReverieSettings) {
        self.settings = settings
        persist(settings, key: SharedKeys.settings)
    }

    func saveSnapshot(_ snapshot: PipelineSnapshot) {
        self.snapshot = snapshot
        persist(snapshot, key: SharedKeys.pipelineSnapshot)
    }

    func reload() {
        settings = Self.loadValue(for: SharedKeys.settings, defaults: defaults) ?? settings
        snapshot = Self.loadValue(for: SharedKeys.pipelineSnapshot, defaults: defaults) ?? snapshot
    }

    private func persist<T: Encodable>(_ value: T, key: String) {
        guard let data = try? encoder.encode(value) else { return }
        defaults.set(data, forKey: key)
    }

    private static func loadValue<T: Decodable>(for key: String, defaults: UserDefaults) -> T? {
        guard let data = defaults.data(forKey: key) else { return nil }
        return try? JSONDecoder().decode(T.self, from: data)
    }
}
