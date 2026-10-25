"""The baseline: a normal week, frozen once per kind, and measured on enough days to count."""

from datetime import date, timedelta

import pytest

from galileo.domain.scoring.baseline import baselines_to_freeze, days_measured, frozen_value
from galileo.domain.scoring.outcome import Kind, Record, Score

TODAY = date(2026, 11, 1)


def week(kind: Kind, baseline: float | None, *values: float) -> Score:
    """One record a day, today first."""
    records = (Record(TODAY - timedelta(days=age), value) for age, value in enumerate(values))
    return Score(kind, baseline, tuple(records))


def test_days_measured_counts_different_days_of_the_last_week() -> None:
    twice_today = Score(Kind.HANDS, None, (Record(TODAY, 30.0), Record(TODAY, 50.0)))
    assert days_measured(twice_today, TODAY) == 1
    assert days_measured(week(Kind.HANDS, None, 1, 2, 3, 4, 5, 6, 7, 8), TODAY) == 7


def test_the_frozen_value_is_the_mean_of_the_last_week() -> None:
    assert frozen_value(week(Kind.FOCUS, None, 60, 90, 120), TODAY) == pytest.approx(90.0)


def test_fewer_than_three_days_is_not_enough() -> None:
    assert frozen_value(week(Kind.FOCUS, None, 60, 90), TODAY) is None


def test_only_kinds_without_a_baseline_are_frozen() -> None:
    scores = {
        Kind.FOCUS: week(Kind.FOCUS, None, 60, 90, 120),
        Kind.HANDS: week(Kind.HANDS, 300.0, 100, 100, 100),
        Kind.UNDERSTANDING: week(Kind.UNDERSTANDING, None, 1, 0),
    }
    assert baselines_to_freeze(scores, TODAY) == {Kind.FOCUS: pytest.approx(90.0)}


def test_a_zero_week_is_not_frozen_because_it_can_never_be_divided_by() -> None:
    scores = {Kind.UNDERSTANDING: week(Kind.UNDERSTANDING, None, 0, 0, 0)}
    assert baselines_to_freeze(scores, TODAY) == {}
