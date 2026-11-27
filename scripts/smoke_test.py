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
                matches = [
                    node for node in nodes
                    if node.get("text") == text and node.get("enabled") == "true"
                ]
                if matches and (rotation is None or hierarchy.get("rotation") == str(rotation)):
                    labels = {node.get("text") for node in nodes}
                    if unexpected := labels.intersection(absent):
                        raise AssertionError(f"Unexpected visible labels: {sorted(unexpected)!r}")
                    return matches
                last_labels = [node.get("text") for node in nodes if node.get("text")]
        time.sleep(0.5)
    raise AssertionError(f"Expected visible text {text!r}. Last app labels: {last_labels!r}")


def visible(text, package=PACKAGE, *, absent=(), rotation=None):
    return visible_matches(text, package, absent=absent, rotation=rotation)[0]


def tap(text, package=PACKAGE):
    node = visible(text, package)
    if node.get("clickable") != "true":
        raise AssertionError(f"Expected a touch control for {text!r}")
    left, top, right, bottom = map(int, re.findall(r"\d+", node.attrib["bounds"]))
    adb("shell", "input", "tap", str((left + right) // 2), str((top + bottom) // 2))


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
    visible("Qui va jouer ?")
    tap("Ajouter un enfant")
    visible("Combien font 7 + 5 ?")
    adb("shell", "input", "text", "11")
    tap("Vérifier")
    visible("Essaie encore.")
    adb("shell", "input", "keyevent", "KEYCODE_MOVE_END")
    adb("shell", "input", "keyevent", "KEYCODE_DEL")
    adb("shell", "input", "keyevent", "KEYCODE_DEL")
    adb("shell", "input", "text", "12")
    tap("Vérifier")
    visible("Prénom ou surnom")
    adb("shell", "input", "text", "Alice")
    tap("Ajouter")
    tap("Ajouter un enfant")
    adb("shell", "input", "text", "12")
    tap("Vérifier")
    adb("shell", "input", "text", "Alice")
    tap("Ajouter")
    visible("Ce nom existe déjà. Choisis un autre surnom.")
    adb("shell", "input", "keyevent", "KEYCODE_MOVE_END")
    for _ in range(5):
        adb("shell", "input", "keyevent", "KEYCODE_DEL")
    adb("shell", "input", "text", "Bob")
    tap("Ajouter")
    tap("Alice")
    visible("Choisis ton année")
    tap("P1")
    visible("Compte des groupes de 1 à 10 étoiles.", absent=("Les mots de même sens",))
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
    visible("Compte des groupes de 1 à 10 étoiles.")
    tap("Changer d’année")
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
    tap("Changer d’année")
    tap("P1")
    tap("Les étoiles à compter")
    tap("Jouer")
    visible("Question 1 sur 3")
    tap("4")
    visible("Bravo, il y a 4 étoiles !")
    tap("Changer d’enfant")
    tap("Bob")
    tap("P1")
    tap("Les étoiles à compter")
    tap("Jouer")
    visible("Question 1 sur 3", absent=("Bravo, il y a 4 étoiles !",))
    tap("Changer d’enfant")
    tap("Alice")
    tap("P3")
    tap("Les mots de même sens")
    tap("Jouer")
    visible("Paires associées : 0 sur 3")
    adb("shell", "am", "start", "-W", "-S", "-n", f"{PACKAGE}/.MainActivity")
    visible("Qui va jouer ?")
    visible("Alice")
    visible("Bob")
    tap("Supprimer Bob")
    adb("shell", "input", "text", "11")
    tap("Vérifier")
    visible("Essaie encore.")
    adb("shell", "input", "keyevent", "KEYCODE_MOVE_END")
    adb("shell", "input", "keyevent", "KEYCODE_DEL")
    adb("shell", "input", "keyevent", "KEYCODE_DEL")
    adb("shell", "input", "text", "12")
    tap("Vérifier")
    visible("Supprimer Bob ?")
    tap("Annuler")
    visible("Bob")
    tap("Supprimer Bob")
    adb("shell", "input", "text", "12")
    tap("Vérifier")
    tap("Supprimer")
    visible("Alice", absent=("Bob",))
    tap("Ajouter un enfant")
    adb("shell", "input", "text", "12")
    tap("Vérifier")
    adb("shell", "input", "text", "Bob")
    tap("Ajouter")
    tap("Bob")
    tap("P3")
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
