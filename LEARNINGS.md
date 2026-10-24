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
