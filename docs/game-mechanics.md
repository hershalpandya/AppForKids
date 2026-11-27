# Extend the game mechanics

Choose the interaction that preserves what a pupil does on the worksheet. Use `tap-to-choose` for one answer among choices and `matching` for pairs spread across two columns. Add a game definition when these interactions fit the task. Add a mechanic through a reviewed code change when the pupil needs a different interaction.

## Portable game definitions

A definition is UTF-8 JSON. Its top-level fields identify the game and provide the French text shared by the Android preview and family APK.

| Field | Value |
| --- | --- |
| `schemaVersion` | Integer `1`. |
| `id` | Stable lowercase letters or digits separated by hyphens, such as `les-mots-de-meme-sens`. |
| `revision` | Positive integer. Start at `1` and increase it for a changed definition. |
| `year` | `P1` or `P3`. |
| `type` | `tap-to-choose` or `matching`. |
| `title`, `objective` | Short French catalogue title and learning goal. |
| `instructions`, `workedExample` | French directions and a worked example before play. |
| `completionMessage` | Optional French end-of-round message. |

Use the [P1 definition and field reference](p1-worksheet-preview.md#write-a-game-definition) for the `questions` array of `tap-to-choose`.

For `matching`, add a `pairs` array with at least two objects. Each object gives the correct pairing through its `left` and `right` text, plus `correctFeedback` and `retryFeedback`. Use distinct labels within each column. Validation trims whitespace and normalizes Unicode when checking duplicates. Left entries appear in array order and the runtime offsets the right column. The pupil taps a left entry, then a right entry, and matching retires both tiles. A wrong attempt leaves the left entry selected for retry. Use short labels and a small set of pairs that fits comfortably on the tablet. [Complete P3 working example](../app/src/main/assets/games/les-mots-de-meme-sens.json)

When Android recreates the activity, a matching round for the same game revision restores matched pairs, the selected left tile, and the last hint or success message. A changed revision or mechanic starts at the instructions. On completion, **Rejouer** starts with every pair unmatched, with no selection or feedback.

Keep source scans and review references in private authoring files. The portable definition contains game content and uses text or symbols for visual cues.

## Add a different interaction

1. Define the pupil’s actions, valid and invalid responses, progress, completion and retry. Specify how the game restores state and what replay resets.
2. Describe the new `type` and its game data in this guide. Follow [GameDefinition](../app/src/main/java/be/hershalpandya/appforkids/GameDefinition.java) and [release validation](../scripts/release.py) to add the corresponding parser and checks. Require information needed to play and reject incomplete or inconsistent answers with a field-level diagnostic. If the mechanic requires packaged assets, validate those paths and include only the approved assets during packaging.
3. Add the round rules and render the controls in [MainActivity](../app/src/main/java/be/hershalpandya/appforkids/MainActivity.java). Use the same parser, rules and UI in preview and release. Follow [MatchingRound](../app/src/main/java/be/hershalpandya/appforkids/MatchingRound.java) for matching selection, retry and progress. Keep instructions, feedback and controls readable in French, with text or symbols for feedback and large touch targets.
4. Add a small synthetic working definition. Run `python3 scripts/release.py validate /path/to/example.json`, open it with `scripts/preview-worksheet.sh`, and review each answer and hint. Add coverage through the approval CLI and installed APK controls for the new interaction, plus a check that existing games still open. [P3 example workflow](p3-worksheet-preview.md)
5. Submit the runtime, validation, tests and working example for code review. After reviewing the exact draft in the preview, use the [approval and signed release commands](parent-handoff.md#validate-and-approve-the-exact-revision) to include it. For a bundled starter, include its catalogue entry and record the digest of its approved definition in [the starter approvals](../app/starter-approvals.json).
