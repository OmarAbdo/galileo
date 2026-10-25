"""The baseline: what a normal week looked like. It is frozen once per kind, so no later week can
lower it and flatter Omar's shares, and only from a week measured on enough different days."""

from collections.abc import Mapping
from datetime import date

from galileo.domain.scoring.outcome import Kind, Score, in_window

MIN_BASELINE_DAYS = 3


def days_measured(score: Score, today: date) -> int:
    return len({record.day for record in in_window(score.records, today)})


def frozen_value(score: Score, today: date) -> float | None:
    """The mean of the last week, or None while it covers fewer than MIN_BASELINE_DAYS days."""
    if days_measured(score, today) < MIN_BASELINE_DAYS:
        return None
    records = in_window(score.records, today)
    return sum(record.value for record in records) / len(records)


def baselines_to_freeze(scores: Mapping[Kind, Score], today: date) -> dict[Kind, float]:
    """Each kind without a baseline whose week allows one. A baseline of 0 could never be divided
    by, so a week of zeros waits for a better one."""
    frozen = {}
    for kind, score in scores.items():
        value = None if score.baseline is not None else frozen_value(score, today)
        if value is not None and value > 0:
            frozen[kind] = value
    return frozen
