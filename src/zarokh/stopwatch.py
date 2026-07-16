"""
A generic stopwatch: start/pause/resume/reset and elapsed time.
Knows nothing about runs, floors, or any business concept — it can
be reused for any "measure elapsed time" need.
"""
import time
from dataclasses import dataclass


@dataclass
class Stopwatch:
    running: bool = False
    _start_time: float = 0.0
    accumulated_time: float = 0.0

    def start(self) -> None:
        if self.running:
            return
        self._start_time = time.time()
        self.running = True

    def pause(self) -> None:
        if not self.running:
            return
        self.accumulated_time += time.time() - self._start_time
        self.running = False

    def toggle(self) -> None:
        self.pause() if self.running else self.start()

    def reset(self) -> None:
        self.running = False
        self.accumulated_time = 0.0

    def elapsed_time(self) -> float:
        if self.running:
            return self.accumulated_time + (time.time() - self._start_time)
        return self.accumulated_time
