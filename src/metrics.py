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

def xirr(cash_flows, tol=1e-10, max_iter=200):
    """Annual return for dated cash flows, as a decimal (0.10 means 10% a year).

    `cash_flows` is a list of (date, amount) pairs: money paid in is negative,
    money received is positive. Needs at least one of each.
    Uses days / 365 as the time unit and finds the rate by bisection.
    """
    if len(cash_flows) < 2:
        raise ValueError("need at least two cash flows")
    amounts = [amount for _, amount in cash_flows]
    if not (any(a < 0 for a in amounts) and any(a > 0 for a in amounts)):
        raise ValueError("need at least one negative and one positive cash flow")

    start = min(d for d, _ in cash_flows)
    years = [(d - start).days / 365 for d, _ in cash_flows]

    def npv(rate):
        return sum(a / (1 + rate) ** t for a, t in zip(amounts, years))

    low, high = -0.99, 100.0
    f_low, f_high = npv(low), npv(high)
    if f_low * f_high > 0:
        raise ValueError("could not find a rate between -99% and 10000%")

    for _ in range(max_iter):
        mid = (low + high) / 2
        f_mid = npv(mid)
        if abs(f_mid) < tol:
            return mid
        if f_mid * f_low > 0:
            low, f_low = mid, f_mid
        else:
            high = mid
    return (low + high) / 2