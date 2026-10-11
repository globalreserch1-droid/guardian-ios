# iPhone/iPad App Without a Mac — Research Report

**Date:** 2026-10-10
**Question:** Cheapest realistic path from "Linux only, no Mac" to "THE BLANKET installed on Eli's iPhone," given his direct-from-website (no App Store) distribution model.

---

## Bottom line

- **Getting THE BLANKET onto Eli's own iPhone/iPad: $0.** A tiny native wrapper app can be written on Linux, built free in the cloud, and installed with his free Apple ID. No Mac ever touches the process.
- **Getting it onto customers' iPhones without the App Store: $99/year** (Apple Developer Program) for Ad Hoc distribution (up to 100 devices/year) or TestFlight (up to 10,000 testers).
- **Hard truth (read this first):** Apple does not allow "download the app from our website" for the general public on iPhone. That model works on Android only. On iOS, every install path runs through Apple: free sideloading (7-day expiry), Ad Hoc (100 devices), TestFlight (10k testers), or the App Store. There is no loophole for mass direct distribution. Enterprise distribution ($299/yr) is not available to a solo LLC — Apple requires 100+ employees.

---

## 1. Can Eli's KV4 VPS build the iPhone app? — Verdict: No

Eli asked whether his Hostinger VPS (KV4, 2.25.231.178) could do the iOS build instead of a paid cloud Mac.

**I could not run the live spec check:** this research environment blocks outbound SSH ("Outbound SSH is turned off for this assistant"), so I couldn't pull the live CPU/RAM readout. But the verdict does not depend on the specs — it fails on three independent grounds that apply to any non-Apple VPS:

1. **Apple's license forbids it.** The macOS license agreement allows macOS to run virtualized **only on Apple-branded hardware**. Running macOS in a VM on Hostinger's Intel/AMD servers violates Apple's terms. No legitimate business should build its product on that.
2. **Technically it won't work reliably.** KV4 is a Linux KVM guest (nested virtualization). A macOS VM needs hardware virtualization passthrough (`/dev/kvm`), which Hostinger VPS plans don't expose, plus a GPU for anything graphical. The "Hackintosh on a VPS" trick is a hobbyist experiment, not a build pipeline — it breaks constantly.
3. **The translation-layer shortcut is a dead end.** Darling (the "Wine for macOS" on Linux) cannot run Xcode, full stop. Xcode is the only tool that compiles iPhone apps.

**Verdict:** KV4 stays as the backend/web server. iPhone builds happen on a real Mac in someone else's cloud — several of which are free.

---

## 2. Cloud Mac build services compared (October 2026)

All of these are usable from Linux (you push code with git, their Macs compile it, you download the `.ipa`).

| Service | Free tier | Paid | Usable from Linux? | Catch |
|---|---|---|---|---|
| **GitHub Actions** (macOS runners) | **Unlimited minutes on public repos**; private repos: 2,000 min/mo Free plan (macOS burns 10×, so ≈200 macOS min) | $0.062/min macOS overage | Yes — everything via git push + web UI | Repo must be public for unlimited free. Fine here: the wrapper is just a web-view shell, no secrets. |
| **Codemagic** | **500 macOS build minutes/month**, single user | $0.04–$0.10/min after | Yes — connect GitHub repo, builds start automatically | Free tier is per-user; generous enough for ~25–50 iOS builds/mo |
| **Expo EAS Build** | **30 builds/mo (max 15 iOS + 15 Android)** | From $19/mo | Yes — `eas-cli` runs on Linux | Only builds Expo/React Native projects — we'd wrap the site in a React Native WebView app |
| **Bitrise** (Hobby) | 300 credits/mo (macOS burns 2 credits/min → ≈150 macOS min) | From $36/mo | Yes | Smaller free allowance than Codemagic |
| **Xcode Cloud** (Apple's own) | 25 compute hrs/mo **included with the $99/yr Apple Developer Program** | Extra hours purchasable | Partial — the one-time workflow setup **must be done in the Xcode app on a Mac** | Dead end for a zero-Mac start; becomes the best option *after* paying Apple |
| **AWS EC2 Mac** | None | ≈$0.67–$1.08/hr **with a 24-hour minimum** (≈$16+ per session) | Yes, but you rent a whole Mac by the day | Absurd for occasional builds |
| **MacStadium** | None (no trial) | $79–$199+/mo for a Mac mini | Yes (remote desktop) | Enterprise-grade, enterprise-priced. Dead end. |

**Winners for Eli:** GitHub Actions (public repo = free forever) or Codemagic (500 free min/mo, simplest setup). Both build a plain native Xcode project — no need to rewrite anything in React Native.

---

## 3. Expo EAS Build — evaluated

EAS *could* work: we'd create a minimal Expo app whose only screen is a WebView loading the Guardian site files, then `eas build --platform ios` from Linux produces a signed-or-unsigned `.ipa` on Expo's cloud Macs. Free tier: 15 iOS builds/month, lower queue priority.

**Why it's plan B, not plan A:** it drags in the entire React Native toolchain for what is really a 100-line native wrapper. A raw Swift + WKWebView Xcode project is smaller, builds faster, and runs on the more generous GitHub/Codemagic free tiers. EAS becomes attractive only if we later want its over-the-air update service.

---

## 4. Getting the app onto iPhones without the App Store

Apple controls every install path. Here are the real ones:

### A. Free Apple ID sideloading — $0 (testing: Eli's own phone/iPad)
- Tools: **Sideloadly** (Windows/Mac desktop + USB cable) or **AltStore/SideStore** (can auto-refresh over Wi-Fi).
- How: build an **unsigned** `.ipa` in the cloud → Eli signs it on his desktop with his free Apple ID → installs on his iPhone/iPad.
- Limits (Apple's, not ours): app **stops opening after 7 days** and must be re-signed (takes ~1 minute); max **3 sideloaded apps per device**.
- Good enough for: Eli testing it himself, showing it to family. Not a customer channel.

### B. Ad Hoc distribution — $99/year Apple Developer Program
- Register each customer's device UDID in Apple's portal (up to **100 devices per device type per year** — slots don't free up if you remove one).
- Build a signed `.ipa` → customers install from a download link. No App Store review. Certificate lasts 1 year.
- Good enough for: first ~100 pilot customers. **Not** a mass channel — and every new customer means collecting their UDID and rebuilding.

### C. TestFlight — $99/year Apple Developer Program
- Upload the build to Apple → invite testers by email/link. Up to **10,000 external testers**, builds work **90 days** then need a rebuild.
- External testers require a light **beta review by Apple (~24 hours)**; internal testers (up to 100) need no review.
- The app **never has to appear on the public App Store**.
- Good enough for: the real customer rollout up to 10,000 users — the most scalable non-App-Store path Apple allows.

### D. Enterprise distribution — DEAD END for Eli
- $299/year, but Apple requires **100+ employees**, a D-U-N-S number, legal-entity verification, and an interview — and the apps may only go to **employees**, never customers. A solo LLC cannot get this, and using it for customers gets the account terminated.

### E. EU alternative app stores — not applicable
- The EU's DMA forced Apple to allow third-party iPhone app stores, but only for users physically in the EU. Eli and his customers are in the US.

---

## 5. Recommended path

### Phase 0 — THE BLANKET on Eli's iPhone: $0
1. **I write the iPhone wrapper** (on Linux, no Mac needed): a minimal native Swift app — one screen, a WKWebView showing the Guardian web files, location permission, shield icon, splash screen. Mirror of what the Android APK does.
2. **Push it to a public GitHub repo** (free account; the code contains no secrets).
3. **GitHub Actions builds it free** on Apple's-cloud Macs → download the unsigned `.ipa`.
4. **Eli installs Sideloadly** (free) on his desktop, plugs in his iPhone/iPad, signs in with his free Apple ID → THE BLANKET installs.
5. Re-sign once a week (~1 minute), or switch to AltStore for automatic Wi-Fi refresh.

**Accounts Eli needs:** GitHub (free), his existing Apple ID (free), Sideloadly (free). Total: **$0**.

### Phase 1 — first customers on iPhone: $99/year
1. Eli enrolls in the **Apple Developer Program** ($99/year, Apple ID + photo-ID verification; an Individual enrollment needs no D-U-N-S).
2. We flip the cloud build to sign with his Apple certificate.
3. Distribute via **Ad Hoc** (first ~100 pilot customers, install from a link, good for a year) and/or **TestFlight** (up to 10,000 customers, 90-day builds, ~24h beta review, never touches the public App Store).

### Phase 2 — if iPhone demand ever outgrows TestFlight
The only mass-market path on iPhone is the public App Store. That decision can wait until the business justifies it — nothing built in Phase 0/1 is wasted, since it's the same app.

---

## 6. Honest limitations to keep in mind

- A WebView wrapper is a **real native app** (icon, splash, GPS permission, installable) but the scam-call blocking and 24/7 background health monitoring Eli advertises still need genuine native iOS engineering later — same caveat as the Android APK.
- iOS WebView apps can't do everything Android can (e.g., true call screening is off-limits to third-party iOS apps entirely — that's an Apple policy wall, not a budget problem).
- Push notifications need the $99/yr program (Apple Push requires a paid membership) — the free sideload path can't do real push.

---

*Sources checked October 2026: GitHub billing docs and community pricing trackers (macOS $0.062/min, 10× multiplier, public repos unlimited); Codemagic pricing (500 free macOS min/mo); Expo pricing (Free: 30 builds/mo, 15 iOS); Bitrise Hobby (300 credits/mo); MacStadium/Vendr ($79–$199+/mo Mac mini); AWS EC2 Mac (~$0.67+/hr, 24-hr minimum); Apple Developer Program ($99/yr) and Enterprise Program (100+ employees, $299/yr) documentation; TestFlight docs (10k external testers, 90-day expiry, beta review); AltStore/Sideloadly community guides (7-day free cert, 3-app limit); Xcode Cloud docs (25 hrs/mo included, first workflow setup requires Xcode GUI).*
