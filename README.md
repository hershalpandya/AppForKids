# AppForKids

AppForKids débute avec **Les étoiles à compter**, un jeu hors ligne pour les enfants de P1. Le jeu utilise trois exercices originaux de dénombrement. Les questions et les réponses se trouvent dans [la fiche du jeu](app/src/main/assets/games/compter-les-etoiles.json).

## Preview a worksheet game

In Codex, attach redacted worksheet pages and use `$worksheet-to-game` with the year, learning goal and teaching constraints. The agent prepares the draft and opens it on an Android emulator for your review. See the [P1 worksheet workflow](docs/p1-worksheet-preview.md) for a sample request and correction.

## Build the family APK

Install JDK 17 and the Android SDK command-line tools. Set `JAVA_HOME` and `ANDROID_HOME` to their installation directories. From the repository root, install the SDK components and accept the Android SDK licences.

```sh
sdkmanager "platforms;android-35" "build-tools;35.0.0" "platform-tools"
sdkmanager --licenses
```

For the first family release, create a signing key outside the repository. Keep a secure backup of the key and its password. Enter the same password for the store and the key when using PKCS12.

```sh
mkdir -p "$HOME/AppForKids-signing"
keytool -genkeypair -storetype PKCS12 \
  -keystore "$HOME/AppForKids-signing/family.p12" -alias appforkids-family \
  -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=AppForKids Family'
```

Use the same key and app ID for future family releases. Increase `versionCode` in `app/build.gradle` for each update. The following Bash commands prompt for the password and clear it from the shell after the build.

```bash
(
  export APPFORKIDS_KEYSTORE="$HOME/AppForKids-signing/family.p12"
  export APPFORKIDS_KEY_ALIAS=appforkids-family
  read -rsp 'Signing key password: ' APPFORKIDS_STORE_PASSWORD
  printf '\n'
  export APPFORKIDS_STORE_PASSWORD
  export APPFORKIDS_KEY_PASSWORD="$APPFORKIDS_STORE_PASSWORD"
  ./gradlew :app:assembleRelease && \
    "$ANDROID_HOME/build-tools/35.0.0/apksigner" verify --print-certs \
      app/build/outputs/apk/release/app-release.apk
)
```

## Install on the tablet

1. Copy `app/build/outputs/apk/release/app-release.apk` to the tablet and open it with the Files app. If asked, enable **Install unknown apps** for Files, complete the installation and turn that permission off again.
2. Enable airplane mode and check that Wi-Fi is off. Open **AppForKids**, choose **P1**, and open **Les étoiles à compter**.
3. In the first question, try **3**, then **4**. Check the retry hint and the correct answer feedback. Complete the round, replay and return to the catalogue. Check that the text and controls are comfortable to use.
4. Record the successful first install in [issue #2](https://github.com/hershalpandya/AppForKids/issues/2), including the tablet model, Android version and APK version. This check requires the family tablet.

GitHub Actions creates a separate, temporary CI signing key per run. Use the APK from the family build for tablet installations and updates. The CI workflow installs the exact APK it uploads and plays through the P1 round on a headless Pixel Tablet emulator with airplane mode on and Wi-Fi off.
