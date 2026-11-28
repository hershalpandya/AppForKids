# Android APK testing

On 2026-11-27, the project owner requested automated tests of the built APK in CI. The ticket plan chose a GitHub-hosted Linux runner with hardware acceleration to install and exercise the APK on a headless tablet emulator. The first checks cover an offline P1 round. The upgrade ticket adds an in-place install check with the baseline and candidate APKs. [Starter APK ticket](https://github.com/hershalpandya/AppForKids/issues/2) · [Tablet update ticket](https://github.com/hershalpandya/AppForKids/issues/4)

On 2026-11-27, the ticket plan kept the family release signing key outside CI and retained a physical tablet install and update check. The emulator test APK uses a CI-only signing identity. [Parent handoff ticket](https://github.com/hershalpandya/AppForKids/issues/6)

On 2026-11-27, GitHub Actions failed before the APK build at `hershalpandya/AppForKids@aff39d5` because the job could not find `sdkmanager` on its path. The first run isolated SDK provisioning from any game or APK failure. [First hosted run](https://github.com/hershalpandya/AppForKids/actions/runs/45934762779)

On 2026-11-27, `hershalpandya/AppForKids@7b40796` resolved the SDK tools from the hosted Android SDK directory before installing the tablet image. In local emulator testing, the default Pixel Tablet profile reserved 12 GB for its data partition, and the API 35 image could boot without a phone service. As of `hershalpandya/AppForKids@018ace3`, the CI emulator used a 2 GB data partition and disabled networking via airplane mode and Wi-Fi settings. [Starter PR](https://github.com/hershalpandya/AppForKids/pull/7)

On 2026-11-27, `hershalpandya/AppForKids@77720c0` added CI coverage for installing a baseline and candidate signed with the same temporary key. The candidate’s catalogue was checked for the selected revisions and exercised offline on the same emulator. [P1 approved releases](p1-approved-release.md) · [Implementation PR](https://github.com/hershalpandya/AppForKids/pull/10)

On 2026-11-27, `hershalpandya/AppForKids@c985a51` added an approved P3 correction to the signed in-place update check. The starter check exercised both years offline and the preview check exercised matching round recreation. [P3 matching starter](p3-matching-starter.md)

On 2026-11-27, the family-signed version 2 passed an in-place update on a Samsung SM-T500 running Android 12. An ADB streamed install timed out, and the APK installed after a USB copy to local tablet storage. Both year catalogues were playable in airplane mode with Wi-Fi off. [Parent handoff](parent-handoff.md)

On 2026-11-28, the offline smoke test at `hershalpandya/AppForKids@34bfbc3` reproduced a failed child switch on an isolated tablet emulator. After the completion badge was found, the switch button had clipped bounds `[600,0][1960,62]`; its midpoint was above the app content's top inset at y=48. The same switch opened the chooser after scrolling the button fully into view. The family app and its data were preserved. [Failed CI run](https://github.com/hershalpandya/AppForKids/actions/runs/46068416200) · [Integration PR](https://github.com/hershalpandya/AppForKids/pull/38)

On 2026-11-28, the offline CI run at `hershalpandya/AppForKids@4e052c4` passed the starter and recovery regressions but opened Gallery during the P1 worksheet preview. An isolated updated app reproduced the same outcome when a worksheet button's midpoint fell inside the Android navigation bar; scrolling the button clear allowed the worksheet to open. [CI run](https://github.com/hershalpandya/AppForKids/actions/runs/46127447902)
