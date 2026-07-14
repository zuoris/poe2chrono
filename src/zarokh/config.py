"""
Application configuration persistence (zarokh_config.json).
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Reads and writes the application's JSON config file.
    Knows nothing about what the config values mean (e.g. what
    "client_txt_path" is used for) — it's a thin, generic key/value
    store backed by a JSON file.
    """

    def __init__(self, config_path: Path | str = "zarokh_config.json"):
        self.config_path = Path(config_path)
        self._data: dict = {}
        self.load()

    def load(self) -> dict:
        """Loads the config file from disk. Returns an empty dict if
        it doesn't exist or can't be parsed."""
        if not self.config_path.exists():
            self._data = {}
            return self._data

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Could not load config file %s: %s", self.config_path, e)
            self._data = {}

        return self._data

    def save(self) -> None:
        """Writes the current config data to disk."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except OSError as e:
            logger.error("Could not save config file %s: %s", self.config_path, e)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value) -> None:
        """Sets a value in memory and persists it immediately."""
        self._data[key] = value
        self.save()