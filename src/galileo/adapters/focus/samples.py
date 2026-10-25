"""Focus samples on disk: `samples-<day>.jsonl` under `focus/`, one sample per line. A day's file
is deleted once the day is closed into a record, so only today's app names are ever kept."""

import json
from datetime import date, datetime
from pathlib import Path

from galileo.domain.focus.blocks import Sample

PREFIX = "samples-"


class FocusFileError(ValueError):
    pass


def parse_sample(path: Path, line: int, text: str) -> Sample:
    try:
        row = json.loads(text)
        return Sample(datetime.fromisoformat(row["taken"]), str(row["app"]), float(row["idle"]))
    except (ValueError, KeyError, TypeError) as problem:
        raise FocusFileError(f"{path}:{line}: not a sample ({problem})") from problem


class FileSamples:
    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def path(self, day: date) -> Path:
        return self.folder / f"{PREFIX}{day.isoformat()}.jsonl"

    def append(self, sample: Sample) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        row = {"taken": sample.taken.isoformat(), "app": sample.app, "idle": sample.idle_seconds}
        with self.path(sample.taken.date()).open("a", encoding="utf-8") as stream:
            stream.write(f"{json.dumps(row)}\n")

    def days(self) -> list[date]:
        if not self.folder.exists():
            return []
        paths = self.folder.glob(f"{PREFIX}*.jsonl")
        return sorted(date.fromisoformat(path.stem.removeprefix(PREFIX)) for path in paths)

    def samples(self, day: date) -> list[Sample]:
        path = self.path(day)
        lines = enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        return [parse_sample(path, number, text) for number, text in lines if text.strip()]

    def forget(self, day: date) -> None:
        self.path(day).unlink(missing_ok=True)
