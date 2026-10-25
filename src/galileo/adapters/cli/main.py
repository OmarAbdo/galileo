"""`python -m galileo.adapters.cli.main`: Omar's commands. The installed `galileo` runs this."""

import argparse
import sys
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import TextIO

from galileo.adapters.cli.baseline_command import baseline
from galileo.adapters.cli.score_command import score
from galileo.adapters.storage.data_folder import data_folder
from galileo.adapters.storage.score_files import ScoreFileError, ScoreFiles

Command = Callable[[ScoreFiles, date, TextIO], int]
COMMANDS: dict[str, tuple[Command, str]] = {
    "score": (score, "this week's scores against the baseline, and the outcome"),
    "baseline": (baseline, "freeze the baselines a week of measuring allows"),
}


def parser() -> argparse.ArgumentParser:
    commands = argparse.ArgumentParser(prog="galileo", description="Omar's learning mode")
    choices = commands.add_subparsers(dest="command", required=True)
    for name, (_, summary) in COMMANDS.items():
        choices.add_parser(name, help=summary)
    return commands


def run(arguments: list[str], folder: Path, today: date, output: TextIO) -> int:
    command, _ = COMMANDS[parser().parse_args(arguments).command]
    try:
        return command(ScoreFiles(folder), today, output)
    except ScoreFileError as problem:
        output.write(f"{problem}\n")
        return 1


def main(arguments: list[str]) -> int:
    return run(arguments, data_folder(), date.today(), sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
