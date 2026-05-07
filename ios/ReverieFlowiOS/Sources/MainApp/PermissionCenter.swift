import AVFoundation

enum PermissionCenter {
    static func microphoneAuthorized() -> Bool {
        AVAudioSession.sharedInstance().recordPermission == .granted
    }

    @discardableResult
    static func requestMicrophonePermissionIfNeeded() async -> Bool {
        let session = AVAudioSession.sharedInstance()
        let permission = session.recordPermission

        if permission == .granted {
            return true
        }

        if permission == .denied {
            return false
        }

        return await withCheckedContinuation { continuation in
            session.requestRecordPermission { granted in
                continuation.resume(returning: granted)
            }
        }
    }
}
