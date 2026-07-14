from pathlib import Path
from unittest.mock import patch

from zarokh.windows_utils import (
    force_taskbar_icon,
    set_app_user_model_id,
    resolve_icon_path,
    GWL_EXSTYLE,
    WS_EX_TOOLWINDOW,
    WS_EX_APPWINDOW,
)


def test_resolve_icon_path_joins_base_and_relative_path():
    result = resolve_icon_path(Path("C:/fake/base"), "assets/images/zarokh.png")
    assert result == Path("C:/fake/base/assets/images/zarokh.png")


def test_force_taskbar_icon_clears_toolwindow_and_sets_appwindow_flags():
    with patch("zarokh.windows_utils.ctypes.windll") as mock_windll:
        mock_windll.user32.GetWindowLongW.return_value = WS_EX_TOOLWINDOW

        force_taskbar_icon(hwnd=123)

        mock_windll.user32.GetWindowLongW.assert_called_once_with(123, GWL_EXSTYLE)
        new_style = mock_windll.user32.SetWindowLongW.call_args[0][2]
        assert new_style & WS_EX_TOOLWINDOW == 0
        assert new_style & WS_EX_APPWINDOW == WS_EX_APPWINDOW


def test_force_taskbar_icon_handles_errors_gracefully():
    with patch("zarokh.windows_utils.ctypes.windll") as mock_windll:
        mock_windll.user32.GetWindowLongW.side_effect = OSError("access denied")

        force_taskbar_icon(hwnd=123)  # should not raise


def test_set_app_user_model_id_handles_errors_gracefully():
    with patch("zarokh.windows_utils.ctypes.windll") as mock_windll:
        mock_windll.shell32.SetCurrentProcessExplicitAppUserModelID.side_effect = OSError("boom")

        set_app_user_model_id("some.app.id")  # should not raise