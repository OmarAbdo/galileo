"""Running a Python kata's tests with the standard library's unittest, in its own process."""

from pathlib import Path

from galileo.adapters.katas.runner import UnittestRunner

TESTS = """
import unittest

from solution import double


class DoubleTest(unittest.TestCase):
    def test_it_doubles(self) -> None:
        self.assertEqual(double(21), 42)
"""


def kata_folder(folder: Path, solution: str, tests: str = TESTS) -> Path:
    (folder / "solution.py").write_text(solution, encoding="utf-8")
    (folder / "test_solution.py").write_text(tests, encoding="utf-8")
    return folder


def test_a_right_solution_passes(tmp_path: Path) -> None:
    folder = kata_folder(tmp_path, "def double(number):\n    return number * 2\n")
    result = UnittestRunner().run(folder, "python")
    assert result.passed
    assert "OK" in result.output


def test_a_wrong_solution_fails_with_the_reason(tmp_path: Path) -> None:
    folder = kata_folder(tmp_path, "def double(number):\n    return number + 2\n")
    result = UnittestRunner().run(folder, "python")
    assert not result.passed
    assert "23 != 42" in result.output


def test_a_folder_without_tests_doesnt_pass(tmp_path: Path) -> None:
    folder = kata_folder(tmp_path, "def double(number):\n    return number * 2\n", tests="")
    assert not UnittestRunner().run(folder, "python").passed


def test_another_language_has_no_runner_yet(tmp_path: Path) -> None:
    result = UnittestRunner().run(tmp_path, "go")
    assert not result.passed
    assert "no runner for go" in result.output
