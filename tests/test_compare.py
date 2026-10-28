import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.compare import run_asset


def test_run_asset_toy_series():
    dates = pd.to_datetime(["2024-01-01", "2024-02-01", "2024-03-01", "2024-03-29"])
    series = pd.Series([100, 125, 200, 250], index=dates)
    r = run_asset(series, monthly=1000)
    years = 88 / 365
    assert r["months"] == 3
    assert r["invested"] == 3000
    assert r["years"] == pytest.approx(years)
    assert r["ls_final"] == pytest.approx(7500)
    assert r["sip_final"] == pytest.approx(5750)
    assert r["ls_cagr"] == pytest.approx((7500 / 3000) ** (1 / years) - 1)


def test_run_asset_real_data_matches_readme_numbers():
    def load(name):
        path = ROOT / "data" / "processed" / name
        return pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]

    nifty = run_asset(load("nifty50_close_clean.csv"))
    gold = run_asset(load("gold_close_clean.csv"))
    tol = 6e-5  # the notes hold 4 decimals, so allow for rounding
    assert nifty["ls_cagr"] == pytest.approx(0.0909, abs=tol)
    assert nifty["sip_xirr"] == pytest.approx(0.0962, abs=tol)
    assert gold["ls_cagr"] == pytest.approx(0.1227, abs=tol)
    assert gold["sip_xirr"] == pytest.approx(0.1385, abs=tol)