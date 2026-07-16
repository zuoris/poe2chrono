"""
Orchestrates Run, RecordsManager, and LogWatcher, translating log
events into run actions and exposing a simple API for the UI to
render. Contains no Tkinter or other UI-framework code.
"""
import logging
from dataclasses import dataclass

from zarokh.records import RecordsManager
from zarokh.run import TOTAL_FLOORS, FloorResult, Run, RunState

logger = logging.getLogger(__name__)

EXPECTED_FLOOR_FOR_EVENT = {
    "START": None,
    "FLOOR_2": 2,
    "FLOOR_3": 3,
    "FLOOR_4": 4,
    "END": 5,
}


@dataclass
class FloorUpdate:
    floor_result: FloorResult
    best_time_for_floor: float | None
    is_run_finished: bool


class AppController:
    def __init__(self, run: Run, records: RecordsManager):
        self.run = run
        self.records = records

    def toggle_pause(self) -> None:
        self.run.toggle_pause()

    def cancel(self) -> None:
        self.run.cancel()

    def best_time_for_current_floor(self) -> float | None:
        if self.run.current_floor > TOTAL_FLOORS:
            return None
        return self.records.best_floor_time(self.run.current_floor)

    def current_delta(self) -> float | None:
        best_time = self.best_time_for_current_floor()
        if best_time is None:
            return None
        return self.run.floor_timer.elapsed_time() - best_time

    def register_floor(self) -> FloorUpdate | None:
        best_time = self.best_time_for_current_floor()
        result = self.run.register_floor(best_time)
        if result is None:
            return None

        self.records.update_floor_time(result.floor_number, result.floor_time)

        is_run_finished = self.run.current_floor > TOTAL_FLOORS
        if is_run_finished:
            self.records.update_total_time(result.cumulative_time)

        return FloorUpdate(
            floor_result=result,
            best_time_for_floor=best_time,
            is_run_finished=is_run_finished,
        )

    def handle_log_event(self, event_name: str) -> FloorUpdate | None:
        if event_name == "START":
            if self.run.state == RunState.IDLE:
                self.run.start()
            else:
                logger.info("Ignoring START event: run already in progress")
            return None

        expected_floor = EXPECTED_FLOOR_FOR_EVENT.get(event_name)
        if expected_floor is None:
            logger.warning("Unknown log event: %s", event_name)
            return None

        if self.run.state != RunState.RUNNING:
            logger.info("Ignoring %s event: no run in progress", event_name)
            return None

        if self.run.current_floor != expected_floor - 1:
            logger.info(
                "Ignoring out-of-order event %s (current floor: %s)",
                event_name, self.run.current_floor,
            )
            return None

        if self.run.is_paused:
            logger.warning(
                "Floor completed while paused (forgot to resume?) — "
                "cancelling this run without saving records."
            )
            self.run.cancel()
            return None

        return self.register_floor()
