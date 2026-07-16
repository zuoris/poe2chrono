"""
Integration tests for CronometroOverlay: real Tkinter widgets wired
to a real AppController (Run + RecordsManager), driven directly
through the overlay's own methods rather than the app's external
log-file boundary. Verifies actual widget state, not just the
underlying business logic (already covered by test_app_controller.py).
"""
import tkinter as tk

import pytest

from zarokh.app_controller import AppController
from zarokh.records import RecordsManager
from zarokh.run import Run
from zarokh.ui.overlay import CronometroOverlay


@pytest.fixture
def overlay(tmp_path):
    run = Run()
    records = RecordsManager(records_path=tmp_path / "records.json")
    controller = AppController(run=run, records=records)

    root = tk.Tk()
    root.withdraw()
    overlay = CronometroOverlay(root, controller)
    yield overlay
    root.destroy()


def test_buttons_disabled_before_run_starts(overlay):
    assert str(overlay.btn_pause_restart["state"]) == "disabled"
    assert str(overlay.btn_cancel["state"]) == "disabled"


def test_buttons_enabled_once_run_starts(overlay):
    overlay.handle_log_event("START")

    assert str(overlay.btn_pause_restart["state"]) == "normal"
    assert str(overlay.btn_cancel["state"]) == "normal"


def test_pause_restart_button_icon_and_tooltip_toggle(overlay):
    overlay.handle_log_event("START")
    assert overlay.btn_pause_restart.cget("text") == "⏸"

    overlay._on_click_pause_restart()
    assert overlay.btn_pause_restart.cget("text") == "▶"

    overlay._on_click_pause_restart()
    assert overlay.btn_pause_restart.cget("text") == "⏸"


def test_completed_run_shows_message_and_disables_buttons(overlay):
    overlay.handle_log_event("START")
    overlay.handle_log_event("FLOOR_2")
    overlay.handle_log_event("FLOOR_3")
    overlay.handle_log_event("FLOOR_4")
    overlay.handle_log_event("END")

    assert overlay.label_delta_live.cget("text") == "Run Completed!"
    assert str(overlay.btn_pause_restart["state"]) == "disabled"


def test_cancel_button_disables_controls_without_saving(overlay):
    overlay.handle_log_event("START")
    overlay.handle_log_event("FLOOR_2")  # floor 1 saved

    overlay._on_click_cancel()

    assert str(overlay.btn_pause_restart["state"]) == "disabled"
    assert str(overlay.btn_cancel["state"]) == "disabled"
    assert overlay.controller.records.best_floor_time(1) is not None
    assert overlay.controller.records.best_total_time() is None


def test_floor_completed_while_paused_cancels_and_updates_ui(overlay):
    overlay.handle_log_event("START")
    overlay._on_click_pause_restart()  # pause before floor 1 completes

    overlay.handle_log_event("FLOOR_2")

    assert str(overlay.btn_pause_restart["state"]) == "disabled"
    assert overlay.controller.records.best_floor_time(1) is None
