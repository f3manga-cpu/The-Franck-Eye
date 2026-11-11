# NBA Picks Lab — v0.1

**Status:** Versioned NBA pick ledger and unit-tested score-grading code. Not a validated predictive model or profitable betting strategy. No automated wagering or spending.

## Data contract

- `nba_lab/data/picks.jsonl` has one recommendation per line. Source odds are snapshots, not verified Winamax quotes.
- `kind` distinguishes assistant research from an actual bet. `stake_eur` remains null without independent evidence of placement and settlement.
- `grade_status` values: pending, hit, miss, manual_review, reported_hit, reported_miss. Historical reports are not independently verified.
- Markets: PTS, REB, AST, 3PM, PR (points+rebounds), PRA. Thresholds are inclusive: 23 means 23+.
- Absent players in final box scores receive manual_review, not invented wins, losses, or voids.

## Operating method

1. Before tip, verify official NBA injury report, expected starters, forecast minutes and actual market price. Exclude ruled-out players, even if an external model recommends them.
2. Freeze line, price, source, and date before results. Track every proposal, misses, passes and version changes; never select retroactive winners.
3. After games finalize, run the standard-library ESPN box-score grader. The GitHub Actions workflow targets **yesterday in U.S. Eastern time**, and commits updated JSONL only if actual results changed. It grades only picks previously entered; it does not automatically learn about new ChatGPT suggestions.
4. Manually review DNP/identity/ESPN schema errors, and distinguish paper outcomes from actual bet receipts.
5. Evaluate calibration, Brier score, log loss, CLV, paper ROI (not bank profit), and results by market, season and roster/injury class.

## Quantitative roadmap — NOT implemented or validated yet

- Train with walk-forward, pre-tip feature snapshots. All rolling features must be shifted to prevent future-data leakage.
- First forecast a **distribution of player minutes** conditioned on rotations, injury news, foul risk, fatigue, blowout chance and team context.
- Predict opportunities: 3-point attempts and efficiency; potential assists and teammate conversion; rebound chances and conversion; field-goal/FTA volume and efficiency.
- Simulate correlated statistics and same-game legs; do not multiply independent leg probabilities.
- Calibrate the probability of crossing **each specific line**, and compare to no-vig consensus and observed odds at the decision time.
- Distinguish exploratory picks from statistically verified edges. Do not calculate wager size or deploy bankroll/essential funds without independently validated out-of-sample evidence.

Inspiration: [tredaman5/NBA-Player-Prop-Model](https://github.com/tredaman5/NBA-Player-Prop-Model) uses shifted rolling features and predicted minutes; its README explicitly warns that an outcome projection is not a demonstrated market edge.

## Commands

```sh
python -m unittest discover -s nba_lab/tests -v
python nba_lab/grade.py --date 2026-11-10 --dry-run
python nba_lab/grade.py --date 2026-11-10
```

Python 3.11+. Grader relies on the public ESPN site API, which can fail or change schema. Verify scores/settlements against official statistics. A committed workflow is **not proof of successful scheduled execution**: monitor actual Actions runs.
