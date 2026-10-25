"""`python -m galileo.adapters.cli.main`: Omar's commands. The installed `galileo` runs this."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import TextIO

from galileo.adapters.cli.commands import COMMANDS
from galileo.adapters.cli.context import Context
from galileo.adapters.katas.bank import KataFileError
from galileo.adapters.storage.data_folder import data_folder
from galileo.adapters.storage.score_files import ScoreFileError
from galileo.adapters.understanding.history import QuizFileError


def parser() -> argparse.ArgumentParser:
    commands = argparse.ArgumentParser(prog="galileo", description="Omar's learning mode")
    choices = commands.add_subparsers(dest="command", required=True)
    for name, command in COMMANDS.items():
        choice = choices.add_parser(name, help=command.summary)
        if command.actions:
            choice.add_argument("action", nargs="?", choices=command.actions)
    return commands


def run(arguments: list[str], folder: Path, now: datetime, output: TextIO) -> int:
    chosen = parser().parse_args(arguments)
    context = Context(folder, now, output, getattr(chosen, "action", None))
    try:
        return COMMANDS[chosen.command].run(context)
    except (ScoreFileError, KataFileError, QuizFileError) as problem:
        output.write(f"{problem}\n")
        return 1


def main(arguments: list[str]) -> int:
    return run(arguments, data_folder(), datetime.now(), sys.stdout)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
