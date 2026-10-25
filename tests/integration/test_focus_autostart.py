"""Keeping the focus sampler running: started hidden at logon, one at a time, and replaced when a
newer Galileo is installed."""

import json
import sys
import venv
from datetime import datetime, timedelta
from pathlib import Path

from galileo.adapters.focus import service
from galileo.adapters.focus.autostart import SAMPLER, autostart, keep_sampling, start
from galileo.adapters.focus.sampler import Sampler
from galileo.adapters.focus.single import hold_lock, installed_commit
from galileo.adapters.focus.samples import FileSamples
from galileo.adapters.storage.score_files import ScoreFiles
from galileo.domain.focus.blocks import Sample


def test_the_startup_file_runs_the_sampler_hidden(tmp_path: Path) -> None:
    script = autostart(tmp_path / "venv", tmp_path / "Startup")
    assert script == tmp_path / "Startup" / "galileo-focus.vbs"
    text = script.read_text(encoding="utf-8")
    assert "pythonw.exe" in text
    assert "-I -m galileo.adapters.focus.service" in text
    assert text.rstrip().endswith(", 0, False")


def test_start_runs_a_module_in_the_background() -> None:
    process = start(Path(sys.executable), "json.tool", "--help")
    assert process.wait(timeout=60) == 0


def test_keep_sampling_writes_the_startup_file_remembers_it_and_starts(tmp_path: Path) -> None:
    venv.EnvBuilder(with_pip=False).create(tmp_path / "app" / "venv")
    (tmp_path / "app" / "installed.json").write_text('{"commit": "abc"}', encoding="utf-8")
    process = keep_sampling(tmp_path / "app", tmp_path / "Startup")
    process.wait(timeout=60)
    assert (tmp_path / "Startup" / "galileo-focus.vbs").exists()
    installed = json.loads((tmp_path / "app" / "installed.json").read_text(encoding="utf-8"))
    assert installed == {"commit": "abc", "startup": str(tmp_path / "Startup")}


def test_a_second_sampler_doesnt_get_the_lock(tmp_path: Path) -> None:
    waits: list[float] = []
    first = hold_lock(tmp_path / "sampler.lock", waits.append)
    assert first is not None
    assert hold_lock(tmp_path / "sampler.lock", waits.append) is None
    assert waits == [15, 15, 15]
    first.close()
    second = hold_lock(tmp_path / "sampler.lock", waits.append)
    assert second is not None
    second.close()


def test_the_installed_commit_is_read_from_the_install(tmp_path: Path) -> None:
    assert installed_commit(tmp_path) == ""
    (tmp_path / "installed.json").write_text('{"commit": "abc"}', encoding="utf-8")
    assert installed_commit(tmp_path) == "abc"


def test_the_sampler_stops_when_a_newer_galileo_is_installed(tmp_path: Path) -> None:
    commits = iter(["old", "old", "old", "new"])
    times = iter(datetime(2026, 11, 2, 9, 0) + timedelta(seconds=15 * step) for step in range(9))
    sampler = Sampler(
        read=lambda now: Sample(now, "code.exe", 0.0),
        samples=FileSamples(tmp_path / "focus"),
        scores=ScoreFiles(tmp_path),
        now=lambda: next(times),
        sleep=lambda _seconds: None,
        installed=lambda: next(commits),
    )
    sampler.run()
    assert len(FileSamples(tmp_path / "focus").samples(datetime(2026, 11, 2).date())) == 2


def test_the_launcher_runs_the_service_module() -> None:
    assert service.__name__ == SAMPLER


def test_the_service_samples_until_a_new_install_then_lets_go(tmp_path: Path) -> None:
    record = tmp_path / "app" / "installed.json"
    record.parent.mkdir()
    record.write_text('{"commit": "old"}', encoding="utf-8")

    def sleep(_seconds: float) -> None:
        record.write_text('{"commit": "new"}', encoding="utf-8")

    code = service.serve(tmp_path, lambda now: Sample(now, "code.exe", 0.0), sleep)
    assert code == 0
    days = FileSamples(tmp_path / "focus").days()
    assert len(FileSamples(tmp_path / "focus").samples(days[0])) == 1
    released = hold_lock(tmp_path / "focus" / "sampler.lock", sleep)
    assert released is not None
    released.close()


def test_the_service_leaves_while_another_sampler_runs(tmp_path: Path) -> None:
    held = hold_lock(tmp_path / "focus" / "sampler.lock", lambda _seconds: None)
    assert held is not None
    assert service.serve(tmp_path, lambda now: Sample(now, "code.exe", 0.0), lambda _: None) == 0
    assert FileSamples(tmp_path / "focus").days() == []
    held.close()
