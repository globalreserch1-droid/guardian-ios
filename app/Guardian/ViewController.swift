import UIKit
import WebKit
import CoreLocation
import MessageUI
import UserNotifications

/// THE BLANKET — single-screen WKWebView wrapper.
///
/// Native responsibilities (everything else lives in the bundled web app):
///  - Load www/index.html from the app bundle (API base + version injected
///    at build time by scripts/copy-web-assets.sh).
///  - Inject window.GuardianPrint so the PWA's "Print my wallet card" button
///    uses AirPrint instead of window.print() (a no-op in WKWebView).
///  - Route tel:/mailto:/sms: links out of the WebView:
///      tel:    -> Phone dialer (same as Android ACTION_DIAL).
///      mailto: -> Mail app; iOS pre-fills subject/body from the URL
///                (same as Android).
///      sms:   -> if the URL carries ?body= AND the device can send texts,
///                MFMessageComposeViewController with recipients + body
///                pre-filled (this is how SOS and "send to doctor" work —
///                the user still taps Send, same as Android).
///                iOS URL schemes cannot pre-fill an SMS body, so without
///                the native composer the body would be silently dropped;
///                if there is no body (or no SMS capability) we just open
///                the URL and let the system Messages app handle it.
///  - Intercept .apk download attempts (the web app's Android self-updater
///    fallback) and explain that iPhone updates come through TestFlight.
///    The GuardianUpdater bridge is deliberately NOT provided on iOS —
///    Apple forbids sideloaded updates.
///  - Request location + notification permissions (notifications reserved
///    for future use; push needs the paid Apple Developer membership).
final class ViewController: UIViewController {

    private var webView: WKWebView!
    private let locationManager = CLLocationManager()
    private var errorView: UIView!

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor(red: 0.039, green: 0.086, blue: 0.157, alpha: 1.0)
        setupErrorView()
        setupWebView()
        requestAppPermissions()
        loadApp()
    }

    // MARK: - WebView

    private func setupWebView() {
        let config = WKWebViewConfiguration()
        config.preferences.javaScriptEnabled = true
        // Default data store: localStorage persists (Guardian number, health).
        config.websiteDataStore = .default()

        // Bridge for the PWA's wallet-card print button. The page checks
        // `typeof window.GuardianPrint.printCard === "function"`, so we
        // provide exactly that shape.
        let bridgeJS = """
        window.GuardianPrint = {
          printCard: function(html) {
            window.webkit.messageHandlers.guardianPrint.postMessage(html);
          }
        };
        """
        let script = WKUserScript(source: bridgeJS,
                                  injectionTime: .atDocumentStart,
                                  forMainFrameOnly: true)
        config.userContentController.addUserScript(script)
        config.userContentController.add(self, name: "guardianPrint")

        webView = WKWebView(frame: view.bounds, configuration: config)
        webView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        webView.navigationDelegate = self
        webView.uiDelegate = self
        webView.allowsBackForwardNavigationGestures = false
        #if os(iOS)
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        #endif
        view.addSubview(webView)
        view.bringSubviewToFront(errorView)
    }

    private func loadApp() {
        guard let url = Bundle.main.url(forResource: "index",
                                        withExtension: "html",
                                        subdirectory: "www") else {
            showError()
            return
        }
        // Allow the page to read its sibling assets (sw.js, icon.svg…).
        webView.loadFileURL(url,
                            allowingReadAccessTo: url.deletingLastPathComponent())
    }

    // MARK: - Permissions

    private func requestAppPermissions() {
        if CLLocationManager.locationServicesEnabled() {
            locationManager.requestWhenInUseAuthorization()
        }
        UNUserNotificationCenter.current().requestAuthorization(
            options: [.alert, .sound, .badge]) { _, _ in }
    }

    // MARK: - Error view (mirrors Android's retry screen)

    private func setupErrorView() {
        let container = UIView(frame: view.bounds)
        container.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        container.backgroundColor = UIColor(red: 0.039, green: 0.086, blue: 0.157, alpha: 1.0)
        container.isHidden = true

        let title = UILabel()
        title.text = "Couldn't load Guardian"
        title.textColor = .white
        title.font = .boldSystemFont(ofSize: 22)
        title.textAlignment = .center
        title.translatesAutoresizingMaskIntoConstraints = false

        let retry = UIButton(type: .system)
        retry.setTitle("Try again", for: .normal)
        retry.titleLabel?.font = .boldSystemFont(ofSize: 18)
        retry.setTitleColor(UIColor(red: 0.039, green: 0.086, blue: 0.157, alpha: 1.0), for: .normal)
        retry.backgroundColor = UIColor(red: 0.0, green: 0.898, blue: 0.628, alpha: 1.0)
        retry.layer.cornerRadius = 12
        retry.translatesAutoresizingMaskIntoConstraints = false
        retry.addTarget(self, action: #selector(retryLoad), for: .touchUpInside)

        container.addSubview(title)
        container.addSubview(retry)
        NSLayoutConstraint.activate([
            title.centerXAnchor.constraint(equalTo: container.centerXAnchor),
            title.centerYAnchor.constraint(equalTo: container.centerYAnchor, constant: -30),
            retry.centerXAnchor.constraint(equalTo: container.centerXAnchor),
            retry.topAnchor.constraint(equalTo: title.bottomAnchor, constant: 24),
            retry.widthAnchor.constraint(equalToConstant: 180),
            retry.heightAnchor.constraint(equalToConstant: 52),
        ])
        view.addSubview(container)
        errorView = container
    }

    private func showError() { errorView.isHidden = false }
    private func hideError() { errorView.isHidden = true }

    @objc private func retryLoad() {
        hideError()
        webView.reload()
    }

    // MARK: - URL routing

    private func handleSMS(url: URL) {
        // PWA format: sms:<digits-or-empty>?body=<url-encoded>
        // (also tolerates &body=).
        var rest = url.absoluteString
        for prefix in ["sms:", "smsto:"] where rest.lowercased().hasPrefix(prefix) {
            rest = String(rest.dropFirst(prefix.count))
            break
        }
        var target = rest
        var body: String? = nil
        if let r = rest.range(of: "?body=") {
            target = String(rest[..<r.lowerBound])
            body = String(rest[r.upperBound...]).removingPercentEncoding
        } else if let r = rest.range(of: "&body=") {
            target = String(rest[..<r.lowerBound])
            body = String(rest[r.upperBound...]).removingPercentEncoding
        }

        if let body = body, MFMessageComposeViewController.canSendText() {
            let composer = MFMessageComposeViewController()
            composer.messageComposeDelegate = self
            if !target.isEmpty { composer.recipients = [target] }
            composer.body = body
            present(composer, animated: true)
        } else {
            // No body to pre-fill, or the device can't send texts:
            // hand the URL to the system Messages app.
            UIApplication.shared.open(url, options: [:])
        }
    }

    private func showTestFlightNotice() {
        let alert = UIAlertController(
            title: "Updates on iPhone",
            message: "New Guardian versions for iPhone come through TestFlight, not downloads. Ask Eli for your TestFlight invite.",
            preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    // MARK: - Printing (AirPrint wallet card)

    private func printCard(html: String) {
        let formatter = UIMarkupTextPrintFormatter(markupText: html)
        formatter.perPageContentInsets = UIEdgeInsets(top: 36, left: 36, bottom: 36, right: 36)
        let controller = UIPrintInteractionController.shared
        controller.printFormatter = formatter
        controller.showsNumberOfCopies = false
        let done: UIPrintInteractionController.CompletionHandler = { _, _, _ in }
        if traitCollection.userInterfaceIdiom == .pad {
            controller.present(from: view.bounds, in: view, animated: true, completionHandler: done)
        } else {
            controller.present(animated: true, completionHandler: done)
        }
    }
}

// MARK: - WKNavigationDelegate

extension ViewController: WKNavigationDelegate {

    func webView(_ webView: WKWebView,
                 decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url else {
            decisionHandler(.cancel); return
        }
        let scheme = (url.scheme ?? "").lowercased()

        switch scheme {
        case "tel", "mailto":
            // iOS pre-fills mailto subject/body natively (same as Android).
            UIApplication.shared.open(url, options: [:])
            decisionHandler(.cancel)
        case "sms", "smsto":
            handleSMS(url: url)
            decisionHandler(.cancel)
        case "http", "https":
            if url.pathExtension.lowercased() == "apk" {
                // The web app's Android self-updater fallback. iOS updates
                // ship via TestFlight — say so instead of opening Safari.
                showTestFlightNotice()
                decisionHandler(.cancel)
            } else {
                decisionHandler(.allow)
            }
        case "file":
            decisionHandler(.allow)
        default:
            decisionHandler(.cancel)
        }
    }

    func webView(_ webView: WKWebView,
                 didFailProvisionalNavigation navigation: WKNavigation!,
                 withError error: Error) {
        showError()
    }
}

// MARK: - WKUIDelegate (target=_blank links, e.g. the updater fallback)

extension ViewController: WKUIDelegate {
    func webView(_ webView: WKWebView,
                 createWebViewWith configuration: WKWebViewConfiguration,
                 for navigationAction: WKNavigationAction,
                 windowFeatures: WKWindowFeatures) -> WKWebView? {
        // Open _blank links in this same WebView so the navigation
        // delegate can route them (including the .apk TestFlight notice).
        if navigationAction.targetFrame == nil {
            webView.load(navigationAction.request)
        }
        return nil
    }
}

// MARK: - Script messages (GuardianPrint bridge)

extension ViewController: WKScriptMessageHandler {
    func userContentController(_ userContentController: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard message.name == "guardianPrint",
              let html = message.body as? String else { return }
        DispatchQueue.main.async { [weak self] in
            self?.printCard(html: html)
        }
    }
}

// MARK: - Message composer delegate

extension ViewController: MFMessageComposeViewControllerDelegate {
    func messageComposeViewController(_ controller: MFMessageComposeViewController,
                                      didFinishWith result: MessageComposeResult) {
        controller.dismiss(animated: true)
    }
}
