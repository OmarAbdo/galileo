"""Freezing the baselines a week of measuring made possible."""

from collections.abc import Mapping
from datetime import date
from typing import Protocol

from galileo.domain.scoring.baseline import baselines_to_freeze
from galileo.domain.scoring.outcome import Kind, Score


class BaselineStore(Protocol):
    def score(self, kind: Kind) -> Score: ...

    def save_baselines(self, values: Mapping[Kind, float]) -> None: ...


def freeze_baselines(store: BaselineStore, today: date) -> dict[Kind, float]:
    frozen = baselines_to_freeze({kind: store.score(kind) for kind in Kind}, today)
    if frozen:
        store.save_baselines(frozen)
    return frozen
