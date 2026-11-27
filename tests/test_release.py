"""Exercise approval and release through the parent-facing command."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

REPO = Path(__file__).resolve().parents[1]
COMMAND = REPO / "scripts/release.py"
FIXTURE = REPO / "tests/fixtures/les-jetons-a-reunir.json"
MATCHING_FIXTURE = FIXTURE.with_name("les-mots-de-meme-sens-corrige.json")


class ReleaseTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.workspace = Path(directory.name)
        self.store = self.workspace / "approved"
        self.draft = self.workspace / "draft.json"
        self.game = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.output = self.workspace / "family.apk"
        self.command = COMMAND

    def release(self, action, *arguments, env=None):
        return subprocess.run(
            [sys.executable, self.command, action, "--store", self.store, *arguments],
            capture_output=True, text=True, cwd=REPO, env=env,
        )

    def approve(self):
        self.draft.write_text(json.dumps(self.game), encoding="utf-8")
        return self.release("approve", self.draft)

    def build(self, *games, env=None):
        selectors = [argument for game in games for argument in ("--game", game)]
        return self.release("build", "--version-code", "2", "--output", self.output, *selectors, env=env)

    def test_v2_multiple_subjects_are_validated_at_authoring_boundary(self):
        self.game.update(schemaVersion=2, vocabularyVersion=1, classification=[
            {"subject": "mathematics", "topics": ["counting"]},
            {"subject": "french", "topics": ["synonyms"]},
        ])
        accepted = self.approve()
        self.assertEqual(0, accepted.returncode, accepted.stderr)
        self.assertIn("Mathématiques", accepted.stdout)
        self.assertIn("Mots de même sens", accepted.stdout)

    def test_v2_rejects_invalid_classification_with_actionable_errors(self):
        self.game.update(schemaVersion=2, vocabularyVersion=1, classification=[
            {"subject": "mathematics", "topics": ["counting"]},
        ])
        cases = [
            ([], "at least one subject"),
            ([{"subject": "mathematics", "topics": []}], "at least 1 entries"),
            ([{"subject": "mathematics", "topics": ["counting", "counting"]}], "duplicate topic"),
            ([{"subject": "french", "topics": ["counting"]}], "unknown or mismatched topic"),
            ([{"subject": "unknown", "topics": ["counting"]}], "unknown subject"),
            ([{"subject": "french", "topics": ["synonyms"]}] * 2, "duplicate subject"),
        ]
        for value, message in cases:
            with self.subTest(value=value):
                self.game["classification"] = value
                result = self.approve()
                self.assertNotEqual(0, result.returncode)
                self.assertIn(message, result.stderr)

    def test_legacy_and_new_approvals_package_without_changing_snapshots(self):
        self.assertEqual(0, self.approve().returncode)
        legacy = self.store / "les-jetons-a-reunir@2.json"
        original = legacy.read_bytes()
        self.game = json.loads(MATCHING_FIXTURE.read_text(encoding="utf-8"))
        self.game.update(schemaVersion=2, vocabularyVersion=1, classification=[
            {"subject": "french", "topics": ["synonyms"]},
        ])
        self.assertEqual(0, self.approve().returncode)
        selection = self.workspace / "selection.json"
        selection.write_text(json.dumps({"store": str(self.store), "games": [
            "les-jetons-a-reunir@2", "les-mots-de-meme-sens@2"]}), encoding="utf-8")
        assets = self.workspace / "assets"
        result = subprocess.run([sys.executable, COMMAND, "package-catalogue", assets,
                                 "--selection", selection], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(original, legacy.read_bytes())
        self.assertEqual(self.game, json.loads((assets / "games/les-mots-de-meme-sens.json").read_text()))
        self.assertTrue((assets / "classification-v1.json").exists())

    def test_v1_classification_is_limited_to_reviewed_starter_revision(self):
        self.draft.write_text(json.dumps(self.game), encoding="utf-8")
        unknown = subprocess.run([sys.executable, COMMAND, "validate", self.draft], capture_output=True, text=True)
        self.assertEqual(0, unknown.returncode, unknown.stderr)
        self.assertIn("À classer", unknown.stdout)
        starter = REPO / "app/src/main/assets/games/compter-les-etoiles.json"
        known = subprocess.run([sys.executable, COMMAND, "validate", starter], capture_output=True, text=True)
        self.assertEqual(0, known.returncode, known.stderr)
        self.assertIn("Mathématiques → Compter", known.stdout)

    def test_a_changed_draft_needs_a_new_approval(self):
        approved = self.approve()
        self.assertEqual(0, approved.returncode, approved.stderr)
        self.assertIn("les-jetons-a-reunir@2", approved.stdout)
        self.game["title"] = "Une autre activité"
        conflict = self.approve()
        self.assertNotEqual(0, conflict.returncode)
        self.assertIn("increase the revision", conflict.stderr)
        self.game["revision"] = 3
        self.draft.write_text(json.dumps(self.game), encoding="utf-8")
        self.output.write_bytes(b"previous signed release")
        unapproved = self.build("les-jetons-a-reunir@3")
        self.assertNotEqual(0, unapproved.returncode)
        self.assertIn("les-jetons-a-reunir@3 is not approved", unapproved.stderr)
        self.assertEqual(b"previous signed release", self.output.read_bytes())

    def test_p3_matching_draft_is_approved_and_packaged_with_p1(self):
        self.game = json.loads(MATCHING_FIXTURE.read_text(encoding="utf-8"))
        approved = self.approve()
        self.assertEqual(0, approved.returncode, approved.stderr)
        self.assertIn("Approved les-mots-de-meme-sens@2", approved.stdout)

        selection = self.workspace / "selection.json"
        selection.write_text(
            json.dumps({"store": str(self.store), "games": ["les-mots-de-meme-sens@2"]}),
            encoding="utf-8",
        )
        assets = self.workspace / "assets"
        packaged = subprocess.run(
            [sys.executable, COMMAND, "package-catalogue", assets, "--selection", selection],
            capture_output=True, text=True, cwd=REPO,
        )
        self.assertEqual(0, packaged.returncode, packaged.stderr)
        games = assets / "games"
        catalogue = json.loads((games / "catalogue.json").read_text(encoding="utf-8"))
        self.assertIn("compter-les-etoiles.json", catalogue["games"])
        self.assertIn("les-mots-de-meme-sens.json", catalogue["games"])
        self.assertEqual(
            self.game, json.loads((games / "les-mots-de-meme-sens.json").read_text(encoding="utf-8"))
        )

    def test_validation_rejects_indistinguishable_matching_tiles(self):
        self.game = json.loads(MATCHING_FIXTURE.read_text(encoding="utf-8"))
        self.game["pairs"][2]["right"] = " heureux "
        self.draft.write_text(json.dumps(self.game), encoding="utf-8")
        checked = subprocess.run(
            [sys.executable, COMMAND, "validate", self.draft],
            capture_output=True, text=True, cwd=REPO,
        )
        self.assertNotEqual(0, checked.returncode)
        self.assertIn("pair 3.right: use distinct labels", checked.stderr)

    def test_duplicate_selections_fail_before_packaging(self):
        approved = self.approve()
        self.assertEqual(0, approved.returncode, approved.stderr)
        invalid = self.build("les-jetons-a-reunir@2", "les-jetons-a-reunir@3")
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("Duplicate game ID 'les-jetons-a-reunir'", invalid.stderr)
        self.assertFalse(self.output.exists())

    def test_invalid_drafts_report_what_to_fix(self):
        for field, value, diagnostic in (
            ("year", "P2", "unsupported year"),
            ("type", "drag", "unsupported game type"),
            ("title", None, "missing field 'title'"),
        ):
            with self.subTest(field=field):
                original = self.game.pop(field)
                if value is not None:
                    self.game[field] = value
                invalid = self.approve()
                self.game[field] = original
                self.assertNotEqual(0, invalid.returncode)
                self.assertIn(diagnostic, invalid.stderr)
        self.game["questions"][0]["answer"] = "9"
        invalid = self.approve()
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("question 1.answer: must match one of the choices", invalid.stderr)
        self.assertFalse(self.store.exists())

    def test_canonically_equivalent_choices_cannot_be_approved(self):
        self.game["questions"][0].update(choices=["é", "e\u0301", "a"], answer="é")
        invalid = self.approve()
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("question 1.choices: use distinct choices", invalid.stderr)
        self.assertFalse(self.store.exists())

    def isolated_starter(self):
        self.command = self.workspace / "scripts/release.py"
        self.command.parent.mkdir()
        shutil.copyfile(COMMAND, self.command)
        games = self.workspace / "app/src/main/assets/games"
        shutil.copytree(REPO / "app/src/main/assets/games", games)
        shutil.copyfile(REPO / "app/src/main/assets/classification-v1.json", games.parent / "classification-v1.json")
        shutil.copyfile(
            REPO / "app/starter-approvals.json", self.workspace / "app/starter-approvals.json"
        )
        return games / "compter-les-etoiles.json"

    def test_receipt_errors_identify_unsupported_fields(self):
        approved = self.approve()
        self.assertEqual(0, approved.returncode, approved.stderr)
        snapshot = self.store / "les-jetons-a-reunir@2.json"
        receipt = json.loads(snapshot.read_text(encoding="utf-8"))
        receipt["extra"] = "invalid"
        snapshot.write_text(json.dumps(receipt), encoding="utf-8")

        invalid = self.build("les-jetons-a-reunir@2")
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn(f"{snapshot}: unsupported field 'extra'", invalid.stderr)
        self.assertNotIn("visualRows", invalid.stderr)

    def test_packaging_rejects_an_invalid_store_even_without_selected_games(self):
        selection = self.workspace / "selection.json"
        selection.write_text(json.dumps({"store": [], "games": []}), encoding="utf-8")
        invalid = subprocess.run(
            [sys.executable, COMMAND, "package-catalogue", self.workspace / "assets",
             "--selection", selection],
            capture_output=True, text=True, cwd=REPO,
        )
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn(f"{selection}: store: expected nonempty text", invalid.stderr)

    def test_editing_vocabulary_v1_stops_packaging(self):
        self.isolated_starter()
        vocabulary = self.workspace / "app/src/main/assets/classification-v1.json"
        data = json.loads(vocabulary.read_text(encoding="utf-8"))
        data["subjects"]["french"]["label"] = "Modifié"
        vocabulary.write_text(json.dumps(data), encoding="utf-8")
        result = self.build()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("retain version 1", result.stderr)

    def test_editing_the_bundled_starter_requires_approval(self):
        starter = self.isolated_starter()
        changed = json.loads(starter.read_text(encoding="utf-8"))
        changed["title"] = "Une modification non approuvée"
        starter.write_text(json.dumps(changed), encoding="utf-8")
        failed = self.build()
        self.assertNotEqual(0, failed.returncode)
        self.assertIn("restore the approved starter", failed.stderr)

    def test_packaging_catches_a_missing_starter_asset(self):
        starter = self.isolated_starter()
        starter.unlink()
        failed = self.build()
        self.assertNotEqual(0, failed.returncode)
        self.assertIn("missing game asset", failed.stderr)
        self.assertIn(starter.name, failed.stderr)

    def test_missing_approved_snapshot_is_reported_as_a_missing_asset(self):
        approved = self.approve()
        self.assertEqual(0, approved.returncode, approved.stderr)
        unavailable = self.build("les-jetons-a-reunir@1")
        self.assertNotEqual(0, unavailable.returncode)
        self.assertIn("missing approval asset", unavailable.stderr)
        self.assertIn("les-jetons-a-reunir@1.json", unavailable.stderr)

    def test_signing_failure_leaves_previous_apk_in_place(self):
        approved = self.approve()
        self.assertEqual(0, approved.returncode, approved.stderr)
        self.output.write_bytes(b"previous signed release")
        environment = {key: value for key, value in os.environ.items()
                       if key != "APPFORKIDS_KEYSTORE"}
        failed = self.build("les-jetons-a-reunir@2", env=environment)
        self.assertNotEqual(0, failed.returncode)
        self.assertIn("APPFORKIDS_KEYSTORE", failed.stderr)
        self.assertEqual(b"previous signed release", self.output.read_bytes())


class ReleaseCatalogueTest(unittest.TestCase):
    def test_apk_verification_rejects_an_edited_prompt_at_the_same_revision(self):
        fixtures = FIXTURE.parent
        games = {
            "compter-les-etoiles.json": json.loads(
                (fixtures / "compter-les-etoiles-corrige.json").read_text(encoding="utf-8")
            ),
            FIXTURE.name: json.loads(FIXTURE.read_text(encoding="utf-8")),
            "les-mots-de-meme-sens.json": json.loads(
                (REPO / "app/src/main/assets/games/les-mots-de-meme-sens.json").read_text(
                    encoding="utf-8"
                )
            ),
        }
        games[FIXTURE.name]["questions"][1]["prompt"] = "Combien de jetons maintenant ?"
        with tempfile.TemporaryDirectory() as directory:
            apk = Path(directory) / "candidate.apk"
            with ZipFile(apk, "w") as archive:
                archive.writestr("assets/classification-v1.json", (REPO / "app/src/main/assets/classification-v1.json").read_bytes())
                archive.writestr("assets/games/catalogue.json", json.dumps({"games": list(games)}))
                for name, game in games.items():
                    archive.writestr(f"assets/games/{name}", json.dumps(game))
            checked = subprocess.run(
                [
                    sys.executable, "-c",
                    "import sys\n"
                    "from release_smoke_test import verify_catalogue\n"
                    "verify_catalogue(sys.argv[1])",
                    apk,
                ],
                cwd=REPO / "scripts", capture_output=True, text=True,
            )

        self.assertNotEqual(0, checked.returncode)
        self.assertIn(f"{FIXTURE.name} differs from its approved fixture", checked.stderr)


if __name__ == "__main__":
    unittest.main()
