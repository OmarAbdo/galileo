"""`python -m galileo.adapters.cli.main`: Omar's commands, starting with `baseline`."""

import io
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from galileo.adapters.cli.commands import COMMANDS
from galileo.adapters.cli.main import run

SOURCE = Path(__file__).resolve().parents[2] / "src"
TODAY = date(2026, 11, 1)
NOW = datetime(2026, 11, 1, 12, 0)


def seed_focus(folder: Path, days: int) -> None:
    scores = folder / "scores"
    scores.mkdir(parents=True)
    lines = [
        json.dumps({"day": (TODAY - timedelta(days=age)).isoformat(), "value": 100})
        for age in range(days)
    ]
    (scores / "focus.jsonl").write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")


def test_baseline_freezes_what_a_week_allows_and_says_what_is_missing(tmp_path: Path) -> None:
    seed_focus(tmp_path, days=3)
    output = io.StringIO()
    assert run(["baseline"], tmp_path, NOW, output) == 0
    text = output.getvalue()
    assert "focus: frozen at 100" in text
    assert "hands: measured on 0 of the 3 days needed" in text
    assert json.loads((tmp_path / "baseline.json").read_text(encoding="utf-8")) == {"focus": 100.0}


def test_baseline_keeps_a_frozen_value(tmp_path: Path) -> None:
    seed_focus(tmp_path, days=3)
    (tmp_path / "baseline.json").write_text('{"focus": 80}', encoding="utf-8")
    output = io.StringIO()
    assert run(["baseline"], tmp_path, NOW, output) == 0
    assert "focus: already 80, kept" in output.getvalue()


def test_bad_data_is_reported(tmp_path: Path) -> None:
    (tmp_path / "baseline.json").write_text("not json", encoding="utf-8")
    output = io.StringIO()
    assert run(["baseline"], tmp_path, NOW, output) == 1
    assert "baseline.json" in output.getvalue()


def test_the_commands_and_their_actions() -> None:
    assert sorted(COMMANDS) == ["baseline", "kata", "score"]
    assert COMMANDS["kata"].actions == ("check", "stop")


def test_the_module_runs_and_lists_its_commands() -> None:
    finished = subprocess.run(
        [sys.executable, "-m", "galileo.adapters.cli.main", "--help"],
        env={**os.environ, "PYTHONPATH": str(SOURCE)},
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    assert "baseline" in finished.stdout
