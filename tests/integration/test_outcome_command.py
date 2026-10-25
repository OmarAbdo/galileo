"""`python -m galileo.adapters.outcome`: one number for doctrine, or a refusal on bad data."""

import io
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from galileo.adapters.outcome import report

SOURCE = Path(__file__).resolve().parents[2] / "src"
TODAY = date(2026, 10, 26)
BASELINE = {"focus": 100, "understanding": 0.5, "hands": 100}


def seed(folder: Path, values: dict[str, float], baseline: dict[str, float]) -> None:
    scores = folder / "scores"
    scores.mkdir(parents=True)
    for kind, value in values.items():
        line = json.dumps({"day": TODAY.isoformat(), "value": value})
        (scores / f"{kind}.jsonl").write_text(f"{line}\n", encoding="utf-8")
    (folder / "baseline.json").write_text(json.dumps(baseline), encoding="utf-8")


def test_the_lowest_share_is_written(tmp_path: Path) -> None:
    seed(tmp_path, {"focus": 90, "understanding": 0.5, "hands": 100}, BASELINE)
    output, errors = io.StringIO(), io.StringIO()
    assert report(tmp_path, TODAY, output, errors) == 0
    assert output.getvalue() == "0.9\n"
    assert errors.getvalue() == ""


def test_bad_data_is_refused_without_a_number(tmp_path: Path) -> None:
    (tmp_path / "baseline.json").write_text("not json", encoding="utf-8")
    output, errors = io.StringIO(), io.StringIO()
    assert report(tmp_path, TODAY, output, errors) == 1
    assert output.getvalue() == ""
    assert "baseline.json" in errors.getvalue()


def test_the_command_prints_one_number() -> None:
    finished = subprocess.run(
        [sys.executable, "-m", "galileo.adapters.outcome"],
        env={**os.environ, "PYTHONPATH": str(SOURCE)},
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    lines = finished.stdout.splitlines()
    assert len(lines) == 1
    assert float(lines[0]) >= 0
