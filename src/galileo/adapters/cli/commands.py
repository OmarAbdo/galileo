"""The `galileo` commands: what runs each one, its one-line help, and its actions."""

from collections.abc import Callable
from dataclasses import dataclass

from galileo.adapters.cli.baseline_command import baseline
from galileo.adapters.cli.context import Context
from galileo.adapters.cli.kata_command import kata
from galileo.adapters.cli.score_command import score
from galileo.adapters.storage.score_files import ScoreFiles


@dataclass(frozen=True)
class Command:
    run: Callable[[Context], int]
    summary: str
    actions: tuple[str, ...] = ()


def score_now(context: Context) -> int:
    return score(ScoreFiles(context.folder), context.now.date(), context.output)


def baseline_now(context: Context) -> int:
    return baseline(ScoreFiles(context.folder), context.now.date(), context.output)


COMMANDS = {
    "score": Command(score_now, "this week's scores against the baseline, and the outcome"),
    "kata": Command(kata, "start the next kata or show the open one", ("check", "stop")),
    "baseline": Command(baseline_now, "freeze the baselines a week of measuring allows"),
}
