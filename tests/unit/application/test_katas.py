"""Starting, checking and stopping a kata, with a fake desk, runner and score file."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from galileo.application.katas import (
    KataTools,
    NoKataError,
    RunResult,
    check_kata,
    start_kata,
    stop_kata,
)
from galileo.domain.katas.kata import Attempt, Kata, Session
from galileo.domain.scoring.outcome import Kind, Record

NOW = datetime(2026, 11, 2, 9, 0)
ALPHA = Kata("alpha", "python", "Alpha", "Write alpha.", 300, solution="stub", tests="tests")


class FakeBank:
    def katas(self, language: str) -> list[Kata]:
        return [ALPHA] if language == "python" else []


@dataclass
class FakeDesk:
    session: Session | None = None
    attempts: list[Attempt] = field(default_factory=list)
    opened: int = 0

    def current(self) -> Session | None:
        return self.session

    def open(self, kata: Kata, started: datetime) -> Session:
        self.opened += 1
        self.session = Session(kata.name, kata.language, started, Path("work") / kata.name)
        return self.session

    def close(self) -> None:
        self.session = None

    def history(self) -> list[Attempt]:
        return self.attempts

    def remember(self, attempt: Attempt) -> None:
        self.attempts.append(attempt)


@dataclass
class FakeRunner:
    result: RunResult

    def run(self, folder: Path, language: str) -> RunResult:
        return self.result


@dataclass
class FakeRecorder:
    records: list[tuple[Kind, Record]] = field(default_factory=list)

    def append(self, kind: Kind, record: Record) -> None:
        self.records.append((kind, record))


def tools(passes: bool, desk: FakeDesk | None = None) -> KataTools:
    result = RunResult(passed=passes, output="1 test run")
    return KataTools(FakeBank(), desk or FakeDesk(), FakeRunner(result), FakeRecorder())


def opened(desk: FakeDesk, minutes_ago: float) -> FakeDesk:
    desk.open(ALPHA, NOW - timedelta(minutes=minutes_ago))
    return desk


def test_starting_opens_the_next_kata() -> None:
    kit = tools(passes=True)
    session = start_kata(kit, "python", NOW)
    assert (session.kata, session.started) == ("alpha", NOW)


def test_starting_again_returns_the_open_kata() -> None:
    desk = opened(FakeDesk(), minutes_ago=5)
    session = start_kata(tools(passes=True, desk=desk), "python", NOW)
    assert desk.opened == 1
    assert session.started == NOW - timedelta(minutes=5)


def test_starting_with_an_empty_bank_is_refused() -> None:
    with pytest.raises(NoKataError, match="the go kata bank is empty"):
        start_kata(tools(passes=True), "go", NOW)


def test_checking_without_an_open_kata_is_refused() -> None:
    with pytest.raises(NoKataError, match="galileo kata"):
        check_kata(tools(passes=True), NOW)


def test_failing_tests_keep_the_kata_open_and_record_nothing() -> None:
    kit = tools(passes=False, desk=opened(FakeDesk(), minutes_ago=5))
    result = check_kata(kit, NOW)
    assert not result.passed
    assert result.output == "1 test run"
    assert kit.desk.current() is not None
    assert isinstance(kit.recorder, FakeRecorder)
    assert kit.recorder.records == []


def test_a_pass_records_hands_and_closes_the_kata() -> None:
    desk = opened(FakeDesk(), minutes_ago=7.5)
    kit = tools(passes=True, desk=desk)
    result = check_kata(kit, NOW)
    assert (result.passed, result.seconds, result.counted) == (True, 450.0, True)
    assert isinstance(kit.recorder, FakeRecorder)
    assert kit.recorder.records == [(Kind.HANDS, Record(NOW.date(), 1.5))]
    assert desk.attempts == [Attempt("alpha", NOW.date(), 450.0)]
    assert desk.current() is None


def test_a_pass_after_two_hours_is_remembered_but_not_counted() -> None:
    desk = opened(FakeDesk(), minutes_ago=120)
    kit = tools(passes=True, desk=desk)
    result = check_kata(kit, NOW)
    assert (result.passed, result.counted) == (True, False)
    assert isinstance(kit.recorder, FakeRecorder)
    assert kit.recorder.records == []
    assert len(desk.attempts) == 1


def test_a_kata_gone_from_the_bank_is_refused() -> None:
    desk = FakeDesk(session=Session("gone", "python", NOW, Path("work")))
    with pytest.raises(NoKataError, match="no longer"):
        check_kata(tools(passes=True, desk=desk), NOW)


def test_stopping_closes_the_open_kata() -> None:
    desk = opened(FakeDesk(), minutes_ago=1)
    assert stop_kata(desk)
    assert desk.current() is None
    assert not stop_kata(desk)
