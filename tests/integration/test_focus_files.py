"""The focus files: one samples file per day, and the list of work apps Omar can edit."""

from datetime import date, datetime
from pathlib import Path

import pytest

from galileo.adapters.focus.samples import FileSamples, FocusFileError
from galileo.adapters.focus.work_apps import DEFAULT_WORK_APPS, work_apps
from galileo.domain.focus.blocks import Sample

MORNING = datetime(2026, 11, 2, 9, 0, 15)


def test_samples_are_kept_per_day_and_read_back(tmp_path: Path) -> None:
    files = FileSamples(tmp_path)
    files.append(Sample(MORNING, "code.exe", 2.5))
    files.append(Sample(datetime(2026, 11, 3, 8, 0), "chrome.exe", 0.0))
    assert files.days() == [date(2026, 11, 2), date(2026, 11, 3)]
    assert files.samples(date(2026, 11, 2)) == [Sample(MORNING, "code.exe", 2.5)]


def test_forgetting_a_day_deletes_its_file(tmp_path: Path) -> None:
    files = FileSamples(tmp_path)
    files.append(Sample(MORNING, "code.exe", 0.0))
    files.forget(MORNING.date())
    assert files.days() == []
    assert list(tmp_path.iterdir()) == []


def test_a_corrupt_line_names_its_file_and_line(tmp_path: Path) -> None:
    files = FileSamples(tmp_path)
    files.append(Sample(MORNING, "code.exe", 0.0))
    with (tmp_path / "samples-2026-11-02.jsonl").open("a", encoding="utf-8") as stream:
        stream.write('{"app": "code.exe"}\n')
    with pytest.raises(FocusFileError, match=r"samples-2026-11-02\.jsonl:2"):
        files.samples(MORNING.date())


def test_the_work_apps_default_and_are_written_for_omar_to_edit(tmp_path: Path) -> None:
    assert work_apps(tmp_path) == frozenset(DEFAULT_WORK_APPS)
    assert "code.exe" in (tmp_path / "focus.toml").read_text(encoding="utf-8")


def test_omars_list_wins_and_is_read_in_lower_case(tmp_path: Path) -> None:
    (tmp_path / "focus.toml").write_text('work = ["Code.exe", "chrome.exe"]\n', encoding="utf-8")
    assert work_apps(tmp_path) == frozenset({"code.exe", "chrome.exe"})


def test_a_bad_list_is_refused(tmp_path: Path) -> None:
    (tmp_path / "focus.toml").write_text("work = 3\n", encoding="utf-8")
    with pytest.raises(FocusFileError, match=r"focus\.toml"):
        work_apps(tmp_path)
