from zarokh.app_controller import AppController
from zarokh.records import RecordsManager
from zarokh.timer import RunTimer


def make_controller(tmp_path):
    timer = RunTimer()
    records = RecordsManager(records_path=tmp_path / "records.json")
    return AppController(timer=timer, records=records), timer, records


def test_start_event_resumes_without_resetting(tmp_path):
    controller, timer, _ = make_controller(tmp_path)
    timer.current_floor = 3  # simulate a run in progress, timer paused

    controller.handle_log_event("START")

    assert timer.current_floor == 3  # untouched
    assert timer.running is True


def test_start_event_ignored_when_already_running(tmp_path):
    controller, timer, _ = make_controller(tmp_path)
    timer.start()
    timer.current_floor = 2

    controller.handle_log_event("START")

    assert timer.current_floor == 2  # untouched
    assert timer.running is True


def test_floor_2_event_registers_floor_when_on_floor_1(tmp_path):
    controller, timer, records = make_controller(tmp_path)
    controller.handle_log_event("START")

    update = controller.handle_log_event("FLOOR_2")

    assert update is not None
    assert update.floor_result.floor_number == 1
    assert timer.current_floor == 2


def test_floor_3_event_ignored_when_still_on_floor_1(tmp_path):
    controller, timer, _ = make_controller(tmp_path)
    controller.handle_log_event("START")

    update = controller.handle_log_event("FLOOR_3")  # out of order, skipped FLOOR_2

    assert update is None
    assert timer.current_floor == 1  # nothing changed


def test_register_floor_updates_records_when_new_best(tmp_path):
    controller, timer, records = make_controller(tmp_path)
    controller.handle_log_event("START")

    controller.handle_log_event("FLOOR_2")

    assert records.best_floor_time(1) is not None


def test_end_event_finishes_run_and_updates_total_record(tmp_path):
    controller, timer, records = make_controller(tmp_path)
    controller.handle_log_event("START")
    controller.handle_log_event("FLOOR_2")
    controller.handle_log_event("FLOOR_3")
    controller.handle_log_event("FLOOR_4")

    update = controller.handle_log_event("END")

    assert update.is_run_finished is True
    assert records.best_total_time() is not None


def test_manual_register_floor_works_without_log_events(tmp_path):
    controller, timer, records = make_controller(tmp_path)
    controller.toggle()  # manual start, no log watcher involved

    update = controller.register_floor()

    assert update is not None
    assert records.best_floor_time(1) is not None
