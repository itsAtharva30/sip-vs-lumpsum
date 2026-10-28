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

## Stage 4: Metrics (src/metrics.py)

**What I built**
- `cagr(start_value, end_value, years)`: `(end / start) ** (1 / years) - 1`, as a decimal.
- `max_drawdown(prices)`: running peak with `cummax()`, drawdown is `price / peak - 1`, result is the most negative value.
- `xirr(cash_flows)`: yearly return for dated cash flows, found by bisection because there is no direct formula.
- `sip` now optionally takes `buy_dates` and `final_date` and returns `cash_flows`, a list of (date, amount) pairs. Old calls still work.

**What I learned**
- CAGR assumes one lump sum at the start. A SIP puts money in over time, so CAGR on it is misleading; XIRR uses each payment's date.
- Drawdown is measured from the highest value so far, not from the start. A price can end where it began and still show a large drawdown (100, 120, 90, 110, 70, 100 gives -41.67%).
- A drawdown is never positive. 0.0 means the price never fell below an earlier high.
- XIRR needs money in negative and money out positive. With one sign only there is no solution, so the function raises a ValueError.
- XIRR solves for the rate by trying a low and a high guess and halving the gap until the net value is near zero.
- Float results carry noise (0.0700000000000006); that is normal and not a bug.

**Mistakes and fixes**
- Skipped some paper steps and asked for the final code; I read the last lines of `max_drawdown` afterwards so I understand how they map to the paper work.
- Wrote "drawdown <= 0 returns 0"; the function returns the worst drawdown, and 0.0 only for a series that never falls below a peak.

**Known limits (for the README)**
- XIRR uses days / 365 and bisection between -99% and 10000%.
- Max drawdown of a SIP's value is softened because new money keeps being added; I'll note that when comparing.
- A short SIP period gives a huge XIRR (3 months, 12% gain, about 99% a year). Annualized numbers over short spans are not meaningful.

## Stage 5: comparison and charts

**Mistakes and surprises**
- A notebook runs from `notebooks/`, so the path `data/processed/...` failed with FileNotFoundError. The fix was `../data/processed/...`. Relative paths depend on where the code runs from, not where the file lives.
- A cell failed with `NameError: fd is not defined`. I had imported `lump_sum` and `sip` but not `fd`. Python only knows names that have been imported.
- Restarting the notebook kernel wiped every variable, so cells had to reload their data and imports. Results I need later should be written down or saved, not left only in memory.
- Gold had one row (2026-01-15) whose close was identical to the previous day's. It is possibly stale, but it is not a SIP buy date, so it does not affect results.

**What changed my mind**
- Lump sum ended with far more rupees than SIP, but that was mostly because its money was invested for the whole 16.8 years. Compared by yearly return, the SIP was slightly ahead (Nifty 9.6% vs 9.1%, gold 13.9% vs 12.3%). Final value alone is not a fair comparison.
- Gold looked clearly better than Nifty, but the chart showed its lead comes mostly from the last two years. Nifty was ahead for much of 2016 to 2024. The ranking depends on the window.
- Max drawdown and depth are different risks. Nifty's worst fall was deeper (-38%, March 2020), but gold's falls were longer (below its peak for most of 2013 to 2019).

**Checks that confirmed things**
- A toy example by hand (prices 100, 80, 120, final 130) matched the code exactly before I trusted it on real data.
- Lump sum CAGR and XIRR gave the same 9.0933%, so the two metrics agree with each other. FD gave exactly 7.9% in both forms, as it should for a fixed rate.
- Only 7 of 202 monthly buy dates differed between the Nifty and gold files (all Januaries, 1 to 3 days apart), so the missing Nifty days are a README known limit, not a fix.
- Lowering the final gold price by 10% and 20% still left gold ahead of Nifty and FD, so the gold result does not depend on the unverified 2026 prices being exact.

@'

## Stage 6: tests and refactor

**Mistakes and surprises**
- I guessed `fd` returned a single number. It returns a dictionary with invested, final_value and gain, so my first test failed. The code was right and the test was wrong; reading the code or running it first would have shown this.
- I worked out the leap-year XIRR by hand and got about 9.99%. The real value is 0.0997136 (about 9.97%). That was my arithmetic slip, not a bug. XIRR counts actual days divided by 365, so a 366-day gap is slightly more than one year.
- Re-running the notebook gave Nifty 9.13% instead of 9.09%. The `yf.download` calls had no end date, so Run All downloaded new data and overwrote the CSVs and charts. The function swap was not the cause.
- Pasting partial edits into a test file kept leaving it out of date. Replacing the whole file in one go was safer.

**What changed my mind**
- Tests are not only for finding bugs. 27 tests found none, but writing them made me read every function's return shape, error guard and assumption, which is why they are worth having.
- A notebook that downloads data is not reproducible unless the end date is fixed. Pinning `end="2026-10-24"` made a fresh Run All match my notes exactly (9.09, 9.62, 12.27, 13.85, 7.9).

**Checks that confirmed things**
- 27 tests pass across `fd`, `lump_sum`, `sip`, `cagr`, `max_drawdown`, `xirr` and `monthly_buy_prices`, including every `ValueError` guard and a pandas Series input.
- The XIRR multi-flow test checks that the returned rate makes the discounted cash flows sum to zero, so it does not depend on a number I computed.
- The notebook now imports `monthly_buy_prices` from `src/data.py` instead of keeping its own copy, and its output matched the old copy.
- `git restore data charts` put back the 23 Oct data after the accidental re-download, so the repo still matches the README notes.
'@ | Add-Content LEARNINGS.md- `run_asset` was defined twice in the notebook, once returning everything and once returning two values. Moving it to `src/compare.py` left one copy, and a test on the real data now checks the README numbers (9.09, 9.62, 12.27, 13.85), so a code change that moves them will fail.
