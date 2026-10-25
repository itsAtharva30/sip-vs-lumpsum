def cagr(start_value, end_value, years):
    """Compound annual growth rate as a decimal (0.12 means 12% a year).

    Needs positive start_value, end_value and years.
    """
    if start_value <= 0 or end_value <= 0 or years <= 0:
        raise ValueError("start_value, end_value and years must be positive")

    return (end_value / start_value) ** (1 / years) - 1