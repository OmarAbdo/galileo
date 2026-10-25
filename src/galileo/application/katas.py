"""Omar's katas: start the next one, check it against its tests, or stop it."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from galileo.domain.katas.kata import Attempt, Kata, Session, hands_value, next_kata
from galileo.domain.scoring.outcome import Kind, Record


@dataclass(frozen=True)
class RunResult:
    passed: bool
    output: str


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    output: str
    seconds: float = 0.0
    counted: bool = False


class NoKataError(LookupError):
    pass


class KataBank(Protocol):
    def katas(self, language: str) -> list[Kata]: ...


class KataDesk(Protocol):
    def current(self) -> Session | None: ...

    def open(self, kata: Kata, started: datetime) -> Session: ...

    def close(self) -> None: ...

    def history(self) -> list[Attempt]: ...

    def remember(self, attempt: Attempt) -> None: ...


class KataRunner(Protocol):
    def run(self, folder: Path, language: str) -> RunResult: ...


class Recorder(Protocol):
    def append(self, kind: Kind, record: Record) -> None: ...


@dataclass(frozen=True)
class KataTools:
    bank: KataBank
    desk: KataDesk
    runner: KataRunner
    recorder: Recorder


def start_kata(tools: KataTools, language: str, now: datetime) -> Session:
    """The open kata, or else the next one in the bank."""
    session = tools.desk.current()
    if session is not None:
        return session
    kata = next_kata(tools.bank.katas(language), tools.desk.history())
    return tools.desk.open(kata, now)


def check_kata(tools: KataTools, now: datetime) -> CheckResult:
    """Runs the open kata's tests. A pass records the time and closes the kata."""
    session = tools.desk.current()
    if session is None:
        raise NoKataError("no kata is open: start one with `galileo kata`")
    run = tools.runner.run(session.folder, session.language)
    if not run.passed:
        return CheckResult(passed=False, output=run.output)
    seconds = (now - session.started).total_seconds()
    value = hands_value(find(tools.bank, session), seconds)
    if value is not None:
        tools.recorder.append(Kind.HANDS, Record(now.date(), value))
    tools.desk.remember(Attempt(session.kata, now.date(), seconds))
    tools.desk.close()
    return CheckResult(passed=True, output=run.output, seconds=seconds, counted=value is not None)


def find(bank: KataBank, session: Session) -> Kata:
    for kata in bank.katas(session.language):
        if kata.name == session.kata:
            return kata
    raise NoKataError(f"the kata {session.kata} is no longer in the bank")


def stop_kata(desk: KataDesk) -> bool:
    """Closes the open kata without a record; False when none was open."""
    if desk.current() is None:
        return False
    desk.close()
    return True
