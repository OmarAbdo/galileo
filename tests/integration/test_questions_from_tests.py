"""Questions from Omar's merged tests: each `assert <call> == <literal>` becomes one, shown with
the test's setup up to that line."""

import subprocess
from pathlib import Path

import pytest

from galileo.adapters.understanding.assertions import questions_in
from galileo.adapters.understanding.git_questions import GitQuestions

TESTS = """import pytest

from shapes import area, label


def helper():
    return 2


def test_area_of_a_square():
    side = helper()
    assert area(side) == 4
    assert area(3) == pytest.approx(9.0)


def test_things_that_are_no_questions():
    value = 4
    assert value == 4
    assert area(2) == helper()
    assert label("x") != "y"
"""


def test_each_assertion_on_a_call_with_a_literal_becomes_a_question() -> None:
    questions = questions_in(TESTS, "shapes: tests/test_shapes.py")
    assert [question.expression for question in questions] == ["area(side)", "area(3)"]
    assert [question.expected for question in questions] == ["4", "9.0"]
    assert questions[0].place == "shapes: tests/test_shapes.py:12"


def test_a_question_shows_the_setup_and_hides_the_answer() -> None:
    question = questions_in(TESTS, "shapes: tests/test_shapes.py")[0]
    assert question.context == (
        "def test_area_of_a_square():\n    side = helper()\n    area(side) == ?"
    )


def test_keys_are_stable_and_distinct() -> None:
    first, second = questions_in(TESTS, "shapes: tests/test_shapes.py")
    assert first.key == questions_in(TESTS, "shapes: tests/test_shapes.py")[0].key
    assert first.key != second.key


def git(folder: Path, *arguments: str) -> None:
    command = ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *arguments]
    subprocess.run(command, cwd=folder, capture_output=True, timeout=60, check=True)


@pytest.fixture(name="repository")
def merged_repository(tmp_path: Path) -> Path:
    repository = tmp_path / "shapes"
    (repository / "tests").mkdir(parents=True)
    (repository / "tests" / "test_shapes.py").write_text(TESTS, encoding="utf-8")
    (repository / "shapes.py").write_text("def area(side):\n    return side * side\n", "utf-8")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", ".")
    git(repository, "commit", "-q", "-m", "shapes")
    git(tmp_path, "init", "-q", "--bare", "origin.git")
    git(repository, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repository, "push", "-q", "origin", "main")
    git(repository, "fetch", "-q", "origin")
    return repository


def test_questions_come_from_tests_merged_on_main(repository: Path) -> None:
    (repository / "tests" / "test_unmerged.py").write_text(TESTS, encoding="utf-8")
    questions = GitQuestions([repository])()
    assert [question.place for question in questions] == [
        "shapes: tests/test_shapes.py:12",
        "shapes: tests/test_shapes.py:13",
    ]


def test_a_repository_that_isnt_there_has_no_questions(tmp_path: Path) -> None:
    assert GitQuestions([tmp_path / "missing"])() == []
