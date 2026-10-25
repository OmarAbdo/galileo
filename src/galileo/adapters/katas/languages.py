"""The languages Omar practises: for each, the file he writes, the file with the tests, any other
file the toolchain needs, and the commands that run the tests. Only standard toolchains: no
test framework to install."""

import dataclasses
import shutil
import subprocess
import sys
from dataclasses import dataclass

CHECK_TIMEOUT_SECONDS = 30


@dataclass(frozen=True)
class Language:
    solution: str
    tests: str
    steps: tuple[tuple[str, ...], ...]
    extra: tuple[tuple[str, str], ...] = ()

    def using(self, program: str) -> "Language":
        """The same language run by another program, as when a toolchain moved."""
        steps = tuple((program, *step[1:]) for step in self.steps)
        return dataclasses.replace(self, steps=steps)


LANGUAGES = {
    "python": Language(
        "solution.py",
        "test_solution.py",
        ((sys.executable, "-I", "-m", "unittest", "discover", "-s", ".", "-t", "."),),
    ),
    "go": Language(
        "solution.go",
        "solution_test.go",
        (("go", "test", "./..."),),
        (("go.mod", "module kata\n\ngo 1.21\n"),),
    ),
    "java": Language(
        "Solution.java",
        "SolutionTest.java",
        (
            ("javac", "-d", "classes", "Solution.java", "SolutionTest.java"),
            ("java", "-cp", "classes", "SolutionTest"),
        ),
    ),
    "typescript": Language(
        "solution.ts",
        "solution.test.ts",
        (("node", "--experimental-strip-types", "--test", "solution.test.ts"),),
    ),
}


def missing_toolchain(language: str) -> str | None:
    """Why this PC can't run the language's katas, or None when it can."""
    programs = {step[0] for step in LANGUAGES[language].steps}
    absent = sorted(program for program in programs if shutil.which(program) is None)
    if absent:
        return f"{', '.join(absent)} isn't installed"
    if language == "typescript":
        probe = ["node", "--experimental-strip-types", "-e", ""]
        finished = subprocess.run(
            probe, capture_output=True, timeout=CHECK_TIMEOUT_SECONDS, check=False
        )
        if finished.returncode != 0:
            return "this Node can't run TypeScript yet (it needs 22.6 or newer)"
    return None
