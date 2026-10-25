"""Running a kata's tests in each language Omar works in, with the toolchain installed on the PC.
A language whose toolchain is missing here is skipped, with the reason."""

from pathlib import Path

import pytest

from galileo.adapters.katas.languages import LANGUAGES, missing_toolchain
from galileo.adapters.katas.runner import KataRunner

# For each language: a right solution, a wrong one, and tests that tell them apart.
CASES = {
    "go": (
        "package kata\n\nfunc Double(number int) int { return number * 2 }\n",
        "package kata\n\nfunc Double(number int) int { return number + 2 }\n",
        'package kata\n\nimport "testing"\n\nfunc TestDouble(t *testing.T) {\n'
        "\tif got := Double(21); got != 42 {\n"
        '\t\tt.Fatalf("Double(21) = %d, want 42", got)\n\t}\n}\n',
    ),
    "java": (
        "public class Solution {\n    static int twice(int number) { return number * 2; }\n}\n",
        "public class Solution {\n    static int twice(int number) { return number + 2; }\n}\n",
        "public class SolutionTest {\n    public static void main(String[] args) {\n"
        "        int got = Solution.twice(21);\n"
        '        if (got != 42) { System.out.println("twice(21) = " + got); System.exit(1); }\n'
        '        System.out.println("OK");\n    }\n}\n',
    ),
    "typescript": (
        "export function double(number: number): number {\n  return number * 2;\n}\n",
        "export function double(number: number): number {\n  return number + 2;\n}\n",
        'import { test } from "node:test";\nimport assert from "node:assert/strict";\n'
        'import { double } from "./solution.ts";\n\n'
        'test("double", () => {\n  assert.equal(double(21), 42);\n});\n',
    ),
}


def folder_with(tmp_path: Path, language: str, solution: str, tests: str) -> Path:
    files = LANGUAGES[language]
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / files.solution).write_text(solution, encoding="utf-8")
    (tmp_path / files.tests).write_text(tests, encoding="utf-8")
    for name, text in files.extra:
        (tmp_path / name).write_text(text, encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("language", sorted(CASES))
def test_a_right_solution_passes_and_a_wrong_one_fails(tmp_path: Path, language: str) -> None:
    reason = missing_toolchain(language)
    if reason:
        pytest.skip(reason)
    right, wrong, tests = CASES[language]
    runner = KataRunner()
    assert runner.run(folder_with(tmp_path / "right", language, right, tests), language).passed
    result = runner.run(folder_with(tmp_path / "wrong", language, wrong, tests), language)
    assert not result.passed
    assert "23" in result.output


def test_every_language_omar_works_in_is_there() -> None:
    assert sorted(LANGUAGES) == ["go", "java", "python", "typescript"]


def test_a_missing_program_is_a_failed_run_with_the_reason(tmp_path: Path) -> None:
    result = KataRunner(LANGUAGES | {"go": LANGUAGES["go"].using("no-such-go")}).run(tmp_path, "go")
    assert not result.passed
    assert "no-such-go isn't installed" in result.output


def test_python_is_never_missing() -> None:
    assert missing_toolchain("python") is None
