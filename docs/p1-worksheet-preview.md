# Preview a P1 game from worksheets

Crop or cover names, school identifiers and unrelated handwriting before attaching worksheets to a coding agent. Keep scans, transcriptions, extraction notes, answer keys and private drafts in a local folder outside the AppForKids checkout. Give the agent access to that folder or attach only the redacted pages. Number image files in page order. For a scan the agent cannot read, type the question and describe any diagrams with page and item numbers.

Open Codex in the AppForKids checkout and send a request like this with the redacted pages or a transcription.

> Use `$worksheet-to-game` to make a P1 game in French from the attached JPG or PNG pages, or the attached scanned PDF. Practise counting two groups together with totals up to 10. Use numerals for the answers, a short worked example, large visual cues and a helpful retry hint. Use two or three questions and give the child time to think.
>
> Tell me what you read with a page and item reference for each exercise. Flag unreadable, missing or conflicting information and use the clear exercises for the first draft. Ask me to confirm any doubtful items you want to include. Give me a JSON draft and a separate answer key listing each question, its visual rows and choices, the solution, the success feedback and the retry hint. Keep the files in my private worksheet folder. Use the preview workflow in this guide to make the draft playable.

Review the page references and answer key, then play through the draft. A correction can be as short as “In question 2, use page 2, item C. The diagram has four and three counters, so seven is correct. Keep question 1 and show me the updated key and preview.” The agent keeps the same game ID and increments the revision when applying a correction. For exercises that ask pupils to match pairs, use the [matching workflow](p3-worksheet-preview.md). For a different interaction, see the [extension guide](game-mechanics.md).

## Open or replace the draft

The agent builds and installs **AppForKids · Aperçu** on an Android emulator, opens the draft from **P1** and verifies it in the app. If the draft shares an ID with an existing game, the preview catalogue shows the draft in that game's place. After a correction, the agent checks the revised content in the app and leaves the game at its instructions screen. The parent can tap **Jouer** to review it.

### Agent setup

Use JDK 17 and the Android SDK from the [README](../README.md). Put the SDK's platform-tools directory on the path, start a tablet emulator and select it with `ANDROID_SERIAL` if more than one Android device is connected. From the checkout, run the preview helper with the private draft path.

```sh
bash scripts/preview-worksheet.sh --build "/path/to/private-worksheets/game-draft.json"
```

With the preview APK already installed, omit `--build` to reload a corrected file. The helper copies one game definition into private storage in the separate preview app. The family APK bundles its own catalogue and uses the same game parser and round rules. After reviewing the final preview, follow the [approval and release commands](../README.md#approve-and-release-a-worksheet-game).

## Write a game definition

Use the [reviewed synthetic P1 fixture](../tests/fixtures/les-jetons-a-reunir.json) as a complete, runnable example. Save drafts as UTF-8 JSON.

| Field | Value |
| --- | --- |
| `schemaVersion` | Integer `1`. |
| `id` | Stable lowercase identifier with hyphens such as `les-jetons-a-reunir`. |
| `revision` | Positive integer. Start at `1` and increase it after changes. |
| `year`, `type` | `P1` and `tap-to-choose` for this workflow. |
| `title`, `objective` | Short French title and learning goal for the catalogue. |
| `instructions`, `workedExample` | Short French instructions and a worked example for the game screen. |
| `completionMessage` | Optional French message shown when the round ends. |
| `questions` | Nonempty array in play order. |

Each question has a French `prompt`, `visualRows` as an array of display strings, and `choices` as an array of distinct strings. Use short choices that fit in a row, such as `["4", "5", "6"]`. Set `answer` to exactly one choice and write item-specific `correctFeedback` and `retryFeedback` in French. Use text or symbols for the diagram and keep page references, review notes and source files in the private folder. Play every response path before asking the parent to review the draft.

The automated APK check loads the reviewed synthetic definition through the preview command and plays it offline. Source reading, uncertainty review and the parent's corrections happen in the coding-agent session.
