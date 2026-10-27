import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import monthly_buy_prices


def make_close():
    dates = pd.to_datetime(
        ["2024-01-01", "2024-01-02", "2024-01-15", "2024-02-01", "2024-02-02", "2024-03-04"]
    )
    return pd.Series([100, 101, 105, 110, 111, 120], index=dates)


def test_monthly_buy_prices_default_picks_first_trading_day():
    result = monthly_buy_prices(make_close())
    assert len(result) == 3
    assert list(result["price"]) == [100, 110, 120]
    assert pd.Timestamp(result["buy_date"].iloc[0]) == pd.Timestamp("2024-01-01")
    assert pd.Timestamp(result["buy_date"].iloc[2]) == pd.Timestamp("2024-03-04")


def test_monthly_buy_prices_sip_day_two():
    result = monthly_buy_prices(make_close(), sip_day=2)
    assert list(result["price"]) == [101, 111, 120]


def test_monthly_buy_prices_skips_months_with_no_trading_day_after_sip_day():
    result = monthly_buy_prices(make_close(), sip_day=10)
    assert len(result) == 1
    assert list(result["price"]) == [105]
    assert pd.Timestamp(result["buy_date"].iloc[0]) == pd.Timestamp("2024-01-15")