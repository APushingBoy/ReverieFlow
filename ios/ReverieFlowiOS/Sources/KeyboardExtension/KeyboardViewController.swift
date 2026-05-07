import UIKit
import SwiftUI

final class KeyboardViewController: UIInputViewController {
    private let viewModel = KeyboardViewModel()

    override func viewDidLoad() {
        super.viewDidLoad()

        let rootView = KeyboardRootView(viewModel: viewModel)
        let host = UIHostingController(rootView: rootView)

        addChild(host)
        host.view.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(host.view)

        NSLayoutConstraint.activate([
            host.view.topAnchor.constraint(equalTo: view.topAnchor),
            host.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            host.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            host.view.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])

        host.didMove(toParent: self)

        viewModel.attach(
            insertText: { [weak self] text in
                self?.insertPolishedText(text)
            },
            requestMicPermission: { [weak self] in
                self?.openHostAppForPermission()
            }
        )
    }

    private func insertPolishedText(_ text: String) {
        guard !text.isEmpty else { return }
        if viewModel.settings.overwriteInput {
            textDocumentProxy.deleteBackward()
        }
        textDocumentProxy.insertText(text)
    }

    private func openHostAppForPermission() {
        guard let url = URL(string: AppGroup.commandURLScheme) else { return }
        let selector = NSSelectorFromString("openURL:")
        var responder: UIResponder? = self
        while responder != nil {
            if let responder, responder.responds(to: selector) {
                responder.perform(selector, with: url)
                return
            }
            responder = responder?.next
        }
    }
}
