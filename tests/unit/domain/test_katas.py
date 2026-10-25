"""Katas: which one comes next, and what a pass says about Omar's hands."""

from datetime import date, timedelta

import pytest

from galileo.domain.katas.kata import Attempt, Kata, hands_value, next_kata

TODAY = date(2026, 11, 2)


def kata(name: str, reference: int = 300) -> Kata:
    return Kata(
        name, "python", name.title(), "", reference_seconds=reference, solution="", tests=""
    )


def done(name: str, days_ago: int) -> Attempt:
    return Attempt(kata=name, day=TODAY - timedelta(days=days_ago), seconds=100.0)


def test_a_kata_never_done_comes_first() -> None:
    katas = [kata("alpha"), kata("beta")]
    assert next_kata(katas, [done("alpha", 10)]).name == "beta"


def test_then_the_one_done_longest_ago() -> None:
    katas = [kata("alpha"), kata("beta")]
    history = [done("alpha", 30), done("alpha", 2), done("beta", 5)]
    assert next_kata(katas, history).name == "beta"


def test_ties_go_by_name() -> None:
    assert next_kata([kata("beta"), kata("alpha")], []).name == "alpha"


def test_an_empty_bank_is_refused() -> None:
    with pytest.raises(ValueError, match="no katas"):
        next_kata([], [])


def test_hands_is_the_time_as_a_multiple_of_the_reference() -> None:
    assert hands_value(kata("alpha", reference=300), 450.0) == pytest.approx(1.5)


def test_an_attempt_left_open_over_an_hour_isnt_counted() -> None:
    assert hands_value(kata("alpha"), 3600.0) == pytest.approx(12.0)
    assert hands_value(kata("alpha"), 3601.0) is None


def test_a_zero_time_isnt_counted() -> None:
    assert hands_value(kata("alpha"), 0.0) is None
