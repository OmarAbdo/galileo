"""`galileo baseline`: freeze the baselines a week of measuring allows. A frozen one is kept."""

from collections.abc import Mapping
from datetime import date
from typing import TextIO

from galileo.adapters.storage.score_files import ScoreFiles
from galileo.application.baseline import freeze_baselines
from galileo.domain.scoring.baseline import MIN_BASELINE_DAYS, days_measured
from galileo.domain.scoring.outcome import Kind


def status(kind: Kind, kept: Mapping[Kind, float], frozen: Mapping[Kind, float], days: int) -> str:
    if kind in kept:
        return f"already {kept[kind]:g}, kept"
    if kind in frozen:
        return f"frozen at {frozen[kind]:g}"
    if days >= MIN_BASELINE_DAYS:
        return "its last week averages 0, which can't be a baseline"
    return f"measured on {days} of the {MIN_BASELINE_DAYS} days needed in the last week"


def baseline(files: ScoreFiles, today: date, output: TextIO) -> int:
    kept = files.baselines()
    frozen = freeze_baselines(files, today)
    for kind in Kind:
        days = days_measured(files.score(kind), today)
        output.write(f"{kind.value}: {status(kind, kept, frozen, days)}\n")
    return 0
