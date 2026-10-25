"""A kata, the order they come in, and what a pass says about Omar's hands."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

# A kata left open longer than this says nothing about hands: Omar was away.
MAX_COUNTED_SECONDS = 3600


@dataclass(frozen=True)
class Kata:
    name: str
    language: str
    title: str
    prompt: str
    reference_seconds: int
    solution: str
    tests: str


@dataclass(frozen=True)
class Attempt:
    kata: str
    day: date
    seconds: float


@dataclass(frozen=True)
class Session:
    kata: str
    language: str
    started: datetime
    folder: Path


def next_kata(katas: Sequence[Kata], history: Sequence[Attempt]) -> Kata:
    """The kata done longest ago; one never done comes first, and ties go by name."""
    if not katas:
        raise ValueError("no katas to choose from")
    last_done: dict[str, date] = {}
    for attempt in history:
        last_done[attempt.kata] = max(attempt.day, last_done.get(attempt.kata, date.min))
    return min(katas, key=lambda kata: (last_done.get(kata.name, date.min), kata.name))


def hands_value(kata: Kata, seconds: float) -> float | None:
    """The time to pass as a multiple of the kata's reference time, so katas of different sizes
    count the same. None when the time can't be a real attempt."""
    if seconds <= 0 or seconds > MAX_COUNTED_SECONDS:
        return None
    return seconds / kata.reference_seconds
