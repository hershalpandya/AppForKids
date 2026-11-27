#!/usr/bin/env python3
"""Installed release APK regressions; run on an isolated, rootable emulator.

This test replaces the app's private preferences with disposable fixtures. It must
never be run on a device containing family data. The app remains offline.
"""
import html
import json
import tempfile

from smoke_test import PACKAGE, adb, airplane_mode_is_on, tap, visible

PREFS = f"/data/user/0/{PACKAGE}/shared_prefs/MainActivity.xml"


def seed(profiles, results):
    adb("shell", "am", "force-stop", PACKAGE)
    xml = '<map><string name="children">' + html.escape(json.dumps(profiles), quote=False)
    xml += '</string><string name="results">' + html.escape(results, quote=False) + '</string></map>'
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
    adb("shell", "am", "start", "-W", "-n", f"{PACKAGE}/.MainActivity")


def parent():
    adb("shell", "input", "text", "12")
    tap("Vérifier")


def main():
    airplane_mode_is_on()
    if adb("shell", "id", "-u").stdout.strip() != "0":
        raise SystemExit("Run adb root on an isolated emulator before this test")
    original = adb("shell", "wm", "user-rotation").stdout.split()
    adb("shell", "wm", "user-rotation", "lock", "0")
    profiles = [{"id": "a", "name": "I"}, {"id": "b", "name": "ı"}]
    seed(profiles, "{}")
    visible("I")
    visible("ı", absent=("Impossible de lire les profils. Ferme et rouvre l’application. Les données n’ont pas été remplacées.",))
    tap("I")
    tap("Année : Toutes")
    tap("P1")
    tap("Matière : Toutes")
    tap("Mathématiques")
    tap("Sujet : Tous")
    tap("Compter")
    tap("Changer d’enfant")
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
    results = json.dumps({"a": {"compter-les-etoiles": {"revision": 1, "count": 3}}, "b": "damaged"})
    seed(profiles, results)
    tap("Alice")
    tap("Réparer les résultats endommagés")
    parent()
    visible("Réparer les résultats ?")
    tap("Annuler")
    visible("Réparer les résultats endommagés")
    tap("Réparer les résultats endommagés")
    parent()
    tap("Réparer")
    visible("★ Jeu terminé")
    tap("Changer d’enfant")
    tap("Supprimer Bob")
    parent()
    tap("Supprimer")
    visible("Alice", absent=("Bob",))

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
