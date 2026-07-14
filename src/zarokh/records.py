"""
Persistence and comparison logic for floor/run best times
(zarokh_records.json).
"""
import json
import logging
from pathlib import Path

from zarokh.timer import TOTAL_FLOORS

logger = logging.getLogger(__name__)

DEFAULT_RECORDS = {
    "floors": [None] * TOTAL_FLOORS,
    "total": None,
}


class RecordsManager:
    """
    Reads, writes, and compares best-time records for floors and
    full runs. Like ConfigManager, this is a thin persistence layer;
    it doesn't know anything about the timer or the UI.
    """

    def __init__(self, records_path: Path | str = "zarokh_records.json"):
        self.records_path = Path(records_path)
        self._data: dict = {}
        self.load()

    def load(self) -> dict:
        """Loads records from disk, falling back to empty defaults
        if the file doesn't exist or can't be parsed."""
        if not self.records_path.exists():
            self._data = self._default_records()
            return self._data

        try:
            with open(self.records_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Could not load records file %s: %s", self.records_path, e)
            self._data = self._default_records()

        return self._data

    def save(self) -> None:
        """Writes the current records to disk."""
        try:
            with open(self.records_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except OSError as e:
            logger.error("Could not save records file %s: %s", self.records_path, e)

    def clear(self) -> None:
        """Resets all records to empty and persists the change."""
        self._data = self._default_records()
        self.save()

    def best_floor_time(self, floor_number: int) -> float | None:
        """Best recorded time for a given floor (1-indexed), or None."""
        return self._data["floors"][floor_number - 1]

    def best_total_time(self) -> float | None:
        """Best recorded total run time, or None."""
        return self._data["total"]

    def update_floor_time(self, floor_number: int, floor_time: float) -> bool:
        """
        Updates the record for a floor if floor_time is better than
        the current one (or if there's no record yet). Persists the
        change if updated. Returns True if a new record was set.
        """
        current_best = self.best_floor_time(floor_number)
        if current_best is None or floor_time < current_best:
            self._data["floors"][floor_number - 1] = floor_time
            self.save()
            return True
        return False

    def update_total_time(self, total_time: float) -> bool:
        """
        Updates the total run record if total_time is better than
        the current one. Persists the change if updated. Returns
        True if a new record was set.
        """
        current_best = self.best_total_time()
        if current_best is None or total_time < current_best:
            self._data["total"] = total_time
            self.save()
            return True
        return False

    @staticmethod
    def _default_records() -> dict:
        return {
            "floors": [None] * TOTAL_FLOORS,
            "total": None,
        }