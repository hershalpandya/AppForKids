#!/usr/bin/env bash
# Install the pinned Android command-line tools, SDK packages and tablet image on a CI runner.
set -euo pipefail

image=${ANDROID_TABLET_IMAGE:?Set ANDROID_TABLET_IMAGE to the tablet system image}
mkdir -p build/ci
export ANDROID_HOME="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$RUNNER_TEMP/android-sdk}}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
tools_dir="$ANDROID_HOME/cmdline-tools/latest/bin"
if [[ ! -x "$tools_dir/sdkmanager" || ! -x "$tools_dir/avdmanager" ]]; then
  archive="$RUNNER_TEMP/commandlinetools-linux-11076708_latest.zip"
  curl --fail --silent --show-error --retry 3 --location \
    --output "$archive" "https://dl.google.com/android/repository/${archive##*/}"
  printf '%s  %s\n' \
    '2d2d50857e4eb553af5a6dc3ad507a17adf43d115264b1afc116f95c92e5e258' "$archive" \
    | sha256sum --check
  unpack_dir="$(mktemp -d "$RUNNER_TEMP/android-tools.XXXXXX")"
  unzip -q "$archive" -d "$unpack_dir"
  mkdir -p "$ANDROID_HOME/cmdline-tools/latest"
  cp -R "$unpack_dir/cmdline-tools/." "$ANDROID_HOME/cmdline-tools/latest/"
  # sdkmanager closes its input once it finishes reading licence responses.
  (set +o pipefail; yes | "$tools_dir/sdkmanager" --sdk_root="$ANDROID_HOME" --licenses)
fi
"$tools_dir/sdkmanager" --sdk_root="$ANDROID_HOME" --install \
  "platforms;android-35" "build-tools;35.0.0" "platform-tools" "emulator" "$image" \
  2>&1 | tee build/ci/sdk-install.log
printf 'ANDROID_HOME=%s\nANDROID_SDK_ROOT=%s\n' "$ANDROID_HOME" "$ANDROID_SDK_ROOT" >> "$GITHUB_ENV"
printf '%s\n' "$tools_dir" >> "$GITHUB_PATH"
