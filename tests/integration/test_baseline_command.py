"""`galileo baseline`: what it freezes, what it keeps, and what it says is still missing."""

import io
import json
from datetime import date, timedelta
from pathlib import Path

from galileo.adapters.cli.baseline_command import baseline
from galileo.adapters.storage.score_files import ScoreFiles

TODAY = date(2026, 11, 1)


def seed(folder: Path, kind: str, value: float, days: int) -> None:
    scores = folder / "scores"
    scores.mkdir(parents=True, exist_ok=True)
    lines = [
        json.dumps({"day": (TODAY - timedelta(days=age)).isoformat(), "value": value})
        for age in range(days)
    ]
    (scores / f"{kind}.jsonl").write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")


def lines_of(folder: Path) -> list[str]:
    output = io.StringIO()
    assert baseline(ScoreFiles(folder), TODAY, output) == 0
    return output.getvalue().splitlines()


def test_each_kind_gets_one_line(tmp_path: Path) -> None:
    seed(tmp_path, "focus", 100, days=3)
    seed(tmp_path, "understanding", 0, days=3)
    seed(tmp_path, "hands", 40, days=1)
    (tmp_path / "baseline.json").write_text('{"hands": 55}', encoding="utf-8")
    assert lines_of(tmp_path) == [
        "focus: frozen at 100",
        "understanding: its last week averages 0, which can't be a baseline",
        "hands: already 55, kept",
    ]


def test_a_short_week_says_how_many_days_are_missing(tmp_path: Path) -> None:
    seed(tmp_path, "focus", 100, days=2)
    assert lines_of(tmp_path)[0] == "focus: measured on 2 of the 3 days needed in the last week"
