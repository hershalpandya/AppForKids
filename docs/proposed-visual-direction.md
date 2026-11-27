# Petits Pas: visual direction and design proposal

**Status: implemented direction, pending physical-tablet review.** The family chose Petits Pas, direction C (blue, purple and green), illustrations throughout, and the separate preview label **Petits Pas · Aperçu** on 27 November 2026. Exact colors remain subject to tablet review. This document and the Android resources are the shared source for the family and preview builds. A preliminary web check on 2026-11-27 found an unrelated [Petits Pas Android app](https://play.google.com/store/apps/details?id=com.petitspas.app) and [Pathstone : Petits pas](https://apps.apple.com/fr/app/pathstone-petits-pas/id6804307935) for children. This is not a trademark search or clearance; assess naming before broader distribution.

## Name and feeling

On 2026-11-27, the family chose **Petits Pas** as the app name and asked for a **brighter, more colorful** style. The family also chose to show all games with optional year, subject and topic filters; the catalogue layout remains open. These are user choices, not yet an implemented redesign. Check possible name conflicts before adoption; this is not a clearance claim. The separate preview is labelled **Petits Pas · Aperçu**.

Explore a cheerful, colorful workspace using multiple distinct accents, clear light surfaces and recognizable shapes. Color should support the activity without obscuring the worksheet task or implying an answer. Use flat, rounded decorative illustrations throughout, separate from instructional text and answer cues. Counting objects must remain distinct and countable; avoid decorative motion that distracts from play.

## Shared design source and candidate tokens

This document is the human-readable source of intent. Both builds consume the same `app/src/main/res/values/colors.xml`, theme, illustration and activity components; only the preview app name is overridden in debug resources. Game definitions remain content, not an additional theme. Review changes here and in executable resources together.

| Role | Example direction to explore | Intended use |
| --- | --- | --- |
| `surface` and `surfaceRaised` | Light neutral surfaces, with room for colorful accents | Backgrounds, cards and interaction areas |
| `textPrimary` | Dark readable ink | Main text on light surfaces |
| `primary` and `onPrimary` | Saturated action color with contrasting text | Primary actions, links and selection outline |
| `accent` | Additional distinct bright colors | Navigation and decoration without encoding correctness |
| `success` and `attention` | Distinguishable colors with contrasting text | Feedback paired with words or a symbol |

Current text combinations have calculated contrast ratios: primary purple on white 8.89:1 and on pale purple 7.38:1; ink on the page 13.99:1 and on the green instruction surface 12.97:1; star ink on green 7.28:1. These are digital calculations, not a substitute for physical-tablet review.

Check actual foreground/background combinations for at least 4.5:1 normal text contrast and 3:1 for large text and meaningful control boundaries; adjust candidates where necessary. Never convey correctness or selection by color alone. Use the platform sans-serif for readable French accents, with candidate sizes of 20sp body, 24sp instruction/section title and 30sp screen title, adapted for available width and user font scaling. Avoid fixed-height text containers; wrap long labels without clipping. Use at least 48 × 48dp interactive targets with space between them (the current buttons already set a 64dp minimum height); keep target bounds visible and independently tappable. Provide text labels, accessible names and clear focus and selected states. Do not rely on icons or sound alone.

Reusable components should include a screen heading and back/return action, game cards, optional year/subject/topic filter controls, primary and secondary buttons, instruction panel, progress indicator, answer or matching tile, feedback panel and completion panel. Each needs default, pressed, focused, disabled and, where relevant, selected/correct/retry states. Wording and layout should remain understandable without decoration. Confirm with screen reader, large text and target tablet review before calling the design accessible.

## Application across the experience

| Surface | Proposed treatment | Preserve and review |
| --- | --- | --- |
| Year filter | An optional, clearly labeled control for narrowing the catalogue by year; its layout remains open. | P1 and P3 remain discoverable, and a child can see all games without selecting a year. |
| Catalogue | Show all games initially, with optional year, subject and topic filters and consistent game cards with readable titles and descriptions. The filter and card layout remains open. | Both existing games remain discoverable; provide a clear way to remove filters and recover from no matches. |
| Game instructions | One instruction panel, example where supplied, prominent start and a secondary return action. | Show the authored instructions and examples without obscuring them. |
| P1 counting | Spacious, countable objects and large answer buttons; feedback in words plus a visual cue. | Wrong answer hint, correct feedback, question progress and retry remain clear. |
| P3 matching | Two clearly separated columns in French reading order, large word tiles and a visible selection cue. | Selection, matched state, retry hint, progress and completion remain understandable; do not reorder pairs unexpectedly. |
| Completion | Colorful celebration, a textual completion message and distinct replay and catalogue actions. | No animation required to understand completion or navigate away. |
| Worksheet preview | Same components and interaction states, with a persistent, legible preview identity that distinguishes the separate preview app; its exact label is open. | Drafts remain private; authored content and parent review stay intact. Preview must not appear to approve or release a draft. |

These are presentation proposals, not changes to game rules, worksheet answers, approval or release behavior. The preview is a separate package sharing parser and round rules with the family app; align presentation without merging the workflows.

## Proposed adoption and verification

1. Build and review examples of the brighter direction, including palette, illustration and preview label, on the target tablet. Record the family’s remaining choices here, then create small implementation issues with owners, dependencies and observable acceptance criteria. Agree how shared Android resources are consumed by both builds first.
2. Introduce shared resources and components, then migrate the catalogue and optional filters together so navigation is coherent. Coordinate with the classification plan and check both P1 and P3 games remain discoverable and open offline.
3. Migrate instructions and P1 counting, then P3 matching and completion. Verify behavior after each slice, including retry and return paths; preserve round recreation behavior.
4. Apply the same resources to worksheet previews and review a representative P1 and P3 draft. Keep preview identity and the private review/approval boundary. Update authoring guidance only after the design is agreed.
5. Review the integrated result on the family's target tablet before release; record findings and fix or explicitly accept them before shipping. Existing signed update and recovery checks remain applicable.

For each implementation slice, run the existing user-visible APK and worksheet preview smoke checks appropriate to it: both offline starters, preview fixtures, and the signed in-place update when release behavior is affected (see [Android APK testing](wiki/android-apk-testing.md) and the [preview guide](p1-worksheet-preview.md)). These checks exercise behavior rather than asserting exact colors. On the actual target tablet, record tablet model, Android version, APK/version and date; inspect the all-games catalogue and optional filters, instructions, both games, completion and both previews at normal and enlarged text settings. Check French labels and feedback for clipping, contrast and reading comfort, consistent components and states, 48dp minimum targets and spacing, and that children can tap intended controls without accidental neighboring taps. Try filtering and clearing filters, the no-matches state, selection, wrong/correct feedback, replay and return; use TalkBack to check meaningful labels, focus and state announcements. Capture issues or screenshots without private worksheet or child data, and record reviewer, outcome and follow-up owner. Automated emulator smoke results do not substitute for this physical review. No such review has yet occurred for this proposal.

## Decisions awaiting review

| Question | Proposed next step |
| --- | --- |
| Name conflicts | Check the name for conflicts before wider distribution; the current choice is not a clearance claim. |
| Palette and illustration | Family reviews the implemented blue, purple and green direction and illustrations on the tablet; refine if needed. |
| Tokens and accessibility | Maintainer measures actual color pairs and prototypes scalable type, targets and focus; family reviews on the target tablet before values are accepted. |
| Catalogue layout | Family reviews the all-games catalogue and optional year/subject/topic filter layout on the tablet; the chosen browsing behavior does not require a separate year-first screen. |
| Scope and sequencing | Maintainer turns agreed decisions into independently verifiable issues; coordinate catalogue changes with the separate classification and profile plans. |
| Tablet review | Family identifies the target tablet and reviewer; maintainer records the results and owns follow-up fixes before release. |
