---
name: worksheet-to-game
description: Turn worksheet images, a scanned PDF, or a transcription into a playable AppForKids P1 draft. Use for a new worksheet game or a parent's correction to an existing draft.
---

## Read the source

For a new draft, take the worksheet batch, intended year, learning goal and teaching constraints. Read each supplied JPG, PNG or PDF page with the available image or document tools. If a page is unreadable, ask for a page-labelled transcription, including the relevant diagram. Use the parent's prompt to select exercises. Record page and item references, what each item says or shows, and conflicts or missing information. Set uncertain exercises aside and use the readable ones. Ask specific questions for decisions that need the parent.

## Create or revise the draft

Read the [P1 game format and preview setup](../../../docs/p1-worksheet-preview.md). Keep the game JSON, source review and answer key in the parent's private folder outside the checkout. Use a temporary private folder if the parent has provided attachments without an output path. Keep only game content in the JSON. Write an answer key for that exact revision with every question, visual rows, choices, solution, success feedback and retry hint.

For a correction, reopen the existing draft and source review. Apply the parent's correction under the same game ID with an increased revision. Keep the previous files and update the source review and answer key to match the revised game.

## Open the preview

Select an Android emulator using `adb devices` and `ANDROID_SERIAL` when needed. Start a tablet AVD with its window visible. If no AVD exists, use the [CI tablet setup](../../../.github/workflows/android-apk.yml) as a reference and select a system image that matches the host architecture. From the checkout, run `bash scripts/preview-worksheet.sh --build "$draft_path"` to build, install and launch the preview app. For a correction using the installed preview, run the same command without `--build` to reload the new definition.

Inspect the Android home screen for **Aperçu du brouillon** and resolve any **Impossible d’ouvrir le brouillon P1.** error. Tap **P1**, open the draft by title and play through it against the answer key. For a correction, navigate to each changed part and verify the revised content is visible, even when the title is the same. Reopen the verified draft at its instructions screen before reporting it ready.

Give the parent the source review, answer key, preview title and any question still awaiting clarification. If the emulator or tooling blocks the preview, keep the draft and answer key available and report the specific blocker. The authoring session ends at the preview and review.
