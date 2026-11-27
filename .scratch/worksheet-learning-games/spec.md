# Android learning games from French-language worksheets

Published as [GitHub issue #1](https://github.com/hershalpandya/AppForKids/issues/1). Track updates there.

## Problem Statement

I want my daughters, aged 6 and 8 and in P1 and P3 at a French-speaking Belgian school, to play short games that help them practise what they are learning. I want to use their worksheets and a short prompt to tell an agent what to make. I need a repeatable way to check the result, get it onto our Android tablet, and add more games as their schoolwork changes.

## Solution

Build a French-language app for a shared Android tablet. Each child picks her school year and plays short activities at that level. The first installation contains a playable activity for each year. Once installed, the girls can open and replay games offline.

Set up a parent-operated workflow outside the children's app. The parent scans or photographs a few worksheets, gives the agent the target year and a short prompt, and receives a playable draft. The parent can check what the agent understood, try the game, verify the answers, and request changes. After approval, the parent can build a tablet update that adds the game to the existing library. The first release is for family use through direct installation.

## User Stories

1. As the parent, I want to install the app directly on our Android tablet, so that the girls can start playing at home.
2. As the parent, I want an illustrated or plainly written setup guide, so that I can do the initial setup and repeat the workflow myself.
3. As a P1 pupil, I want to pick P1 on the home screen, so that I can easily find activities for my year.
4. As a P3 pupil, I want to pick P3 on the home screen, so that I can easily find activities for my year.
5. As a pupil, I want to switch years from the home screen, so that my sister and I can take turns on the same tablet.
6. As a pupil, I want to see what an activity is about before I open it, so that I can choose what to practise.
7. As a pupil, I want a game available for my year on first launch, so that I can start straight away.
8. As a pupil, I want my instructions and feedback in French, so that they feel familiar from school.
9. As a P1 pupil, I want short instructions with a worked example or clear visual cues, so that I can start even while I am learning to read.
10. As a P3 pupil, I want the questions and wording to fit the schoolwork I am doing, so that the practice feels relevant.
11. As a pupil, I want large touch controls and readable text, so that I can play comfortably on the tablet.
12. As a pupil, I want to know what I got right and get a helpful prompt after a mistake, so that I can try again.
13. As a pupil, I want time to think, so that I can focus on the exercise at my own pace.
14. As a pupil, I want to tell when a round is finished and choose whether to replay or go back, so that I can use the app on my own.
15. As a pupil, I want to exit a game mid-round, so that I can choose a different activity or hand the tablet to my sister.
16. As a pupil, I want my installed games to open in airplane mode, so that I can play wherever the tablet goes.
17. As the parent, I want to give the agent several worksheet photos or a PDF scan, so that I can use the material I already have.
18. As the parent, I want to specify the year, skill and any teaching instructions in a short prompt, so that I can decide what a game should practise.
19. As the parent, I want the agent to summarise what it read and flag unclear items, so that I can catch scan errors before they become exercises.
20. As the parent, I want the agent to recognise conflicting or missing instructions, so that I can confirm which items to use.
21. As the parent, I want to review the proposed questions, correct answers and feedback, so that I can check the game against the worksheet.
22. As the parent, I want to preview the full game, so that I can see whether it makes sense to a child at the target year.
23. As the parent, I want to ask the agent to adjust the draft, so that I can fix a mistake or change the wording without editing code myself.
24. As the parent, I want to approve a specific draft before it ships, so that the children see the version I checked.
25. As the parent, I want automatic checks to catch incomplete or invalid game content, so that a draft with broken exercises cannot reach the tablet.
26. As the parent, I want a clear result when a scan, check or build fails, so that I can correct the problem and retry.
27. As the parent, I want repeatable build and install steps, so that I can move an approved game onto the tablet from my computer.
28. As the parent, I want the new game to appear in the right year alongside current games, so that the library grows with the children's lessons.
29. As the parent, I want to correct an existing game in a later update, so that a mistake can be fixed without making a duplicate.
30. As the parent, I want worksheet scans and personal information kept out of the children's app, so that their schoolwork stays private.
31. As the parent, I want the first version to avoid logins, advertising and analytics, so that the girls can simply open it and play.
32. As the project owner, I want reviewed content to be portable, so that I can reuse it if I rebuild the app before publishing it.
33. As a coding agent, I want a documented game format and sample requests, so that I can create a valid draft in a new session.
34. As a coding agent, I want a documented way to add a new game mechanic, so that worksheets that need a different form of interaction can extend the app.

## Implementation Decisions

- Build an Android tablet app with a French home screen, a P1/P3 year picker, and a game catalogue grouped by year. The same tablet can serve both children without accounts or real names. Bundle the catalogue and game assets with the app. The app runs offline from first launch, including instructions, gameplay and feedback.
- Launch with two original activities, one for P1 and one for P3, made from synthetic worksheets. Use examples from French and maths to exercise the workflow. For new games, use the actual worksheets and the parent's prompt to establish the learning goal, vocabulary, answer conventions and difficulty. Use the Fédération Wallonie-Bruxelles reference material when checking how a proposed objective fits the requested year. [Fédération Wallonie-Bruxelles learning content](https://www.enseignement.be/parcours-dapprentissage/maternel-et-primaire-ordinaire/organisation-de-lenseignement-maternel-et-primaire/contenus-dapprentissage)
- Start with reusable tap-to-choose and matching interactions. Give games short rounds with a clear objective, a way to retry, and a way to exit. Use encouraging French feedback without time pressure. Use large touch targets, readable text and response cues that can be understood without relying on colour.
- Store games as structured, versioned definitions. Each definition has a stable game ID, a revision, a target year, a title, a learning objective, a game type, prompts, solutions, feedback and any packaged asset references. Keep game definitions separate from the Android interface and execution code so they can be reused in a future rewrite. Support additions through the catalogue and revisions through the same game ID. To add a genuinely new interaction, the agent can extend the runtime through a reviewed code change and supply a working example.
- Start authoring in a coding-agent session on the parent's computer. Document a repeatable request format for attaching a small batch of JPG or PNG photos or a scanned PDF, naming P1 or P3, and describing the skill, constraints and desired game. Read worksheet images using the agent's document or image tools. Provide a path for the parent to supply a transcription when the scan is unusable. Keep the workflow independent of any particular model provider.
- Have the agent return a short extraction summary with page references, a list of items that need clarification, a playable draft and a reviewable answer key. Surface ambiguous handwriting, contradictory answers and uncertain diagram readings. Base drafts on clearly readable material or the parent's confirmed corrections. Use the parent's requested scope when worksheets cover multiple skills.
- Preview the game with the same rules and content it will use on the tablet. Document how to open the preview, inspect every question and answer, and send revisions. Include only approved versions in the release catalogue. A changed draft must be reviewed again before release.
- Validate the release catalogue and game definitions before packaging, including duplicate IDs, grade and game type, required text, answer consistency and referenced assets. Fail with actionable messages. If a draft or build fails, keep the previous approved version available for release and leave the tablet installation usable.
- Keep the raw scans and extraction notes on the authoring side. Document how to crop or redact names, school identifiers and handwriting that is irrelevant to the exercise before giving material to a connected agent. Do not commit or bundle raw worksheets, identifying details, agent credentials or signing secrets. Use synthetic material for examples shared with developers or agents.
- Deliver a reproducible build, a signed APK for direct installation, and instructions for transferring, installing and updating on the family's tablet. Keep the app identifier and signing key stable across home releases and increase the app version on each update. Document how the parent backs up the signing key. Verify installation and an in-place update on the target tablet. Document any device-specific installation steps observed during that verification. [Android release preparation](https://developer.android.com/studio/publish/preparing), [Android app signing](https://developer.android.com/studio/publish/app-signing)
- Include a parent handoff covering the initial setup, sample prompt, scan handling, reviewing and approving a revision, validation, building, installing and recovering from a failed attempt. A parent following the guide should be able to add a second wave of content with agent help and without learning the Android codebase.

## Testing Decisions

- Use the parent-to-tablet workflow as the main acceptance test. Start with a synthetic worksheet batch and a short prompt. Inspect the extraction, request a correction, play the draft, approve the revision, build the signed APK, install it over the starter version and play the new game in airplane mode. Confirm earlier games still open and the new title appears under the correct year. Repeat or parameterise with P1 and P3 material across the two starter interactions.
- Test the children’s app through its visible controls. Verify year selection and switching, game selection, correct and incorrect answers, feedback and retry, round completion, replay and returning to the catalogue. Check touch usability and legibility on the target tablet.
- Exercise the authoring workflow and release validation through their normal entry points. Use representative synthetic scans and game definitions. Verify that unclear source material is surfaced, answer-key inconsistencies and missing assets prevent packaging, an unapproved revision stays out of the release, and retrying a corrected game revision gives one entry under its stable ID.
- Assert outcomes a parent, pupil or agent can observe. Check the questions shown, the feedback received, the catalogue that ships, and the result of installing an update. Use stable approved fixtures for automated checks of the game runtime and catalogue. Review live agent output against the source and prompt because repeated generation can vary.
- The workspace contains no app or existing test suite. Establish the end-to-end workflow and add focused fixture checks where they catch catalogue or game-validation regressions reliably.

## Out of Scope

- Google Play submission, store assets, public distribution and preparation for a public launch.
- iOS support, classroom administration, school integrations, online multiplayer and public sharing of games.
- Cloud accounts, cross-device sync, long-term progress reporting and in-app AI chat.
- In-app scanning, a visual game editor and automatic release to the tablet.
- Complete curriculum coverage and an initial library beyond the starter activities.

## Further Notes

- The offline experience, external authoring workflow, starter interactions and stable game format are proposed first-version decisions. The initial curriculum examples should be replaced or supplemented with the family's actual worksheets as soon as they are available.
- A future Play Store launch can revisit the Android implementation and distribution model. Keep the approved exercises and original assets reusable for that later decision.
