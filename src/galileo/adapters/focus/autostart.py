"""Keeping the focus sampler running: a hidden launcher in Omar's Startup folder for every logon,
and a sampler started right away by the install and by `galileo update`."""

import json
import subprocess
import sys
from pathlib import Path

from galileo.adapters.storage.data_folder import windows_profile

SAMPLER = "galileo.adapters.focus.service"
STARTUP = Path("AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup")
# Started on its own, with no window, and not ended with the terminal that started it.
DETACHED = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)


def startup_folder() -> Path:
    return windows_profile() / STARTUP


def background_interpreter(environment: Path) -> Path:
    return environment / ("Scripts/pythonw.exe" if sys.platform == "win32" else "bin/python")


def autostart(environment: Path, startup: Path) -> Path:
    """A launcher that Windows runs at logon: the sampler, hidden (window style 0)."""
    python = environment / "Scripts" / "pythonw.exe"
    line = f'CreateObject("WScript.Shell").Run """{python}"" -I -m {SAMPLER}", 0, False\r\n'
    startup.mkdir(parents=True, exist_ok=True)
    script = startup / "galileo-focus.vbs"
    script.write_text(line, encoding="utf-8")
    return script


def start(python: Path, module: str, *arguments: str) -> subprocess.Popen[bytes]:
    command = [str(python), "-I", "-m", module, *arguments]
    stream = subprocess.DEVNULL
    return subprocess.Popen(  # the sampler runs for as long as Omar is logged on
        command, stdin=stream, stdout=stream, stderr=stream, creationflags=DETACHED
    )


def keep_sampling(home: Path, startup: Path) -> subprocess.Popen[bytes]:
    """The launcher, remembered in the install record for `galileo update`, and a sampler now.
    A sampler already running keeps its lock, so the new one waits for it or leaves."""
    autostart(home / "venv", startup)
    installed_path = home / "installed.json"
    installed = json.loads(installed_path.read_text(encoding="utf-8"))
    installed_path.write_text(json.dumps({**installed, "startup": str(startup)}), "utf-8")
    return start(background_interpreter(home / "venv"), SAMPLER)
