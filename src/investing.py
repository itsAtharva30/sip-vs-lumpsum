def lump_sum(buy_price, final_price, amount):
    """Invest `amount` once at `buy_price`, value it at `final_price`.

    Assumes no fees; fractional units are allowed.
    Returns a dict with units, invested, final_value and gain.
    """
    if buy_price <= 0 or amount <= 0:
        raise ValueError("buy_price and amount must be positive")

    units = amount / buy_price
    invested = amount
    final_value = units * final_price
    gain = final_value - invested

    return {
        "units": units,
        "invested": invested,
        "final_value": final_value,
        "gain": gain,
    }