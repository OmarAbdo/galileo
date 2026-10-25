"""Turning finished days of samples into focus records."""

from datetime import date
from typing import Protocol

from galileo.domain.focus.blocks import Sample, focus_minutes, worked
from galileo.domain.scoring.outcome import Kind, Record


class SampleStore(Protocol):
    def days(self) -> list[date]: ...

    def samples(self, day: date) -> list[Sample]: ...

    def forget(self, day: date) -> None: ...


class Recorder(Protocol):
    def append(self, kind: Kind, record: Record) -> None: ...


def close_days(
    store: SampleStore, recorder: Recorder, work_apps: frozenset[str], today: date
) -> dict[date, float]:
    """Each day before today becomes one record, unless it was a day off; then its samples are
    forgotten, so only app names of the current day are ever kept."""
    recorded = {}
    for day in store.days():
        if day >= today:
            continue
        samples = store.samples(day)
        if worked(samples, work_apps):
            recorded[day] = focus_minutes(samples, work_apps)
            recorder.append(Kind.FOCUS, Record(day, recorded[day]))
        store.forget(day)
    return recorded
