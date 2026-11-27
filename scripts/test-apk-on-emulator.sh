#!/usr/bin/env bash
set -euo pipefail

apk=${1:?Usage: test-apk-on-emulator.sh APK}
reports=build/ci
avd=appforkids-tablet
image=${ANDROID_TABLET_IMAGE:?Set ANDROID_TABLET_IMAGE to the installed system image}
emulator="${ANDROID_HOME:?Set ANDROID_HOME}/emulator/emulator"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
export ANDROID_SERIAL=emulator-5554

mkdir -p "$reports"
adb start-server
avdmanager create avd --force --name "$avd" --package "$image" --device pixel_tablet \
    <<< 'no' > "$reports/avd.log" 2>&1

"$emulator" -avd "$avd" -port 5554 -accel on -no-window -gpu swiftshader_indirect \
    -no-snapshot -no-audio -no-boot-anim > "$reports/emulator.log" 2>&1 &
emulator_pid=$!

finish() {
    result=$?
    if (( result != 0 )); then
        timeout 15s adb logcat -d > "$reports/logcat.txt" 2>&1 || true
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
adb shell cmd connectivity airplane-mode enable
adb shell svc wifi disable
adb shell svc data disable
adb install "$apk" 2>&1 | tee "$reports/install.log"
python3 scripts/smoke_test.py "$reports"
