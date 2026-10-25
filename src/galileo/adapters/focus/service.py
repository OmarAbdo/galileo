"""`python -m galileo.adapters.focus.service`: the focus sampler as Omar's Startup folder runs it,
hidden, one at a time, on the real screen."""

import sys
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from galileo.adapters.focus.probe import foreground_app, idle_seconds, windows_dlls
from galileo.adapters.focus.sampler import Sampler
from galileo.adapters.focus.samples import FileSamples
from galileo.adapters.focus.single import hold_lock, installed_commit
from galileo.adapters.storage.data_folder import data_folder
from galileo.adapters.storage.score_files import ScoreFiles
from galileo.domain.focus.blocks import Sample


def serve(folder: Path, read: Callable[[datetime], Sample], sleep: Callable[[float], None]) -> int:
    """Samples until a newer Galileo is installed; leaves at once when another sampler runs."""
    held = hold_lock(folder / "focus" / "sampler.lock", sleep)
    if held is None:
        return 0
    with held:
        sampler = Sampler(read, FileSamples(folder / "focus"), ScoreFiles(folder), sleep=sleep)
        sampler.installed = lambda: installed_commit(folder / "app")
        sampler.run()
    return 0


def main() -> int:
    dlls = windows_dlls()
    return serve(
        data_folder(), lambda now: Sample(now, foreground_app(dlls), idle_seconds(dlls)), time.sleep
    )


if __name__ == "__main__":
    sys.exit(main())
