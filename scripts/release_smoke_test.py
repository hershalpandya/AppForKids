#!/usr/bin/env python3
"""Verify the signed update in place on a tablet with the starter installed."""

import json
import re
import sys
from zipfile import ZipFile

from smoke_test import PACKAGE, adb, airplane_mode_is_on, tap, visible, visible_matches


def verify_catalogue(apk):
    with ZipFile(apk) as archive:
        catalogue = "assets/games/catalogue.json"
        entries = json.loads(archive.read(catalogue))["games"]
        expected = {"compter-les-etoiles": 2, "les-jetons-a-reunir": 2}
        games = [json.loads(archive.read(f"assets/games/{entry}")) for entry in entries]
        actual = {game["id"]: game["revision"] for game in games}
        if len(games) != len(expected) or actual != expected:
            raise AssertionError(f"Expected one entry per approved revision {expected}, got {actual}")
        assets = {entry for entry in archive.namelist() if entry.startswith("assets/")}
        if assets != {catalogue, *(f"assets/games/{entry}" for entry in entries)}:
            raise AssertionError(f"Unexpected update assets: {sorted(assets)}")


def installed_version():
    package = adb("shell", "dumpsys", "package", PACKAGE).stdout
    version = re.search(r"versionCode=(\d+)", package)
    installed = re.search(r"firstInstallTime=(.+)", package)
    if not version or not installed:
        raise AssertionError("The family app is missing from the tablet")
    return int(version[1]), installed[1].strip()


def verify_installed_update(apk):
    airplane_mode_is_on()
    baseline_version, first_install = installed_version()
    if baseline_version != 1:
        raise AssertionError(f"Expected the installed starter v1, got v{baseline_version}")
    installed = adb("install", "-r", apk)
    if "Success" not in installed.stdout:
        raise AssertionError(installed.stdout + installed.stderr)
    if installed_version() != (2, first_install):
        raise AssertionError("Expected an in-place update to version 2")
    launched = adb("shell", "am", "start", "-W", "-S", "-n", f"{PACKAGE}/.MainActivity")
    if "Status: ok" not in launched.stdout:
        raise AssertionError(launched.stdout + launched.stderr)

    tap("P1")
    if len(visible_matches("Les étoiles à compter (corrigé)")) != 1:
        raise AssertionError("The corrected stars game must appear once in the P1 catalogue")
    tap("Les étoiles à compter (corrigé)")
    visible("Exemple corrigé : ★ ★ = 2")
    tap("Jouer")
    tap("4")
    visible("Bravo, il y a 4 étoiles !")
    tap("Retour au catalogue")

    tap("Les jetons à réunir")
    tap("Jouer")
    visible("Combien de jetons en tout ?")
    tap("5")
    visible("Bravo, 3 et 2 font 5 jetons !")
    tap("Retour au catalogue")
    visible("Les étoiles à compter (corrigé)")
    airplane_mode_is_on()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: release_smoke_test.py SIGNED_UPDATE_APK")
    verify_catalogue(sys.argv[1])
    verify_installed_update(sys.argv[1])
    print("Signed P1 update passed the offline in-place install check.")
