#!/usr/bin/env python3
"""Approve an exact P1 game revision and build a signed family APK."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STARTER = REPO / "app/src/main/assets/games"
STARTER_APPROVALS = REPO / "app/starter-approvals.json"
GAME_ID = r"[a-z0-9]+(?:-[a-z0-9]+)*"
SELECTOR = re.compile(rf"({GAME_ID})@([1-9][0-9]*)")
PACKAGE = "be.hershalpandya.appforkids"


class ReleaseError(Exception):
    pass


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReleaseError(f"Duplicate JSON field {key!r}")
        result[key] = value
    return result


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_fields)
    except (OSError, ValueError, ReleaseError) as error:
        raise ReleaseError(f"{path}: {error}") from error


def encoded(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def fields(value, required, optional, location):
    if not isinstance(value, dict):
        raise ReleaseError(f"{location}: expected a JSON object")
    for key in sorted(required - value.keys()):
        raise ReleaseError(f"{location}: missing field {key!r}")
    for key in sorted(value.keys() - required - optional):
        raise ReleaseError(f"{location}: unsupported field {key!r}; use visualRows for text or symbols")


def nonempty(value, location):
    if not isinstance(value, str) or not value.strip():
        raise ReleaseError(f"{location}: expected nonempty text")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise ReleaseError(f"{location}: expected valid UTF-8 text") from error


def text_array(value, location, minimum):
    if not isinstance(value, list) or len(value) < minimum:
        raise ReleaseError(f"{location}: expected an array with at least {minimum} entries")
    for index, item in enumerate(value, 1):
        nonempty(item, f"{location}[{index}]")


def validate_game(game, source):
    text_fields = {"title", "objective", "instructions", "workedExample"}
    fields(
        game, text_fields | {"schemaVersion", "id", "revision", "year", "type", "questions"},
        {"completionMessage"}, source,
    )
    if type(game["schemaVersion"]) is not int or game["schemaVersion"] != 1:
        raise ReleaseError(f"{source}: unsupported schemaVersion; expected 1")
    if not isinstance(game["id"], str) or not re.fullmatch(GAME_ID, game["id"]):
        raise ReleaseError(f"{source}: id must use lowercase letters or digits separated by hyphens")
    if game["id"] == "catalogue":
        raise ReleaseError(f"{source}: game id 'catalogue' is reserved")
    if type(game["revision"]) is not int or not 1 <= game["revision"] <= 2147483647:
        raise ReleaseError(f"{source}: revision must be a positive 32-bit integer")
    if game["year"] != "P1":
        raise ReleaseError(f"{source}: unsupported year {game['year']!r}; expected P1")
    if game["type"] != "tap-to-choose":
        raise ReleaseError(f"{source}: unsupported game type {game['type']!r}; expected tap-to-choose")
    for key in sorted(text_fields | ({"completionMessage"} & game.keys())):
        nonempty(game[key], f"{source}: {key}")
    if not isinstance(game["questions"], list) or not game["questions"]:
        raise ReleaseError(f"{source}: questions must contain at least one question")

    question_fields = {"prompt", "visualRows", "choices", "answer", "correctFeedback", "retryFeedback"}
    for index, question in enumerate(game["questions"], 1):
        location = f"{source}: question {index}"
        fields(question, question_fields, set(), location)
        for key in ("prompt", "answer", "correctFeedback", "retryFeedback"):
            nonempty(question[key], f"{location}.{key}")
        text_array(question["visualRows"], f"{location}.visualRows", 0)
        text_array(question["choices"], f"{location}.choices", 2)
        if len({choice.strip() for choice in question["choices"]}) != len(question["choices"]):
            raise ReleaseError(f"{location}.choices: use distinct choices")
        if question["answer"] not in question["choices"]:
            raise ReleaseError(f"{location}.answer: must match one of the choices exactly")
    return game


def starter_games():
    catalogue = STARTER / "catalogue.json"
    data = read_json(catalogue)
    fields(data, {"games"}, set(), catalogue)
    if not isinstance(data["games"], list) or not data["games"]:
        raise ReleaseError(f"{catalogue}: games must list at least one game definition")

    games = {}
    approvals = read_json(STARTER_APPROVALS)
    if not isinstance(approvals, dict):
        raise ReleaseError(f"{STARTER_APPROVALS}: expected game IDs and their approval hashes")
    for name in data["games"]:
        if (not isinstance(name, str) or name == catalogue.name
                or not re.fullmatch(rf"{GAME_ID}\.json", name)):
            raise ReleaseError(f"{catalogue}: invalid game asset name {name!r}")
        path = STARTER / name
        if not path.is_file():
            raise ReleaseError(f"{catalogue}: missing game asset {path}")
        game = validate_game(read_json(path), path)
        if game["id"] in games:
            raise ReleaseError(f"{catalogue}: duplicate game ID {game['id']!r}")
        if approvals.get(game["id"]) != receipt(game)["sha256"]:
            raise ReleaseError(
                f"{path}: restore the approved starter; approve changes as a separate revision"
            )
        games[game["id"]] = game
    for game_id in sorted(approvals.keys() - games.keys()):
        raise ReleaseError(f"{catalogue}: missing game asset for approved starter {game_id!r}")
    return games


def receipt(game):
    return {"sha256": hashlib.sha256(encoded(game)).hexdigest(), "game": game}


def approve(store, draft):
    game = validate_game(read_json(draft), draft)
    starter = starter_games().get(game["id"])
    if starter and game["revision"] <= starter["revision"]:
        raise ReleaseError(f"{draft}: increase the revision beyond the bundled starter revision")
    identifier = f"{game['id']}@{game['revision']}"
    store.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = store / f"{identifier}.json"
    approval = receipt(game)
    with tempfile.TemporaryDirectory(dir=store) as directory:
        temporary = Path(directory) / "approval.json"
        temporary.write_bytes(encoded(approval))
        try:
            os.link(temporary, target)
        except FileExistsError:
            if read_json(target) != approval:
                raise ReleaseError(f"{identifier} already has an approval; increase the revision")
    print(f"Approved {identifier}")


def release_games(store, identifiers):
    games = starter_games()
    selected = set()
    for identifier in identifiers:
        match = SELECTOR.fullmatch(identifier)
        if not match:
            raise ReleaseError(f"Invalid selection {identifier!r}; use game-id@revision")
        game_id, revision = match.groups()
        if game_id in selected:
            raise ReleaseError(f"Duplicate game ID {game_id!r}; select only one approved revision")
        selected.add(game_id)
        path = store / f"{identifier}.json"
        if not path.is_file():
            raise ReleaseError(f"{identifier} is not approved; missing approval asset {path}")
        data = read_json(path)
        fields(data, {"sha256", "game"}, set(), path)
        game = validate_game(data["game"], path)
        if (data != receipt(game) or game["id"] != game_id or str(game["revision"]) != revision):
            raise ReleaseError(f"{path}: approval does not match its game; restore the approved snapshot")
        if game_id in games and game["revision"] <= games[game_id]["revision"]:
            raise ReleaseError(f"{path}: revision must be higher than the bundled starter revision")
        games[game_id] = game
    return games


def package_catalogue(output, selection):
    store, identifiers = None, []
    if selection:
        manifest = read_json(selection)
        fields(manifest, {"store", "games"}, set(), selection)
        identifiers = manifest["games"]
        text_array(identifiers, f"{selection}: games", 0)
        if identifiers:
            nonempty(manifest["store"], f"{selection}: store")
            store = Path(manifest["store"])
    games = release_games(store, identifiers)

    assets = output / "games"
    assets.mkdir(parents=True, exist_ok=True)
    filenames = [f"{game_id}.json" for game_id in games]
    for obsolete in assets.glob("*.json"):
        if obsolete.name != "catalogue.json" and obsolete.name not in filenames:
            obsolete.unlink()
    for game_id, game in games.items():
        (assets / f"{game_id}.json").write_bytes(encoded(game))
    (assets / "catalogue.json").write_bytes(encoded({"games": filenames}))


def inspect_apk(apk, sdk_tools):
    signature = subprocess.run(
        [sdk_tools / "apksigner", "verify", "--print-certs", apk],
        check=True, capture_output=True, text=True,
    ).stdout
    certificates = re.findall(r"^Signer #\d+ certificate SHA-256 digest: (\w+)$", signature, re.M)
    manifest = subprocess.run(
        [sdk_tools / "aapt", "dump", "badging", apk],
        check=True, capture_output=True, text=True,
    ).stdout
    identity = re.search(r"^package: name='([^']+)' versionCode='(\d+)'", manifest, re.M)
    if not certificates or not identity:
        raise ReleaseError(f"{apk}: could not read the signed APK identity and version")
    return identity[1], int(identity[2]), certificates


def build_apk(args):
    if args.game and args.store is None:
        raise ReleaseError("--store is required when choosing approved games")
    release_games(args.store, args.game)
    if not 1 <= args.version_code <= 2100000000:
        raise ReleaseError("--version-code must be between 1 and 2100000000")
    if args.output.suffix != ".apk":
        raise ReleaseError("--output must end in .apk")

    for key in ("APPFORKIDS_KEYSTORE", "APPFORKIDS_KEY_ALIAS", "APPFORKIDS_STORE_PASSWORD",
                "APPFORKIDS_KEY_PASSWORD"):
        if not os.environ.get(key):
            raise ReleaseError(f"Set {key} to configure release signing; see the README")
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not sdk:
        raise ReleaseError("Set ANDROID_HOME to the Android SDK; see the README")
    sdk_tools = Path(sdk) / "build-tools/35.0.0"
    previous = inspect_apk(args.previous_apk.resolve(), sdk_tools) if args.previous_apk else None
    if previous and (previous[0] != PACKAGE or args.version_code <= previous[1]):
        raise ReleaseError(f"Use a previous {PACKAGE} APK and a version code higher than {previous[1]}")

    with tempfile.TemporaryDirectory(prefix="appforkids-release-") as directory:
        work = Path(directory)
        manifest = work / "selection.json"
        manifest.write_bytes(encoded({
            "store": str(args.store.resolve()) if args.store else None,
            "games": args.game,
        }))
        build = work / "build"
        subprocess.run([
            REPO / "gradlew", ":app:assembleRelease",
            f"-PappforkidsReleaseSelection={manifest}",
            f"-PappforkidsReleaseBuildDir={build}",
            f"-PappforkidsVersionCode={args.version_code}",
        ], cwd=REPO, check=True)
        apk = build / "outputs/apk/release/app-release.apk"
        package, version, certificates = inspect_apk(apk, sdk_tools)
        if package != PACKAGE or version != args.version_code:
            raise ReleaseError(f"{apk}: unexpected APK identity {package!r} or version {version}")
        if previous and certificates != previous[2]:
            raise ReleaseError("The update was signed with a different key from the previous APK")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=args.output.parent) as publication:
            temporary = Path(publication) / "release.apk"
            shutil.copyfile(apk, temporary)
            temporary.replace(args.output)
    print(f"Built signed {PACKAGE} version {args.version_code}: {args.output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    approval = commands.add_parser("approve", help="approve the reviewed draft")
    approval.add_argument("--store", required=True, type=Path)
    approval.add_argument("draft", type=Path)
    release = commands.add_parser("build", help="build a signed APK from selected approvals")
    release.add_argument("--store", type=Path)
    release.add_argument("--game", action="append", default=[], metavar="ID@REVISION")
    release.add_argument("--version-code", required=True, type=int)
    release.add_argument("--output", required=True, type=Path)
    release.add_argument("--previous-apk", type=Path, help="verify an update against this signed APK")
    package = commands.add_parser("package-catalogue", help="stage the game assets for Gradle")
    package.add_argument("output", type=Path)
    package.add_argument("--selection", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "approve":
            approve(args.store, args.draft)
        elif args.command == "build":
            build_apk(args)
        else:
            package_catalogue(args.output, args.selection)
    except (OSError, ReleaseError, subprocess.CalledProcessError) as error:
        print(f"Release stopped: {error}", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
