#!/bin/bash
# Stage the Guardian PWA into the iOS Xcode project, injecting the
# backend API base URL and the app version (same placeholder technique
# as the Android build: __GUARDIAN_API_BASE__, __APP_VERSION_CODE__,
# __APP_VERSION__).
#
# Source priority: live workspace sibling (~/workspace/guardian-pwa)
# for development, then the vendored pwa/ snapshot (used by CI).
# Override with PWA_SRC env var.
set -e

API_BASE_URL="${API_BASE_URL:-http://2.25.231.178:8898}"
APP_VERSION_CODE="${APP_VERSION_CODE:-5}"
APP_VERSION="${APP_VERSION:-1.4}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
IOS_DIR="$(dirname "$SCRIPT_DIR")"

SRC="${PWA_SRC:-}"
if [ -z "$SRC" ]; then
  for c in "$IOS_DIR/../guardian-pwa" "$IOS_DIR/pwa"; do
    if [ -f "$c/index.html" ]; then SRC="$c"; break; fi
  done
fi
[ -n "$SRC" ] || { echo "ERROR: PWA source not found (tried ../guardian-pwa and ./pwa)"; exit 1; }

DEST="$IOS_DIR/app/Guardian/www"
mkdir -p "$DEST"
for f in index.html sw.js icon.svg manifest.json; do
  sed -e "s|__GUARDIAN_API_BASE__|$API_BASE_URL|g" \
      -e "s|__APP_VERSION_CODE__|$APP_VERSION_CODE|g" \
      -e "s|__APP_VERSION__|$APP_VERSION|g" \
      "$SRC/$f" > "$DEST/$f"
done

# Sanity: no placeholders may survive.
if grep -q "__GUARDIAN_API_BASE__\|__APP_VERSION_CODE__\|__APP_VERSION__" "$DEST/index.html"; then
  echo "ERROR: unreplaced placeholder in staged index.html"; exit 1
fi

echo "Staged PWA from $SRC -> $DEST (api=$API_BASE_URL version=$APP_VERSION/$APP_VERSION_CODE)"
