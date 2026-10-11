# THE BLANKET — Guardian iOS app

Native iOS wrapper around the Guardian web app — the iPhone twin of the
Android APK. One screen, a `WKWebView` loading the bundled PWA
(`www/index.html`), plus the native pieces a web page can't do itself.

**Same credentials, same backend.** The iOS app talks to the exact same
Guardian server (`http://2.25.231.178:8898`) and uses the exact same
Guardian number + access code system. One account works on both phones —
"keep the credentials" is automatic because there is only one backend.

## Project layout

```
guardian-ios/
├── .github/workflows/ios-build.yml  # free cloud build (unsigned IPA)
├── .gitignore
├── pwa/                             # vendored PWA snapshot (for CI)
├── scripts/
│   ├── copy-web-assets.sh           # stages PWA into the app (run first)
│   └── gen-pbxproj.py               # regenerates project.pbxproj
└── app/
    ├── Guardian.xcodeproj/          # incl. shared scheme "Guardian"
    └── Guardian/
        ├── AppDelegate.swift
        ├── ViewController.swift     # WebView + all native bridges
        ├── Info.plist
        ├── Assets.xcassets/         # shield icon set + launch color
        └── www/                     # staged by the script (gitignored)
```

## Building

**Prerequisite:** run the staging script once (and again whenever the PWA
changes) — it copies `~/workspace/guardian-pwa` (or the vendored `pwa/`)
into the app and injects the API base URL + version:

```bash
bash scripts/copy-web-assets.sh
# overrides: API_BASE_URL=… APP_VERSION_CODE=… APP_VERSION=… bash scripts/…
```

**On a Mac with Xcode:** open `app/Guardian.xcodeproj`, pick the
"Guardian" scheme, Run. No signing is configured — Xcode will offer to
sign with your free Apple ID.

**In the cloud (no Mac):** push this folder to a public GitHub repo.
The workflow builds an **unsigned** `.ipa` on `macos-latest` and uploads
it as an artifact. Eli then signs it on his desktop with his free Apple
ID (Sideloadly/AltStore) and installs it on his iPhone/iPad.

## Feature parity: Android vs iOS

| Feature | Android (APK) | iOS (this app) | Notes |
|---|---|---|---|
| Bundled PWA UI (activation, dashboard, Health, Meds, Emergency Tag, wallet card) | ✅ | ✅ | Identical web code, same backend, same Guardian numbers |
| Guardian number + access code login | ✅ | ✅ | Same `http://2.25.231.178:8898` backend |
| Location permission + real phone GPS in the WebView | ✅ | ✅ | iOS: `NSLocationWhenInUseUsageDescription` + `CLLocationManager`; the WebView shows its own one-time location prompt |
| `tel:` links | ✅ opens dialer | ✅ opens dialer | |
| `mailto:` links (SOS email, "send to doctor") | ✅ pre-filled | ✅ pre-filled | iOS Mail handles subject/body natively |
| `sms:` links (SOS text, "send to doctor") | ✅ pre-filled via URL | ✅ pre-filled via **native composer** | iOS URL schemes can't pre-fill SMS bodies, so the app intercepts `sms:` URLs and presents `MFMessageComposeViewController` with recipients + body. No body / no SMS capability → falls back to the system Messages app. User still taps Send (same as Android) |
| Wallet card printing | ✅ Android print framework | ✅ AirPrint | `window.GuardianPrint.printCard(html)` is injected; prints via `UIPrintInteractionController`. No printer? Choose "Save as PDF" |
| Notifications permission | ✅ requested | ✅ requested | Reserved for future use — real push needs the paid Apple Developer membership |
| Self-updater (checks version.json, one-tap APK install) | ✅ | ❌ **not built, on purpose** | Apple forbids sideloaded updates. On iOS the app intercepts `.apk` URLs and explains updates come through TestFlight |
| App icon / splash | ✅ shield | ✅ shield | Full iOS icon set generated from the shield logo; navy launch screen |

## What still needs Eli (none of this is code)

1. **GitHub repo (free).** Push this `guardian-ios` folder to a **public**
   repo so Actions macOS minutes are unlimited. The workflow runs on
   every push to `main`.
2. **Download the unsigned IPA** from the workflow's artifacts.
3. **Sign + install ($0, testing only).** On his desktop: install
   [Sideloadly](https://sideloadly.io) (free), plug in the iPhone/iPad,
   sign in with his **free Apple ID** → THE BLANKET installs. Limits are
   Apple's, not ours: the app stops opening after **7 days** (re-sign,
   ~1 minute) and max **3 sideloaded apps per device**. Good for Eli's
   own testing, not a customer channel.
4. **Apple Developer Program ($99/year) — when he's ready for customers.**
   Enroll with his Apple ID (individual, photo-ID check). Then:
   - **Ad Hoc** (first ~100 pilot customers): register each device UDID,
     distribute a signed `.ipa` from a link, no App Store review.
   - **TestFlight** (up to 10,000 customers): upload the build, invite by
     email/link, ~24h beta review for external testers, never touches
     the public App Store. **This is the real iPhone customer channel.**
5. **TestFlight setup (after #4).** Flip the workflow to sign with his
   certificate (import via GitHub Secrets) and upload to App Store
   Connect — or build once on any borrowed Mac and upload manually.

## Exact next steps (in order)

1. `bash scripts/copy-web-assets.sh` (already done once — re-run after
   any PWA change).
2. Create the public GitHub repo, push `guardian-ios/`.
3. Watch the "iOS build (unsigned)" workflow go green; download
   `Guardian-unsigned-ipa`.
4. Sideloadly + free Apple ID → install on Eli's iPhone/iPad.
5. Test: activation with a real Guardian number, GPS tile, SOS text,
   "send to doctor", wallet-card print.
6. When customer-ready: Apple Developer enrollment → TestFlight.

## Honest limitations (same as Android, plus Apple's)

- The wrapper is a real native app, but scam-call blocking and 24/7
  health monitoring still need genuine native engineering later. On iOS,
  true call screening is off-limits to third-party apps entirely (Apple
  policy, not budget).
- HTTP backend: the app allows cleartext loads (`NSAllowsArbitraryLoads`)
  because the server is plain HTTP on a numeric IP — same tradeoff as
  the Android build. Revisit when the server gets HTTPS.
- No push notifications on the free sideload path (needs the $99/yr
  membership).
