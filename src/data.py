import pandas as pd


def monthly_buy_prices(close, sip_day=1):
    """One SIP buy per calendar month: the first trading day on or after `sip_day`.

    `close` is a pandas Series of closing prices with a sorted DatetimeIndex.
    Returns a DataFrame indexed by month (Period) with columns buy_date and price.
    Months with no trading day on or after `sip_day` are skipped (possible for a
    high sip_day or a partial last month).
    """
    if not 1 <= sip_day <= 31:
        raise ValueError("sip_day must be between 1 and 31")
    if not isinstance(close.index, pd.DatetimeIndex):
        raise ValueError("close needs a date index (use parse_dates=True when reading the CSV)")
    if close.empty:
        raise ValueError("close must not be empty")
    if not close.index.is_monotonic_increasing:
        raise ValueError("close must be sorted by date, oldest first")

    months = close.index.to_period("M")
    rows = []
    for period in months.unique():
        month = close[months == period]
        eligible = month[month.index.day >= sip_day]
        if len(eligible) == 0:
            continue
        rows.append({"month": period,
                     "buy_date": eligible.index[0],
                     "price": eligible.iloc[0]})

    if not rows:
        raise ValueError("no buy dates found for this sip_day")
    return pd.DataFrame(rows).set_index("month")