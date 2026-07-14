"""
Orchestrates RunTimer, RecordsManager, and LogWatcher, translating
log events into timer actions and exposing a simple API for the UI
to render. Contains no Tkinter or other UI-framework code.
"""
import logging
from dataclasses import dataclass

from zarokh.records import RecordsManager
from zarokh.timer import RunTimer, FloorResult

logger = logging.getLogger(__name__)

# Maps a LogWatcher event name to "how many floors should already be
# cleared for this event to make sense". e.g. FLOOR_2 only makes
# sense right after floor 1 is cleared (current_floor == 2).
EXPECTED_FLOOR_FOR_EVENT = {
    "START": None,   # special-cased: always (re)starts the run
    "FLOOR_2": 2,
    "FLOOR_3": 3,
    "FLOOR_4": 4,
    "END": 5,        # "END" registers the 4th floor, finishing the run
}


@dataclass
class FloorUpdate:
    """What the UI needs to know after a floor is registered."""
    floor_result: FloorResult
    best_time_for_floor: float | None
    is_run_finished: bool


class AppController:
    """
    Central orchestrator. The UI calls its methods (toggle, reset,
    register_floor, handle_log_event) and reads its properties to
    render state — it never touches RunTimer or RecordsManager
    directly.
    """

    def __init__(self, timer: RunTimer, records: RecordsManager):
        self.timer = timer
        self.records = records

    def toggle(self) -> None:
        self.timer.toggle()

    def reset(self) -> None:
        self.timer.reset()

    def best_time_for_current_floor(self) -> float | None:
        if self.timer.is_finished:
            return None
        return self.records.best_floor_time(self.timer.current_floor)

    def current_delta(self) -> float | None:
        return self.timer.current_delta(self.best_time_for_current_floor())

    def register_floor(self) -> FloorUpdate | None:
        """
        Registers the current floor, updating records if it's a new
        best. Returns None if the timer couldn't register (stopped
        or run already finished).
        """
        best_time = self.best_time_for_current_floor()
        result = self.timer.register_floor(best_time)
        if result is None:
            return None

        self.records.update_floor_time(result.floor_number, result.floor_time)

        if self.timer.is_finished:
            self.records.update_total_time(result.cumulative_time)

        return FloorUpdate(
            floor_result=result,
            best_time_for_floor=best_time,
            is_run_finished=self.timer.is_finished,
        )

    def handle_log_event(self, event_name: str) -> FloorUpdate | None:
        """
        Called by LogWatcher (via callback) whenever a trigger line
        is detected in Client.txt. Decides whether the event makes
        sense given the current run state, ignoring stale/out-of-order
        events instead of blindly acting on every line.
        """
        if event_name == "START":
            if not self.timer.running:
                self.timer.start()
            else:
                logger.info("Ignoring START event: timer already running")
            return None

        expected_floor = EXPECTED_FLOOR_FOR_EVENT.get(event_name)
        if expected_floor is None:
            logger.warning("Unknown log event: %s", event_name)
            return None

        if self.timer.current_floor != expected_floor - 1:
            logger.info(
                "Ignoring out-of-order event %s (current floor: %s)",
                event_name, self.timer.current_floor,
            )
            return None

        return self.register_floor()