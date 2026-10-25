## Stage 0:
A virtual environment keeps each project's libraries separate, and requirements.txt plus .gitignore let anyone rebuild it without committing .venv.

## Stage 1: Finance by hand

**SIP vs lump sum depends on the price path, not on the method alone.**
- Price dips then recovers (100, 80, 120): SIP gained 3,500, lump sum gained 3,000. SIP won because it bought more units at the dip.
- Price rises steadily (100, 110, 120, 130): lump sum gained 6,000, SIP gained 2,826. Lump sum won because all the money was invested at the lowest price.
- Price falls steadily (100, 90, 80): SIP lost 1,556, lump sum lost 3,000. SIP lost less because its average cost per unit came down (about 89 vs 100), but it was still a loss.

**Conclusion:** neither method is better in general. SIP helps when prices dip or fall by averaging the cost down. Lump sum helps when prices keep rising because it is fully invested from day one. The real Nifty 50 data in Stage 2 will show which path actually happened.

**Metrics**
- CAGR = (final / start)^(1/years) - 1. It assumes one lump of money invested at one time, so it hides when cash actually went in.
- XIRR = the single yearly rate that fits a list of dated cash flows (money in, money out). It weights each payment by how long it stayed invested, so it is the right metric for a SIP.
  - Example: A puts 15,000 in on day 1 and B puts 5,000 in at the start of each of 3 years. Both end with 18,000 after 3 years.
  - CAGR would give both about 6.27%. XIRR gives A about 6.3% and B about 9.4%, because B earned the same 3,000 on money that was invested for less time.
  - Use CAGR for a lump sum. Use XIRR for a SIP or any money that goes in at different times.
- Max drawdown = the worst fall from the highest peak so far. A 25% fall needs a 33.3% gain to recover, because the gain is measured on a smaller base.
- CAGR alone doesn't show the whole picture: it ignores the timing of cash flows and the falls along the way. 

**Habits to keep**
- Check any result backwards: grow the CAGR to see if it gives back the final value, and check that more units at the same final price means a higher value.
- Keep full decimals while calculating and round only at the end.

## Stage 2: Data

- **Source:** Nifty 50 index (`^NSEI`) from yfinance, 4,128 daily rows from 2010-01-04 to 2026-10-23. Raw `Close` is saved in `data/raw/` so results can be reproduced.
- **Price choice:** use `Close`, not High or Low. Those are single moments in the day that nobody can reliably buy at.
- **Check data before using it:** sorted, no duplicate dates, no prices at or below zero. Gaps of a few days are weekends or holidays.
- **Extreme days are not errors by default.** The biggest falls and rises were all in March and April 2020 (the COVID crash, -12.98% on 2020-03-23). Real events stay in the data, because removing them would make every result look better than it was. A suspicious day is one that is isolated, reverses the next day, or disagrees with a second source.
- **Buy rule:** for each month, buy at the Close on the first trading day on or after `sip_day`. "On or after" is needed because markets close on weekends and holidays, so the exact date may have no row. This gave 202 months, and `sip_day` is a setting, not a fixed number.
- **Limits:** the data ends on 23 October, so the last month is partial. With a late `sip_day` that month can be skipped. Results should state the end date.
- **Habits:** check the dtype of the index after loading a CSV (`parse_dates`), and don't leave `...` placeholders in code.

## Stage 3: Core functions (src/investing.py)

**What I built**
- `lump_sum(buy_price, final_price, amount)`: one purchase, valued at the final price.
- `sip(buy_prices, final_price, monthly_amount)`: the same amount bought at each monthly price, valued at the final price.
- `fd(amount, annual_rate, years)`: fixed deposit with yearly compounding, `amount * (1 + annual_rate) ** years`.
- Each returns a dict (`units`, `invested`, `final_value`, `gain`; `fd` has no units). A dict is easy to read by name and can gain more fields later, such as the cash flows XIRR will need.

**What I learned**
- `invested` is the money I put in, so it is an input (`amount`, or `monthly_amount * len(buy_prices)`). Price varies, money doesn't; price only changes how many units I get. Computing it as `price * units` undoes an earlier division and adds floating-point noise.
- A SIP is a running total: each month adds `monthly_amount / price` units. Low-price months buy more units, which is the whole mechanism.
- Bad input should fail loudly. Each function raises a `ValueError` with a clear message instead of giving a division error or nonsense numbers.
- Rates are decimals: 0.079 means 7.9%. Passing 7.9 means 790% and gives no error, only an absurd result, so check outputs against a rough number in my head.
- Every function was checked against a hand calculation first: gains of 6,000 and -3,000 for lump sum, 355 and 3,500 for SIP, 12,250 for FD.

**Mistakes and fixes**
- Wrote `total_units += monthly_amount / buy_prices in lump_sum`. The loop variable is `price`, and nothing from `lump_sum` belongs inside `sip`. Fixed to `monthly_amount / price`.
- Used the wrong variable name (`final_amount` instead of `final_value`), which would have been a `NameError`.
- Left `...` placeholders in the code, so the function returned `Ellipsis` and, before that, `None` (no `return`).

**Known limits (for the README)**
- No fees, taxes or inflation; fractional units are allowed.
- FD rate is a single fixed rate and compounds yearly. Real Indian FDs usually compound quarterly, and rates changed a lot between 2010 and 2026.
- `sip` returns totals only, with no dates or individual payments, so it cannot feed XIRR yet. In Stage 4 it needs to produce a dated cash-flow list.
