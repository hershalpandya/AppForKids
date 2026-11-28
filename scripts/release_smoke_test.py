#!/usr/bin/env python3
"""Verify the signed update in place on a tablet with the starter installed."""

import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from release import encoded, read_json, unique_fields
from smoke_test import (
    PACKAGE,
    adb,
    airplane_mode_is_on,
    restart_app,
    tap,
    visible,
    visible_matches,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests/fixtures"


def verify_catalogue(apk: Path) -> None:
    approved = {
        "compter-les-etoiles.json": FIXTURES / "compter-les-etoiles-corrige.json",
        "les-jetons-a-reunir.json": FIXTURES / "les-jetons-a-reunir.json",
        "les-mots-de-meme-sens.json": FIXTURES / "les-mots-de-meme-sens-corrige.json",
    }
    catalogue = "assets/games/catalogue.json"
    with ZipFile(apk) as archive:
        entries = json.loads(archive.read(catalogue), object_pairs_hook=unique_fields)["games"]
        if not isinstance(entries, list) or sorted(entries) != sorted(approved):
            raise AssertionError(
                f"Expected one entry per approved game {sorted(approved)}, got {entries}"
            )

        assets = sorted(entry for entry in archive.namelist() if entry.startswith("assets/"))
        expected_assets = sorted(
            [
                "assets/classification-v1.json",
                catalogue,
                *(f"assets/games/{entry}" for entry in approved),
            ]
        )
        if assets != expected_assets:
            raise AssertionError(f"Expected APK assets {expected_assets}, got {assets}")

        for name, fixture in approved.items():
            game = json.loads(archive.read(f"assets/games/{name}"), object_pairs_hook=unique_fields)
            if encoded(game) != encoded(read_json(fixture)):
                raise AssertionError(f"{name} differs from its approved fixture {fixture.name}")


def installed_version() -> tuple[int, str]:
    package = adb("shell", "dumpsys", "package", PACKAGE).stdout
    version = re.search(r"versionCode=(\d+)", package)
    installed = re.search(r"firstInstallTime=(.+)", package)
    if not version or not installed:
        raise AssertionError("The family app is missing from the tablet")
    return int(version[1]), installed[1].strip()


def verify_installed_update(apk: Path) -> None:
    airplane_mode_is_on()
    baseline_version, first_install = installed_version()
    if baseline_version != 1:
        raise AssertionError(f"Expected the installed starter v1, got v{baseline_version}")
    installed = adb("install", "-r", apk)
    if "Success" not in installed.stdout:
        raise AssertionError(installed.stdout + installed.stderr)
    if installed_version() != (2, first_install):
        raise AssertionError("Expected an in-place update to version 2")
    restart_app()

    tap("Alice")
    tap("Année : Toutes")
    tap("P1")
    if len(visible_matches("Les étoiles à compter (corrigé)")) != 1:
        raise AssertionError("The corrected stars game must appear once in the P1 catalogue")
    visible("★ Ancienne version terminée")
    tap("Les étoiles à compter (corrigé)")
    visible("Exemple corrigé : ★ ★ = 2")
    tap("Jouer")
    tap("4")
    visible("Bravo, il y a 4 étoiles !")
    tap("Retour au catalogue")
    visible("★ Ancienne version terminée")
    tap("Les étoiles à compter (corrigé)")
    tap("Jouer")
    tap("4")
    tap("Suivant")
    tap("6")
    tap("Suivant")
    tap("8")
    tap("Terminer")
    tap("Retour au catalogue")
    visible("★ Jeu terminé", absent=("★ Ancienne version terminée",))

    tap("Les jetons à réunir")
    tap("Jouer")
    visible("Combien de jetons en tout ?")
    tap("5")
    visible("Bravo, 3 et 2 font 5 jetons !")
    tap("Retour au catalogue")
    visible("Les étoiles à compter (corrigé)")
    # Exercise the year filter with its tap point under the status bar.
    for _ in range(5):
        target = visible("Année : P1")
        left, top, right, bottom = map(int, re.findall(r"\d+", target.attrib["bounds"]))
        x, y = (left + right) // 2, (top + bottom) // 2
        status = re.search(
            r"type=statusBars frame=\[(\d+),(\d+)\]\[(\d+),(\d+)\] visible=true",
            adb("shell", "dumpsys", "window").stdout,
        )
        if status is None:
            raise AssertionError("Could not determine the Android status-bar bounds")
        sl, st, sr, sb = map(int, status.groups())
        if sl <= x < sr and st <= y < sb:
            break
        sizes = re.findall(r"(\d+)x(\d+)", adb("shell", "wm", "size").stdout)
        if not sizes:
            raise AssertionError("Could not determine the tablet screen size")
        _, height = map(int, sizes[-1])
        start = 3 * height // 4
        end = max(height // 4, start - (y - sb + 20))
        adb("shell", "input", "swipe", str(x), str(start), str(x), str(end), "500")
    else:
        raise AssertionError("Could not position the year filter under the status bar")
    tap("Année : P1")
    tap("P3")
    if len(visible_matches("Les mots de même sens")) != 1:
        raise AssertionError("The corrected synonyms game must appear once in the P3 catalogue")
    tap("Les mots de même sens")
    tap("Jouer")
    tap("commencer")
    tap("beau")
    visible("Les acteurs entrent en scène. Quel mot peut remplacer « commencer » ?")
    tap("débuter")
    visible("Oui ! Le spectacle va commencer, il va débuter.")
    tap("content")
    tap("heureux")
    visible("Oui ! Sami est content : il est heureux.")
    airplane_mode_is_on()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: release_smoke_test.py SIGNED_UPDATE_APK")
    verify_catalogue(Path(sys.argv[1]))
    verify_installed_update(Path(sys.argv[1]))
    print("Signed P1 and P3 updates passed the offline in-place install check.")
