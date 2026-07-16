"""
Application entry point. Wires together ConfigManager, RecordsManager,
Run, AppController, LogWatcher, and the Tkinter UI.
"""
import logging
import logging.handlers
import sys
from pathlib import Path

import tkinter as tk
from tkinter import filedialog

from zarokh.app_controller import AppController
from zarokh.client_log_locator import find_client_log_path
from zarokh.config import ConfigManager
from zarokh.log_watcher import LogWatcher
from zarokh.records import RecordsManager
from zarokh.run import Run
from zarokh.ui.overlay import CronometroOverlay


def setup_logging() -> None:
    if getattr(sys, "frozen", False):
        log_dir = Path(sys.executable).parent
    else:
        log_dir = Path(__file__).resolve().parents[2]

    log_file = log_dir / "zarokh.log"

    handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when="midnight", backupCount=1, encoding="utf-8",
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[handler],
    )


def _prompt_for_client_log(config: ConfigManager) -> str | None:
    while True:
        selected = filedialog.askopenfilename(
            title="Zarokh: Select your Client.txt to continue",
            filetypes=[("Text Files", "Client.txt"), ("All Files", "*.*")],
        )
        if not selected:
            return None
        config.set("client_txt_path", selected)
        path = find_client_log_path(config)
        if path:
            return path


def main() -> None:
    setup_logging()
    logging.getLogger(__name__).info("Zarokh starting up")

    config = ConfigManager()
    records = RecordsManager()
    run = Run()
    controller = AppController(run=run, records=records)

    root = tk.Tk()
    root.withdraw()

    client_log_path = find_client_log_path(config) or _prompt_for_client_log(config)
    if not client_log_path:
        root.destroy()
        return

    overlay = CronometroOverlay(root, controller)
    root.deiconify()

    def on_log_trigger(event_name: str) -> None:
        root.after(0, overlay.handle_log_event, event_name)

    watcher = LogWatcher(client_log_path, on_trigger=on_log_trigger)
    watcher.start()

    root.mainloop()


if __name__ == "__main__":
    main()
