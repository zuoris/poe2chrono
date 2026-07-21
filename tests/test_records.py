from zarokh.records import RecordsManager


def test_load_returns_defaults_when_file_does_not_exist(tmp_path):
    records = RecordsManager(data_path=tmp_path / "does_not_exist.json")
    assert records.best_floor_time(1) is None
    assert records.best_total_time() is None


def test_update_floor_time_sets_record_when_none_exists(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")

    is_new_record = records.update_floor_time(1, 45.5)

    assert is_new_record is True
    assert records.best_floor_time(1) == 45.5


def test_update_floor_time_replaces_record_when_better(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")
    records.update_floor_time(1, 45.5)

    is_new_record = records.update_floor_time(1, 40.0)

    assert is_new_record is True
    assert records.best_floor_time(1) == 40.0


def test_update_floor_time_keeps_record_when_worse(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")
    records.update_floor_time(1, 40.0)

    is_new_record = records.update_floor_time(1, 45.5)

    assert is_new_record is False
    assert records.best_floor_time(1) == 40.0


def test_update_total_time_sets_record_when_none_exists(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")

    is_new_record = records.update_total_time(180.0)

    assert is_new_record is True
    assert records.best_total_time() == 180.0


def test_clear_resets_all_records(tmp_path):
    records = RecordsManager(data_path=tmp_path / "records.json")
    records.update_floor_time(1, 40.0)
    records.update_total_time(180.0)

    records.clear()

    assert records.best_floor_time(1) is None
    assert records.best_total_time() is None


def test_records_persist_across_instances(tmp_path):
    data_path = tmp_path / "records.json"

    first_instance = RecordsManager(data_path=data_path)
    first_instance.update_floor_time(2, 30.0)

    second_instance = RecordsManager(data_path=data_path)

    assert second_instance.best_floor_time(2) == 30.0


def test_load_recovers_from_corrupted_file(tmp_path):
    data_path = tmp_path / "records.json"
    data_path.write_text("{ not valid json", encoding="utf-8")

    records = RecordsManager(data_path=data_path)

    assert records.best_floor_time(1) is None

def test_add_run_assigns_sequential_attempt_numbers(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    records.add_run([10.0, 12.0], 22.0)
    attempt = records.add_run([9.0], None)
    assert attempt == 2


def test_list_runs_returns_most_recent_first(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    records.add_run([10.0], None)
    records.add_run([9.0], None)
    runs = records.list_runs()
    assert runs[0]["attempt"] == 2
    assert runs[1]["attempt"] == 1


def test_cancelled_run_has_null_total_time(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    records.add_run([10.0, 12.0], None)
    assert records.list_runs()[0]["total_time"] is None


def test_migrates_legacy_records_file(tmp_path):
    legacy_path = tmp_path / "zarokh_records.json"
    legacy_path.write_text(
        '{"floors": [40.0, null, null, null], "total": null}', encoding="utf-8",
    )
    records = RecordsManager(data_path=tmp_path / "zarokh_data.json")
    assert records.best_floor_time(1) == 40.0
    assert records.list_runs() == []

def test_add_run_initializes_relics_only_when_completed(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    completed = records.add_run([10.0, 12.0, 11.0, 13.0], 46.0)
    cancelled = records.add_run([10.0], None)

    completed_run = records._find_run(completed)
    cancelled_run = records._find_run(cancelled)

    assert "relics" in completed_run
    assert all(count == 0 for count in completed_run["relics"].values())
    assert "relics" not in cancelled_run


def test_adjust_relic_count_increments_and_decrements(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    attempt = records.add_run([10.0, 12.0, 11.0, 13.0], 46.0)

    new_count = records.adjust_relic_count(attempt, "The Last Flame", 1)
    assert new_count == 1

    new_count = records.adjust_relic_count(attempt, "The Last Flame", -1)
    assert new_count == 0


def test_adjust_relic_count_never_goes_below_zero(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    attempt = records.add_run([10.0, 12.0, 11.0, 13.0], 46.0)

    new_count = records.adjust_relic_count(attempt, "The Last Flame", -1)
    assert new_count == 0


def test_adjust_relic_count_returns_none_for_cancelled_run(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    attempt = records.add_run([10.0], None)

    assert records.adjust_relic_count(attempt, "The Last Flame", 1) is None


def test_relic_totals_sums_across_completed_runs_only(tmp_path):
    records = RecordsManager(data_path=tmp_path / "data.json")
    a1 = records.add_run([10.0, 12.0, 11.0, 13.0], 46.0)
    a2 = records.add_run([9.0, 12.0, 11.0, 13.0], 45.0)
    records.add_run([10.0], None)  # cancelled, shouldn't count

    records.adjust_relic_count(a1, "The Last Flame", 1)
    records.adjust_relic_count(a2, "The Last Flame", 2)

    totals = records.relic_totals()
    assert totals["The Last Flame"] == 3
    assert totals["The Desperate Alliance"] == 0

def test_backfills_relics_for_old_completed_runs_missing_the_field(tmp_path):
    data_path = tmp_path / "data.json"
    data_path.write_text(
        '{"records": {"floors": [null, null, null, null], "total": null}, '
        '"runs": [{"attempt": 1, "floor_times": [10.0, 12.0, 11.0, 13.0], "total_time": 46.0}]}',
        encoding="utf-8",
    )

    records = RecordsManager(data_path=data_path)

    run = records._find_run(1)
    assert "relics" in run
    assert all(count == 0 for count in run["relics"].values())
