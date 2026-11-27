# Child selection and privacy proposal

Status: **proposed for family review**, 27 November 2026. Related: [#24](https://github.com/hershalpandya/AppForKids/issues/24), parent [#22](https://github.com/hershalpandya/AppForKids/issues/22). This is a plan, not an implementation, an agreed decision, or a compliance determination. The existing family app has P1 and P3 offline starters; worksheet previews are a separate package and approval workflow. The family app currently sets `allowBackup=false`; it has no child profiles yet.

## Proposed family journey

1. On first launch show “Who is playing?” with an empty state and a prominent “Add a child” action for a parent. Explain briefly that names stay on this tablet and may be nicknames. The same screen later shows every child's name as a large, readable selection; do not rely on color alone.
2. A parent enters a display name. Trim surrounding whitespace; reject empty or whitespace-only input with a useful message and retain the entry. Propose a reasonable length limit (for example 40 characters), support accented and non-Latin text, and reject control characters. Compare trimmed names case-insensitively; on a duplicate, explain and request a distinguishable nickname rather than silently merging children. Confirm exact comparison and limits with the family.
3. Select a name to enter the game catalogue, with the selected name visible and a clear “Change child” action. Choose a year and then an available game; P1 and P3 remain available. A catalogue with no matching games offers a way back to the available choices. Returning from a game or completion returns to the selected child's catalogue. Details of year and subject navigation belong to the separate classification plan.
4. “Change child” returns to the name list without deleting anything. If switching during a game, ask whether to leave the current round; discard its unsaved state on confirmation, so another child never inherits it. Cancelling keeps the current round.
5. A parent can remove a child from the selection screen. Before confirming, name the child and explain that their local profile and any saved progress are permanently deleted on this tablet; other children and bundled games remain. Cancel changes nothing. On confirmation clear selection if it points to that child, delete related data, and show the remaining list or the first-launch empty state. Adding the same name later creates a new child, not restored progress. This is a shared family device, not a security boundary: a child can select another name. Whether parent actions need a gate is open.

## Proposed minimal data and lifecycle

| Data | Purpose and lifecycle |
| --- | --- |
| Local opaque child ID | Stable key to separate children even when a name changes or is reused. Generated on device, never displayed or transmitted. |
| Display name | Only information requested from a parent; nickname encouraged. Stored until removal. No birth date, photo, contact, school or account. |
| Selected child ID | Local convenience only; clear on removal. Proposal: show the chooser at each fresh launch rather than automatically selecting a child; retain selection only while navigating a session. |

Recommend **no persistent progress in the first profile release**: the games can be replayed, and this avoids collecting a history before the family establishes its value. In-round state may survive Android activity recreation for the current child and game; discard it on switch, removal, or a fresh app session. Do not show rankings or compare children. If the family asks for progress later, separately agree a small model such as child ID, game ID, revision and a completion flag, with a simple “completed” indicator; no scores, timestamps or answer history by default. Keep it until the parent deletes the child or resets progress, delete it with the child, and define revision/reset behavior before implementation. This optional model is not an approved feature.

## Storage, backup and sharing boundary

Propose app-private local storage on the tablet, no sign-in, analytics, ads, cloud sync, export or developer collection of names or progress. No data needs to leave the device for child selection or the bundled games. Installation on another device starts empty; uninstall or clearing app data loses local profiles. Tell the family this trade-off before implementation. The app's current manifest disables backup, but [Android's backup documentation](https://developer.android.com/identity/data/autobackup) warns that on some Android 12+ devices `allowBackup=false` does not disable device-to-device transfer. Before claiming a boundary, choose and verify appropriate cloud, device-transfer and supported cross-platform transfer rules across supported Android versions and the family tablet; account for OS or device behavior outside the app's control. Audit crash reporting, logs, dependencies, previews and release builds for accidental profile data or network transfer. Avoid names in logs. App-private storage separates app data from ordinary other apps, not from someone with device access or privileged tools.

Selection must work with airplane mode enabled, including adding, selecting, switching, removing and opening both bundled games. Keep each child's transient round separate: never use a global restored game state after another child is selected. Decide how to handle an interrupted deletion or corrupted/missing local data without presenting another child's state; show a recoverable empty/error state rather than silently reassigning data.

## Questions before a possible Google Play release

Reviewed against the following Google sources on 27 November 2026; recheck the current policies, the actual build and all SDK behavior at release. This is a question list, not a conclusion that the proposal complies with policy or law.

- Which age groups are actually targeted, and what answers are accurate for Target Audience and Content and IARC? If children are in the target audience, what Families requirements apply to content, data and any SDKs? [Target audience guidance](https://support.google.com/googleplay/android-developer/answer/9867159) and [Families policies](https://support.google.com/googleplay/android-developer/answer/9893335).
- Does any app version, library, system backup, transfer, log, crash tool or future feature transmit names, identifiers or other data? Google defines Data safety collection around off-device transmission and says solely on-device processing is not declared as collection; confirm the full build and any exceptions before answering collection, sharing, purposes and security questions. [Data safety guidance](https://support.google.com/googleplay/android-developer/answer/10787469).
- What privacy policy and in-app disclosure are required and how will they accurately describe local storage, deletion, backups and any third parties? Google requires a privacy policy on the store listing and in the app; check the current detailed requirements. [Prepare for review](https://support.google.com/googleplay/android-developer/answer/9859455) and [User Data policy](https://support.google.com/googleplay/android-developer/answer/10144311).
- Are local child profiles considered accounts under the then-current account-deletion rules, and if so what in-app and web deletion paths are required? What consent, parental and local-law requirements apply to the actual audience and data? Obtain appropriate legal advice; do not infer an answer from the local-only design.
- Who owns the release inventory and policy review, and how will declarations and privacy text be updated after a change? The maintainer should review app and SDK data flows, backup behavior and the live Play Console questions before submission.

## Observable checks for later implementation

At the installed family app seam, with synthetic names and offline mode, verify:

- First launch shows the empty chooser; add two names, see both prominently, reject blank and duplicate input with actionable feedback, and select each into the catalogue.
- Start a game as one child, switch with cancel and confirm paths, and verify no round or optional saved progress appears for the other child. Both P1 and P3 still open and play offline.
- Restart the app and verify the names persist and the chooser appears, without restoring another child's round. Rotate/recreate within a round and verify the current child's state survives as proposed.
- Cancel removal, then confirm it; after restart the removed name and any associated progress remain absent, other child and games remain, and reusing the name does not restore old data. Removing the selected or final child reaches the appropriate chooser/empty state.
- On supported emulator versions and the family tablet, inspect backup/transfer outcomes against the agreed policy; document what was actually tested and device limitations. Check offline create, play and deletion after reinstall/clear-data behavior is understood.

These are proposed acceptance checks, not evidence of implemented behavior. Visual review on the family tablet should check name readability, touch targets and comprehension.

## Decisions and next steps

Family: review the chooser, duplicate policy, parent gate, switching interruption, whether any progress is useful, and the no-backup/data-loss trade-off. Maintainer: validate supported-device backup behavior and release data inventory; resolve deletion and recovery semantics, then turn agreed choices into sequenced implementation issues with the checks above. Keep progress and any sharing in separate decisions. Revisit Play questions and legal advice before a release. No choice in this document authorizes implementation by itself.
