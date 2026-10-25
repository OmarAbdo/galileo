"""The number doctrine records as Galileo's outcome, from wherever the scores are kept."""

from datetime import date
from typing import Protocol

from galileo.domain.scoring.outcome import Kind, Score, outcome


class ScoreSource(Protocol):
    def score(self, kind: Kind) -> Score: ...


def compute_outcome(source: ScoreSource, today: date) -> float:
    return outcome({kind: source.score(kind) for kind in Kind}, today)
