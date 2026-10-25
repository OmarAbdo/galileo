"""Runs a kata's tests with the language's own toolchain, in processes of their own, so Omar's
solution can't touch Galileo and needs no test framework installed."""

import subprocess
from pathlib import Path

from galileo.adapters.katas.languages import LANGUAGES, Language
from galileo.application.katas import RunResult

TIMEOUT_SECONDS = 120
REPORT_LINES = 30


def report(text: str) -> str:
    return "\n".join(text.strip().splitlines()[-REPORT_LINES:])


class KataRunner:
    def __init__(self, languages: dict[str, Language] = LANGUAGES) -> None:
        self.languages = languages

    def run(self, folder: Path, language: str) -> RunResult:
        if language not in self.languages:
            return RunResult(passed=False, output=f"no runner for {language} yet")
        output = ""
        for step in self.languages[language].steps:
            try:
                finished = subprocess.run(
                    step,
                    cwd=folder,
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT_SECONDS,
                    check=False,
                )
            except FileNotFoundError:
                return RunResult(passed=False, output=f"{step[0]} isn't installed")
            except subprocess.TimeoutExpired:
                return RunResult(passed=False, output=f"the tests ran over {TIMEOUT_SECONDS} s")
            output += f"{finished.stdout}{finished.stderr}"
            if finished.returncode != 0:
                return RunResult(passed=False, output=report(output))
        return RunResult(passed=True, output=report(output))
