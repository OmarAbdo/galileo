"""`galileo quiz`: the due questions from Omar's repositories, each answer graded and recorded."""

import io
import json
import subprocess
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest

from galileo.adapters.cli.context import Context
from galileo.adapters.cli.main import run
from galileo.adapters.cli.quiz_command import quiz
from galileo.adapters.understanding.history import FileHistory, QuizFileError
from galileo.adapters.understanding.repositories import repositories
from galileo.domain.understanding.question import Asked

NOW = datetime(2026, 11, 9, 18, 0)
TESTS = """from shapes import area


def test_area():
    side = 2
    assert area(side) == 4
    assert area(3) == 9
"""


def git(folder: Path, *arguments: str) -> None:
    command = ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *arguments]
    subprocess.run(command, cwd=folder, capture_output=True, timeout=60, check=True)


@pytest.fixture(name="data")
def data_with_a_repository(tmp_path: Path) -> Path:
    repository = tmp_path / "shapes"
    (repository / "tests").mkdir(parents=True)
    (repository / "tests" / "test_shapes.py").write_text(TESTS, encoding="utf-8")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", ".")
    git(repository, "commit", "-q", "-m", "shapes")
    git(tmp_path, "init", "-q", "--bare", "origin.git")
    git(repository, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repository, "push", "-q", "origin", "main")
    git(repository, "fetch", "-q", "origin")
    data = tmp_path / "data"
    data.mkdir()
    listed = json.dumps(str(repository))
    (data / "understanding.toml").write_text(f"repositories = [{listed}]\n", encoding="utf-8")
    return data


def answers(*given: str) -> Iterator[str]:
    return iter(given)


def quiz_with(data: Path, *given: str) -> tuple[int, str]:
    replies = answers(*given)
    output = io.StringIO()
    context = Context(data, NOW, output, ask=lambda _prompt: next(replies))
    return quiz(context), output.getvalue()


def test_each_question_shows_its_setup_and_is_graded(data: Path) -> None:
    code, text = quiz_with(data, "4", "8")
    assert code == 0
    assert "Question 1 of 2 · shapes: tests/test_shapes.py:6" in text
    assert "    side = 2\n    area(side) == ?" in text
    assert "Right." in text
    assert "Not quite: it's 9." in text
    assert text.endswith("1 of 2 right. Recorded for understanding.\n")
    lines = (data / "scores" / "understanding.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(line)["value"] for line in lines] == [1.0, 0.0]


def test_answered_questions_wait_a_week(data: Path) -> None:
    quiz_with(data, "4", "9")
    code, text = quiz_with(data)
    assert code == 0
    assert text.startswith("No questions due.")


def test_the_history_reads_back_and_refuses_a_bad_line(tmp_path: Path) -> None:
    history = FileHistory(tmp_path)
    history.remember(Asked("abc", NOW.date(), right=True))
    assert history.asked() == [Asked("abc", NOW.date(), right=True)]
    with (tmp_path / "asked.jsonl").open("a", encoding="utf-8") as stream:
        stream.write("{}\n")
    with pytest.raises(QuizFileError, match=r"asked\.jsonl:2"):
        history.asked()


def test_the_repositories_default_to_galileos_own(tmp_path: Path) -> None:
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "installed.json").write_text('{"repository": "D:/galileo"}', "utf-8")
    assert repositories(tmp_path) == [Path("D:/galileo")]
    assert "D:/galileo" in (tmp_path / "understanding.toml").read_text(encoding="utf-8")


def test_without_an_install_the_list_starts_empty(tmp_path: Path) -> None:
    assert repositories(tmp_path) == []


def test_the_command_line_knows_quiz(tmp_path: Path) -> None:
    output = io.StringIO()
    assert run(["quiz"], tmp_path, NOW, output) == 0
    assert output.getvalue().startswith("No questions due.")
