# From a worksheet to the family tablet

Use this guide to make a game from schoolwork, review it on your computer and install a signed update on the Android tablet. For a practice run, use the two invented pages and follow the [sample review](samples/parent-handoff/review.md). Use a clean emulator and a throwaway signing key for that rehearsal.

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

4. In Android Studio’s **Device Manager**, create and start a Pixel Tablet virtual device with an API 35 image for your computer’s processor. Wait for its home screen. If `adb devices` lists multiple devices, set `ANDROID_SERIAL` to the serial of your emulator. Use the emulator for reviewing drafts. [Android virtual device setup](https://developer.android.com/studio/run/managing-avds)

## Prepare the worksheets and ask for a draft

Photograph the pages in order or scan them to a PDF. Make working copies and crop or permanently cover children’s names, school identifiers and unrelated handwriting. Open the redacted copies to check them before sharing them with a connected agent. Keep scans, transcriptions, source notes, answer keys and drafts in a private folder outside the checkout, for example `$HOME/AppForKids-private`. Keep real worksheets and review files out of GitHub. Share only the redacted pages or a redacted transcription with the agent, and keep signing keys and passwords out of the chat. For a scan the agent cannot read, type the instructions and describe the diagram using the page and item numbers.

Try this request with the sample [page 1](samples/parent-handoff/worksheet-page-1.png) and [page 2](samples/parent-handoff/worksheet-page-2.png). For your own material, replace P1, the skill and the teaching constraints. For a P3 example with pairs, see the [matching request](p3-worksheet-preview.md#sample-parent-request).

> Use `$worksheet-to-game` to make a short French P1 game from the attached pages. Practise choosing which of two rows has more counters, or whether there are as many in both. Use two questions, a worked example and a helpful retry hint. Use the choices « En haut », « En bas » and « Autant ». Skip exercises that ask the child to draw and give the child time to think.
>
> Tell me what you read with page and item references. Flag missing or conflicting information. Ask me about uncertain items and use the clear ones for the first draft. Give me a playable preview and an answer key for this revision with the diagrams, choices, correct answers and feedback. Save the draft and review in my private worksheet folder. Wait for my approval before including a draft in a release.

Compare the source review with the pages. For the sample, the agent can use page 1 items A and B while it asks about a possible sixth counter on page 2 item C. For your own batch, confirm the exact item and supply the corrected text or diagram. Review the answer key by counting or solving each exercise yourself.

## Play the preview and request changes

Ask the agent to open **AppForKids · Aperçu** on the emulator and leave the draft at its instructions screen. From the app’s home screen, check for **Aperçu du brouillon**, choose the target year and open the draft by title. Read the example, tap **Jouer** and play every question. Try a wrong answer and retry. Check the feedback against the key. Finish the round, replay and return to the catalogue.

The agent can build and open the preview with the following command. Point it at the private JSON for your own worksheet.

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

For your own worksheet, set `draft` to the private JSON you just played. Set up a separate approval store for the rehearsal so it stays apart from family releases.

```bash
private_dir="$HOME/AppForKids-private"
# For a rehearsal, instead use: private_dir="$(mktemp -d)"
mkdir -p -m 700 "$private_dir"
draft="$sample_dir/les-rangees-a-comparer-v2.json"
python3 scripts/release.py validate "$draft"
```

You can practise fixing a validation failure using this private copy of the sample. The command should print `question 2.answer: must match one of the choices exactly` and stop.

```bash
broken_draft="$(mktemp "$private_dir/invalid-draft.XXXXXX")"
python3 - "$draft" "$broken_draft" <<'PY'
import json
import sys
from pathlib import Path

game = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
game["questions"][1]["answer"] = "En dessous"
Path(sys.argv[2]).write_text(json.dumps(game, ensure_ascii=False), encoding="utf-8")
PY
python3 scripts/release.py validate "$broken_draft"
```

For an actual failure, give the agent the file, question number and message. Ask it to correct the draft and key, run validation again and reopen the preview before you approve. For the rehearsal, the reviewed `$draft` already has the corrected answer, **En bas**. Retry with that file.

```bash
python3 scripts/release.py validate "$draft"
python3 scripts/release.py approve --store "$private_dir/approved" "$draft"
```

Confirm the selector matches the draft you reviewed and record it with the private answer key. If the agent is running the approval command for you, name the revision in your approval, for example “I approve `les-rangees-a-comparer@2` for release.” Approval saves a snapshot of the exact content. If you change a game after approval, preview it again under a higher revision and approve that revision.

## Sign and build the APK

Use the original family key for every family update. On the first build, create one key outside the checkout. The rehearsal gets its own key in its temporary private folder.

```bash
signing_dir="$HOME/AppForKids-signing"
# For a rehearsal, instead use: signing_dir="$private_dir/signing"
key_alias=appforkids-family
mkdir -p -m 700 "$signing_dir"
keytool -genkeypair -storetype PKCS12 \
  -keystore "$signing_dir/family.p12" -alias "$key_alias" \
  -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=AppForKids Family'
```

For the family key, back up `family.p12` in a second secure location such as an encrypted drive. Store the password separately in a password manager and record the alias. Test the backup with `keytool -list -keystore "/path/to/backup/family.p12" -alias appforkids-family`. Android uses the signing key to recognise updates. Losing it will prevent in-place updates to releases signed with it. [Android signing guide](https://developer.android.com/studio/publish/app-signing)

Set `signing_dir` and `key_alias` to your existing key settings when you return for an update. Define this Bash function once per terminal session. It prompts privately for the PKCS12 password each time it builds.

```bash
build_signed() (
  export APPFORKIDS_KEYSTORE="$signing_dir/family.p12"
  export APPFORKIDS_KEY_ALIAS="$key_alias"
  read -rsp 'Signing key password: ' APPFORKIDS_STORE_PASSWORD || exit 1
  printf '\n'
  export APPFORKIDS_STORE_PASSWORD
  export APPFORKIDS_KEY_PASSWORD="$APPFORKIDS_STORE_PASSWORD"
  python3 scripts/release.py build "$@"
)
apk_dir="$private_dir/apks"
```

For a first installation, build the starter APK and [install it](#transfer-and-install-on-the-tablet). If the family app is already installed, use its saved APK as the baseline for the update.

```bash
build_signed --version-code 1 --output "$apk_dir/appforkids-v1.apk"
```

For an update, use a higher Android version code and pass the APK currently installed to `--previous-apk`. The build checks the Android app ID, signing certificate and version code. Replace the sample selector with your own approval and repeat `--game ID@REVISION` for each other approved game you want to retain. The P1 and P3 starters are included automatically. Selecting an approved correction under the same game ID replaces the old revision in that year.

```bash
build_signed --store "$private_dir/approved" --game les-rangees-a-comparer@2 \
  --version-code 2 --previous-apk "$apk_dir/appforkids-v1.apk" \
  --output "$apk_dir/appforkids-v2.apk"
```

Keep the APK for each installed release and record which game revisions it contains. If validation or building fails, keep using the last good APK, fix the error shown in the terminal and build again. If you need to restore earlier content after installing an update, select its earlier approved revisions and build another APK with a version code higher than the installed one. For example, to restore the sample baseline, build version 3 against the installed version 2 with the same key and no sample game selector.

## Transfer and install on the tablet

1. Connect the unlocked tablet to the computer with a data-capable USB cable. If Android asks what to do with USB, select **File transfer**. With a computer that can browse the tablet, copy the APK to **Downloads**. You can also use a USB-C drive if the tablet supports it.
   If your computer cannot browse the tablet and you have Android platform-tools installed, enable **USB debugging** in Android’s developer options and accept the tablet’s USB debugging prompt. Find the tablet serial in `adb devices` and copy the file with `adb -s TABLET_SERIAL push "$apk_dir/appforkids-v2.apk" /sdcard/Download/`. Substitute your tablet serial and the APK you built. Turn USB debugging off after the transfer. [Android device connection](https://developer.android.com/studio/run/device)
2. On the tablet, open **Files** and tap the APK. If prompted, open **Settings** from the prompt and enable **Allow from this source** for the app opening the file. Return to the installer. Tap **Install** for a first installation or accept the update over the existing **AppForKids**. Afterwards turn off the permission for the file-opening app.
3. If Android refuses an update, check that the existing app is the family build and that both APKs have the same signing key. Check that the new version code exceeds the installed version and that the transferred file is complete. Keep the existing installation while you correct the problem. Build against the installed APK again and transfer the corrected result.

## Check the physical tablet in airplane mode

For the sample, the expected transition is from the starters-only APK to one with **Les rangées à comparer** under **P1**. For a first setup, install the baseline from Files and open both starters before installing the update. Keep the app installed when you open the update APK.

After the update, turn on airplane mode and make sure Wi-Fi is off. Close and reopen **AppForKids**. Check that the new title appears once under its intended year. Play it to the end with the approved answer key. For the sample, under **P1**, answer **En haut** then **En bas**. Play **Les étoiles à compter** through one round. Use **Changer d’année**, choose **P3** and play **Les mots de même sens** through one round. Try a mistake and retry in each starter. Check that the text and buttons are comfortable to use on the actual tablet.

**Physical tablet record for the sample:** Pending access to the family tablet. Record first installation and in-place update separately with the date, tablet model, Android version, both APK version codes, verified titles by year, airplane-mode result and any model-specific USB or installer steps you observed. Add the result to the physical check record in [issue #6](https://github.com/hershalpandya/AppForKids/issues/6). [First installation ticket](https://github.com/hershalpandya/AppForKids/issues/2) · [Android APK testing notes](wiki/android-apk-testing.md)

## Find CI results and diagnostic files

Open [Android APK smoke test runs](https://github.com/hershalpandya/AppForKids/actions/workflows/android-apk.yml) and select the run for the commit or pull request you are checking. Open the **offline-tablet** job to see build and test status. On a passing run, return to **Summary → Artifacts** for **appforkids-ci-tested-apk** (starter) and **appforkids-ci-tested-update-apk** (in-place update). Each run builds both APKs with the same temporary CI key and exercises its checked-in fixtures in an offline Pixel Tablet emulator. For the family tablet, use the APK built above with your family key.

On a failed run, open the failed step first for its log. In **Summary → Artifacts**, look for **android-failure-diagnostics**. Depending on how far the run got, it can contain SDK and Gradle logs, emulator and install logs, the latest screen and window dump, Android logcat and the lint report. If the run stopped before it produced diagnostic files, use the failed step’s log on the run page. [GitHub artifact downloads](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts) · [Workflow definition](../.github/workflows/android-apk.yml)
