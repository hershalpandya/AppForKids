# Game classification contract

Game schema 2 uses `vocabularyVersion: 1` and a nonempty `classification` array. Each entry has a unique `subject` and a nonempty list of unique `topics` belonging to that subject. Several subjects and topics are supported, for example:

```json
"vocabularyVersion": 1,
"classification": [
  {"subject": "mathematics", "topics": ["counting"]},
  {"subject": "french", "topics": ["synonyms"]}
]
```

`app/src/main/assets/classification-v1.json` is the shared offline vocabulary and compatibility mapping used by authoring, preview and release. The family approved the two starter labels. Version 1 is immutable: the validator checks its digest and the mapping applies only to the exact original starter revisions. Other v1 definitions remain playable and display « À classer »; their approved snapshots and receipts are not rewritten. A same-ID preview draft uses its own revision and classification.

A parent reviewing a game or the maintainer may approve a new French subject or topic name. Check its curriculum fit against the worksheet and the relevant Fédération Wallonie-Bruxelles reference, record who approved it, and add it in a new vocabulary version, retaining version 1 unchanged. Extend runtime and release validation together to support that version before authoring a game with it. Never reuse an ID with a different meaning. To change classification of an existing game, create and review a new game revision; never mutate its approval. Updating the legacy mapping requires an explicitly reviewed compatibility migration, a new mapping version and a way to preserve prior releases' mappings, not an edit to version 1.

Run `python3 scripts/release.py validate path/to/draft.json` before preview. It reports the resolved labels or « À classer » and identifies malformed metadata. Review the labels with the game in the preview before approving the exact revision. Existing schema 1 drafts continue to work; author new classified drafts using schema 2. The release packages the shared vocabulary with selected games for offline use.
