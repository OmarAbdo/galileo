"""Reading what is in front of Omar through the Windows calls: with fakes of the two DLLs here,
and with the real ones on Windows."""

import ctypes
import sys
from types import SimpleNamespace
from typing import Any

import pytest

from galileo.adapters.focus.probe import (
    Dlls,
    LastInput,
    foreground_app,
    idle_seconds,
    windows_dlls,
)

CODE = r"C:\Users\Omar\AppData\Local\Programs\Microsoft VS Code\Code.exe"


def fake_dlls(path: str = CODE, process_id: int = 4242) -> tuple[Dlls, list[Any]]:
    closed: list[Any] = []

    def thread_process(_window: Any, process: Any) -> int:
        process._obj.value = process_id
        return 1

    def image_name(_handle: Any, _flags: int, buffer: Any, _size: Any) -> int:
        buffer.value = path
        return 1 if path else 0

    def last_input(info: Any) -> int:
        info._obj.time = 1000
        return 1

    user32 = SimpleNamespace(
        GetForegroundWindow=lambda: 77,
        GetWindowThreadProcessId=thread_process,
        GetLastInputInfo=last_input,
    )
    kernel32 = SimpleNamespace(
        OpenProcess=lambda _access, _inherit, found: 9 if found == 4242 else 0,
        QueryFullProcessImageNameW=image_name,
        CloseHandle=closed.append,
        GetTickCount=lambda: 6500,
    )
    return Dlls(user32, kernel32), closed


def test_the_app_in_front_is_its_lower_case_file_name() -> None:
    dlls, closed = fake_dlls()
    assert foreground_app(dlls) == "code.exe"
    assert len(closed) == 1


def test_a_process_that_cant_be_opened_is_an_unknown_app() -> None:
    dlls, closed = fake_dlls(process_id=1)
    assert foreground_app(dlls) == ""
    assert closed == []


def test_a_name_that_cant_be_read_is_an_unknown_app() -> None:
    dlls, closed = fake_dlls(path="")
    assert foreground_app(dlls) == ""
    assert len(closed) == 1


def test_idle_seconds_since_the_last_input() -> None:
    assert idle_seconds(fake_dlls()[0]) == pytest.approx(5.5)


@pytest.mark.skipif(sys.platform != "win32", reason="the real Windows calls")
def test_the_real_calls_answer() -> None:
    dlls = windows_dlls()
    assert isinstance(foreground_app(dlls), str)
    assert idle_seconds(dlls) >= 0


@pytest.mark.skipif(sys.platform == "win32", reason="elsewhere")
def test_other_systems_are_refused() -> None:
    with pytest.raises(OSError, match="Windows"):
        windows_dlls()


def test_the_structure_has_the_size_windows_expects() -> None:
    assert ctypes.sizeof(LastInput) == 8
