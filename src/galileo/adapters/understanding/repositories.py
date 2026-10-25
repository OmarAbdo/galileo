"""The repositories the quiz asks about: `understanding.toml` in Omar's data folder. The first time
it lists Galileo's own repository, from the install; Omar adds his other projects to it."""

import json
import tomllib
from pathlib import Path

from galileo.adapters.understanding.history import QuizFileError

HEADER = "# Repositories whose merged tests the quiz asks about. Add your other projects.\n"


def installed_repository(folder: Path) -> str | None:
    installed = folder / "app" / "installed.json"
    if not installed.exists():
        return None
    found = json.loads(installed.read_text(encoding="utf-8")).get("repository")
    return str(found) if found else None


def repositories(folder: Path) -> list[Path]:
    path = folder / "understanding.toml"
    if not path.exists():
        found = installed_repository(folder)
        listed = json.dumps([found] if found else [])
        folder.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{HEADER}repositories = {listed}\n", encoding="utf-8")
    try:
        listed_paths = tomllib.loads(path.read_text(encoding="utf-8"))["repositories"]
    except (tomllib.TOMLDecodeError, KeyError) as problem:
        raise QuizFileError(f"{path}: no list of repositories ({problem})") from problem
    if not isinstance(listed_paths, list):
        raise QuizFileError(f"{path}: repositories must be a list of folders")
    return [Path(str(entry)) for entry in listed_paths]
