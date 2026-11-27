# Petits Pas: visual direction and design proposal

**Status: the name and broad visual direction are chosen; design details remain proposals for family review.** This is the shared design source proposed for [#23](https://github.com/hershalpandya/AppForKids/issues/23), within the planning scope of [#22](https://github.com/hershalpandya/AppForKids/issues/22). No redesign or change to game content is authorized by this document. Record further decisions here and create focused implementation issues after the remaining design details are agreed.

## Name and feeling

On 2026-11-27, the family chose **Petits Pas** as the app name and asked for a **brighter, more colorful** style. These are user choices, not yet an implemented redesign. Check possible name conflicts before adoption; this is not a clearance claim. The preview label and whether the app needs a logo remain open; **Petits Pas · Aperçu** is one candidate, not a decision.

Explore a cheerful, colorful workspace using multiple distinct accents, clear light surfaces and recognizable shapes. Color should support the activity without obscuring the worksheet task or implying an answer. Candidate illustrations could use flat, rounded shapes and consistent line weight, sparingly in navigation or completion and never as a replacement for instructional text. Their use and style need family review. Counting objects must remain distinct and countable; avoid decorative motion that distracts from play.

## Shared design source and candidate tokens

This document is the proposed human-readable source of intent. Once agreed, give each token a semantic name and implement it in shared Android theme/color, typography and component resources used by the family and preview builds. Activity code should consume those resources rather than independently inventing values; game definitions remain content, not an additional theme. Review changes to this document and executable resources together. Existing `styles.xml` and activity-level styling currently split those responsibilities; this proposal changes neither.

| Role | Example direction to explore | Intended use |
| --- | --- | --- |
| `surface` and `surfaceRaised` | Light neutral surfaces, with room for colorful accents | Backgrounds, cards and interaction areas |
| `textPrimary` | Dark readable ink | Main text on light surfaces |
| `primary` and `onPrimary` | Saturated action color with contrasting text | Primary actions, links and selection outline |
| `accent` | Additional distinct bright colors | Navigation and decoration without encoding correctness |
| `success` and `attention` | Distinguishable colors with contrasting text | Feedback paired with words or a symbol |

These describe roles to explore, not approved colors or a finished palette. Develop sample combinations with the family and test them on the physical tablet before selecting values.

Check actual foreground/background combinations for at least 4.5:1 normal text contrast and 3:1 for large text and meaningful control boundaries; adjust candidates where necessary. Never convey correctness or selection by color alone. Use the platform sans-serif for readable French accents, with candidate sizes of 20sp body, 24sp instruction/section title and 30sp screen title, adapted for available width and user font scaling. Avoid fixed-height text containers; wrap long labels without clipping. Use at least 48 × 48dp interactive targets with space between them (the current buttons already set a 64dp minimum height); keep target bounds visible and independently tappable. Provide text labels, accessible names and clear focus and selected states. Do not rely on icons or sound alone.

Reusable components should include a screen heading and back/return action, year and game cards, primary and secondary buttons, instruction panel, progress indicator, answer or matching tile, feedback panel and completion panel. Each needs default, pressed, focused, disabled and, where relevant, selected/correct/retry states. Wording and layout should remain understandable without decoration. Confirm with screen reader, large text and target tablet review before calling the design accessible.

## Application across the experience

| Surface | Proposed treatment | Preserve and review |
| --- | --- | --- |
| Year selection | Welcoming title and large, equally prominent P1 and P3 cards; small decorative motif away from labels. | Both years remain findable; do not assume a profile or new classification. |
| Catalogue | Consistent game cards with readable title, short description and clear return to year selection. | Both existing games remain discoverable; future taxonomy is a separate decision. |
| Game instructions | One instruction panel, example where supplied, prominent start and a secondary return action. | Show the authored instructions and examples without obscuring them. |
| P1 counting | Spacious, countable objects and large answer buttons; feedback in words plus a visual cue. | Wrong answer hint, correct feedback, question progress and retry remain clear. |
| P3 matching | Two clearly separated columns in French reading order, large word tiles and a visible selection cue. | Selection, matched state, retry hint, progress and completion remain understandable; do not reorder pairs unexpectedly. |
| Completion | Colorful celebration, a textual completion message and distinct replay and catalogue actions. | No animation required to understand completion or navigate away. |
| Worksheet preview | Same components and interaction states, with a persistent, legible preview identity that distinguishes the separate preview app; its exact label is open. | Drafts remain private; authored content and parent review stay intact. Preview must not appear to approve or release a draft. |

These are presentation proposals, not changes to game rules, worksheet answers, approval or release behavior. The preview is a separate package sharing parser and round rules with the family app; align presentation without merging the workflows.

## Proposed adoption and verification

1. Build and review examples of the brighter direction, including palette, illustration and preview label, on the target tablet. Record the family’s remaining choices here, then create small implementation issues with owners, dependencies and observable acceptance criteria. Agree how shared Android resources are consumed by both builds first.
2. Introduce shared resources and components, then migrate year selection and catalogue together so navigation is coherent. Check P1 and P3 still open offline.
3. Migrate instructions and P1 counting, then P3 matching and completion. Verify behavior after each slice, including retry and return paths; preserve round recreation behavior.
4. Apply the same resources to worksheet previews and review a representative P1 and P3 draft. Keep preview identity and the private review/approval boundary. Update authoring guidance only after the design is agreed.
5. Review the integrated result on the family's target tablet before release; record findings and fix or explicitly accept them before shipping. Existing signed update and recovery checks remain applicable.

For each implementation slice, run the existing user-visible APK and worksheet preview smoke checks appropriate to it: both offline starters, preview fixtures, and the signed in-place update when release behavior is affected (see [Android APK testing](wiki/android-apk-testing.md) and the [preview guide](p1-worksheet-preview.md)). These checks exercise behavior rather than asserting exact colors. On the actual target tablet, record tablet model, Android version, APK/version and date; inspect year selection, catalogue, instructions, both games, completion and both previews at normal and enlarged text settings. Check French labels and feedback for clipping, contrast and reading comfort, consistent components and states, 48dp minimum targets and spacing, and that children can tap intended controls without accidental neighboring taps. Try selection, wrong/correct feedback, replay and return; use TalkBack to check meaningful labels, focus and state announcements. Capture issues or screenshots without private worksheet or child data, and record reviewer, outcome and follow-up owner. Automated emulator smoke results do not substitute for this physical review. No such review has yet occurred for this proposal.

## Decisions awaiting review

| Question | Proposed next step |
| --- | --- |
| Preview label | Family reviews a distinct preview label, including the **Petits Pas · Aperçu** candidate; check name conflicts before adoption. |
| Palette and illustration | Family reviews bright, colorful samples on the tablet and chooses the palette, whether illustrations or a logo are wanted, and their style. |
| Tokens and accessibility | Maintainer measures actual color pairs and prototypes scalable type, targets and focus; family reviews on the target tablet before values are accepted. |
| Scope and sequencing | Maintainer turns agreed decisions into independently verifiable issues; coordinate catalogue changes with the separate classification and profile plans. |
| Tablet review | Family identifies the target tablet and reviewer; maintainer records the results and owns follow-up fixes before release. |
