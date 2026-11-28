#!/usr/bin/env python3
"""Run the installed-app suites in a reproducible shuffled order.

Each suite starts from cleared app data, so a passing run in any order shows the
suites do not depend on state left by another. Run on the disposable, rooted,
offline emulator prepared by test-apk-on-emulator.sh.
"""

import argparse
import random
import sys
from collections.abc import Callable
from pathlib import Path

import review_regression
import smoke_test
from smoke_test import PACKAGE, adb, stop_app


def clear_app() -> None:
    stop_app()
    cleared = adb("shell", "pm", "clear", PACKAGE)
    if "Success" not in cleared.stdout:
        raise AssertionError(cleared.stdout + cleared.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, type=int, help="reproducible shuffle seed")
    parser.add_argument("reports", type=Path, help="directory for the smoke test report")
    args = parser.parse_args()
    suites: list[tuple[str, Callable[[], int | None]]] = [
        ("review regressions", review_regression.main),
        ("starter smoke test", lambda: smoke_test.run(args.reports)),
    ]
    random.Random(args.seed).shuffle(suites)
    print(f"Installed-app suite order for seed {args.seed}: {[name for name, _ in suites]}")
    for name, suite in suites:
        clear_app()
        print(f"Running {name}", flush=True)
        if suite():
            return 1
    stop_app()
    return 0


if __name__ == "__main__":
    sys.exit(main())
