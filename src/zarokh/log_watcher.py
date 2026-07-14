"""
Watches Path of Exile 2's Client.txt log file for Sanctum-related
triggers, running on a background thread.
"""
import logging
import os
import threading
import time
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

TRIGGERS = {
    "START": 'area "Sanctum_1_Foyer',
    "FLOOR_2": 'area "Sanctum_2_Foyer',
    "FLOOR_3": 'area "Sanctum_3_Foyer',
    "FLOOR_4": 'area "Sanctum_4_Foyer',
    "END": 'Zarokh, the Temporal: Ugh...',
}


class LogWatcher:
    """
    Tails a Client.txt file on a background thread and invokes
    `on_trigger(event_name)` whenever a known trigger line appears.
    Knows nothing about the timer, the UI, or Tkinter.
    """

    def __init__(
        self,
        log_path: Path | str,
        on_trigger: Callable[[str], None],
        poll_interval: float = 0.1,
    ):
        self.log_path = Path(log_path)
        self.on_trigger = on_trigger
        self.poll_interval = poll_interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Starts watching the log file on a daemon thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signals the watcher thread to stop."""
        self._stop_event.set()

    def _watch(self) -> None:
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="ignore") as f:
                f.seek(0, os.SEEK_END)
                while not self._stop_event.is_set():
                    line = f.readline()
                    if not line:
                        time.sleep(self.poll_interval)
                        continue
                    self._process_line(line)
        except OSError as e:
            logger.error("Could not read log file %s: %s", self.log_path, e)

    def _process_line(self, line: str) -> None:
        event_name = match_trigger(line)
        if event_name:
            self.on_trigger(event_name)


def match_trigger(line: str) -> str | None:
    """
    Returns the name of the trigger matched in `line`, or None if
    no trigger matches. Pulled out as a standalone function so it
    can be tested without threads or real files.
    """
    for event_name, trigger_text in TRIGGERS.items():
        if trigger_text in line:
            return event_name
    return None