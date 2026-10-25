"""Asking questions and recording each answer for understanding."""

from dataclasses import dataclass, field
from datetime import date

from galileo.application.understanding import QuizTools, answer, next_questions
from galileo.domain.scoring.outcome import Kind, Record
from galileo.domain.understanding.question import Asked, Question

TODAY = date(2026, 11, 9)
SHARE = Question("share", "galileo: tests/unit/test_x.py:3", "share(score)", "0.75")


@dataclass
class Fakes:
    questions: list[Question]
    asked_before: list[Asked] = field(default_factory=list)
    records: list[tuple[Kind, Record]] = field(default_factory=list)

    def all(self) -> list[Question]:
        return self.questions

    def asked(self) -> list[Asked]:
        return self.asked_before

    def remember(self, asked: Asked) -> None:
        self.asked_before.append(asked)

    def append(self, kind: Kind, record: Record) -> None:
        self.records.append((kind, record))


def tools(fakes: Fakes) -> QuizTools:
    return QuizTools(source=fakes.all, history=fakes, recorder=fakes)


def test_the_next_questions_are_the_due_ones() -> None:
    fakes = Fakes([SHARE])
    assert next_questions(tools(fakes), TODAY) == [SHARE]
    fakes.remember(Asked("share", TODAY, right=True))
    assert next_questions(tools(fakes), TODAY) == []


def test_a_right_answer_records_one_and_is_remembered() -> None:
    fakes = Fakes([SHARE])
    assert answer(tools(fakes), SHARE, "0.75", TODAY)
    assert fakes.records == [(Kind.UNDERSTANDING, Record(TODAY, 1.0))]
    assert fakes.asked_before == [Asked("share", TODAY, right=True)]


def test_a_wrong_answer_records_zero() -> None:
    fakes = Fakes([SHARE])
    assert not answer(tools(fakes), SHARE, "1", TODAY)
    assert fakes.records == [(Kind.UNDERSTANDING, Record(TODAY, 0.0))]
