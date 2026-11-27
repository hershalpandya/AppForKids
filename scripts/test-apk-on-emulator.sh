#!/usr/bin/env bash
set -euo pipefail

apk=${1:?Usage: test-apk-on-emulator.sh RELEASE_APK [PREVIEW_APK] [UPDATE_APK]}
preview_apk=${2:-}
update_apk=${3:-}
reports=build/ci
avd=appforkids-tablet
avd_dir="$PWD/build/$avd.avd"
image=${ANDROID_TABLET_IMAGE:?Set ANDROID_TABLET_IMAGE to the installed system image}
emulator="${ANDROID_HOME:?Set ANDROID_HOME}/emulator/emulator"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
export ANDROID_SERIAL=emulator-5554
export ANDROID_AVD_HOME="$PWD/build/avd-home"

mkdir -p "$reports" "$ANDROID_AVD_HOME"
adb start-server
avdmanager create avd --force --name "$avd" --package "$image" --device pixel_tablet \
    --path "$avd_dir" <<< 'no' > "$reports/avd.log" 2>&1

# Leave room for Android's first-boot setup and the installed APK.
config="$avd_dir/config.ini"
sed '/^disk\.dataPartition\.size[[:space:]]*=/d' "$config" > "$config.tmp"
printf 'disk.dataPartition.size=2G\n' >> "$config.tmp"
mv "$config.tmp" "$config"

"$emulator" -avd "$avd" -port 5554 -partition-size 2048 -accel on -no-window -gpu swiftshader \
    -no-snapshot -no-audio -no-boot-anim -no-metrics > "$reports/emulator.log" 2>&1 &
emulator_pid=$!

finish() {
    result=$?
    if (( result != 0 )); then
        timeout 15s adb logcat -d > "$reports/logcat.txt" 2>&1 || true
        timeout 10s adb shell dumpsys connectivity > "$reports/connectivity.txt" 2>&1 || true
        timeout 10s adb shell cmd wifi status > "$reports/wifi-status.txt" 2>&1 || true
        timeout 10s adb exec-out cat /sdcard/appforkids-window.xml > "$reports/last-window.xml" || true
        timeout 10s adb exec-out screencap -p > "$reports/last-screen.png" || true
        tail -n 60 "$reports/emulator.log"
    fi
    kill "$emulator_pid" 2>/dev/null || true
    wait "$emulator_pid" 2>/dev/null || true
}
trap finish EXIT

timeout 8m bash -c '
    until [[ "$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d "\r")" == 1 ]]; do
        kill -0 "$1" || exit 1
        sleep 2
    done
' bash "$emulator_pid"

adb shell input keyevent KEYCODE_WAKEUP
adb shell wm dismiss-keyguard
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
# Android can still initialize its radio services after reporting boot complete.
if ! timeout 90s bash -c '
    stable=0
    while true; do
        airplane=$(adb shell settings get global airplane_mode_on | tr -d "\r")
        wifi=$(adb shell cmd wifi status | tr -d "\r")
        network=$(adb shell dumpsys connectivity | tr -d "\r" | sed -n "/^[[:space:]]*Active default network:/p")
        printf "Airplane mode: %s\n%s\n%s\n" "$airplane" "$wifi" "$network"

        if [[ "$airplane" == 1 && "$wifi" == *"Wifi is disabled"* &&
              "$network" =~ ^[[:space:]]*Active\ default\ network:\ none[[:space:]]*$ ]]; then
            stable=$((stable + 1))
            if (( stable == 2 )); then
                exit 0
            fi
        else
            stable=0
            if [[ "$airplane" != 1 ]]; then
                adb shell cmd connectivity airplane-mode enable
            fi
            if [[ "$wifi" != *"Wifi is disabled"* ]]; then
                adb shell svc wifi disable
            fi
        fi
        sleep 2
    done
' 2>&1 | tee "$reports/offline-setup.log"; then
    echo 'The emulator did not reach a stable offline state.' >&2
    exit 1
fi

adb install "$apk" 2>&1 | tee "$reports/install.log"
# This AVD is disposable. Root access is needed only to seed corrupt private
# preferences, which cannot be produced through the normal release UI.
adb root
adb wait-for-device
python3 scripts/review_regression.py 2>&1 | tee "$reports/review-regression.log"
# The regression fixtures are disposable and must not influence the normal flow.
adb shell pm clear be.hershalpandya.appforkids
python3 scripts/smoke_test.py "$reports"

if [[ -n "$preview_apk" ]]; then
    adb install "$preview_apk" 2>&1 | tee "$reports/preview-install.log"
    python3 scripts/worksheet_smoke_test.py "$apk" 2>&1 | tee "$reports/worksheet-smoke.log"
fi

if [[ -n "$update_apk" ]]; then
    python3 scripts/release_smoke_test.py "$update_apk" 2>&1 | tee "$reports/release-smoke.log"
fi
