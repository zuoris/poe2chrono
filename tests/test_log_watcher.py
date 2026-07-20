import pytest

from zarokh.log_watcher import match_trigger


def test_matches_start_trigger():
    line = 'some log prefix area "Sanctum_1_Foyer" more text'
    assert match_trigger(line) == "START"


def test_matches_floor_2_trigger():
    line = 'area "Sanctum_2_Foyer" some text'
    assert match_trigger(line) == "FLOOR_2"


@pytest.mark.parametrize("end_message", [
    "Zarokh, the Temporal: The sands shift, Taljari...",
    "Zarokh, the Temporal: This cannot be... it is not my time...",
    "Zarokh, the Temporal: My sand... runs out...",
    "Zarokh, the Temporal: Ugh... who are you to overthrow your fate?",
    "Zarokh, the Temporal: Ugh, this is not the future I had forseen!",
])
def test_matches_any_end_variant(end_message):
    line = f"2026/07/14 20:00:00 {end_message}"
    assert match_trigger(line) == "END"


def test_returns_none_when_no_trigger_matches():
    line = 'some unrelated log line'
    assert match_trigger(line) is None


def test_returns_first_match_when_line_could_match_multiple():
    line = 'area "Sanctum_1_Foyer" and area "Sanctum_2_Foyer"'
    assert match_trigger(line) == "START"
