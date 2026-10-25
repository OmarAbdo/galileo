"""What every `galileo` command gets: Omar's data folder, the time, where to write, the command's
action (`check` in `galileo kata check`), and how to ask him something."""

from collections.abc import Callable
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
    ask: Callable[[str], str] = input
