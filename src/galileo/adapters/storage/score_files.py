"""Omar's scores on disk: `scores/<kind>.jsonl`, one record per line, and `baseline.json`, the
baseline of each kind. A bad line stops the reading instead of being skipped."""

import json
from datetime import date
from pathlib import Path

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


class ScoreFiles:
    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def score(self, kind: Kind) -> Score:
        return Score(kind=kind, baseline=self.baseline(kind), records=self.records(kind))

    def records(self, kind: Kind) -> tuple[Record, ...]:
        path = self.folder / SCORES_FOLDER / f"{kind.value}.jsonl"
        if not path.exists():
            return ()
        lines = enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        return tuple(parse_record(path, number, text) for number, text in lines if text.strip())

    def baseline(self, kind: Kind) -> float | None:
        path = self.folder / BASELINE_FILE
        if not path.exists():
            return None
        try:
            values = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as problem:
            raise ScoreFileError(path, 1, f"not JSON ({problem})") from problem
        if not isinstance(values, dict):
            raise ScoreFileError(path, 1, "not an object of baselines")
        value = values.get(kind.value)
        if value is None:
            return None
        if not is_number(value) or value <= 0:
            raise ScoreFileError(path, 1, f"{kind.value} must be a number above 0")
        return float(value)
