"""`python -m galileo.adapters.outcome`: the number doctrine records as Galileo's outcome."""

import sys
from datetime import date
from pathlib import Path
from typing import TextIO

from galileo.adapters.storage.data_folder import data_folder
from galileo.adapters.storage.score_files import ScoreFileError, ScoreFiles
from galileo.application.outcome import compute_outcome


def report(folder: Path, today: date, output: TextIO, errors: TextIO) -> int:
    try:
        value = compute_outcome(ScoreFiles(folder), today)
    except ScoreFileError as problem:
        errors.write(f"{problem}\n")
        return 1
    output.write(f"{value:g}\n")
    return 0


def main() -> int:
    return report(data_folder(), date.today(), sys.stdout, sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
