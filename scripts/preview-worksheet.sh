#!/usr/bin/env bash
set -euo pipefail

build_preview=false
if [[ ${1:-} == --build ]]; then
    build_preview=true
    shift
fi

if [[ $# != 1 || $1 != *.json || ! -f $1 || ! -r $1 ]]; then
    echo 'Usage: bash scripts/preview-worksheet.sh [--build] /path/to/game-draft.json' >&2
    exit 2
fi

if "$build_preview"; then
    repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
    "$repo/gradlew" -p "$repo" :app:assembleDebug
    adb install -r "$repo/app/build/outputs/apk/debug/app-debug.apk"
fi

package=be.hershalpandya.appforkids.preview
# Move the complete definition into place inside the preview app's private storage.
install_draft='
    mkdir -p files || exit 1
    temporary=$(mktemp files/worksheet-draft.XXXXXX) || exit 1
    if ! cat > "$temporary" || ! mv "$temporary" files/worksheet-draft.json; then
        rm -f "$temporary"
        exit 1
    fi
'
if ! adb shell -T "run-as $package sh -c '$install_draft'" < "$1"; then
    echo 'Could not load the draft. Check the adb device and install the debug APK first.' >&2
    exit 1
fi
adb shell am start -W -S -f 0x10008000 -n "$package/be.hershalpandya.appforkids.MainActivity"
