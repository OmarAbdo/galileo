"""`galileo score`: this week's three scores against the baseline, and the outcome."""

from datetime import date
from typing import TextIO

from galileo.adapters.storage.score_files import ScoreFiles
from galileo.application.outcome import compute_outcome
from galileo.domain.scoring.outcome import Kind, Score, share, weekly_mean

WEEK_FORMATS = {
    Kind.FOCUS: "{:.0f} min a day",
    Kind.UNDERSTANDING: "{:.0%} right",
    Kind.HANDS: "{:.1f} s a kata",
}
BASELINE_FORMATS = {Kind.FOCUS: "{:.0f}", Kind.UNDERSTANDING: "{:.0%}", Kind.HANDS: "{:.1f} s"}


def describe(score: Score, today: date) -> str:
    mean = weekly_mean(score, today)
    if mean is None:
        return f"{score.kind.value}: not measured this week"
    week = WEEK_FORMATS[score.kind].format(mean)
    if score.baseline is None:
        return f"{score.kind.value}: {week} (no baseline yet)"
    baseline = BASELINE_FORMATS[score.kind].format(score.baseline)
    return f"{score.kind.value}: {week} (baseline {baseline}): {share(score, today):.2f}"


def score(files: ScoreFiles, today: date, output: TextIO) -> int:
    for kind in Kind:
        output.write(f"{describe(files.score(kind), today)}\n")
    lowest = compute_outcome(files, today)
    output.write(f"outcome: {lowest:.2f}, the lowest share (0 until every kind has a baseline)\n")
    return 0
