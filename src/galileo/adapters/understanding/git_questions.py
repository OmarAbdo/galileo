"""Questions from the test files changed on main in the last 30 days, read from main itself, so a
test on an unmerged branch or in the working tree never becomes a question."""

import subprocess
from pathlib import Path, PurePosixPath

from galileo.adapters.understanding.assertions import questions_in
from galileo.domain.understanding.question import Question

MAIN = "origin/main"
SINCE = "30.days"
GIT_TIMEOUT_SECONDS = 60


def git(repository: Path, *arguments: str) -> str:
    command = ["git", "-c", "core.fsmonitor=false", "-C", str(repository), *arguments]
    finished = subprocess.run(
        command, capture_output=True, text=True, timeout=GIT_TIMEOUT_SECONDS, check=True
    )
    return finished.stdout


def changed_tests(repository: Path) -> list[str]:
    """Test files changed on main in the window, newest change first, that still exist there."""
    changed = git(repository, "log", f"--since={SINCE}", "--name-only", "--pretty=format:", MAIN)
    present = set(git(repository, "ls-tree", "-r", "--name-only", MAIN).splitlines())
    paths = dict.fromkeys(line for line in changed.splitlines() if line in present)
    return [path for path in paths if PurePosixPath(path).name.startswith("test_")]


class GitQuestions:
    def __init__(self, repositories: list[Path]) -> None:
        self.repositories = repositories

    def __call__(self) -> list[Question]:
        questions: list[Question] = []
        for repository in self.repositories:
            try:
                paths = changed_tests(repository)
            except (subprocess.CalledProcessError, NotADirectoryError, FileNotFoundError):
                continue
            for path in paths:
                source = git(repository, "show", f"{MAIN}:{path}")
                questions += questions_in(source, f"{repository.name}: {path}")
        return questions
