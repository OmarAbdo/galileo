"""The kata bank: one TOML file per kata, under a folder per language."""

from pathlib import Path

import pytest

from galileo.adapters.katas.bank import KataFileError, TomlBank

KATA = '''
title = "Pairs that add up"
reference_seconds = 300
prompt = "Write pairs(numbers, target)."
solution = """
def pairs(numbers, target):
    raise NotImplementedError
"""
tests = """
import unittest
"""
'''


def bank_with(folder: Path, name: str, text: str) -> TomlBank:
    language = folder / "python"
    language.mkdir(parents=True, exist_ok=True)
    (language / f"{name}.toml").write_text(text, encoding="utf-8")
    return TomlBank(folder)


def test_a_kata_is_read_with_its_name_from_the_file(tmp_path: Path) -> None:
    [kata] = bank_with(tmp_path, "pairs", KATA).katas("python")
    assert (kata.name, kata.language, kata.title) == ("pairs", "python", "Pairs that add up")
    assert kata.reference_seconds == 300
    assert "raise NotImplementedError" in kata.solution


def test_katas_come_sorted_by_name(tmp_path: Path) -> None:
    bank_with(tmp_path, "beta", KATA)
    bank = bank_with(tmp_path, "alpha", KATA)
    assert [kata.name for kata in bank.katas("python")] == ["alpha", "beta"]


def test_a_language_without_katas_has_none(tmp_path: Path) -> None:
    assert TomlBank(tmp_path).katas("go") == []


def test_a_missing_field_is_refused(tmp_path: Path) -> None:
    bank = bank_with(tmp_path, "short", 'title = "Short"\n')
    with pytest.raises(KataFileError, match=r"short\.toml: missing prompt"):
        bank.katas("python")


def test_bad_toml_is_refused(tmp_path: Path) -> None:
    bank = bank_with(tmp_path, "broken", "title = \n")
    with pytest.raises(KataFileError, match=r"broken\.toml"):
        bank.katas("python")


def test_the_installed_bank_loads() -> None:
    assert all(kata.reference_seconds > 0 for kata in TomlBank().katas("python"))
