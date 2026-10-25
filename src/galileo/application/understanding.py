"""The quiz: the questions due today, and each answer recorded for understanding."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from galileo.domain.scoring.outcome import Kind, Record
from galileo.domain.understanding.question import Asked, Question, due, is_right

QUESTIONS_PER_QUIZ = 3


class QuizHistory(Protocol):
    def asked(self) -> list[Asked]: ...

    def remember(self, asked: Asked) -> None: ...


class Recorder(Protocol):
    def append(self, kind: Kind, record: Record) -> None: ...


@dataclass(frozen=True)
class QuizTools:
    source: Callable[[], list[Question]]
    history: QuizHistory
    recorder: Recorder


def next_questions(tools: QuizTools, today: date) -> list[Question]:
    return due(tools.source(), tools.history.asked(), today, QUESTIONS_PER_QUIZ)


def answer(tools: QuizTools, question: Question, given: str, today: date) -> bool:
    right = is_right(given, question.expected)
    tools.history.remember(Asked(question.key, today, right))
    tools.recorder.append(Kind.UNDERSTANDING, Record(today, 1.0 if right else 0.0))
    return right
