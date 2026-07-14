"""
Application entry point. Wires together ConfigManager, RecordsManager,
RunTimer, AppController, LogWatcher, and the Tkinter UI.
"""
import logging
import logging.handlers
import sys
from pathlib import Path

import tkinter as tk

from zarokh.app_controller import AppController
from zarokh.client_log_locator import find_client_log_path
from zarokh.config import ConfigManager
from zarokh.log_watcher import LogWatcher
from zarokh.records import RecordsManager
from zarokh.timer import RunTimer
from zarokh.ui.overlay import CronometroOverlay


def setup_logging() -> None:
    """
    Configures logging once, at startup. Writes to a file next to
    the executable (or the script, in dev), rotating daily and
    keeping only the last 24 hours of logs.
    """
    if getattr(sys, "frozen", False):
        log_dir = Path(sys.executable).parent
    else:
        log_dir = Path(__file__).resolve().parents[2]

    log_file = log_dir / "zarokh.log"

    handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when="midnight",
        backupCount=1,
        encoding="utf-8",
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[handler],
    )


def main() -> None:
    setup_logging()
    logging.getLogger(__name__).info("Zarokh starting up")

    config = ConfigManager()
    records = RecordsManager()
    timer = RunTimer()
    controller = AppController(timer=timer, records=records)

    client_log_path = find_client_log_path(config)

    root = tk.Tk()
    log_watcher_holder: dict = {"instance": None}

    def start_log_watcher(path: str, overlay: CronometroOverlay) -> None:
        if log_watcher_holder["instance"] is not None:
            log_watcher_holder["instance"].stop()

        def on_log_trigger(event_name: str) -> None:
            root.after(0, overlay.handle_log_event, event_name)

        watcher = LogWatcher(path, on_trigger=on_log_trigger)
        watcher.start()
        log_watcher_holder["instance"] = watcher

    def on_manual_path_selected(path: str) -> None:
        config.set("client_txt_path", path)
        start_log_watcher(path, overlay)

    overlay = CronometroOverlay(
        root,
        controller,
        auto_mode=bool(client_log_path),
        on_manual_path_selected=on_manual_path_selected,
    )

    if client_log_path:
        start_log_watcher(client_log_path, overlay)

    root.mainloop()


if __name__ == "__main__":
    main()