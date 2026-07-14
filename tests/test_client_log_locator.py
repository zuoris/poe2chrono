# tests/test_client_log_locator.py
from unittest.mock import patch, MagicMock

from zarokh.config import ConfigManager
from zarokh.client_log_locator import find_client_log_path, _find_path_in_registry


def test_returns_saved_path_if_it_still_exists(tmp_path):
    fake_client_log = tmp_path / "Client.txt"
    fake_client_log.write_text("")

    config = ConfigManager(config_path=tmp_path / "config.json")
    config.set("client_txt_path", str(fake_client_log))

    result = find_client_log_path(config)

    assert result == str(fake_client_log)


def test_ignores_saved_path_if_file_no_longer_exists(tmp_path):
    config = ConfigManager(config_path=tmp_path / "config.json")
    config.set("client_txt_path", str(tmp_path / "deleted.txt"))

    result = find_client_log_path(
        config,
        default_paths=[],
        registry_lookup=lambda: None,
    )

    assert result is None


def test_find_path_in_registry_returns_path_when_key_exists():
    fake_install_path = r"C:\Games\Path of Exile 2"

    with patch("zarokh.client_log_locator.winreg.OpenKey") as mock_open_key, \
         patch("zarokh.client_log_locator.winreg.QueryValueEx") as mock_query:

        mock_open_key.return_value.__enter__.return_value = MagicMock()
        mock_query.return_value = (fake_install_path, 1)

        result = _find_path_in_registry()

        assert result == r"C:\Games\Path of Exile 2\logs\Client.txt"


def test_find_path_in_registry_returns_none_when_key_missing():
    with patch("zarokh.client_log_locator.winreg.OpenKey", side_effect=OSError("key not found")):
        result = _find_path_in_registry()

    assert result is None