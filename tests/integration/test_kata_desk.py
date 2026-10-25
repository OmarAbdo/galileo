"""Omar's kata desk: the open kata, its folder, and the history of passes."""

import json
from datetime import date, datetime
from pathlib import Path

import pytest

from galileo.adapters.katas.bank import KataFileError
from galileo.adapters.katas.desk import FileDesk
from galileo.domain.katas.kata import Attempt, Kata

STARTED = datetime(2026, 11, 2, 9, 30, 5)
PAIRS = Kata("pairs", "python", "Pairs", "Write pairs.", 300, solution="# yours", tests="# ours")


def test_opening_a_kata_writes_its_folder_and_remembers_it(tmp_path: Path) -> None:
    desk = FileDesk(tmp_path)
    session = desk.open(PAIRS, STARTED)
    assert session.folder == tmp_path / "work" / "pairs-20261102-093005"
    assert (session.folder / "solution.py").read_text(encoding="utf-8") == "# yours"
    assert (session.folder / "test_solution.py").read_text(encoding="utf-8") == "# ours"
    assert (session.folder / "KATA.md").read_text(encoding="utf-8") == "# Pairs\n\nWrite pairs.\n"
    assert FileDesk(tmp_path).current() == session


def test_closing_forgets_the_open_kata(tmp_path: Path) -> None:
    desk = FileDesk(tmp_path)
    desk.open(PAIRS, STARTED)
    desk.close()
    assert desk.current() is None
    desk.close()


def test_the_history_reads_back_what_was_remembered(tmp_path: Path) -> None:
    desk = FileDesk(tmp_path)
    assert desk.history() == []
    desk.remember(Attempt("pairs", date(2026, 11, 2), 451.5))
    desk.remember(Attempt("words", date(2026, 11, 3), 300.0))
    assert FileDesk(tmp_path).history() == [
        Attempt("pairs", date(2026, 11, 2), 451.5),
        Attempt("words", date(2026, 11, 3), 300.0),
    ]


def test_a_corrupt_history_line_names_its_line(tmp_path: Path) -> None:
    desk = FileDesk(tmp_path)
    desk.remember(Attempt("pairs", date(2026, 11, 2), 451.5))
    with (tmp_path / "history.jsonl").open("a", encoding="utf-8") as stream:
        stream.write('{"kata": "words"}\n')
    with pytest.raises(KataFileError, match=r"history\.jsonl:2"):
        desk.history()


def test_a_corrupt_open_kata_is_refused(tmp_path: Path) -> None:
    (tmp_path / "open.json").write_text(json.dumps({"kata": "pairs"}), encoding="utf-8")
    with pytest.raises(KataFileError, match=r"open\.json"):
        FileDesk(tmp_path).current()
