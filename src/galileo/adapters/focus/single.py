"""One sampler at a time: a lock held for the sampler's life, and the installed commit, so an old
sampler knows when to leave."""

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import IO

from galileo.domain.focus.blocks import SAMPLE_SECONDS

LOCK_TRIES = 3

if sys.platform == "win32":
    import msvcrt

    def lock(stream: IO[bytes]) -> None:
        msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)

else:
    import fcntl

    def lock(stream: IO[bytes]) -> None:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)


def hold_lock(path: Path, sleep: Callable[[float], None]) -> IO[bytes] | None:
    """A lock held for as long as the file stays open, or None when another sampler keeps it
    through three tries, 15 seconds apart."""
    path.parent.mkdir(parents=True, exist_ok=True)
    stream = path.open("a+b")
    for _ in range(LOCK_TRIES):
        try:
            lock(stream)
            return stream
        except OSError:
            sleep(SAMPLE_SECONDS)
    stream.close()
    return None


def installed_commit(home: Path) -> str:
    path = home / "installed.json"
    return str(json.loads(path.read_text(encoding="utf-8"))["commit"]) if path.exists() else ""
