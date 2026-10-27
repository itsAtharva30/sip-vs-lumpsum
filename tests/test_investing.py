import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.investing import fd, lump_sum, sip


def test_fd_two_years_at_8_percent():
    result = fd(1000, 0.08, 2)
    assert result["invested"] == 1000
    assert result["final_value"] == pytest.approx(1166.40)
    assert result["gain"] == pytest.approx(166.40)


def test_lump_sum_price_rises_by_half():
    result = lump_sum(100, 150, 10000)
    assert result["units"] == pytest.approx(100)
    assert result["invested"] == 10000
    assert result["final_value"] == pytest.approx(15000)
    assert result["gain"] == pytest.approx(5000)


def test_sip_three_months_rising_prices():
    result = sip([100, 125, 200], 250, 1000)
    assert result["units"] == pytest.approx(23)
    assert result["invested"] == 3000
    assert result["final_value"] == pytest.approx(5750)
    assert result["gain"] == pytest.approx(2750)


def test_sip_cash_flows_with_dates():
    dates = [date(2024, 1, 1), date(2024, 2, 1), date(2024, 3, 1)]
    result = sip([100, 125, 200], 250, 1000, buy_dates=dates, final_date=date(2024, 4, 1))
    flows = result["cash_flows"]
    assert len(flows) == 4
    assert flows[0] == (date(2024, 1, 1), -1000)
    assert flows[2] == (date(2024, 3, 1), -1000)
    assert flows[3][0] == date(2024, 4, 1)
    assert flows[3][1] == pytest.approx(5750)


def test_sip_rejects_non_positive_price():
    with pytest.raises(ValueError):
        sip([100, 0, 200], 250, 1000)


def test_sip_rejects_missing_final_date():
    dates = [date(2024, 1, 1), date(2024, 2, 1), date(2024, 3, 1)]
    with pytest.raises(ValueError):
        sip([100, 125, 200], 250, 1000, buy_dates=dates)


def test_sip_rejects_date_count_mismatch():
    dates = [date(2024, 1, 1), date(2024, 2, 1)]
    with pytest.raises(ValueError):
        sip([100, 125, 200], 250, 1000, buy_dates=dates, final_date=date(2024, 4, 1))


def test_sip_rejects_final_date_before_last_buy():
    dates = [date(2024, 1, 1), date(2024, 2, 1), date(2024, 3, 1)]
    with pytest.raises(ValueError):
        sip([100, 125, 200], 250, 1000, buy_dates=dates, final_date=date(2024, 2, 15))