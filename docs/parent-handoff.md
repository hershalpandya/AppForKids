# From a worksheet to the family tablet

Use this guide to make a game from schoolwork, review it on your computer and install a signed update on the Android tablet. For a practice run, use the two invented pages and follow the sample review and emulator rehearsal. [Sample review](samples/parent-handoff/review.md) · [Emulator rehearsal](#rehearse-the-signed-update-on-a-clean-emulator)

## Set up the computer once

1. Open the [AppForKids repository](https://github.com/hershalpandya/AppForKids) and clone it to your computer or open your existing checkout. Start a coding-agent session in that folder.
2. Install Python 3, JDK 17 and Android Studio. In Android Studio’s SDK Manager, install **Android SDK Command-line Tools (latest)** and note the **Android SDK Location**. The examples below use Bash. Run `bash` if your terminal uses another shell, and run the commands from the AppForKids folder. [Android Studio setup](https://developer.android.com/studio/install)
3. Set `JAVA_HOME` to JDK 17 and `ANDROID_HOME` to your SDK location. The paths below are the macOS example. Reuse these settings when you open a new terminal.

```bash
export JAVA_HOME="$(/usr/libexec/java_home -v 17)"
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager "platforms;android-35" "build-tools;35.0.0" "platform-tools"
sdkmanager --licenses
```

4. In Android Studio’s **Device Manager**, create and start a Pixel Tablet virtual device with an API 35 image for your computer’s processor. Wait for its home screen. Run `adb devices` and find the emulator serial, such as `emulator-5554`. Before running the preview commands, set `ANDROID_SERIAL` with `export ANDROID_SERIAL=emulator-5554`, using your emulator’s serial. [Android virtual device setup](https://developer.android.com/studio/run/managing-avds)

## Prepare the worksheets and ask for a draft

Photograph the pages in order or scan them to a PDF. Make working copies and crop or permanently cover children’s names, school identifiers and unrelated handwriting. Open the redacted copies to check them before sharing them with a connected agent. Keep scans, transcriptions, source notes, answer keys and drafts in a private folder outside the checkout, for example `$HOME/AppForKids-private`. Keep real worksheets and review files out of GitHub. Share only the redacted pages or a redacted transcription with the agent, and keep signing keys and passwords out of the chat. For a scan the agent cannot read, type the instructions and describe the diagram using the page and item numbers.

Try this request with the sample [page 1](samples/parent-handoff/worksheet-page-1.png) and [page 2](samples/parent-handoff/worksheet-page-2.png). For your own material, replace P1, the skill and the teaching constraints. For a P3 example with pairs, see the [matching request](p3-worksheet-preview.md#sample-parent-request).

> Use `$worksheet-to-game` to make a short French P1 game from the attached pages. Practise choosing which of two rows has more counters, or whether there are as many in both. Use two questions, a worked example and a helpful retry hint. Use the choices « En haut », « En bas » and « Autant ». Skip exercises that ask the child to draw and give the child time to think.
>
> Tell me what you read with page and item references. Flag missing or conflicting information. Ask me about uncertain items and use the clear ones for the first draft. Give me a playable preview and an answer key for this revision with the diagrams, choices, correct answers and feedback. Save the draft and review in my private worksheet folder. Wait for my approval before including a draft in a release.

Compare the source review with the pages. For the sample, the agent can use page 1 items A and B while it asks about a possible sixth counter on page 2 item C. For your own batch, confirm the exact item and supply the corrected text or diagram. Review the answer key by counting or solving each exercise yourself.

## Play the preview and request changes

Ask the agent to open **Petits Pas · Aperçu** on the emulator and leave the draft at its instructions screen. From the app’s home screen, check for **Aperçu du brouillon** and find the draft by title in the all-games catalogue. Check the year and displayed subject and topics with the [classification contract](classification-contract.md); try the applicable year, subject and topic filters, clear them and check no-match recovery. Raise uncertain labels with the agent. Review legibility and touch targets against the [visual source](proposed-visual-direction.md). Read the example, tap **Jouer** and play every question. Try a wrong answer and retry. Check the feedback against the key. Finish the round, replay and return to the catalogue.

For your own worksheet, set `family_draft` to the path of the private JSON the agent saved. The agent can build and open the preview with these commands. After a correction, set `family_draft` to the revised file and rerun the preview command without `--build`.

```bash
family_draft="/absolute/path/to/your-reviewed-draft.json"
bash scripts/preview-worksheet.sh --build "$family_draft"
```

For the sample, build and open revision 1 on the emulator.

```bash
sample_dir=docs/samples/parent-handoff
bash scripts/preview-worksheet.sh --build "$sample_dir/les-rangees-a-comparer-v1.json"
```

For the sample, play **Les rangées à comparer** under **P1**. The first answers are **En haut** and **Autant**. Then use the correction in the [sample review](samples/parent-handoff/review.md#source-review-and-clarification). The agent keeps the game ID and increases the revision. Open the new preview and compare the updated answer key against the confirmed source. With the preview app installed, reload without `--build`.

```bash
bash scripts/preview-worksheet.sh "$sample_dir/les-rangees-a-comparer-v2.json"
```

In revised question 2, try **Autant**, check the hint « Compte en bas, puis compare avec les 3 d’en haut. » and retry with **En bas**. Play question 1 again and make sure the two questions still form a complete round.

## Validate and approve the exact revision

Use the private JSON you just played as `family_draft`. Set `family_private_dir` to the private folder where you keep family release records and approvals. Use the same approval store for later updates.

```bash
family_private_dir="$HOME/AppForKids-private"
mkdir -p -m 700 "$family_private_dir"
family_store="$family_private_dir/approved"
python3 scripts/release.py validate "$family_draft"
```

If validation fails, give the agent the file, question number and message. Ask it to correct the draft and key, run validation again and reopen the preview before you approve.

Once you approve the answers, feedback, year, resolved classification and playable preview for that revision, run the approval command.

```bash
python3 scripts/release.py approve --store "$family_store" "$family_draft"
```

Confirm the selector printed by the command matches the revision you reviewed and record it with the private answer key. If the agent is running the command for you, name that revision in your approval. Approval saves a snapshot of the exact content. If you change a game after approval, preview it again under a higher revision and approve that revision.

## Set up the signing command

Define this Bash function once per terminal session. Pass the keystore path and alias as its first two arguments. It prompts privately for the PKCS12 password each time it builds.

```bash
build_signed() (
  export APPFORKIDS_KEYSTORE="$1"
  export APPFORKIDS_KEY_ALIAS="$2"
  shift 2
  read -rsp 'Signing key password: ' APPFORKIDS_STORE_PASSWORD || exit 1
  printf '\n'
  export APPFORKIDS_STORE_PASSWORD
  export APPFORKIDS_KEY_PASSWORD="$APPFORKIDS_STORE_PASSWORD"
  python3 scripts/release.py build "$@"
)
```

## Build the family APK

Sign the first family APK and every update with the same original family key. Set `family_keystore` and `family_alias` to your existing key settings. The paths below show the suggested locations for a new setup.

```bash
family_signing_dir="$HOME/AppForKids-signing"
family_keystore="$family_signing_dir/family.p12"
family_alias=appforkids-family
family_apk_dir="$family_private_dir/apks"
```

If you are creating the first family release, create one key outside the checkout.

```bash
mkdir -p -m 700 "$family_signing_dir"
keytool -genkeypair -storetype PKCS12 \
  -keystore "$family_keystore" -alias "$family_alias" \
  -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=AppForKids Family'
```

Back up the family keystore in a second secure location such as an encrypted drive. Store its password separately in a password manager and record the alias. Test the backup with `keytool -list -keystore "/path/to/backup/family.p12" -alias "$family_alias"`. Android uses the signing key to recognise updates. Losing it will prevent in-place updates to releases signed with it. [Android signing guide](https://developer.android.com/studio/publish/app-signing)

If an earlier macOS setup saved the password in Keychain, open **Keychain Access**, select the **login** keychain and look for the generic password item **AppForKids family APK signing**. The Passwords app may omit this item. Enter the password only at the signing prompt.

For a first installation, build the starter APK and install it on the tablet. For an existing installation, use its saved APK as the baseline for the update. [Tablet installation](#transfer-and-install-on-the-tablet)

```bash
build_signed "$family_keystore" "$family_alias" \
  --version-code 1 --output "$family_apk_dir/appforkids-v1.apk"
```

For an update, set `family_previous_apk` to the saved APK currently installed on the tablet and choose a higher Android version code. Replace `family_selector` with the selector printed for your approved family revision. Repeat `--game ID@REVISION` for each other approved game you want to retain. The P1 and P3 starters are included automatically. Selecting an approved correction under the same game ID replaces the old revision in the catalogue. Existing schema 1 approvals remain usable without changing their snapshots: only the exact original starter revisions have mapped labels; other schema 1 games show **À classer**. See the [classification contract](classification-contract.md).

```bash
family_previous_apk="/absolute/path/to/the-installed-family-release.apk"
family_version_code=2
family_selector='your-game-id@revision'
family_update_apk="$family_apk_dir/appforkids-v$family_version_code.apk"
build_signed "$family_keystore" "$family_alias" \
  --store "$family_store" --game "$family_selector" \
  --version-code "$family_version_code" --previous-apk "$family_previous_apk" \
  --output "$family_update_apk"
```

The build checks the Android app ID, signing certificate and version code. Keep the APK for each installed release and record which game revisions it contains. If validation or building fails, keep using the last good APK, fix the error shown in the terminal and build again. To restore earlier content after installing an update, select its earlier approved revisions and build another APK with a version code higher than the installed one.

## Transfer and install on the tablet

1. Connect the unlocked tablet to the computer with a data-capable USB cable. If Android asks what to do with USB, select **File transfer**. With a computer that can browse the tablet, copy the APK to **Downloads**. You can also use a USB-C drive if the tablet supports it.
   If your computer cannot browse the tablet and you have Android platform-tools installed, enable **USB debugging** in Android’s developer options and accept the tablet’s USB debugging prompt. Find the tablet serial in `adb devices` and copy the file with `adb -s TABLET_SERIAL push "$family_update_apk" /sdcard/Download/`. Substitute your tablet serial and, for a first installation, use the path to the starter APK. Turn USB debugging off after the transfer. [Android device connection](https://developer.android.com/studio/run/device)
2. On the tablet, open **Files** and tap the APK. If prompted, open **Settings** from the prompt and enable **Allow from this source** for the app opening the file. Return to the installer. Tap **Install** for a first installation or accept the update over the existing **Petits Pas**. Afterwards turn off the permission for the file-opening app.
3. If Android refuses an update, check that the existing app is the family build and that both APKs have the same signing key. Check that the new version code exceeds the installed version and that the transferred file is complete. Keep the existing installation while you correct the problem. Build against the installed APK again and transfer the corrected result.

## Check the physical tablet in airplane mode

For a first setup, install the family baseline from Files and open both starters before installing the update. Keep the app installed when you open the update APK. Use the original family key for both APKs, including when checking the sample on the physical tablet.

After the update, turn on airplane mode and make sure Wi-Fi is off. Close and reopen **Petits Pas**. Select a child, or use **Ajouter un enfant** and the parent check to create a local profile first. The separate worksheet preview does not use profiles. Check that the new activity card appears once under its intended year and play it to the end with the approved answer key. For the sample, open **Les rangées à comparer** under **P1** and answer **En haut** then **En bas**. Play **Les étoiles à compter** through one round. Clear or change the year filter to **P3** and play **Les mots de même sens** through one round. Try a mistake and retry in each starter. If you selected other approved activities to retain, check that each appears under its year and opens offline. Check that the text and buttons are comfortable to use on the actual tablet.

### Physical tablet verification record

On 2026-11-27, a Samsung SM-T500 running Android 12 installed the original family APK at version code 1 and opened **Les étoiles à compter**. The family-signed version 2 installed over it, and Android reported the same first installation time. In airplane mode with Wi-Fi off, **Les rangées à comparer** and **Les étoiles à compter** completed under **P1**, and **Les mots de même sens** completed under **P3**. The check exercised wrong answers and retry feedback in all three games.

On this Samsung tablet, **File transfer** let the Mac see the device. ADB also needed **USB debugging** in Developer options and approval of the USB prompt. The streamed ADB install timed out. Copying the APK to the tablet before invoking the package installer worked for the first install and update. With the tablet authorized over USB, the update command was:

```bash
adb -s TABLET_SERIAL push "$family_update_apk" /data/local/tmp/appforkids-update.apk
adb -s TABLET_SERIAL shell pm install --user 0 -r /data/local/tmp/appforkids-update.apk
adb -s TABLET_SERIAL shell rm /data/local/tmp/appforkids-update.apk
```

Replace `TABLET_SERIAL` with the serial from `adb devices`. The first install used the original APK and omitted `-r`. For future checks, record the tablet model, Android version, APK version codes, game titles by year, offline result and any device-specific steps. [Samsung Developer options instructions](https://www.samsung.com/uk/support/mobile-devices/how-do-i-turn-on-developer-options-menu-on-my-samsung-galaxy-device/) · [Handoff ticket](https://github.com/hershalpandya/AppForKids/issues/6) · [Android APK testing notes](wiki/android-apk-testing.md)

## Rehearse the signed update on a clean emulator

Use a clean emulator and the throwaway key below for this rehearsal. After playing sample revision 2, define the [signing command](#set-up-the-signing-command) and create a temporary folder for the sample draft, its approvals, key and APKs.

```bash
rehearsal_dir="$(mktemp -d)"
rehearsal_draft="$rehearsal_dir/les-rangees-a-comparer-v2.json"
rehearsal_store="$rehearsal_dir/approved"
rehearsal_selector=les-rangees-a-comparer@2
rehearsal_keystore="$rehearsal_dir/rehearsal.p12"
rehearsal_alias=appforkids-rehearsal
cp docs/samples/parent-handoff/les-rangees-a-comparer-v2.json "$rehearsal_draft"
```

To practise fixing a validation failure, run this optional block. The final command should fail and report `question 2.answer: must match one of the choices exactly`.

```bash
broken_draft="$rehearsal_dir/invalid-draft.json"
python3 - "$rehearsal_draft" "$broken_draft" <<'PYTHON'
import json
import sys
from pathlib import Path

game = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
game["questions"][1]["answer"] = "En dessous"
Path(sys.argv[2]).write_text(json.dumps(game, ensure_ascii=False), encoding="utf-8")
PYTHON
python3 scripts/release.py validate "$broken_draft"
```

Validate the reviewed sample, approve `les-rangees-a-comparer@2` and build both APKs with the rehearsal key.

```bash
python3 scripts/release.py validate "$rehearsal_draft"
python3 scripts/release.py approve --store "$rehearsal_store" "$rehearsal_draft"
keytool -genkeypair -storetype PKCS12 \
  -keystore "$rehearsal_keystore" -alias "$rehearsal_alias" \
  -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=AppForKids Rehearsal'
build_signed "$rehearsal_keystore" "$rehearsal_alias" \
  --version-code 1 --output "$rehearsal_dir/appforkids-v1.apk"
build_signed "$rehearsal_keystore" "$rehearsal_alias" \
  --store "$rehearsal_store" --game "$rehearsal_selector" \
  --version-code 2 --previous-apk "$rehearsal_dir/appforkids-v1.apk" \
  --output "$rehearsal_dir/appforkids-v2.apk"
```

Use `adb devices` to find the clean emulator’s serial, such as `emulator-5554`, and substitute it for `EMULATOR_SERIAL` in both commands. Install the baseline on that emulator.

```bash
adb -s EMULATOR_SERIAL install "$rehearsal_dir/appforkids-v1.apk"
```

Turn on airplane mode and make sure Wi-Fi is off. Open **Petits Pas**, add or select a child, play both starters and confirm the sample card is absent from **P1**. Keep the baseline installed and install the update over it while the emulator stays offline.

```bash
adb -s EMULATOR_SERIAL install -r "$rehearsal_dir/appforkids-v2.apk"
```

Reopen **Petits Pas** while offline and select a child. Confirm that **Les rangées à comparer** appears once under **P1** and play it with **En haut** then **En bas**. Confirm the P1 and P3 starters still open. To practise restoring the starters-only catalogue, build version 3 against version 2 with the rehearsal key and omit the `--game` selection. For the physical tablet, use the family-signed APKs and follow the tablet installation steps above.

## Find CI results and diagnostic files

Open [Android APK smoke test runs](https://github.com/hershalpandya/AppForKids/actions/workflows/android-apk.yml) and select the run for the commit or pull request you are checking. Open the **offline-tablet** job to see build and test status. On a passing run, return to **Summary → Artifacts** for **appforkids-ci-tested-apk** (starter) and **appforkids-ci-tested-update-apk** (in-place update). Each run builds both APKs with the same temporary CI key and exercises its checked-in fixtures in an offline Pixel Tablet emulator. For the family tablet, use the APK built above with your family key.

On a failed run, open the failed step first for its log. In **Summary → Artifacts**, look for **android-failure-diagnostics**. Depending on how far the run got, it can contain SDK and Gradle logs, emulator and install logs, the latest screen and window dump, Android logcat and the lint report. If the run stopped before it produced diagnostic files, use the failed step’s log on the run page. [GitHub artifact downloads](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts) · [Workflow definition](../.github/workflows/android-apk.yml)
