#!/usr/bin/env python3
"""Installed release APK regressions; run on an isolated, rootable emulator.

This test replaces the app's private preferences with disposable fixtures. It must
never be run on a device containing family data. The app remains offline.
"""

import html
import json
import tempfile

from smoke_test import (
    ACTIVITY,
    PACKAGE,
    SWITCH_CHILD,
    adb,
    airplane_mode_is_on,
    enter_text,
    stop_app,
    tap,
    visible,
)

# Activity.getPreferences names the file after getLocalClassName(), which keeps the
# Java package when the application ID differs from it (as in the coverage build).
_ACTIVITY_NAME = "be.hershalpandya.appforkids.MainActivity".removeprefix(f"{PACKAGE}.")
PREFS = f"/data/user/0/{PACKAGE}/shared_prefs/{_ACTIVITY_NAME}.xml"


def seed(profiles: list[dict[str, str]], results: str) -> None:
    stop_app()
    xml = '<map><string name="children">' + html.escape(json.dumps(profiles), quote=False)
    xml += (
        '</string><string name="results">' + html.escape(results, quote=False) + "</string></map>"
    )
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as fixture:
        fixture.write(xml)
        fixture.flush()
        adb("push", fixture.name, "/data/local/tmp/appforkids-regression.xml")
    owner = adb("shell", "stat", "-c", "%u:%g", f"/data/user/0/{PACKAGE}").stdout.strip()
    directory = f"/data/user/0/{PACKAGE}/shared_prefs"
    adb("shell", "mkdir", "-p", directory)
    adb("shell", "chown", owner, directory)
    adb("shell", "chmod", "771", directory)
    adb("shell", "cp", "/data/local/tmp/appforkids-regression.xml", PREFS)
    adb("shell", "chown", owner, PREFS)
    adb("shell", "chmod", "660", PREFS)
    adb("shell", "restorecon", "-R", directory)
    adb("shell", "am", "start", "-W", "-n", ACTIVITY)


def parent() -> None:
    enter_text("12")
    tap("Vérifier")


def main() -> None:
    airplane_mode_is_on()
    if adb("shell", "id", "-u").stdout.strip() != "0":
        raise SystemExit("Run adb root on an isolated emulator before this test")
    original = adb("shell", "wm", "user-rotation").stdout.split()
    adb("shell", "wm", "user-rotation", "lock", "0")
    profiles = [{"id": "a", "name": "I"}, {"id": "b", "name": "ı"}]
    seed(profiles, "{}")
    visible("I")
    visible(
        "ı",
        absent=(
            "Impossible de lire les profils. Ferme et rouvre l’application. Les données n’ont pas été remplacées.",
        ),
    )
    tap("I")
    tap("Année : Toutes")
    tap("P1")
    tap("Matière : Toutes")
    tap("Mathématiques")
    tap("Sujet : Tous")
    tap("Compter")
    tap(SWITCH_CHILD, scroll_up_first=True)
    try:
        adb("shell", "wm", "user-rotation", "lock", "1")
        visible("Qui va jouer ?", rotation=1)
        tap("ı")
        visible("Année : P1")
        visible("Matière : Mathématiques")
        visible("Sujet : Compter")
    finally:
        adb("shell", "wm", "user-rotation", *original)

    profiles = [{"id": "a", "name": "Alice"}, {"id": "b", "name": "Bob"}]
    results = json.dumps(
        {
            "a": {
                "compter-les-etoiles": {"revision": 1, "count": 3},
                "les-mots-de-meme-sens": {"revision": 1, "count": 0},
            },
            "b": "damaged",
        }
    )
    seed(profiles, results)
    tap("Alice")
    tap("Réparer les résultats endommagés")
    parent()
    visible(
        "Les résultats endommagés seront perdus. Les résultats lisibles seront conservés, y compris ceux du même enfant."
    )
    tap("Annuler")
    visible("Réparer les résultats endommagés")
    tap("Réparer les résultats endommagés")
    parent()
    tap("Réparer")
    visible("★ Jeu terminé", absent=("Réparer les résultats endommagés",))
    tap(SWITCH_CHILD, scroll_up_first=True)
    tap("Supprimer Bob")
    parent()
    tap("Supprimer")
    visible("Alice", absent=("Bob",))
    tap("Alice")
    visible("★ Jeu terminé")

    seed([{"id": "a", "name": "Alice"}], "{broken")
    tap("Réparer les résultats endommagés")
    parent()
    visible("Tous les résultats enregistrés seront perdus.")
    tap("Réparer")
    tap("Alice")
    tap("Réinitialiser les résultats")
    parent()
    tap("Réinitialiser")
    tap("Les étoiles à compter")
    tap("Jouer")
    for answer in ("4", "6", "8"):
        tap(answer)
        tap("Terminer" if answer == "8" else "Suivant")
    visible("Partie terminée !")
    airplane_mode_is_on()
    print("Installed APK recovery and session regressions passed.")


if __name__ == "__main__":
    main()
