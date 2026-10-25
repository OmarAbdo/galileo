"""Every Python kata in the bank: its starting file fails its tests, and its answer, kept here in
the tests, passes them. A kata that can't be solved, or is solved by its stub, is a broken kata."""

from pathlib import Path

from galileo.adapters.katas.bank import TomlBank
from galileo.adapters.katas.runner import UnittestRunner
from galileo.domain.katas.kata import Kata

ANSWERS = Path(__file__).parent / "kata_answers" / "python"


def passes(folder: Path, kata: Kata, solution: str) -> bool:
    folder.mkdir()
    (folder / "solution.py").write_text(solution, encoding="utf-8")
    (folder / "test_solution.py").write_text(kata.tests, encoding="utf-8")
    return UnittestRunner().run(folder, "python").passed


def answer(kata: Kata) -> str:
    return (ANSWERS / f"{kata.name.replace('-', '_')}.py").read_text(encoding="utf-8")


def test_every_starting_file_fails_and_every_answer_passes(tmp_path: Path) -> None:
    katas = TomlBank().katas("python")
    assert len(katas) >= 6
    for kata in katas:
        assert not passes(tmp_path / f"{kata.name}-start", kata, kata.solution), kata.name
        assert passes(tmp_path / f"{kata.name}-answer", kata, answer(kata)), kata.name
    names = {kata.name.replace("-", "_") for kata in katas}
    assert {path.stem for path in ANSWERS.glob("*.py")} == names
