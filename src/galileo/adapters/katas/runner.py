"""Runs a kata's tests with the standard library's unittest, in a process of its own, so Omar's
solution can't touch Galileo and needs nothing installed."""

import subprocess
import sys
from pathlib import Path

from galileo.application.katas import RunResult

TIMEOUT_SECONDS = 120
REPORT_LINES = 30


class UnittestRunner:
    def run(self, folder: Path, language: str) -> RunResult:
        if language != "python":
            return RunResult(passed=False, output=f"no runner for {language} yet")
        command = [sys.executable, "-I", "-m", "unittest", "discover", "-s", ".", "-t", "."]
        try:
            finished = subprocess.run(
                command,
                cwd=folder,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return RunResult(passed=False, output=f"the tests ran over {TIMEOUT_SECONDS} s")
        lines = f"{finished.stdout}{finished.stderr}".strip().splitlines()
        return RunResult(finished.returncode == 0, "\n".join(lines[-REPORT_LINES:]))
