#!/usr/bin/env python3
"""Exercise the installed starter APK through Android's visible controls."""

import re
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path

PACKAGE = "be.hershalpandya.appforkids"
HIERARCHY = "/sdcard/appforkids-window.xml"


def adb(*arguments, check=True):
    return subprocess.run(
        ["adb", *arguments], capture_output=True, text=True, check=check, timeout=30
    )


def visible_matches(text, package=PACKAGE, *, absent=(), rotation=None):
    deadline = time.monotonic() + 20
    last_labels = []
    attempts = 0
    while time.monotonic() < deadline:
        adb("shell", "rm", "-f", HIERARCHY)
        dumped = adb("shell", "uiautomator", "dump", HIERARCHY, check=False)
        if dumped.returncode == 0:
            result = adb("exec-out", "cat", HIERARCHY, check=False)
            if result.returncode == 0 and result.stdout.strip().startswith("<?xml"):
                hierarchy = ET.fromstring(result.stdout)
                nodes = [
                    node
                    for node in hierarchy.iter("node")
                    if node.get("package") == package
                ]
                matches = [node for node in nodes
                           if node.get("text") == text and node.get("enabled") == "true"]
                if not matches:
                    matches = [node for node in nodes
                               if (node.get("text") or "").casefold() == text.casefold()
                               and node.get("enabled") == "true"]
                    if len({node.get("text") for node in matches}) > 1:
                        raise AssertionError(f"Ambiguous capitalization for {text!r}")
                if matches and (rotation is None or hierarchy.get("rotation") == str(rotation)):
                    parents = {child: parent for parent in hierarchy.iter() for child in parent}
                    targets = []
                    for match in matches:
                        target = match
                        while target.get("clickable") != "true" and target in parents:
                            parent = parents[target]
                            if parent.get("class") == "android.widget.ListView":
                                # Dialog list rows are selectable even when Android 35
                                # does not expose the click action in accessibility.
                                match.set("test-selectable", "true")
                                target = match
                                break
                            target = parent
                        targets.append(target if target.get("clickable") == "true" else match)
                    labels = {node.get("text") for node in nodes}
                    if unexpected := labels.intersection(absent):
                        raise AssertionError(f"Unexpected visible labels: {sorted(unexpected)!r}")
                    return targets
                last_labels = [node.get("text") for node in nodes if node.get("text")]
        # Only scroll an actual scroll container. Swiping outside an open dialog
        # dismisses it, hiding the very control we are waiting for.
        scrollable = next((node for node in nodes if node.get("scrollable") == "true"), None) if dumped.returncode == 0 and result.returncode == 0 and result.stdout.strip().startswith("<?xml") else None
        if scrollable is not None:
            left, top, right, bottom = map(int, re.findall(r"\d+", scrollable.attrib["bounds"]))
            height = bottom - top
            start, end = ((top + 3 * height // 4, top + height // 4) if attempts % 8 < 4
                          else (top + height // 4, top + 3 * height // 4))
            adb("shell", "input", "swipe", str((left + right) // 2), str(start),
                str((left + right) // 2), str(end), "300")
        attempts += 1
        time.sleep(0.2)
    raise AssertionError(f"Expected visible text {text!r}. Last app labels: {last_labels!r}")


def visible(text, package=PACKAGE, *, absent=(), rotation=None):
    return visible_matches(text, package, absent=absent, rotation=rotation)[0]


def tap(text, package=PACKAGE):
    node = visible(text, package)
    if node.get("clickable") != "true" and node.get("test-selectable") != "true":
        raise AssertionError(f"Expected a touch control for {text!r}")
    left, top, right, bottom = map(int, re.findall(r"\d+", node.attrib["bounds"]))
    adb("shell", "input", "tap", str((left + right) // 2), str((top + bottom) // 2))


def enter_text(value, package=PACKAGE):
    """Focus the visible editor and verify input before submitting its dialog."""
    deadline = time.monotonic() + 20
    tapped = False
    while time.monotonic() < deadline:
        adb("shell", "rm", "-f", HIERARCHY)
        dumped = adb("shell", "uiautomator", "dump", HIERARCHY, check=False)
        if dumped.returncode == 0:
            result = adb("exec-out", "cat", HIERARCHY, check=False)
            if result.returncode == 0 and result.stdout.strip().startswith("<?xml"):
                hierarchy = ET.fromstring(result.stdout)
                editors = [node for node in hierarchy.iter("node")
                           if node.get("package") == package
                           and node.get("class") == "android.widget.EditText"
                           and node.get("enabled") == "true"]
                if len(editors) > 1:
                    raise AssertionError("Expected a single visible text field")
                if editors:
                    editor = editors[0]
                    if editor.get("focused") == "true" and tapped:
                        adb("shell", "input", "text", value)
                        visible(value, package)
                        return
                    left, top, right, bottom = map(int, re.findall(r"\d+", editor.attrib["bounds"]))
                    adb("shell", "input", "tap", str((left + right) // 2),
                        str((top + bottom) // 2))
                    tapped = True
        time.sleep(0.2)
    raise AssertionError("Text field did not become focused")


def airplane_mode_is_on():
    result = adb("shell", "settings", "get", "global", "airplane_mode_on").stdout.strip()
    if result != "1":
        raise AssertionError(f"Expected airplane mode to be on, got {result!r}")
    wifi = adb("shell", "cmd", "wifi", "status").stdout
    if "Wifi is disabled" not in wifi:
        raise AssertionError(f"Expected Wi-Fi to be disabled, got {wifi!r}")


def play_starter():
    airplane_mode_is_on()
    launched = adb("shell", "am", "start", "-W", "-S", "-n", f"{PACKAGE}/.MainActivity")
    if "Status: ok" not in launched.stdout:
        raise AssertionError(launched.stdout + launched.stderr)
    visible("Petits Pas")
    visible("Qui va jouer ?")
    tap("Ajouter un enfant")
    visible("Combien font 7 + 5 ?")
    enter_text("11")
    tap("Vérifier")
    visible("Essaie encore.")
    adb("shell", "input", "keyevent", "KEYCODE_MOVE_END")
    adb("shell", "input", "keyevent", "KEYCODE_DEL")
    adb("shell", "input", "keyevent", "KEYCODE_DEL")
    enter_text("12")
    tap("Vérifier")
    visible("Prénom ou surnom")
    enter_text("Alice")
    tap("Ajouter")
    tap("Ajouter un enfant")
    enter_text("12")
    tap("Vérifier")
    enter_text("Alice")
    tap("Ajouter")
    visible("Ce nom existe déjà. Choisis un autre surnom.")
    adb("shell", "input", "keyevent", "KEYCODE_MOVE_END")
    for _ in range(5):
        adb("shell", "input", "keyevent", "KEYCODE_DEL")
    enter_text("Bob")
    tap("Ajouter")
    tap("Alice")
    visible("Les jeux")
    visible("Les étoiles à compter")
    visible("Les mots de même sens")
    tap("Année : Toutes")
    tap("P1")
    tap("Matière : Toutes")
    tap("Mathématiques")
    tap("Sujet : Tous")
    tap("Compter")
    visible("Compte des groupes de 1 à 10 étoiles.", absent=("Les mots de même sens", "★ Jeu terminé"))
    tap("Les étoiles à compter")
    visible("Exemple : ★ ★ ★ = 3")
    tap("Jouer")
    visible("Question 1 sur 3")
    tap("3")
    visible("Compte chaque étoile une fois, puis réessaie.")
    tap("4")
    visible("Bravo, il y a 4 étoiles !")
    tap("Suivant")
    tap("6")
    tap("Suivant")
    tap("8")
    tap("Terminer")
    visible("Partie terminée !")
    tap("Rejouer")
    visible("Question 1 sur 3")
    tap("Retour au catalogue")
    visible("★ Jeu terminé")
    visible("Compte des groupes de 1 à 10 étoiles.")
    visible("Année : P1")
    visible("Matière : Mathématiques")
    visible("Sujet : Compter")
    tap("Année : P1")
    tap("P3")
    visible("Aucun jeu pour ce choix.")
    tap("Effacer les filtres")
    tap("Année : Toutes")
    tap("P3")
    visible("Les mots de même sens", absent=("Les étoiles à compter",))
    tap("Les mots de même sens")
    visible("Exemple : vite ↔ rapidement")
    tap("Jouer")
    visible("Paires associées : 0 sur 3")
    tap("content")
    visible("Mot choisi : content")
    tap("débuter")
    visible("Sami est content de gagner. Quel mot dit aussi qu’il a de la joie ?")
    visible("Paires associées : 0 sur 3")
    tap("heureux")
    visible("Oui ! Sami est content : il est heureux.")
    visible("Paires associées : 1 sur 3")
    tap("commencer")
    tap("débuter")
    tap("joli")
    tap("beau")
    visible("Paires associées : 3 sur 3")
    tap("Terminer")
    visible("Partie terminée !")
    tap("Rejouer")
    visible("Paires associées : 0 sur 3")
    tap("Retour au catalogue")
    visible("★ Jeu terminé")
    tap("Année : P3")
    tap("P1")
    tap("Les étoiles à compter")
    tap("Jouer")
    visible("Question 1 sur 3")
    tap("4")
    visible("Bravo, il y a 4 étoiles !")
    tap("Changer d’enfant")
    tap("Bob")
    visible("Les étoiles à compter", absent=("★ Jeu terminé",))
    tap("Les étoiles à compter")
    tap("Jouer")
    visible("Question 1 sur 3", absent=("Bravo, il y a 4 étoiles !",))
    tap("4")
    tap("Suivant")
    tap("6")
    tap("Suivant")
    tap("8")
    tap("Terminer")
    tap("Retour au catalogue")
    visible("★ Jeu terminé")
    tap("Changer d’enfant")
    tap("Alice")
    tap("Effacer les filtres")
    tap("Les mots de même sens")
    tap("Jouer")
    visible("Paires associées : 0 sur 3")
    adb("shell", "am", "start", "-W", "-S", "-n", f"{PACKAGE}/.MainActivity")
    visible("Qui va jouer ?")
    visible("Alice")
    visible("Bob")
    tap("Alice")
    tap("Année : Toutes")
    tap("P1")
    visible("★ Jeu terminé")
    tap("Réinitialiser les résultats")
    enter_text("12")
    tap("Vérifier")
    tap("Annuler")
    visible("★ Jeu terminé")
    tap("Réinitialiser les résultats")
    enter_text("12")
    tap("Vérifier")
    tap("Réinitialiser")
    visible("Les étoiles à compter", absent=("★ Jeu terminé",))
    tap("Les étoiles à compter")
    tap("Jouer")
    tap("4")
    tap("Suivant")
    tap("6")
    tap("Suivant")
    tap("8")
    tap("Terminer")
    tap("Changer d’enfant")
    tap("Supprimer Bob")
    enter_text("11")
    tap("Vérifier")
    visible("Essaie encore.")
    adb("shell", "input", "keyevent", "KEYCODE_MOVE_END")
    adb("shell", "input", "keyevent", "KEYCODE_DEL")
    adb("shell", "input", "keyevent", "KEYCODE_DEL")
    enter_text("12")
    tap("Vérifier")
    visible("Supprimer Bob ?")
    tap("Annuler")
    visible("Bob")
    tap("Supprimer Bob")
    enter_text("12")
    tap("Vérifier")
    tap("Supprimer")
    visible("Alice", absent=("Bob",))
    tap("Ajouter un enfant")
    enter_text("12")
    tap("Vérifier")
    enter_text("Bob")
    tap("Ajouter")
    tap("Bob")
    visible("Les étoiles à compter", absent=("★ Jeu terminé",))
    tap("Effacer les filtres")
    tap("Les mots de même sens")
    tap("Jouer")
    visible("Paires associées : 0 sur 3")
    airplane_mode_is_on()


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: smoke_test.py REPORT_DIRECTORY")
    report_directory = Path(sys.argv[1])
    report_directory.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    failure = None
    try:
        play_starter()
    except Exception:
        failure = traceback.format_exc()
        print(failure, file=sys.stderr)

    suite = ET.Element("testsuite", name="APK smoke", tests="1", failures=str(int(bool(failure))))
    case = ET.SubElement(
        suite, "testcase", name="Pupils switch years and play both starters in airplane mode",
        time=f"{time.monotonic() - started:.2f}",
    )
    if failure:
        ET.SubElement(case, "failure", message="The installed APK failed the UI smoke test").text = failure
    ET.ElementTree(suite).write(
        report_directory / "starters-smoke.xml", encoding="utf-8", xml_declaration=True
    )
    if failure:
        return 1
    print("P1 and P3 offline APK smoke test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
