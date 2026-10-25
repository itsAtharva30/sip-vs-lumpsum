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
    
def sip(buy_prices, final_price, monthly_amount):
    """Invest `monthly_amount` at each price in `buy_prices`, value at `final_price`.

    Assumes no fees; fractional units are allowed.
    Returns a dict with units, invested, final_value and gain.
    """
    if len(buy_prices) == 0 or monthly_amount <= 0:
        raise ValueError("need at least one price and a positive monthly_amount")

    total_units = 0
    for price in buy_prices:
        if price <= 0:
            raise ValueError("all buy prices must be positive")
        total_units += monthly_amount / price        # units bought this month

    invested = monthly_amount * len(buy_prices)                # monthly_amount times how many months?
    final_value = total_units * final_price             # total_units times what?
    gain = final_value - invested                    # final_value minus what?

    return {
        "units": total_units,
        "invested": invested,
        "final_value": final_value,
        "gain": gain,
    }
def fd(amount, annual_rate, years):
    """Fixed deposit: `amount` grows at `annual_rate` (decimal, 0.079 = 7.9%) for `years`.

    Assumes yearly compounding, no tax, no fees; `years` may be fractional.
    Returns a dict with invested, final_value and gain.
    """
    if amount <= 0:
        raise ValueError("amount must be positive")
    if years < 0:
        raise ValueError("years cannot be negative")
    if annual_rate <= -1:
        raise ValueError("annual_rate must be greater than -1 (use 0.079 for 7.9%)")

    invested = amount
    final_value = amount * (1 + annual_rate) ** years
    gain = final_value - invested

    return {
        "invested": invested,
        "final_value": final_value,
        "gain": gain,
    }