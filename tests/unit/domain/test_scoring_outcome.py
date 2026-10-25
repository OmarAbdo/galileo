"""Omar's three scores: the last week against his baseline, and the lowest share wins."""

from datetime import date, timedelta

import pytest

from galileo.domain.scoring.outcome import (
    Kind,
    Record,
    Score,
    outcome,
    recent,
    share,
    weekly_mean,
)

TODAY = date(2026, 10, 26)


def days_ago(count: int) -> date:
    return TODAY - timedelta(days=count)


def score_of(kind: Kind, baseline: float | None, *values: float) -> Score:
    return Score(
        kind=kind, baseline=baseline, records=tuple(Record(TODAY, value) for value in values)
    )


def test_the_last_seven_days_count_today_included() -> None:
    records = [Record(days_ago(age), float(age)) for age in range(9)]
    assert recent(records, TODAY) == [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]


def test_days_after_today_dont_count() -> None:
    records = [Record(TODAY + timedelta(days=1), 5.0), Record(TODAY, 2.0)]
    assert recent(records, TODAY) == [2.0]


def test_the_weekly_mean_is_none_without_records_this_week() -> None:
    assert weekly_mean(score_of(Kind.FOCUS, None, 60.0, 90.0), TODAY) == pytest.approx(75.0)
    assert weekly_mean(score_of(Kind.FOCUS, 100.0), TODAY) is None


def test_a_share_is_the_recent_mean_over_the_baseline() -> None:
    assert share(score_of(Kind.FOCUS, 100.0, 60.0, 90.0), TODAY) == pytest.approx(0.75)


def test_hands_is_better_when_faster() -> None:
    assert share(score_of(Kind.HANDS, 300.0, 200.0, 400.0), TODAY) == pytest.approx(1.0)
    assert share(score_of(Kind.HANDS, 300.0, 150.0), TODAY) == pytest.approx(2.0)


def test_understanding_is_better_when_higher() -> None:
    assert share(score_of(Kind.UNDERSTANDING, 0.5, 1.0), TODAY) == pytest.approx(2.0)


def test_no_baseline_or_no_records_gives_zero() -> None:
    assert share(score_of(Kind.UNDERSTANDING, None, 0.5), TODAY) == 0.0
    assert share(score_of(Kind.UNDERSTANDING, 0.0, 0.5), TODAY) == 0.0
    assert share(score_of(Kind.UNDERSTANDING, -1.0, 0.5), TODAY) == 0.0
    assert share(score_of(Kind.UNDERSTANDING, 0.6), TODAY) == 0.0


def test_a_record_older_than_the_week_doesnt_count() -> None:
    old = Score(Kind.FOCUS, 100.0, (Record(days_ago(7), 100.0),))
    assert share(old, TODAY) == 0.0


def test_hands_with_a_zero_time_gives_zero() -> None:
    assert share(score_of(Kind.HANDS, 300.0, 0.0), TODAY) == 0.0


def test_hands_under_one_second_still_counts() -> None:
    assert share(score_of(Kind.HANDS, 1.0, 0.5), TODAY) == pytest.approx(2.0)


def test_the_outcome_is_the_lowest_share() -> None:
    scores = {
        Kind.FOCUS: score_of(Kind.FOCUS, 100.0, 120.0),
        Kind.UNDERSTANDING: score_of(Kind.UNDERSTANDING, 0.5, 0.4),
        Kind.HANDS: score_of(Kind.HANDS, 300.0, 250.0),
    }
    assert outcome(scores, TODAY) == pytest.approx(0.8)


def test_the_outcome_is_zero_while_a_kind_is_missing() -> None:
    scores = {Kind.FOCUS: score_of(Kind.FOCUS, 100.0, 120.0)}
    assert outcome(scores, TODAY) == 0.0
