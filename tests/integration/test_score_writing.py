"""Writing Omar's scores: records are appended, and a frozen baseline is never overwritten."""

import json
from datetime import date
from pathlib import Path

from galileo.adapters.storage.score_files import ScoreFiles
from galileo.domain.scoring.outcome import Kind, Record


def test_appended_records_read_back_in_order(tmp_path: Path) -> None:
    files = ScoreFiles(tmp_path)
    files.append(Kind.HANDS, Record(date(2026, 10, 26), 41.5))
    files.append(Kind.HANDS, Record(date(2026, 10, 27), 38.0))
    assert files.score(Kind.HANDS).records == (
        Record(date(2026, 10, 26), 41.5),
        Record(date(2026, 10, 27), 38.0),
    )


def test_saving_baselines_keeps_the_ones_already_frozen(tmp_path: Path) -> None:
    files = ScoreFiles(tmp_path)
    files.save_baselines({Kind.FOCUS: 90.0})
    files.save_baselines({Kind.FOCUS: 10.0, Kind.HANDS: 300.0})
    assert files.score(Kind.FOCUS).baseline == 90.0
    assert files.score(Kind.HANDS).baseline == 300.0
    saved = json.loads((tmp_path / "baseline.json").read_text(encoding="utf-8"))
    assert saved == {"focus": 90.0, "hands": 300.0}
    assert sorted(path.name for path in tmp_path.iterdir()) == ["baseline.json"]
