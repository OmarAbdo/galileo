"""The `galileo` commands: what runs each one, its one-line help, and its actions."""

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from galileo.adapters.cli.baseline_command import baseline
from galileo.adapters.cli.context import Context
from galileo.adapters.cli.kata_command import kata
from galileo.adapters.cli.score_command import score
from galileo.adapters.focus.autostart import keep_sampling
from galileo.adapters.install import update
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


def update_now(context: Context) -> int:
    home = context.folder / "app"
    if not (home / "installed.json").exists():
        context.output.write("Not installed yet: run `python -m galileo.adapters.install`.\n")
        return 1
    commit = update(home)
    startup = json.loads((home / "installed.json").read_text(encoding="utf-8")).get("startup")
    if startup:
        keep_sampling(home, Path(startup))
    context.output.write(f"Galileo is now at {commit[:12]}.\n")
    return 0


COMMANDS = {
    "score": Command(score_now, "this week's scores against the baseline, and the outcome"),
    "kata": Command(kata, "start the next kata or show the open one", ("check", "stop")),
    "baseline": Command(baseline_now, "freeze the baselines a week of measuring allows"),
    "update": Command(update_now, "install the newest Galileo from the main branch"),
}
