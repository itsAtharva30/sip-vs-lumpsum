import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.metrics import cagr, max_drawdown, xirr


def test_cagr_two_years_ten_percent():
    assert cagr(100, 121, 2) == pytest.approx(0.10)


def test_cagr_doubling_in_one_year():
    assert cagr(100, 200, 1) == pytest.approx(1.0)


def test_cagr_no_change_is_zero():
    assert cagr(100, 100, 5) == pytest.approx(0.0)


def test_cagr_rejects_zero_start_value():
    with pytest.raises(ValueError):
        cagr(0, 100, 2)


def test_cagr_rejects_zero_years():
    with pytest.raises(ValueError):
        cagr(100, 121, 0)


def test_cagr_rejects_negative_end_value():
    with pytest.raises(ValueError):
        cagr(100, -5, 2)


def test_max_drawdown_deepest_fall_from_running_peak():
    assert max_drawdown([100, 120, 90, 110, 60, 80]) == pytest.approx(-0.5)


def test_max_drawdown_always_rising_is_zero():
    assert max_drawdown([100, 110, 120, 130]) == pytest.approx(0.0)


def test_max_drawdown_simple_halving():
    assert max_drawdown([100, 50]) == pytest.approx(-0.5)


def test_max_drawdown_biggest_fall_is_not_from_highest_peak():
    assert max_drawdown([100, 80, 200, 190]) == pytest.approx(-0.2)


def test_max_drawdown_accepts_pandas_series():
    assert max_drawdown(pd.Series([100, 120, 90, 110, 60, 80])) == pytest.approx(-0.5)


def test_xirr_365_day_year_is_ten_percent():
    flows = [(date(2025, 1, 1), -1000), (date(2026, 1, 1), 1100)]
    assert xirr(flows) == pytest.approx(0.10, abs=1e-8)


def test_xirr_leap_year_uses_365_day_count():
    flows = [(date(2024, 1, 1), -1000), (date(2025, 1, 1), 1100)]
    expected = 1.1 ** (365 / 366) - 1
    assert xirr(flows) == pytest.approx(expected, abs=1e-8)


def test_xirr_multiple_flows_make_npv_zero():
    flows = [
        (date(2024, 1, 1), -1000),
        (date(2024, 7, 1), -1000),
        (date(2025, 1, 1), 2200),
    ]
    rate = xirr(flows)
    start = flows[0][0]
    npv = sum(a / (1 + rate) ** ((d - start).days / 365) for d, a in flows)
    assert npv == pytest.approx(0.0, abs=1e-4)

def test_xirr_rejects_all_negative_flows():
    flows = [(date(2024, 1, 1), -1000), (date(2025, 1, 1), -500)]
    with pytest.raises(ValueError):
        xirr(flows)


def test_xirr_rejects_all_positive_flows():
    flows = [(date(2024, 1, 1), 1000), (date(2025, 1, 1), 500)]
    with pytest.raises(ValueError):
        xirr(flows)