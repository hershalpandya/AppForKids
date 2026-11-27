# P3 worksheet to matching game

[Les mots de même sens](../app/src/main/assets/games/les-mots-de-meme-sens.json) is the original French starter for P3. It comes from the [synthetic worksheet transcription](p3-synonyms-worksheet.md). Choose **P3**, open the game, and tap **Jouer**. Tap a word at the left and its synonym at the right. A hint lets you retry with the same word. After all pairs are matched, tap **Terminer** to finish, then **Rejouer** or **Retour au catalogue**.

## Sample parent request

> Create a P3 game in French from the attached worksheet. Use matching to practise recognizing synonyms in familiar phrases. Use three pairs, a worked example and a helpful hint for each pair. Tell me which page and item each pair came from and flag missing or illegible text. Give me the draft, the answer key and a playable preview.

## Extraction and review

Page 1 supplies a worked example and three complete items. Item D has a missing word and answer. Ask for its full sentence and its column entry before using it. The three complete items form the round. Keep the worksheet, extraction and answer key on the authoring side. The family APK contains the reviewed game definition.

The P3 *Traiter/utiliser les unités lexicales* section identifies synonym recognition between written words on p. 80. Under *Utiliser le lexique*, p. 81 calls for replacing a word with one of the same meaning. Each answer here preserves the relevant meaning and part of speech in its worksheet sentence. The activity practises recognizing the relationship, with the substitution shown in the success feedback. [Fédération Wallonie-Bruxelles, Référentiel de français et langues anciennes, pp. 80–81](https://www.enseignement.be/fileadmin/portail_age/uploads/parcours_apprentissage/maternel_primaire_ordinaire/Organisation/Contenus_apprentissages_Maternel_Primaire/Referentiels/2022_REF_Francais-FRALA.pdf#page=80)

| Page 1 item | Answer and success feedback | Retry hint in the approved starter |
| --- | --- | --- |
| Example | `vite ↔ rapidement` (two adverbs describing how Mouna runs) | Shown before play. |
| A | `content ↔ heureux` (two adjectives). « Oui ! Sami est content : il est heureux. » | « Sami est content de gagner. Quel mot dit aussi qu’il a de la joie ? » |
| B | `commencer ↔ débuter` (two verbs). « Oui ! Le spectacle va commencer, il va débuter. » | « Le spectacle va commencer. Quel mot dit aussi qu’il va se mettre en route ? » |
| C | `joli ↔ beau` (two adjectives). « Oui ! Ce dessin est joli, il est beau. » | « Ce dessin est joli. Quel mot dit aussi qu’il est agréable à regarder ? » |

The trial correction asks for a clue that puts item B back in the context of a show. [Revision 2](../tests/fixtures/les-mots-de-meme-sens-corrige.json) uses « Les acteurs entrent en scène. Quel mot peut remplacer “commencer” ? » for B and keeps the answer key above. The correct pairing leaves the other two right-column words as distractors on the board.

## Preview and approve the reviewed revision

Use the [preview prerequisites](p1-worksheet-preview.md#agent-setup), with an Android tablet or emulator selected for `adb`. From the repository root, preview the synthetic revision.

```sh
bash scripts/preview-worksheet.sh --build tests/fixtures/les-mots-de-meme-sens-corrige.json
```

In **AppForKids · Aperçu**, open **P3** and **Les mots de même sens**. Tap **commencer**, then **beau** to check the changed hint. Tap **débuter** to retry, match the other pairs against the answer key, and finish the round. Run the same preview command without `--build` after updating the draft. The preview helper validates the draft before loading it.

After reviewing the exact revision, record approval in private storage and use the [signed release workflow](../README.md#approve-and-release-a-worksheet-game) with the printed selector.

```sh
python3 scripts/release.py approve --store "$HOME/AppForKids-private/approved" \
  tests/fixtures/les-mots-de-meme-sens-corrige.json
```

Approval prints `Approved les-mots-de-meme-sens@2`. Selecting it replaces the same game ID in a release. Selecting no revision for that ID uses the bundled revision 1. The automated worksheet preview plays revision 2 and checks its revised hint offline. The approval and packaging test checks that the exact reviewed JSON stays under the same ID alongside the P1 starter.

For authoring fields and runtime changes, see the [game mechanics extension guide](game-mechanics.md).
