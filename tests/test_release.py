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

    def test_duplicate_selections_fail_before_packaging(self):
        approved = self.approve()
        self.assertEqual(0, approved.returncode, approved.stderr)
        invalid = self.build("les-jetons-a-reunir@2", "les-jetons-a-reunir@3")
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("Duplicate game ID 'les-jetons-a-reunir'", invalid.stderr)
        self.assertFalse(self.output.exists())

    def test_invalid_drafts_report_what_to_fix(self):
        for field, value, diagnostic in (
            ("year", "P3", "unsupported year"),
            ("type", "matching", "unsupported game type"),
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
        }
        games[FIXTURE.name]["questions"][1]["prompt"] = "Combien de jetons maintenant ?"
        with tempfile.TemporaryDirectory() as directory:
            apk = Path(directory) / "candidate.apk"
            with ZipFile(apk, "w") as archive:
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
