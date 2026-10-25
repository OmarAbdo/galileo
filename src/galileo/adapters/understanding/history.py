"""Every answered question, in `understanding/asked.jsonl`: which one, when, and whether right."""

import json
from datetime import date
from pathlib import Path

from galileo.domain.understanding.question import Asked


class QuizFileError(ValueError):
    pass


def parse_asked(path: Path, line: int, text: str) -> Asked:
    try:
        row = json.loads(text)
        return Asked(str(row["key"]), date.fromisoformat(row["day"]), bool(row["right"]))
    except (ValueError, KeyError, TypeError) as problem:
        raise QuizFileError(f"{path}:{line}: not an answer ({problem})") from problem


class FileHistory:
    def __init__(self, folder: Path) -> None:
        self.path = folder / "asked.jsonl"

    def asked(self) -> list[Asked]:
        if not self.path.exists():
            return []
        lines = enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1)
        return [parse_asked(self.path, number, text) for number, text in lines if text.strip()]

    def remember(self, asked: Asked) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        row = {"key": asked.key, "day": asked.day.isoformat(), "right": asked.right}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(f"{json.dumps(row)}\n")
