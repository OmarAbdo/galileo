"""The outcome: the lowest of Omar's three shares of his baseline, so no score covers another."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

WINDOW_DAYS = 7


class Kind(Enum):
    FOCUS = "focus"
    UNDERSTANDING = "understanding"
    HANDS = "hands"


# Hands is the time Omar needs to pass a kata, so less is better.
LOWER_IS_BETTER = frozenset({Kind.HANDS})


@dataclass(frozen=True)
class Record:
    day: date
    value: float


@dataclass(frozen=True)
class Score:
    kind: Kind
    baseline: float | None
    records: tuple[Record, ...] = ()


def in_window(records: Iterable[Record], today: date) -> list[Record]:
    """The records of the last WINDOW_DAYS days, today included."""
    first = today - timedelta(days=WINDOW_DAYS - 1)
    return [record for record in records if first <= record.day <= today]


def recent(records: Iterable[Record], today: date) -> list[float]:
    return [record.value for record in in_window(records, today)]


def weekly_mean(score: Score, today: date) -> float | None:
    values = recent(score.records, today)
    return sum(values) / len(values) if values else None


def share(score: Score, today: date) -> float:
    """The weekly mean as a share of the baseline: 1 is the baseline, more is better."""
    mean = weekly_mean(score, today)
    if score.baseline is None or score.baseline <= 0 or mean is None:
        return 0.0
    if score.kind in LOWER_IS_BETTER:
        return score.baseline / mean if mean > 0 else 0.0
    return mean / score.baseline


def outcome(scores: Mapping[Kind, Score], today: date) -> float:
    """The lowest share; a kind without data counts as 0."""
    return min(share(scores[kind], today) if kind in scores else 0.0 for kind in Kind)
