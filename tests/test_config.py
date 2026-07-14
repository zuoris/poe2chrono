import json

from zarokh.config import ConfigManager


def test_load_returns_empty_dict_when_file_does_not_exist(tmp_path):
    config = ConfigManager(config_path=tmp_path / "does_not_exist.json")
    assert config.get("anything") is None


def test_set_persists_value_to_disk(tmp_path):
    config_path = tmp_path / "config.json"
    config = ConfigManager(config_path=config_path)

    config.set("client_txt_path", r"C:\some\path\Client.txt")

    with open(config_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data["client_txt_path"] == r"C:\some\path\Client.txt"


def test_get_returns_default_when_key_missing(tmp_path):
    config = ConfigManager(config_path=tmp_path / "config.json")
    assert config.get("missing_key", default="fallback") == "fallback"


def test_load_recovers_from_corrupted_file(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text("{ not valid json", encoding="utf-8")

    config = ConfigManager(config_path=config_path)

    assert config.get("anything") is None