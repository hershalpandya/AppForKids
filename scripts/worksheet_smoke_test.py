#!/usr/bin/env python3
"""Play the reviewed worksheet fixture through the installed preview APK."""

import json
import subprocess
import sys
from functools import partial
from pathlib import Path
from zipfile import ZipFile

from smoke_test import PACKAGE as RELEASE_PACKAGE
from smoke_test import adb, airplane_mode_is_on, tap, visible

PACKAGE = "be.hershalpandya.appforkids.preview"
FIXTURE = Path(__file__).resolve().parents[1] / "tests/fixtures/les-jetons-a-reunir.json"


def play_worksheet():
    airplane_mode_is_on()
    subprocess.run(["bash", "scripts/preview-worksheet.sh", str(FIXTURE)], check=True)
    see = partial(visible, package=PACKAGE)
    touch = partial(tap, package=PACKAGE)
    see("Aperçu du brouillon")
    touch("P1")
    see("Les étoiles à compter")
    touch("Les jetons à réunir")
    see("Exemple : ● ● et ● font 3 jetons.")
    touch("Jouer")
    see("Combien de jetons en tout ?")
    see("● ● ●")
    see("● ●")
    touch("4")
    see("Compte chaque jeton des deux lignes.")
    touch("5")
    see("Bravo, 3 et 2 font 5 jetons !")
    touch("Suivant")
    see("● ● ● ●")
    see("● ● ●")
    touch("8")
    see("Commence à 4 et compte encore 3 jetons.")
    touch("7")
    see("Bravo, 4 et 3 font 7 jetons !")
    touch("Terminer")
    see("Partie terminée !")
    see("Bravo, tu as répondu à toutes les questions.")
    touch("Retour au catalogue")
    see("Les jetons à réunir")
    airplane_mode_is_on()


def verify_release_isolation(apk):
    # Inspect the exact signed artifact installed by the release smoke test.
    with ZipFile(apk) as archive:
        entries = archive.namelist()
        catalogue = "assets/games/catalogue.json"
        bundled_games = json.loads(archive.read(catalogue))["games"]
        expected_assets = {catalogue, *(f"assets/games/{game}" for game in bundled_games)}
        actual_assets = {entry for entry in entries if entry.startswith("assets/")}
        if actual_assets != expected_assets or FIXTURE.name in bundled_games:
            raise AssertionError(f"Unexpected release assets: {sorted(actual_assets)}")
        for entry in entries:
            if entry.startswith("classes") and entry.endswith(".dex"):
                if b"worksheet-draft.json" in archive.read(entry):
                    raise AssertionError("Release APK can still load the preview draft")

    result = adb("shell", "run-as", RELEASE_PACKAGE, "id", check=False)
    if result.returncode == 0 or "package not debuggable" not in result.stdout + result.stderr:
        raise AssertionError("Expected the installed release APK to refuse draft injection: "
                             + result.stdout + result.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: worksheet_smoke_test.py SIGNED_RELEASE_APK")
    play_worksheet()
    print("P1 worksheet preview APK smoke test passed.")
    verify_release_isolation(sys.argv[1])
    print("Signed release APK excludes the worksheet preview.")
