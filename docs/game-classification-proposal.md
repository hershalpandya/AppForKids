# Proposal: finding worksheet games by year and subject

Status: **proposal for review**, not an implementation specification. On 2026-11-27, the family chose an all-games catalogue with optional year, subject and topic filters, multiple topics per game, and visibility for unknown legacy games labelled **À classer**. Other details below remain proposals unless stated otherwise. This addresses [#25](https://github.com/hershalpandya/AppForKids/issues/25), part of [#22](https://github.com/hershalpandya/AppForKids/issues/22). Labels and examples below are candidates. There is no fun-games category.

## Vocabulary and examples

Keep `P1` and `P3` as school-year codes. A **subject** is a broad area a child recognizes; a **topic** is a more specific practice area inside one subject. Propose stable, language-independent IDs and French display labels:

| Subject ID | French label | Topic ID | French label | Example |
| --- | --- | --- | --- | --- |
| `mathematics` | Mathématiques | `counting` | Compter | P1 **Les étoiles à compter**, `compter-les-etoiles@1` |
| `french` | Français | `synonyms` | Mots de même sens | P3 **Les mots de même sens**, `les-mots-de-meme-sens@1` |

These are illustrative classifications, not curriculum claims or an exhaustive curriculum. Add a subject or topic deliberately when a real worksheet needs it; do not force unrelated work into an existing topic. A topic belongs to exactly one subject in this initial proposal. Review the names with the family and check curriculum alignment before adoption. Years and subjects do not imply difficulty within a year.

## Proposed child journey

1. Open the catalogue with **all games visible** and no filters selected. If child selection is agreed under #22, enter this journey after selection; classification does not require a profile.
2. Optionally filter by year, subject or topic, independently or in combination. Offer an all/clear choice for each filter and a clear-all action. Retain P1 and P3. Proposed matching semantics: filters combine with AND; a topic filter matches a game containing that topic. A game appears once even if it has multiple topics. Show game titles and objectives, including **À classer** for unknown legacy classifications in the unfiltered catalogue. Year filtering can still find those games; subject or topic filters exclude them until classified. These matching and filter interaction details remain for review.
3. Select a game to open its instructions, then **Jouer**. Completion offers replay and **Retour au catalogue**, proposed to return to the same filters. Provide visible controls to change or clear filters.
4. When filters yield no games, show a plain French message such as « Aucun jeu pour ce choix. » and offer **Effacer les filtres**; clearing returns to all games. Keep browsing and filters usable offline, with no loading or network dependency.

The precise layout, labels, filter persistence after app restart, and interaction with child selection remain for review. The flow must work with both starters and future entries, not expose internal IDs, and not suggest that a game is appropriate merely because of a topic label.

## Proposed metadata contract

Keep the current `id`, positive `revision`, `year`, `title`, `objective`, `type`, and game content. For newly authored definitions, propose one required `subject` ID and a nonempty `topics` array of unique topic IDs, each of whose subject/topic pairs must exist in a versioned, bundled vocabulary. `year` remains a single supported year; adding years is a separate decision. The catalogue remains an index of game asset filenames, not a second independent source of classification. The runtime resolves IDs to display labels locally. For example, additions to the existing definitions would be:

```json
{"year":"P1", "subject":"mathematics", "topics":["counting"]}
{"year":"P3", "subject":"french", "topics":["synonyms"]}
```

The examples omit the other required fields and are not complete game definitions. Authoring validation should reject missing or empty topic arrays, duplicate, blank, unknown, or mismatched subject/topic IDs with an actionable error, rather than silently assigning an incorrect label. Vocabulary IDs should remain stable if display labels change; removing or reassigning an ID needs an explicit migration. Decide vocabulary ownership, versioning and localization before implementation. The current parser and release validator accept schema version 1 and the release validator rejects unexpected fields, so both must evolve together; adding fields alone is not compatible.

## Compatibility and rollout proposal

- Introduce a supported new definition schema and a local vocabulary in the runtime, preview and release validator together. Continue to accept existing version 1 definitions without editing them. For the two known starter IDs, derive the example classifications at read/package time from a maintained compatibility mapping; for an unknown old ID, show it in the all-games catalogue with **À classer**, never guess or hide it. Its known year remains filterable; the proposed subject/topic filter behavior is described above.
- Keep the bundled `catalogue.json` filename list and ID replacement behavior. A preview draft with the same ID replaces the bundled game in the preview catalogue; classification, including all topics, comes from the draft if new, or the legacy mapping/fallback if old. The authoring workflow should request classification, validate it and show it for parent review with the game.
- An approval is a snapshot of an exact `id@revision`. Do not modify an existing approved snapshot, receipt or starter asset in place to add metadata. Existing approvals and release selections should remain usable through compatibility handling; changing a definition requires a new revision and review/approval. Release packaging should preserve the selected bytes and validate old and new definitions using their respective rules. The exact mapping storage and how it is versioned alongside releases need review, including how to prevent later mapping changes from silently changing a previously reviewed classification.
- Deliver parser/validator and compatibility first, then catalogue navigation and preview/authoring changes, then migrate content only when reviewed. Coordinate with the design and profile plans; do not make either a prerequisite for playing existing games. Create sequenced implementation issues only after the family agrees the plan.

## Verification plan for implementation

Use the installed Android app and worksheet preview as the user-visible seams agreed in #22. With no filters selected, verify that both starters and an unknown legacy fixture are visible, the latter labelled **À classer**. Filter independently by year, subject and topic, then combine P1, Mathématiques and Compter to start the stars game and P3, Français and Mots de même sens to start the synonym game. Use a new fixture with multiple topics: either topic should find it, combined filters should narrow results, and it should appear once. Check clear-one and clear-all actions, an empty combination and recovery, return from completion with filters retained, and both starters in airplane mode. Confirm the unclassified game remains visible when unfiltered and under its year, and follows the proposed behavior under subject/topic filters. Human review on the family tablet should check that French labels and controls are understandable and usable.

At workflow boundaries, validate and preview representative existing v1 and new-schema definitions, including a same-ID draft replacement; check that empty, duplicate, unknown or mismatched topic IDs are rejected with a useful message. Approve a reviewed new revision and build a release selecting it alongside an existing approval. Inspect packaged definitions and play both offline after an in-place update; verify old approvals still package without rewriting their snapshots and that recovery with an earlier approved revision remains possible under the existing version-code rules. Exercise an unsupported schema and missing classification as negative cases. Add lower-level validation tests only where these seams cannot reliably expose the case.

## Decisions and next steps

- **Family:** review the French labels, filter controls and empty-state actions.
- **Maintainer and family:** review the proposed single-subject contract, filter matching and unclassified behavior, support for more years, vocabulary ownership and localization, and whether filters persist after restart.
- **Maintainer:** settle the schema transition and immutable/versioned legacy mapping, including how classifications of older approvals are reviewed and changed. Confirm how preview and release tools surface the resolved classification.
- **Maintainer:** reconcile the journey with the design and child-selection plans; after agreement, split work into ordered issues with acceptance criteria and the checks above. The dated family choices above are agreed; the remaining technical and interaction details are recommendations pending review.
