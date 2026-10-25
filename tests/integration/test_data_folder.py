"""Where Galileo keeps Omar's data: outside every repository, where a session can't move it."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from galileo.adapters.storage.data_folder import data_folder, windows_profile

SOURCE = Path(__file__).resolve().parents[2] / "src"
PRINT_FOLDER = (
    "import sys; from galileo.adapters.storage.data_folder import data_folder; "
    "sys.stdout.write(str(data_folder()))"
)


@pytest.mark.skipif(sys.platform != "win32", reason="the Windows lookup")
def test_on_windows_it_is_local_app_data_of_the_profile() -> None:
    folder = data_folder()
    assert folder == windows_profile() / "AppData" / "Local" / "Galileo"
    assert folder.is_absolute()


@pytest.mark.skipif(sys.platform != "win32", reason="the Windows lookup")
def test_environment_variables_dont_move_it(tmp_path: Path) -> None:
    faked = {
        **os.environ,
        "PYTHONPATH": str(SOURCE),
        "USERPROFILE": str(tmp_path),
        "LOCALAPPDATA": str(tmp_path),
        "HOMEPATH": str(tmp_path),
    }
    finished = subprocess.run(
        [sys.executable, "-c", PRINT_FOLDER],
        env=faked,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    assert finished.stdout == str(data_folder())


@pytest.mark.skipif(sys.platform == "win32", reason="the lookup elsewhere")
def test_elsewhere_it_is_in_the_home_folder() -> None:
    assert data_folder() == Path.home() / ".local" / "share" / "Galileo"


@pytest.mark.skipif(sys.platform == "win32", reason="the lookup elsewhere")
def test_the_windows_lookup_refuses_other_systems() -> None:
    with pytest.raises(OSError, match="Windows"):
        windows_profile()
