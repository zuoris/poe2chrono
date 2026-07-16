import pytest

from zarokh.stopwatch import Stopwatch


def test_starts_at_zero():
    sw = Stopwatch()
    assert sw.elapsed_time() == 0.0


def test_start_then_pause_accumulates_time():
    sw = Stopwatch()
    sw.start()
    sw.accumulated_time = 0.0
    sw._start_time -= 5.0  # simulate 5 seconds elapsed
    sw.pause()
    assert sw.elapsed_time() == pytest.approx(5.0, abs=0.05)


def test_toggle_switches_between_running_and_paused():
    sw = Stopwatch()
    sw.toggle()
    assert sw.running is True
    sw.toggle()
    assert sw.running is False


def test_reset_clears_everything():
    sw = Stopwatch()
    sw.start()
    sw.accumulated_time = 10.0
    sw.reset()
    assert sw.running is False
    assert sw.elapsed_time() == 0.0


def test_resume_continues_from_accumulated_time():
    sw = Stopwatch()
    sw.start()
    sw._start_time -= 3.0
    sw.pause()
    assert sw.accumulated_time == pytest.approx(3.0, abs=0.05)
    sw.start()
    assert sw.elapsed_time() == pytest.approx(3.0, abs=0.05)
