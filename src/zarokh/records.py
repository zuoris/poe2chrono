"""
Persistence for best-time records and full run history
(zarokh_data.json). This file replaces zarokh_records.json — if the
new file doesn't exist yet but the old one does, its content is
migrated in automatically the first time the app runs after this
change, so existing users don't lose their saved records.
"""
import json
import logging
from pathlib import Path

from zarokh.run import TOTAL_FLOORS

logger = logging.getLogger(__name__)

LEGACY_RECORDS_FILENAME = "zarokh_records.json"


def _default_data() -> dict:
    return {
        "records": {"floors": [None] * TOTAL_FLOORS, "total": None},
        "runs": [],
    }


class RecordsManager:
    """
    Reads, writes, and compares best-time records, and stores the
    full history of past runs. Both live in a single JSON file since
    they're always read/written together.
    """

    def __init__(self, data_path: Path | str = "zarokh_data.json"):
        self.data_path = Path(data_path)
        self._data: dict = {}
        self.load()

    def load(self) -> dict:
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Could not load data file %s: %s", self.data_path, e)
                self._data = _default_data()
            return self._data

        migrated = self._migrate_legacy_records()
        if migrated is not None:
            self._data = migrated
            return self._data

        self._data = _default_data()
        return self._data

    def _migrate_legacy_records(self) -> dict | None:
        legacy_path = self.data_path.parent / LEGACY_RECORDS_FILENAME
        if not legacy_path.exists():
            return None

        try:
            with open(legacy_path, "r", encoding="utf-8") as f:
                legacy_records = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Could not migrate legacy records file %s: %s", legacy_path, e)
            return None

        logger.info("Migrating legacy records file %s to %s", legacy_path, self.data_path)
        data = _default_data()
        data["records"] = legacy_records
        self._data = data
        self.save()
        return data

    def save(self) -> None:
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except OSError as e:
            logger.error("Could not save data file %s: %s", self.data_path, e)

    def clear(self) -> None:
        """Resets best-time records only — run history is untouched,
        it's a permanent log, not a "current best" you'd want to
        accidentally wipe."""
        self._data["records"] = _default_data()["records"]
        self.save()

    # --- best-time records --------------------------------------------

    def best_floor_time(self, floor_number: int) -> float | None:
        return self._data["records"]["floors"][floor_number - 1]

    def best_total_time(self) -> float | None:
        return self._data["records"]["total"]

    def update_floor_time(self, floor_number: int, floor_time: float) -> bool:
        current_best = self.best_floor_time(floor_number)
        if current_best is None or floor_time < current_best:
            self._data["records"]["floors"][floor_number - 1] = floor_time
            self.save()
            return True
        return False

    def update_total_time(self, total_time: float) -> bool:
        current_best = self.best_total_time()
        if current_best is None or total_time < current_best:
            self._data["records"]["total"] = total_time
            self.save()
            return True
        return False

    # --- run history -----------------------------------------------------

    def next_attempt_number(self) -> int:
        return len(self._data["runs"]) + 1

    def add_run(self, floor_times: list[float], total_time: float | None) -> int:
        """Appends a new run to history and persists it. total_time
        is None for a cancelled run. Returns the assigned attempt
        number."""
        attempt = self.next_attempt_number()
        self._data["runs"].append({
            "attempt": attempt,
            "floor_times": floor_times,
            "total_time": total_time,
        })
        self.save()
        return attempt

    def list_runs(self) -> list[dict]:
        """Runs in reverse chronological order (most recent first)."""
        return list(reversed(self._data["runs"]))
