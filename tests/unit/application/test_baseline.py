"""Freezing the baselines that a week of measuring made possible, and nothing else."""

from collections.abc import Mapping
from datetime import date, timedelta

from galileo.application.baseline import freeze_baselines
from galileo.domain.scoring.outcome import Kind, Record, Score

TODAY = date(2026, 11, 1)


class MemoryStore:
    def __init__(self, scores: dict[Kind, Score]) -> None:
        self.scores = scores
        self.saved: list[dict[Kind, float]] = []

    def score(self, kind: Kind) -> Score:
        return self.scores.get(kind, Score(kind, None))

    def save_baselines(self, values: Mapping[Kind, float]) -> None:
        self.saved.append(dict(values))


def three_days(kind: Kind, value: float) -> Score:
    records = tuple(Record(TODAY - timedelta(days=age), value) for age in range(3))
    return Score(kind, None, records)


def test_what_can_be_frozen_is_saved_and_returned() -> None:
    store = MemoryStore({Kind.FOCUS: three_days(Kind.FOCUS, 80.0)})
    assert freeze_baselines(store, TODAY) == {Kind.FOCUS: 80.0}
    assert store.saved == [{Kind.FOCUS: 80.0}]


def test_nothing_is_saved_when_nothing_can_be_frozen() -> None:
    store = MemoryStore({})
    assert freeze_baselines(store, TODAY) == {}
    assert store.saved == []
