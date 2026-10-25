"""The sampler: samples what is in front of Omar every 15 seconds and closes each finished day
into a focus record. It stops when a newer Galileo is installed, so the new one can take over."""

import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

from galileo.adapters.focus.samples import FileSamples
from galileo.adapters.focus.work_apps import work_apps
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
    installed: Callable[[], str] = str
    last_day: date | None = None

    def tick(self) -> None:
        """On the first round and at each new day, the finished days are closed first."""
        now = self.now()
        if now.date() != self.last_day:
            close_days(self.samples, self.scores, work_apps(self.scores.folder), now.date())
            self.last_day = now.date()
        self.samples.append(self.read(now))

    def run(self, rounds: int | None = None) -> None:
        release, done = self.installed(), 0
        while (rounds is None or done < rounds) and self.installed() == release:
            self.tick()
            self.sleep(SAMPLE_SECONDS)
            done += 1
