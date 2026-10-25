"""What is in front of Omar, through the Windows calls: the file name of the app in front (never
the window's title) and the seconds since his last key or mouse input. The two DLLs are passed
in, so the logic here also runs against fakes."""

import ctypes
import sys
from dataclasses import dataclass
from pathlib import PureWindowsPath
from typing import Any

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MAX_PATH = 260
TICK_MASK = 0xFFFFFFFF  # GetTickCount wraps around after 49.7 days


class LastInput(ctypes.Structure):
    """Windows' LASTINPUTINFO."""

    _fields_ = [("size", ctypes.c_uint), ("time", ctypes.c_uint)]


@dataclass(frozen=True)
class Dlls:
    user32: Any
    kernel32: Any


def windows_dlls() -> Dlls:
    if sys.platform != "win32":
        raise OSError("the focus sampler reads the screen on Windows only")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    return Dlls(ctypes.WinDLL("user32", use_last_error=True), kernel32)


def foreground_app(dlls: Dlls) -> str:
    """The lower-case file name of the app in front, or "" when Windows won't say."""
    process = ctypes.c_ulong()
    window = ctypes.c_void_p(dlls.user32.GetForegroundWindow())
    dlls.user32.GetWindowThreadProcessId(window, ctypes.byref(process))
    handle = dlls.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, process.value)
    if not handle:
        return ""
    try:
        size = ctypes.c_ulong(MAX_PATH)
        buffer = ctypes.create_unicode_buffer(MAX_PATH)
        found = dlls.kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size))
        return PureWindowsPath(buffer.value).name.lower() if found else ""
    finally:
        dlls.kernel32.CloseHandle(ctypes.c_void_p(handle))


def idle_seconds(dlls: Dlls) -> float:
    last = LastInput(ctypes.sizeof(LastInput), 0)
    dlls.user32.GetLastInputInfo(ctypes.byref(last))
    ticks = int(dlls.kernel32.GetTickCount()) - int(last.time)
    return (ticks & TICK_MASK) / 1000
