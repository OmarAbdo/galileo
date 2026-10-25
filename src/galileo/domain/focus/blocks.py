"""Focus blocks. Every 15 seconds a sample says which app is in front and how long since the last
key or mouse input. A block is an unbroken run on work apps: a glance of up to 30 seconds at
another app doesn't break it (and isn't counted), but a longer switch, 5 minutes without input,
or a gap in the samples does. Only blocks of 10 minutes or more count."""

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

SAMPLE_SECONDS = 15
GLANCE_SECONDS = 30
AWAY_SECONDS = 300
GAP_SECONDS = 60
BLOCK_SECONDS = 600

WORK, OTHER, AWAY = "work", "other", "away"


@dataclass(frozen=True)
class Sample:
    taken: datetime
    app: str
    idle_seconds: float


def state(sample: Sample, work_apps: frozenset[str]) -> str:
    if sample.idle_seconds >= AWAY_SECONDS:
        return AWAY
    return WORK if sample.app in work_apps else OTHER


@dataclass
class Tally:
    """Counts work seconds sample by sample and keeps the blocks long enough to count."""

    work_apps: frozenset[str]
    blocks: list[float] = field(default_factory=list)
    current: float = 0.0
    glance: float = 0.0
    previous: datetime | None = None

    def add(self, sample: Sample) -> None:
        if self.previous and (sample.taken - self.previous).total_seconds() < SAMPLE_SECONDS / 2:
            return  # a second sampler running at the same time: count each moment once
        kind = state(sample, self.work_apps)
        if self.breaks(sample, kind):
            self.close()
        if kind == WORK:
            self.current += SAMPLE_SECONDS
            self.glance = 0.0
        elif kind == OTHER and self.current > 0:
            self.glance += SAMPLE_SECONDS
        self.previous = sample.taken

    def breaks(self, sample: Sample, kind: str) -> bool:
        if kind == AWAY:
            return True
        if self.previous and (sample.taken - self.previous).total_seconds() > GAP_SECONDS:
            return True
        return kind == OTHER and self.glance + SAMPLE_SECONDS > GLANCE_SECONDS

    def close(self) -> None:
        if self.current >= BLOCK_SECONDS:
            self.blocks.append(self.current)
        self.current = self.glance = 0.0


def focus_minutes(samples: Iterable[Sample], work_apps: frozenset[str]) -> float:
    tally = Tally(work_apps)
    for sample in sorted(samples, key=lambda sample: sample.taken):
        tally.add(sample)
    tally.close()
    return sum(tally.blocks) / 60


def worked(samples: Iterable[Sample], work_apps: frozenset[str]) -> bool:
    """Whether Omar was at a work app at all; a day without that is a day off, not a 0."""
    return any(state(sample, work_apps) == WORK for sample in samples)
