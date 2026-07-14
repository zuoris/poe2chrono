from zarokh.timer import RunTimer


def test_register_floor_calculates_time_correctly():
    timer = RunTimer()
    timer.start()
    timer.accumulated_time = 10.0  # simulate 10s already elapsed
    timer.running = False
    timer.start()  # resume from 10.0

    result = timer.register_floor(best_time_for_floor=None)

    assert result.floor_number == 1
    assert result.is_new_record is True
    assert timer.current_floor == 2


def test_finished_run_is_marked_as_finished():
    timer = RunTimer(current_floor=5)
    assert timer.is_finished is True