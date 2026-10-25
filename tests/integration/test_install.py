"""Installing Galileo from a repository: a release, a venv that finds it, and the command."""

import io
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from galileo.adapters.cli.main import run
from galileo.adapters.install import commands_folder, install, update

FAKE_MAIN = """import sys


def main(arguments):
    sys.stdout.write("fake galileo " + " ".join(arguments))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
"""


def git(repository: Path, *arguments: str) -> str:
    command = ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", *arguments]
    finished = subprocess.run(
        command, cwd=repository, capture_output=True, text=True, timeout=60, check=True
    )
    return finished.stdout.strip()


@pytest.fixture(name="repository")
def fake_repository(tmp_path: Path) -> Path:
    repository = tmp_path / "repository"
    package = repository / "src" / "galileo" / "adapters" / "cli"
    package.mkdir(parents=True)
    for folder in (package.parents[1], package.parent, package):
        (folder / "__init__.py").write_text("", encoding="utf-8")
    (package / "main.py").write_text(FAKE_MAIN, encoding="utf-8")
    git(repository, "init", "-q", "-b", "main")
    git(repository, "add", ".")
    git(repository, "commit", "-q", "-m", "fake galileo")
    git(tmp_path, "init", "-q", "--bare", "origin.git")
    git(repository, "remote", "add", "origin", str(tmp_path / "origin.git"))
    git(repository, "push", "-q", "origin", "main")
    return repository


def run_command(command: Path, *arguments: str) -> str:
    launcher = ["cmd", "/c", str(command)] if sys.platform == "win32" else [str(command)]
    finished = subprocess.run(
        [*launcher, *arguments], capture_output=True, text=True, timeout=60, check=True
    )
    return finished.stdout


def test_the_installed_command_runs_the_release(repository: Path, tmp_path: Path) -> None:
    command = install(repository, tmp_path / "app", tmp_path / "bin", "HEAD")
    assert command.parent == tmp_path / "bin"
    assert run_command(command, "score") == "fake galileo score"


def test_the_install_is_recorded(repository: Path, tmp_path: Path) -> None:
    install(repository, tmp_path / "app", tmp_path / "bin", "HEAD")
    installed = json.loads((tmp_path / "app" / "installed.json").read_text(encoding="utf-8"))
    commit = git(repository, "rev-parse", "HEAD")
    assert installed["commit"] == commit
    assert installed["repository"] == str(repository)
    assert (tmp_path / "app" / "releases" / commit[:12] / "src" / "galileo").is_dir()


def test_update_installs_main_from_the_recorded_repository(
    repository: Path, tmp_path: Path
) -> None:
    install(repository, tmp_path / "app", tmp_path / "bin", "HEAD")
    (repository / "src" / "galileo" / "newer.py").write_text("", encoding="utf-8")
    git(repository, "add", ".")
    git(repository, "commit", "-q", "-m", "newer")
    git(repository, "push", "-q", "origin", "main")
    commit = update(tmp_path / "app")
    assert commit == git(repository, "rev-parse", "HEAD")
    assert (tmp_path / "app" / "releases" / commit[:12] / "src" / "galileo" / "newer.py").exists()


def test_galileo_update_reports_the_commit(repository: Path, tmp_path: Path) -> None:
    install(repository, tmp_path / "data" / "app", tmp_path / "bin", "HEAD")
    output = io.StringIO()
    assert run(["update"], tmp_path / "data", datetime(2026, 11, 2, 9, 0), output) == 0
    commit = git(repository, "rev-parse", "HEAD")
    assert output.getvalue() == f"Galileo is now at {commit[:12]}.\n"


def test_the_command_goes_where_the_path_already_looks() -> None:
    assert commands_folder().parts[-2:] == (".local", "bin")


def test_installing_again_keeps_the_newest_three_releases(repository: Path, tmp_path: Path) -> None:
    releases = tmp_path / "app" / "releases"
    for name in ("old-1", "old-2", "old-3"):
        (releases / name).mkdir(parents=True)
    install(repository, tmp_path / "app", tmp_path / "bin", "HEAD")
    install(repository, tmp_path / "app", tmp_path / "bin", "HEAD")
    kept = sorted(path.name for path in releases.iterdir())
    assert len(kept) == 3
    assert git(repository, "rev-parse", "HEAD")[:12] in kept
