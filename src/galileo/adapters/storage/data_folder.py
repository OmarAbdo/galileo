"""Omar's data folder, outside every repository. On Windows it is found through his account, not
through environment variables, so a session can't point Galileo at a folder of its own."""

import ctypes
import sys
from pathlib import Path

FOLDER_NAME = "Galileo"
MAX_PATH = 260
CURRENT_PROCESS_TOKEN = -4  # GetCurrentProcessToken(), a pseudo-handle since Windows 8


def windows_profile() -> Path:
    """The profile folder of the account this process runs as. USERPROFILE doesn't change it."""
    if sys.platform != "win32":
        raise OSError("the profile folder is looked up on Windows only")
    userenv = ctypes.WinDLL("userenv", use_last_error=True)
    size = ctypes.c_ulong(MAX_PATH)
    buffer = ctypes.create_unicode_buffer(MAX_PATH)
    token = ctypes.c_void_p(CURRENT_PROCESS_TOKEN)
    if not userenv.GetUserProfileDirectoryW(token, buffer, ctypes.byref(size)):
        raise ctypes.WinError(ctypes.get_last_error())
    return Path(buffer.value)


def data_folder() -> Path:
    if sys.platform == "win32":
        return windows_profile() / "AppData" / "Local" / FOLDER_NAME
    return Path.home() / ".local" / "share" / FOLDER_NAME
