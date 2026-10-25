"""What every `galileo` command gets: Omar's data folder, the time, where to write, and the
command's action (`check` in `galileo kata check`)."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO


@dataclass(frozen=True)
class Context:
    folder: Path
    now: datetime
    output: TextIO
    action: str | None = None
