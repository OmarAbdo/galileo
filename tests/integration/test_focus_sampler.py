"""The sampler: a sample every 15 seconds, and each new day closes the days before it."""

import json
from datetime import datetime, timedelta
from pathlib import Path

from galileo.adapters.focus.sampler import Sampler
from galileo.adapters.focus.samples import FileSamples
from galileo.adapters.storage.score_files import ScoreFiles
from galileo.domain.focus.blocks import Sample


class Clock:
    def __init__(self, start: datetime) -> None:
        self.now = start
        self.slept: list[float] = []

    def read(self) -> datetime:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += timedelta(seconds=seconds)


def sampler(folder: Path, clock: Clock) -> Sampler:
    return Sampler(
        read=lambda now: Sample(now, "code.exe", 0.0),
        samples=FileSamples(folder / "focus"),
        scores=ScoreFiles(folder),
        now=clock.read,
        sleep=clock.sleep,
    )


def test_each_round_samples_then_waits_fifteen_seconds(tmp_path: Path) -> None:
    clock = Clock(datetime(2026, 11, 2, 9, 0))
    sampler(tmp_path, clock).run(rounds=3)
    assert clock.slept == [15, 15, 15]
    assert len(FileSamples(tmp_path / "focus").samples(clock.now.date())) == 3


def test_a_new_day_closes_yesterday_into_a_focus_record(tmp_path: Path) -> None:
    clock = Clock(datetime(2026, 11, 2, 23, 45))
    sampler(tmp_path, clock).run(rounds=4 * 15 + 1)
    line = (tmp_path / "scores" / "focus.jsonl").read_text(encoding="utf-8")
    assert json.loads(line) == {"day": "2026-11-02", "value": 15.0}
    assert FileSamples(tmp_path / "focus").days() == [clock.now.date()]
