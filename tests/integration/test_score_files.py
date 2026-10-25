"""Omar's scores on disk: one JSON-lines file per kind and the frozen baseline."""

import json
from datetime import date
from pathlib import Path

import pytest

from galileo.adapters.storage.score_files import ScoreFileError, ScoreFiles
from galileo.domain.scoring.outcome import Kind, Record


def write_records(folder: Path, kind: Kind, *lines: str) -> Path:
    path = folder / "scores" / f"{kind.value}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    return path


def write_baseline(folder: Path, text: str) -> None:
    (folder / "baseline.json").write_text(text, encoding="utf-8")


def test_a_kind_is_read_with_its_baseline(tmp_path: Path) -> None:
    write_records(tmp_path, Kind.FOCUS, '{"day": "2026-10-26", "value": 95}', "")
    write_baseline(tmp_path, json.dumps({"focus": 120.5}))
    score = ScoreFiles(tmp_path).score(Kind.FOCUS)
    assert score.kind is Kind.FOCUS
    assert score.baseline == 120.5
    assert score.records == (Record(date(2026, 10, 26), 95.0),)


def test_nothing_on_disk_is_an_empty_score(tmp_path: Path) -> None:
    score = ScoreFiles(tmp_path).score(Kind.HANDS)
    assert score.baseline is None
    assert score.records == ()


def test_a_kind_missing_from_the_baseline_has_none(tmp_path: Path) -> None:
    write_baseline(tmp_path, json.dumps({"focus": 120}))
    assert ScoreFiles(tmp_path).score(Kind.HANDS).baseline is None


@pytest.mark.parametrize(
    "line",
    [
        "not json",
        '{"value": 3}',
        '{"day": "yesterday", "value": 3}',
        '{"day": "2026-10-26", "value": "3"}',
        '{"day": "2026-10-26", "value": true}',
        '{"day": "2026-10-26", "value": -1}',
        "[1, 2]",
    ],
)
def test_a_corrupt_line_names_its_file_and_line(tmp_path: Path, line: str) -> None:
    write_records(tmp_path, Kind.HANDS, '{"day": "2026-10-26", "value": 30}', line)
    with pytest.raises(ScoreFileError, match=r"hands\.jsonl:2: "):
        ScoreFiles(tmp_path).score(Kind.HANDS)


@pytest.mark.parametrize("text", ["not json", "[120]", '{"focus": 0}', '{"focus": true}'])
def test_a_corrupt_baseline_is_refused(tmp_path: Path, text: str) -> None:
    write_baseline(tmp_path, text)
    with pytest.raises(ScoreFileError, match=r"baseline\.json"):
        ScoreFiles(tmp_path).score(Kind.FOCUS)
