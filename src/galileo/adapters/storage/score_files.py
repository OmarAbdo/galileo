"""Omar's scores on disk: `scores/<kind>.jsonl`, one record per line, and `baseline.json`, the
baseline of each kind. A bad line stops the reading instead of being skipped. Records are only
appended, and a frozen baseline is never overwritten."""

import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

from galileo.domain.scoring.outcome import Kind, Record, Score

SCORES_FOLDER = "scores"
BASELINE_FILE = "baseline.json"


class ScoreFileError(ValueError):
    def __init__(self, path: Path, line: int, reason: str) -> None:
        super().__init__(f"{path}:{line}: {reason}")


def is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def parse_record(path: Path, line: int, text: str) -> Record:
    try:
        row = json.loads(text)
        day = date.fromisoformat(row["day"])
        value = row["value"]
    except (ValueError, KeyError, TypeError) as problem:
        raise ScoreFileError(path, line, f"not a record ({problem})") from problem
    if not is_number(value) or value < 0:
        raise ScoreFileError(path, line, "the value must be a number of 0 or more")
    return Record(day=day, value=float(value))


def parse_baselines(path: Path, text: str) -> dict[Kind, float]:
    try:
        values: Any = json.loads(text)
    except ValueError as problem:
        raise ScoreFileError(path, 1, f"not JSON ({problem})") from problem
    if not isinstance(values, dict):
        raise ScoreFileError(path, 1, "not an object of baselines")
    baselines = {}
    for kind in Kind:
        value = values.get(kind.value)
        if value is not None and (not is_number(value) or value <= 0):
            raise ScoreFileError(path, 1, f"{kind.value} must be a number above 0")
        if value is not None:
            baselines[kind] = float(value)
    return baselines


class ScoreFiles:
    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def score(self, kind: Kind) -> Score:
        return Score(kind=kind, baseline=self.baselines().get(kind), records=self.records(kind))

    def records(self, kind: Kind) -> tuple[Record, ...]:
        path = self.records_path(kind)
        if not path.exists():
            return ()
        lines = enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        return tuple(parse_record(path, number, text) for number, text in lines if text.strip())

    def baselines(self) -> dict[Kind, float]:
        path = self.folder / BASELINE_FILE
        if not path.exists():
            return {}
        return parse_baselines(path, path.read_text(encoding="utf-8"))

    def append(self, kind: Kind, record: Record) -> None:
        path = self.records_path(kind)
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps({"day": record.day.isoformat(), "value": record.value})
        with path.open("a", encoding="utf-8") as stream:
            stream.write(f"{line}\n")

    def save_baselines(self, values: Mapping[Kind, float]) -> None:
        """Adds new kinds to the baseline file; a kind already in it keeps its value."""
        merged = {**values, **self.baselines()}
        text = json.dumps({kind.value: merged[kind] for kind in Kind if kind in merged})
        self.folder.mkdir(parents=True, exist_ok=True)
        path = self.folder / BASELINE_FILE
        written = path.with_suffix(".writing")
        written.write_text(text, encoding="utf-8")
        written.replace(path)

    def records_path(self, kind: Kind) -> Path:
        return self.folder / SCORES_FOLDER / f"{kind.value}.jsonl"
