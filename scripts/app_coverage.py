#!/usr/bin/env python3
"""Save JaCoCo execution data from the installed coverage APK.

JaCoCo keeps execution data in the app process, so installed-app tests call
``save`` before every step that stops the process. It does nothing unless
``APPFORKIDS_COVERAGE_DIR`` names the host directory for the ``.ec`` files.
Pulling the file needs the root adb connection of the disposable test emulator.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

RECEIVER = "be.hershalpandya.appforkids.CoverageDumpReceiver"


def directory() -> Path | None:
    configured = os.environ.get("APPFORKIDS_COVERAGE_DIR")
    return Path(configured) if configured else None


def save(package: str) -> Path | None:
    """Write the running app's execution data to a new file in the coverage directory."""
    target = directory()
    if target is None:
        return None
    pid = subprocess.run(
        ["adb", "shell", "pidof", package], capture_output=True, text=True, timeout=30
    ).stdout.strip()
    if not pid:
        # A stopped process has no data left to save; the previous save holds it.
        return None
    broadcast = subprocess.run(
        ["adb", "shell", "am", "broadcast", "-n", f"{package}/{RECEIVER}"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    if "result=1" not in broadcast.stdout:
        raise AssertionError("The coverage APK did not save its data: " + broadcast.stdout)
    data = subprocess.run(
        ["adb", "exec-out", "cat", f"/data/user/0/{package}/files/coverage.ec"],
        capture_output=True,
        check=True,
        timeout=30,
    ).stdout
    if not data:
        raise AssertionError("The coverage APK saved no execution data")
    target.mkdir(parents=True, exist_ok=True)
    output = target / f"{time.time_ns()}-{pid}.ec"
    output.write_bytes(data)
    return output


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: app_coverage.py PACKAGE")
    saved = save(sys.argv[1])
    if saved:
        print(f"Saved app coverage to {saved}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
