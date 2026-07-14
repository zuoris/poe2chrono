from zarokh.log_watcher import match_trigger


def test_matches_start_trigger():
    line = 'some log prefix area "Sanctum_1_Foyer" more text'
    assert match_trigger(line) == "START"


def test_matches_floor_2_trigger():
    line = 'area "Sanctum_2_Foyer" some text'
    assert match_trigger(line) == "FLOOR_2"


def test_matches_end_trigger():
    line = 'Zarokh, the Temporal: Ugh... you have freed me'
    assert match_trigger(line) == "END"


def test_returns_none_when_no_trigger_matches():
    line = 'some unrelated log line'
    assert match_trigger(line) is None


def test_returns_first_match_when_line_could_match_multiple():
    # Extremely unlikely in real logs, but verifies deterministic behavior
    line = 'area "Sanctum_1_Foyer" and area "Sanctum_2_Foyer"'
    assert match_trigger(line) == "START"