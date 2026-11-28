---
name: worksheet-to-game
description: Turn worksheet images, a scanned PDF, or a transcription into a playable AppForKids P1 or P3 draft. Use for a new worksheet game or a parent's correction to an existing draft.
---

## Read the source

For a new draft, take the worksheet batch, intended year, learning goal and teaching constraints. Read each supplied JPG, PNG or PDF page with the available image or document tools. If a page is unreadable, ask for a page-labelled transcription, including the relevant diagram. Use the parent's prompt to select exercises. Record page and item references, what each item says or shows, and conflicts or missing information. Set uncertain exercises aside and use the readable ones. Ask specific questions for decisions that need the parent.

## Create or revise the draft

Read the [visual source](../../../docs/proposed-visual-direction.md) and [classification contract](../../../docs/classification-contract.md). Choose the year and every applicable reviewed subject and topic; surface uncertain or missing vocabulary to the parent instead of guessing. Author new classified drafts with schema 2 and show the resolved labels to the parent. Use the [P1 tap-to-choose format](../../../docs/p1-worksheet-preview.md) when the pupil picks one answer and the [P3 matching workflow](../../../docs/p3-worksheet-preview.md) when the pupil pairs items. Check the level and terminology against the worksheet and the appropriate Fédération Wallonie-Bruxelles reference. Keep the game JSON, source review and answer key in the parent's private folder outside the checkout. Use a temporary private folder if the parent has provided attachments without an output path. Keep only game content in the JSON. Write an answer key for that exact revision with the displayed prompts and choices or matchable tiles, each solution, success feedback and retry hint.

For a correction, reopen the existing draft and source review. Apply the parent's correction under the same game ID with an increased revision. Keep the previous files and update the source review and answer key to match the revised game.

## Open the preview

Select an Android emulator using `adb devices` and `ANDROID_SERIAL` when needed. Start a tablet AVD with its window visible. If no AVD exists, use the [CI tablet setup](../../../.github/workflows/android-apk.yml) as a reference and select a system image that matches the host architecture. From the checkout, run `bash scripts/preview-worksheet.sh --build "$draft_path"` to build, install and launch the preview app. For a correction using the installed preview, run the same command without `--build` to reload the new definition.

Inspect **Petits Pas · Aperçu** for **Aperçu du brouillon** and resolve any **Impossible d’ouvrir le brouillon.** error. In the all-games catalogue, check the draft’s year and resolved labels, exercise applicable year, subject and topic filters, clear filters and check no-match recovery. A same-ID draft replaces the bundled game and uses its own classification. Open the draft by title and play it against the answer key, including wrong answers, retry hints, correct feedback, completion, replay and return. Check legibility, countable objects, tile states and touch targets against the visual source. For a correction, navigate to each changed part and verify the revised content is visible, even when the title is the same. Reopen the verified draft at its instructions screen before reporting it ready.

Give the parent the source review, answer key, preview title and any question still awaiting clarification. If the emulator or tooling blocks the preview, keep the draft and answer key available and report the specific blocker. The parent reviews the private draft, labels and answer key before approving the exact revision; follow the [parent handoff](../../../docs/parent-handoff.md#validate-and-approve-the-exact-revision) for a separate approval and release.
