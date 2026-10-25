"""Closing finished days: each becomes one focus record, and its samples are forgotten."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

import pytest

from galileo.application.focus import close_days
from galileo.domain.focus.blocks import Sample
from galileo.domain.scoring.outcome import Kind, Record

TODAY = date(2026, 11, 3)
WORK = frozenset({"code.exe"})


def minutes_on(day: date, app: str, minutes: int) -> list[Sample]:
    start = datetime(day.year, day.month, day.day, 9, 0)
    return [Sample(start + timedelta(seconds=15 * index), app, 0) for index in range(minutes * 4)]


@dataclass
class MemoryStore:
    by_day: dict[date, list[Sample]]
    forgotten: list[date] = field(default_factory=list)

    def days(self) -> list[date]:
        return sorted(self.by_day)

    def samples(self, day: date) -> list[Sample]:
        return self.by_day[day]

    def forget(self, day: date) -> None:
        self.forgotten.append(day)
        del self.by_day[day]


@dataclass
class MemoryRecorder:
    records: list[tuple[Kind, Record]] = field(default_factory=list)

    def append(self, kind: Kind, record: Record) -> None:
        self.records.append((kind, record))


def test_finished_days_are_recorded_and_forgotten_today_waits() -> None:
    monday, tuesday = TODAY - timedelta(days=2), TODAY - timedelta(days=1)
    store = MemoryStore(
        {
            monday: minutes_on(monday, "code.exe", 20),
            tuesday: minutes_on(tuesday, "code.exe", 5),
            TODAY: minutes_on(TODAY, "code.exe", 30),
        }
    )
    recorder = MemoryRecorder()
    assert close_days(store, recorder, WORK, TODAY) == {monday: 20.0, tuesday: 0.0}
    assert recorder.records == [
        (Kind.FOCUS, Record(monday, pytest.approx(20.0))),
        (Kind.FOCUS, Record(tuesday, 0.0)),
    ]
    assert store.forgotten == [monday, tuesday]
    assert store.days() == [TODAY]


def test_a_day_without_work_records_nothing_but_is_forgotten() -> None:
    sunday = TODAY - timedelta(days=1)
    store = MemoryStore({sunday: minutes_on(sunday, "game.exe", 120)})
    recorder = MemoryRecorder()
    assert close_days(store, recorder, WORK, TODAY) == {}
    assert recorder.records == []
    assert store.forgotten == [sunday]
