#!/usr/bin/env python3
"""Run the release unittest suite in a reproducible shuffled order."""

import argparse
import random
import sys
import unittest
from collections.abc import Iterator
from pathlib import Path


def cases(suite: unittest.TestSuite) -> Iterator[unittest.TestCase]:
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from cases(test)
        else:
            yield test


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", required=True, type=int, help="reproducible shuffle seed")
    args = parser.parse_args()
    tests_dir = Path(__file__).resolve().parents[1] / "tests"
    discovered = unittest.defaultTestLoader.discover(str(tests_dir), pattern="test_*.py")
    tests = list(cases(discovered))
    if not tests:
        raise SystemExit("No tests discovered")
    random.Random(args.seed).shuffle(tests)
    print(f"Running {len(tests)} tests with shuffle seed {args.seed}", flush=True)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(tests))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
