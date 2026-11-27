# AppForKids

AppForKids propose deux jeux hors ligne. En **P1**, [Les étoiles à compter](app/src/main/assets/games/compter-les-etoiles.json) fait pratiquer le dénombrement. En **P3**, [Les mots de même sens](app/src/main/assets/games/les-mots-de-meme-sens.json) fait associer des synonymes. Utilise **Changer d’année** pour passer d’un catalogue à l’autre.

## Preview a worksheet game

In Codex, attach redacted worksheet pages and use `$worksheet-to-game` with the year, learning goal and teaching constraints. The agent prepares the draft and opens it on an Android emulator for your review. See the [P1 counting workflow](docs/p1-worksheet-preview.md) or [P3 matching workflow](docs/p3-worksheet-preview.md) for a sample request and correction. See the [game mechanics extension guide](docs/game-mechanics.md) for the portable format and how to add an interaction.

## Build the family APK

Install Python 3, JDK 17 and the Android SDK command-line tools. Set `JAVA_HOME` and `ANDROID_HOME` to their installation directories. From the repository root, install the SDK components and accept the Android SDK licences.

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

Use the same key for all family releases. Use a higher Android version code each time you install an update. The following Bash commands prompt for the password and clear it from the shell after the build.

```bash
(
  export APPFORKIDS_KEYSTORE="$HOME/AppForKids-signing/family.p12"
  export APPFORKIDS_KEY_ALIAS=appforkids-family
  read -rsp 'Signing key password: ' APPFORKIDS_STORE_PASSWORD
  printf '\n'
  export APPFORKIDS_STORE_PASSWORD
  export APPFORKIDS_KEY_PASSWORD="$APPFORKIDS_STORE_PASSWORD"
  python3 scripts/release.py build --version-code 1 --output build/releases/appforkids-v1.apk
)
```

## Approve and release a worksheet game

After playing the exact draft you want to release, approve its JSON definition. Keep approvals with your private material outside the checkout. The command prints the selected game ID and revision.

```sh
python3 scripts/release.py approve \
  --store "$HOME/AppForKids-private/approved" "$HOME/AppForKids-private/game-draft.json"
```

Use the signing subshell above and replace its build command with the following example. Substitute the ID and revision printed by the approval command. Repeat `--game` for each approved game you want to keep in the update. The bundled starters are included automatically. Selecting an approved correction under the same ID replaces that entry.

```sh
python3 scripts/release.py build --store "$HOME/AppForKids-private/approved" \
  --game les-jetons-a-reunir@2 --version-code 2 \
  --previous-apk build/releases/appforkids-v1.apk \
  --output build/releases/appforkids-v2.apk
```

Keep each installed APK and its list of game revisions. Pass the installed APK to `--previous-apk` so the command verifies the app ID, signing certificate and increased version before publishing the update. If a draft changes, preview it with a higher game revision before approving it. You can recover by selecting the earlier approved game revision and building with an Android version code higher than the version currently installed. Build failures leave the existing APK at the output path available.

Release validation treats choices that differ only by surrounding whitespace or Unicode composition as duplicates. Enter the answer with exactly the same text as its choice.

## Install on the tablet

1. Copy the signed APK from `build/releases/` to the tablet and open it with the Files app. For an update, keep the existing AppForKids installation and confirm the update when prompted. If asked, enable **Install unknown apps** for Files, complete the installation and turn that permission off again.
2. Enable airplane mode and check that Wi-Fi is off. Open **AppForKids** and choose **P1**.
3. For a first install, open **Les étoiles à compter**. In the first question, try **3**, then **4**. Check the retry hint and the correct answer feedback. Complete the round, replay and return to the catalogue. Tap **Changer d’année**, choose **P3** and open **Les mots de même sens**. Try matching **content** to **débuter**, then to **heureux**, and finish the round. Check that the text and controls are comfortable to use. Record the successful first install in [issue #2](https://github.com/hershalpandya/AppForKids/issues/2), including the tablet model, Android version and APK version.
4. For an update, open each newly approved title and each previously installed title that you included in the update. Tap **Jouer** to check that each opens offline. If the update includes a correction, check that its title appears once in its year’s catalogue and that it opens with the corrected content.

GitHub Actions creates a separate, temporary CI signing key per run. Use the APK from the family build for tablet installations and updates. The CI workflow plays both starters and both worksheet previews, then installs the candidate APK over the baseline. It opens the approved P1 games and the P3 starter on a headless Pixel Tablet emulator with airplane mode on and Wi-Fi off.
