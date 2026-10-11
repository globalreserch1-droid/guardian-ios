import UIKit

/// THE BLANKET — Guardian Protection (iOS).
///
/// A full-screen native wrapper around the bundled Guardian web app
/// (www/index.html). Mirrors the Android wrapper: real iOS runtime
/// permissions, real phone GPS wired into the WebView, native handling of
/// tel:/mailto:/sms: links, a native print bridge for the wallet card,
/// shield icon and launch screen.
///
/// What this wrapper deliberately does NOT do:
///  - No self-updater. Apple forbids sideloaded updates; iOS updates ship
///    via TestFlight. The web app's update banner is intercepted natively
///    and explained (see ViewController).
///  - No App Store / TestFlight submission from this project: that needs
///    Eli's paid Apple Developer membership (not present at build time).
@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    var window: UIWindow?

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        let window = UIWindow(frame: UIScreen.main.bounds)
        window.rootViewController = ViewController()
        window.backgroundColor = UIColor(red: 0.039, green: 0.086, blue: 0.157, alpha: 1.0)
        window.makeKeyAndVisible()
        self.window = window
        return true
    }
}
