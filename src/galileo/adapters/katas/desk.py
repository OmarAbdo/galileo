"""Omar's kata desk in his data folder: `open.json` for the kata in progress, `history.jsonl`
for every pass, and one folder per attempt under `work/`."""

import json
from datetime import date, datetime
from pathlib import Path

from galileo.adapters.katas.bank import KataFileError
from galileo.adapters.katas.languages import LANGUAGES
from galileo.domain.katas.kata import Attempt, Kata, Session


def parse_session(path: Path) -> Session:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        started = datetime.fromisoformat(data["started"])
        return Session(data["kata"], data["language"], started, Path(data["folder"]))
    except (ValueError, KeyError, TypeError) as problem:
        raise KataFileError(f"{path}: not an open kata ({problem})") from problem


def parse_attempt(path: Path, line: int, text: str) -> Attempt:
    try:
        data = json.loads(text)
        return Attempt(data["kata"], date.fromisoformat(data["day"]), float(data["seconds"]))
    except (ValueError, KeyError, TypeError) as problem:
        raise KataFileError(f"{path}:{line}: not an attempt ({problem})") from problem


class FileDesk:
    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def current(self) -> Session | None:
        path = self.folder / "open.json"
        return parse_session(path) if path.exists() else None

    def open(self, kata: Kata, started: datetime) -> Session:
        work = self.folder / "work" / f"{kata.name}-{started:%Y%m%d-%H%M%S}"
        work.mkdir(parents=True)
        files = LANGUAGES[kata.language]
        (work / files.solution).write_text(kata.solution, encoding="utf-8")
        (work / files.tests).write_text(kata.tests, encoding="utf-8")
        for name, text in files.extra:
            (work / name).write_text(text, encoding="utf-8")
        (work / "KATA.md").write_text(f"# {kata.title}\n\n{kata.prompt}\n", encoding="utf-8")
        session = Session(kata.name, kata.language, started, work)
        opened = {"kata": kata.name, "language": kata.language, "folder": str(work)}
        text = json.dumps({**opened, "started": started.isoformat()})
        (self.folder / "open.json").write_text(text, encoding="utf-8")
        return session

    def close(self) -> None:
        (self.folder / "open.json").unlink(missing_ok=True)

    def history(self) -> list[Attempt]:
        path = self.folder / "history.jsonl"
        if not path.exists():
            return []
        lines = enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        return [parse_attempt(path, number, text) for number, text in lines if text.strip()]

    def remember(self, attempt: Attempt) -> None:
        self.folder.mkdir(parents=True, exist_ok=True)
        row = {"kata": attempt.kata, "day": attempt.day.isoformat(), "seconds": attempt.seconds}
        with (self.folder / "history.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(f"{json.dumps(row)}\n")
