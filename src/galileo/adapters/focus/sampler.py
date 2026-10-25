"""`python -m galileo.adapters.focus.sampler`: samples what is in front of Omar every 15 seconds
and closes each finished day into a focus record. It runs hidden from his Startup folder."""

import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

from galileo.adapters.focus.probe import foreground_app, idle_seconds, windows_dlls
from galileo.adapters.focus.samples import FileSamples
from galileo.adapters.focus.work_apps import work_apps
from galileo.adapters.storage.data_folder import data_folder
from galileo.adapters.storage.score_files import ScoreFiles
from galileo.application.focus import close_days
from galileo.domain.focus.blocks import SAMPLE_SECONDS, Sample


@dataclass
class Sampler:
    read: Callable[[datetime], Sample]
    samples: FileSamples
    scores: ScoreFiles
    now: Callable[[], datetime] = datetime.now
    sleep: Callable[[float], None] = time.sleep
    last_day: date | None = None

    def tick(self) -> None:
        """On the first round and at each new day, the finished days are closed first."""
        now = self.now()
        if now.date() != self.last_day:
            close_days(self.samples, self.scores, work_apps(self.scores.folder), now.date())
            self.last_day = now.date()
        self.samples.append(self.read(now))

    def run(self, rounds: int | None = None) -> None:
        done = 0
        while rounds is None or done < rounds:
            self.tick()
            self.sleep(SAMPLE_SECONDS)
            done += 1


def main() -> int:
    dlls = windows_dlls()
    folder = data_folder()

    def read(now: datetime) -> Sample:
        return Sample(now, foreground_app(dlls), idle_seconds(dlls))

    Sampler(read, FileSamples(folder / "focus"), ScoreFiles(folder)).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
