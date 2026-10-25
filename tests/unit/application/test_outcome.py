"""The outcome doctrine records for Galileo, asked of a score source."""

from datetime import date

import pytest

from galileo.application.outcome import compute_outcome
from galileo.domain.scoring.outcome import Kind, Record, Score

TODAY = date(2026, 10, 26)


class FixedSource:
    def __init__(self, scores: dict[Kind, Score]) -> None:
        self.scores = scores

    def score(self, kind: Kind) -> Score:
        return self.scores.get(kind, Score(kind=kind, baseline=None))


def test_every_kind_is_asked_for() -> None:
    scores = {kind: Score(kind, 2.0, (Record(TODAY, 2.0),)) for kind in Kind}
    assert compute_outcome(FixedSource(scores), TODAY) == pytest.approx(1.0)


def test_a_source_without_data_gives_zero() -> None:
    assert compute_outcome(FixedSource({}), TODAY) == 0.0
