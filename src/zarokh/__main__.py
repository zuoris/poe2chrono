"""
Application entry point. Wires together ConfigManager, RecordsManager,
RunTimer, AppController, LogWatcher, and the Tkinter UI.
"""
import tkinter as tk

from zarokh.app_controller import AppController
from zarokh.client_log_locator import find_client_log_path
from zarokh.config import ConfigManager
from zarokh.log_watcher import LogWatcher
from zarokh.records import RecordsManager
from zarokh.timer import RunTimer
from zarokh.ui.overlay import CronometroOverlay


def main() -> None:
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