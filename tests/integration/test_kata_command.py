"""`galileo kata`: start the next kata or show the open one, `check` it, `stop` it."""

import io
import json
from datetime import datetime, timedelta
from pathlib import Path

from galileo.adapters.cli.context import Context
from galileo.adapters.cli.kata_command import kata_tools, run_kata
from galileo.adapters.cli.main import run
from galileo.adapters.katas.bank import TomlBank
from galileo.adapters.katas.desk import FileDesk

NOW = datetime(2026, 11, 2, 9, 0)
DOUBLE = '''
title = "Double it"
reference_seconds = 300
prompt = "Write double(number), which returns twice the number."
solution = """
def double(number):
    raise NotImplementedError
"""
tests = """
import unittest

from solution import double


class DoubleTest(unittest.TestCase):
    def test_it_doubles(self) -> None:
        self.assertEqual(double(21), 42)
"""
'''


def bank(folder: Path, *katas: tuple[str, str]) -> TomlBank:
    (folder / "bank" / "python").mkdir(parents=True)
    for name, text in katas:
        (folder / "bank" / "python" / f"{name}.toml").write_text(text, encoding="utf-8")
    return TomlBank(folder / "bank")


def command(folder: Path, action: str | None, minutes: float = 0) -> tuple[int, str]:
    output = io.StringIO()
    context = Context(folder / "data", NOW + timedelta(minutes=minutes), output, action)
    tools = kata_tools(folder / "data", TomlBank(folder / "bank"))
    return run_kata(context, tools), output.getvalue()


def solve(folder: Path) -> None:
    session = FileDesk(folder / "data" / "katas").current()
    assert session is not None
    solution = "def double(number):\n    return number * 2\n"
    (session.folder / "solution.py").write_text(solution, encoding="utf-8")


def test_starting_shows_the_kata_and_where_to_write_it(tmp_path: Path) -> None:
    bank(tmp_path, ("double", DOUBLE))
    code, text = command(tmp_path, None)
    assert code == 0
    assert "Double it (reference 5 min)" in text
    assert "Write double(number), which returns twice the number." in text
    assert "solution.py" in text
    assert "Started at 09:00." in text


def test_starting_again_shows_the_open_kata(tmp_path: Path) -> None:
    bank(tmp_path, ("double", DOUBLE))
    command(tmp_path, None)
    assert "Open since 09:00 (12 min)." in command(tmp_path, None, minutes=12)[1]


def test_a_failing_check_keeps_the_kata_open(tmp_path: Path) -> None:
    bank(tmp_path, ("double", DOUBLE))
    command(tmp_path, None)
    code, text = command(tmp_path, "check", minutes=3)
    assert code == 1
    assert text.startswith("Not passing yet:")
    assert "NotImplementedError" in text


def test_a_passing_check_records_hands(tmp_path: Path) -> None:
    bank(tmp_path, ("double", DOUBLE))
    command(tmp_path, None)
    solve(tmp_path)
    code, text = command(tmp_path, "check", minutes=7.5)
    assert code == 0
    assert "Passed in 7 min 30 s: 1.50 times the reference. Recorded for hands." in text
    line = (tmp_path / "data" / "scores" / "hands.jsonl").read_text(encoding="utf-8")
    assert json.loads(line) == {"day": "2026-11-02", "value": 1.5}


def test_a_pass_after_two_hours_isnt_counted(tmp_path: Path) -> None:
    bank(tmp_path, ("double", DOUBLE))
    command(tmp_path, None)
    solve(tmp_path)
    text = command(tmp_path, "check", minutes=120)[1]
    assert "Passed in 120 min 0 s, but a kata open over an hour isn't counted." in text
    assert not (tmp_path / "data" / "scores" / "hands.jsonl").exists()


def test_checking_or_stopping_without_an_open_kata(tmp_path: Path) -> None:
    bank(tmp_path, ("double", DOUBLE))
    code, text = command(tmp_path, "check")
    assert (code, text) == (1, "no kata is open: start one with `galileo kata`\n")
    assert command(tmp_path, "stop") == (0, "No kata is open.\n")


def test_stopping_records_nothing(tmp_path: Path) -> None:
    bank(tmp_path, ("double", DOUBLE))
    command(tmp_path, None)
    assert command(tmp_path, "stop", minutes=2) == (0, "Stopped. Nothing was recorded.\n")
    assert FileDesk(tmp_path / "data" / "katas").current() is None


def test_an_empty_bank_is_reported(tmp_path: Path) -> None:
    bank(tmp_path)
    assert command(tmp_path, None) == (1, "the python kata bank is empty\n")


def test_the_command_line_knows_kata_and_its_actions(tmp_path: Path) -> None:
    output = io.StringIO()
    assert run(["kata", "stop"], tmp_path, NOW, output) == 0
    assert output.getvalue() == "No kata is open.\n"
