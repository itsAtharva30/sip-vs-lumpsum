import pandas as pd


def cagr(start_value, end_value, years):
    """Compound annual growth rate as a decimal (0.12 means 12% a year).

    Needs positive start_value, end_value and years.
    """
    if start_value <= 0 or end_value <= 0 or years <= 0:
        raise ValueError("start_value, end_value and years must be positive")

    return (end_value / start_value) ** (1 / years) - 1


def max_drawdown(prices):
    """Largest fall from a running peak to a later low, as a negative decimal.

    `prices` is a list or pandas Series in time order; -0.4167 means a 41.67% fall.
    Returns 0.0 if the series never falls below an earlier peak.
    """
    prices = pd.Series(prices, dtype=float)
    if prices.empty:
        raise ValueError("prices must not be empty")
    if (prices <= 0).any():
        raise ValueError("all prices must be positive")

    running_peak = prices.cummax()
    drawdowns = prices / running_peak - 1

    return drawdowns.min()