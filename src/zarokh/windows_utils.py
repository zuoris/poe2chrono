"""
Windows-specific utilities: taskbar icon handling and app icon
loading via ctypes.
"""
import ctypes
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_APPWINDOW = 0x00000040


def set_app_user_model_id(app_id: str) -> None:
    """
    Sets the AppUserModelID for the current process, so Windows
    groups the app's taskbar icon correctly instead of falling back
    to the Python interpreter's icon.
    """
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except OSError as e:
        logger.warning("Could not set AppUserModelID: %s", e)


def force_taskbar_icon(hwnd: int) -> None:
    """
    Applies native Windows window styles so a borderless/overrideredirect
    Tkinter window still shows up in the taskbar.

    `hwnd` is the native window handle (e.g. obtained via
    ctypes.windll.user32.GetParent(root.winfo_id()) in the caller).
    """
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    except OSError as e:
        logger.warning("Could not force taskbar icon style: %s", e)


def resolve_icon_path(base_path: Path | str, relative_path: str = "assets/images/zarokh.png") -> Path:
    """
    Resolves the icon path relative to `base_path`, which should be
    the PyInstaller-aware base directory (sys._MEIPASS when frozen,
    or the script's directory otherwise). Kept separate from the
    ctypes calls so it's trivial to test without mocking Windows APIs.
    """
    return Path(base_path) / relative_path


def get_window_handle(tk_window_id: int) -> int:
    """
    Given a Tkinter window id (root.winfo_id()), returns the native
    Win32 window handle (HWND) for its parent — needed to apply
    taskbar styles via force_taskbar_icon.
    """
    return ctypes.windll.user32.GetParent(tk_window_id)