"""A question is an expression from one of Omar's tests, `assert <expression> == <expected>`, with
the expected value as its answer: CI already ran it, so no model has to grade him. Answers are
compared by value. A question comes back once, a week later, to test what stayed."""

import ast
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

REPEAT_AFTER = timedelta(days=7)


@dataclass(frozen=True)
class Question:
    key: str
    place: str
    expression: str
    expected: str
    context: str = ""  # what Omar sees: the test's setup, ending with `<expression> == ?`


@dataclass(frozen=True)
class Asked:
    key: str
    day: date
    right: bool


def value_of(text: str) -> object:
    """The Python value of an answer; text that isn't one, like an unquoted word, is that string."""
    try:
        return ast.literal_eval(text.strip())
    except (ValueError, SyntaxError):
        return text.strip()


def is_right(answer: str, expected: str) -> bool:
    given, wanted = value_of(answer), value_of(expected)
    if isinstance(given, bool) or isinstance(wanted, bool):
        return given is wanted
    if isinstance(given, int | float) and isinstance(wanted, int | float):
        return math.isclose(given, wanted, rel_tol=1e-9, abs_tol=1e-9)
    return given == wanted


def due(
    questions: Sequence[Question], history: Sequence[Asked], today: date, count: int
) -> list[Question]:
    """First the questions asked once, a week ago or more; then the ones never asked."""
    asked: dict[str, list[Asked]] = {}
    for entry in history:
        asked.setdefault(entry.key, []).append(entry)
    repeats = [
        question
        for question in questions
        if len(asked.get(question.key, [])) == 1
        and today - asked[question.key][0].day >= REPEAT_AFTER
    ]
    fresh = [question for question in questions if question.key not in asked]
    return [*repeats, *fresh][:count]
