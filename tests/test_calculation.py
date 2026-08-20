from dilution_calculator import (
    calculate_water_needed,
    calculate_total_mix,
    calculate_final_strength,
    parse_number,
)
import pytest


def test_calculate_water_needed():
    result = calculate_water_needed(initial_strength=10, alcohol_volume=100, target_strength=2)
    assert result["water_to_add"] == 400.0
    assert result["final_volume"] == 500.0


def test_calculate_total_mix():
    result = calculate_total_mix(initial_strength=36, target_strength=3, final_volume=1000)
    assert result["alcohol_volume"] == 83.33
    assert result["water_to_add"] == 916.67


def test_calculate_final_strength():
    result = calculate_final_strength(initial_strength=5, alcohol_volume=20, water_volume=80)
    assert result["final_strength"] == 1.0
    assert result["total_volume"] == 100.0


def test_parse_number_accepts_decimal_comma():
    assert parse_number(" 12,50 ", "strength") == 12.5


def test_parse_number_rejects_non_finite_values():
    with pytest.raises(ValueError):
        parse_number("inf", "strength")
