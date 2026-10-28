import pandas as pd

from src.data import monthly_buy_prices
from src.investing import lump_sum, sip
from src.metrics import cagr, xirr


def run_asset(series, monthly=5000):
    """Lump sum vs monthly SIP on one price series (a Series with a DatetimeIndex).

    The SIP buys once a month on the first trading day (see monthly_buy_prices).
    The lump sum puts the same total in at the first buy price.
    Both are valued at the last price in the series.
    """
    m = monthly_buy_prices(series)
    prices = m["price"].tolist()
    dates = pd.to_datetime(m["buy_date"]).tolist()
    final_price = series.iloc[-1]
    final_date = series.index[-1]
    total = monthly * len(prices)
    years = (final_date - dates[0]).days / 365

    ls = lump_sum(buy_price=prices[0], final_price=final_price, amount=total)
    sp = sip(buy_prices=prices, final_price=final_price, monthly_amount=monthly,
             buy_dates=dates, final_date=final_date)

    return {
        "months": len(prices),
        "years": years,
        "invested": total,
        "ls_final": ls["final_value"],
        "ls_cagr": cagr(total, ls["final_value"], years),
        "sip_final": sp["final_value"],
        "sip_xirr": xirr(sp["cash_flows"]),
    }