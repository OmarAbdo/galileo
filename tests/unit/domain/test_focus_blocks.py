"""Focus blocks: unbroken runs of 10 minutes or more on work apps, from 15-second samples."""

from datetime import datetime, timedelta

import pytest

from galileo.domain.focus.blocks import Sample, focus_minutes, worked

START = datetime(2026, 11, 2, 9, 0)
WORK = frozenset({"code.exe"})


def run(app: str, minutes: float, *, after: float = 0, idle: float = 0) -> list[Sample]:
    """Samples every 15 seconds on one app, starting `after` minutes past START."""
    first = START + timedelta(minutes=after)
    count = int(minutes * 4)
    return [Sample(first + timedelta(seconds=15 * index), app, idle) for index in range(count)]


def test_a_run_of_twelve_minutes_is_a_block() -> None:
    assert focus_minutes(run("code.exe", 12), WORK) == pytest.approx(12.0)


def test_a_run_under_ten_minutes_doesnt_count() -> None:
    assert focus_minutes(run("code.exe", 9.5), WORK) == 0.0


def test_other_apps_dont_count() -> None:
    assert focus_minutes(run("chrome.exe", 30), WORK) == 0.0


def test_a_switch_longer_than_a_glance_breaks_the_block() -> None:
    samples = run("code.exe", 8) + run("chrome.exe", 1, after=8) + run("code.exe", 8, after=9)
    assert focus_minutes(samples, WORK) == 0.0


def test_a_glance_of_thirty_seconds_doesnt_break_it_and_isnt_counted() -> None:
    samples = run("code.exe", 8) + run("explorer.exe", 0.5, after=8) + run("code.exe", 8, after=8.5)
    assert focus_minutes(samples, WORK) == pytest.approx(16.0)


def test_five_idle_minutes_mean_away() -> None:
    samples = run("code.exe", 8) + run("code.exe", 6, after=8, idle=300)
    samples += run("code.exe", 11, after=14)
    assert focus_minutes(samples, WORK) == pytest.approx(11.0)


def test_a_gap_in_the_samples_breaks_the_block() -> None:
    samples = run("code.exe", 8) + run("code.exe", 8, after=10)
    assert focus_minutes(samples, WORK) == 0.0


def test_samples_out_of_order_are_sorted_first() -> None:
    assert focus_minutes(list(reversed(run("code.exe", 12))), WORK) == pytest.approx(12.0)


def test_two_blocks_add_up() -> None:
    samples = run("code.exe", 10) + run("chrome.exe", 5, after=10) + run("code.exe", 15, after=15)
    assert focus_minutes(samples, WORK) == pytest.approx(25.0)


def test_worked_means_any_moment_on_a_work_app_while_present() -> None:
    assert worked(run("chrome.exe", 5) + run("code.exe", 0.25, after=5), WORK)
    assert not worked(run("chrome.exe", 5) + run("code.exe", 1, after=5, idle=600), WORK)
