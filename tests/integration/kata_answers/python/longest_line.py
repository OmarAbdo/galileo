from pathlib import Path


def longest_line(path: Path) -> str:
    return max(path.read_text(encoding="utf-8").splitlines(), key=len, default="")


def count_lines(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
