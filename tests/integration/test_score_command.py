"""`galileo score`: this week against the baseline, one line per kind, and the outcome."""

import io
import json
from datetime import date
from pathlib import Path

from galileo.adapters.cli.main import run
from galileo.adapters.cli.score_command import score
from galileo.adapters.storage.score_files import ScoreFiles

TODAY = date(2026, 11, 1)


def seed(folder: Path, kind: str, *values: float) -> None:
    scores = folder / "scores"
    scores.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps({"day": TODAY.isoformat(), "value": value}) for value in values]
    (scores / f"{kind}.jsonl").write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")


def test_each_kind_and_the_outcome_get_a_line(tmp_path: Path) -> None:
    seed(tmp_path, "focus", 95)
    seed(tmp_path, "understanding", 1, 0)
    (tmp_path / "baseline.json").write_text('{"focus": 100}', encoding="utf-8")
    output = io.StringIO()
    assert score(ScoreFiles(tmp_path), TODAY, output) == 0
    assert output.getvalue().splitlines() == [
        "focus: 95 min a day (baseline 100): 0.95",
        "understanding: 50% right (no baseline yet)",
        "hands: not measured this week",
        "outcome: 0.00, the lowest share (0 until every kind has a baseline)",
    ]


def test_hands_shows_seconds_and_its_share(tmp_path: Path) -> None:
    seed(tmp_path, "hands", 40, 50)
    (tmp_path / "baseline.json").write_text('{"hands": 90}', encoding="utf-8")
    output = io.StringIO()
    score(ScoreFiles(tmp_path), TODAY, output)
    assert "hands: 45.0 s a kata (baseline 90.0 s): 2.00" in output.getvalue()


def test_the_command_line_knows_score(tmp_path: Path) -> None:
    output = io.StringIO()
    assert run(["score"], tmp_path, TODAY, output) == 0
    assert output.getvalue().endswith("(0 until every kind has a baseline)\n")
