#!/usr/bin/env python3
"""Play the reviewed worksheet fixtures through the installed preview APK."""

import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from functools import partial
from pathlib import Path
from zipfile import ZipFile

from smoke_test import PACKAGE as RELEASE_PACKAGE
from smoke_test import adb, airplane_mode_is_on, tap, visible, visible_matches

PACKAGE = "be.hershalpandya.appforkids.preview"
FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures"
P1_FIXTURE = FIXTURES / "les-jetons-a-reunir.json"
P3_FIXTURE = FIXTURES / "les-mots-classifies.json"


def play_p1_worksheet():
    airplane_mode_is_on()
    subprocess.run(["bash", "scripts/preview-worksheet.sh", str(P1_FIXTURE)], check=True)
    see = partial(visible, package=PACKAGE)
    touch = partial(tap, package=PACKAGE)
    see("Petits Pas · Aperçu")
    see("Aperçu du brouillon")
    see("Les étoiles à compter")
    see("Mathématiques → Compter")
    see("À classer")
    touch("Année : Toutes")
    touch("P1")
    see("Les jetons à réunir")
    touch("Matière : Toutes")
    touch("Mathématiques")
    see("Les étoiles à compter", absent=("Les jetons à réunir",))
    touch("Effacer les filtres")
    # Place the game's tap point under the taskbar, as in the failed tablet run.
    for _ in range(5):
        see("Les jetons à réunir")
        window = "/sdcard/appforkids-preview-regression.xml"
        adb("shell", "uiautomator", "dump", window)
        hierarchy = ET.fromstring(adb("exec-out", "cat", window).stdout)
        nodes = list(hierarchy.iter("node"))
        game = next(node for node in nodes if node.get("text") == "Les jetons à réunir")
        bar = next(node for node in nodes if node.get("resource-id") == "android:id/navigationBarBackground")
        left, top, right, bottom = map(int, re.findall(r"\d+", game.attrib["bounds"]))
        nav_left, nav_top, nav_right, nav_bottom = map(int, re.findall(r"\d+", bar.attrib["bounds"]))
        x, y = (left + right) // 2, (top + bottom) // 2
        if nav_left <= x < nav_right and nav_top <= y < nav_bottom:
            break
        start = nav_top // 3
        end = min(start + nav_top - y + 20, nav_top * 3 // 4)
        adb("shell", "input", "swipe", str(x), str(start), str(x), str(end), "500")
    else:
        raise AssertionError("Could not position the worksheet button under the taskbar")
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


def play_p3_worksheet():
    airplane_mode_is_on()
    subprocess.run(["bash", "scripts/preview-worksheet.sh", str(P3_FIXTURE)], check=True)
    see = partial(visible, package=PACKAGE)
    touch = partial(tap, package=PACKAGE)
    see("Petits Pas · Aperçu")
    see("Aperçu du brouillon")
    if len(visible_matches("Les mots de même sens", PACKAGE)) != 1:
        raise AssertionError("The matching draft must replace the bundled game in the preview")
    see("Mathématiques → Compter; Français → Mots de même sens")
    touch("Sujet : Tous")
    touch("Compter")
    if len(visible_matches("Les mots de même sens", PACKAGE)) != 1:
        raise AssertionError("The draft must appear once under its counting topic")
    touch("Sujet : Compter")
    touch("Mots de même sens")
    see("Les mots de même sens", absent=("Les étoiles à compter",))
    touch("Les mots de même sens")
    touch("Jouer")
    touch("content")
    source_x = int(re.match(r"\[(\d+),", see("content").attrib["bounds"])[1])
    answer_x = int(re.match(r"\[(\d+),", see("heureux").attrib["bounds"])[1])
    if source_x >= answer_x:
        raise AssertionError("The source words must be in the physical left column")
    touch("heureux")
    touch("commencer")
    touch("beau")
    hint = "Les acteurs entrent en scène. Quel mot peut remplacer « commencer » ?"
    see(hint)

    original_rotation = adb("shell", "wm", "user-rotation").stdout.split()
    try:
        adb("shell", "wm", "user-rotation", "lock", "0")
        see(hint, rotation=0)
        adb("shell", "wm", "user-rotation", "lock", "1")
        see(hint, rotation=1)
        see("Paires associées : 1 sur 3")
        if see("commencer").get("selected") != "true":
            raise AssertionError("Recreating the matching round must restore the selected tile")
        see("Mot choisi : commencer")
    finally:
        adb("shell", "wm", "user-rotation", *original_rotation)

    touch("débuter")
    touch("joli")
    touch("beau")
    touch("Terminer")
    see("Bravo, tu as retrouvé toutes les paires de synonymes !")
    airplane_mode_is_on()


def verify_release_isolation(apk):
    # Inspect the exact signed artifact installed by the release smoke test.
    with ZipFile(apk) as archive:
        entries = archive.namelist()
        catalogue = "assets/games/catalogue.json"
        bundled_games = json.loads(archive.read(catalogue))["games"]
        expected_assets = {"assets/classification-v1.json", catalogue, *(f"assets/games/{game}" for game in bundled_games)}
        actual_assets = {entry for entry in entries if entry.startswith("assets/")}
        if actual_assets != expected_assets or {P1_FIXTURE.name, P3_FIXTURE.name}.intersection(bundled_games):
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
    play_p1_worksheet()
    play_p3_worksheet()
    print("P1 and P3 worksheet previews passed the offline APK smoke test.")
    verify_release_isolation(sys.argv[1])
    print("Signed release APK excludes the worksheet preview.")
