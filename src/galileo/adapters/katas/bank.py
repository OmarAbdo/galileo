"""The kata bank: one TOML file per kata under `bank/<language>/`, named after the kata."""

import tomllib
from pathlib import Path

from galileo.domain.katas.kata import Kata

BANK = Path(__file__).parent / "bank"
FIELDS = ("title", "prompt", "reference_seconds", "solution", "tests")


class KataFileError(ValueError):
    pass


def parse_kata(path: Path, language: str) -> Kata:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as problem:
        raise KataFileError(f"{path}: {problem}") from problem
    missing = [name for name in FIELDS if name not in data]
    if missing:
        raise KataFileError(f"{path}: missing {', '.join(missing)}")
    return Kata(
        name=path.stem,
        language=language,
        title=str(data["title"]),
        prompt=str(data["prompt"]).strip(),
        reference_seconds=int(data["reference_seconds"]),
        solution=str(data["solution"]).lstrip("\n"),
        tests=str(data["tests"]).lstrip("\n"),
    )


class TomlBank:
    def __init__(self, folder: Path = BANK) -> None:
        self.folder = folder

    def katas(self, language: str) -> list[Kata]:
        paths = sorted((self.folder / language).glob("*.toml"))
        return [parse_kata(path, language) for path in paths]
