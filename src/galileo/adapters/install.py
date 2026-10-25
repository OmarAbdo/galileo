"""Installs Galileo for Omar from the repository's main branch: a release folder per commit, a
venv that finds the current one, and the `galileo` command in ~/.local/bin, which is already on
his PATH. Run `python -m galileo.adapters.install` once from the repository; after that,
`galileo update`."""

import io
import json
import shutil
import subprocess
import sys
import tarfile
import venv
from datetime import UTC, datetime
from pathlib import Path

from galileo.adapters.focus.autostart import keep_sampling, startup_folder
from galileo.adapters.storage.data_folder import data_folder, windows_profile

KEEP_RELEASES = 3
GIT_TIMEOUT_SECONDS = 120
WINDOWS = sys.platform == "win32"
VERSION = f"python{sys.version_info.major}.{sys.version_info.minor}"
# The command's file name and text on Windows and elsewhere. `-I` keeps environment variables
# from redirecting it.
COMMAND_FILES = {
    True: ("galileo.cmd", '@"{python}" -I -m galileo.adapters.cli.main %*\r\n'),
    False: ("galileo", '#!/bin/sh\nexec "{python}" -I -m galileo.adapters.cli.main "$@"\n'),
}


def git(repository: Path, *arguments: str) -> bytes:
    command = ["git", "-c", "core.fsmonitor=false", "-C", str(repository), *arguments]
    return subprocess.run(
        command, capture_output=True, timeout=GIT_TIMEOUT_SECONDS, check=True
    ).stdout


def commands_folder() -> Path:
    return (windows_profile() if WINDOWS else Path.home()) / ".local" / "bin"


def interpreter(environment: Path) -> Path:
    return environment / ("Scripts/python.exe" if WINDOWS else "bin/python")


def site_packages(environment: Path) -> Path:
    return environment / ("Lib" if WINDOWS else f"lib/{VERSION}") / "site-packages"


def unpack(repository: Path, commit: str, release: Path) -> None:
    """The commit's `src/galileo`, extracted beside the release and then moved into place."""
    archive = git(repository, "archive", "--format=tar", commit, "src/galileo")
    partial = release.with_name(f"{release.name}.partial")
    shutil.rmtree(partial, ignore_errors=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as bundle:
        bundle.extractall(partial, filter="data")
    partial.rename(release)


def write_command(commands: Path, python: Path) -> Path:
    name, text = COMMAND_FILES[WINDOWS]
    commands.mkdir(parents=True, exist_ok=True)
    command = commands / name
    command.write_text(text.format(python=python), "utf-8")
    command.chmod(0o755)
    return command


def prune(releases: Path, current: Path) -> None:
    others = [release for release in releases.iterdir() if release != current]
    others.sort(key=lambda release: release.stat().st_mtime, reverse=True)
    for release in others[KEEP_RELEASES - 1 :]:
        shutil.rmtree(release, ignore_errors=True)


def install(repository: Path, home: Path, commands: Path, ref: str) -> Path:
    """Installs `ref` and returns the `galileo` command."""
    commit = git(repository, "rev-parse", ref).decode().strip()
    release = home / "releases" / commit[:12]
    if not release.exists():
        unpack(repository, commit, release)
    environment = home / "venv"
    if not interpreter(environment).exists():
        venv.EnvBuilder(with_pip=False).create(environment)
    (site_packages(environment) / "galileo.pth").write_text(f"{release / 'src'}\n", "utf-8")
    command = write_command(commands, interpreter(environment))
    record = home / "installed.json"
    installed = json.loads(record.read_text(encoding="utf-8")) if record.exists() else {}
    installed |= {"commit": commit, "repository": str(repository), "commands": str(commands)}
    installed["at"] = datetime.now(UTC).isoformat(timespec="seconds")
    record.write_text(json.dumps(installed), encoding="utf-8")
    prune(home / "releases", release)
    return command


def install_main(repository: Path, home: Path, commands: Path) -> Path:
    git(repository, "fetch", "-q", "origin")
    return install(repository, home, commands, "origin/main")


def update(home: Path) -> str:
    """Installs main again from the repository and into the folder recorded at the install;
    returns the commit."""
    installed = json.loads((home / "installed.json").read_text(encoding="utf-8"))
    install_main(Path(installed["repository"]), home, Path(installed["commands"]))
    return str(json.loads((home / "installed.json").read_text(encoding="utf-8"))["commit"])


def main() -> int:
    repository = Path(__file__).resolve().parents[3]
    home = data_folder() / "app"
    command = install_main(repository, home, commands_folder())
    if WINDOWS:
        keep_sampling(home, startup_folder())
    sys.stdout.write(f"Installed: {command}. Open a new terminal and run `galileo score`.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
