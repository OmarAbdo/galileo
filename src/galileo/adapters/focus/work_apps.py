"""The apps that count as Omar's own work: `focus.toml` in his data folder, written with these
defaults the first time so he can edit it. Browsers aren't in it: a browser can be docs or a
feed, and the sampler can't tell which without reading titles, which it never does."""

import tomllib
from pathlib import Path

from galileo.adapters.focus.samples import FocusFileError

DEFAULT_TEXT = """# Apps that count as your own work for the focus score: their file names.
work = [
    "code.exe", "cursor.exe", "devenv.exe", "idea64.exe", "pycharm64.exe", "goland64.exe",
    "windowsterminal.exe", "powershell.exe", "pwsh.exe", "cmd.exe", "obsidian.exe",
]
"""
DEFAULT_WORK_APPS = frozenset(tomllib.loads(DEFAULT_TEXT)["work"])


def work_apps(folder: Path) -> frozenset[str]:
    path = folder / "focus.toml"
    if not path.exists():
        folder.mkdir(parents=True, exist_ok=True)
        path.write_text(DEFAULT_TEXT, encoding="utf-8")
    try:
        names = tomllib.loads(path.read_text(encoding="utf-8"))["work"]
    except (tomllib.TOMLDecodeError, KeyError) as problem:
        raise FocusFileError(f"{path}: no list of work apps ({problem})") from problem
    if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
        raise FocusFileError(f"{path}: work must be a list of app file names")
    return frozenset(name.lower() for name in names)
