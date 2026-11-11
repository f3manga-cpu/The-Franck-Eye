# NBA Picks Lab: evidence and model-design decisions
Updated for the 2026-11-10 US Eastern slate.

## Critical second-pass amendments (before tip-off)

See git history of data/picks.jsonl for original recommendations. Do not erase, backdate or silently change them.

- Tatum 8+ rebounds withdrawn: 2026-27 season averaging **6.0 rebounds**, 2/9 at 8+; earlier figure 7.8 was AST, not REB. Retained in records to measure and expose first-pass data-quality error. New research candidate: **Tatum 7+ assists**, season 7/9, average 7.8, sampled -130.
- Lillard 5+ assists downgraded: 4/9 over 4.5, close to 44.6% break-even of quoted +124. Hitting 4+ in several games is not evidence for 5+.
- Franz Wagner 24+ points withdrawn as a preferred candidate: 3/9 over 23.5 and 20.8 average; -117 has 53.9% break-even. New exploratory candidate: **Wagner 9+ assists**, 5/9 on season, 4/5 recent games, 8.8 average; +104 sample quote; Paolo Banchero and Jalen Suggs out.
- Carter Jr. 23+ PR retained research only: 5/9 over 22.5, needs 53.1% at -113; relatively slim historical margin. Most recent 3 games 34, 34, 40 minutes.
- Embiid 10+ rebounds retains high-variance role: 5/9 overall, 2/5 recent at 10+; +140 source was not user-book price.
- Klay Thompson 4+ made threes retained speculative: 5/10 last ten, 4/5 last five.
- Sabonis 13+ rebounds conditional on minutes/knee clearance.

All figures are historical and **NOT a calibrated next-game event probability**. Books and source lines differ. Do not bet automatically.

## Primary facts and reconciliation
- Schedule: https://www.nba.com/games?date=2026-11-10
- Official injuries: https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-11-10_06_30PM.pdf
- Tatum last ten and season: https://oddsloft.com/nba/players/jayson-tatum/props ; https://www.statmuse.com/nba/game/11-10-2026-bos-at-phi-78773
- Wagner assists/points history: https://slipsurgeon.com/stats/nba/franz-wagner/
- Lillard 4.5 assists market and quotes: https://snori.com/nba/players/2643-damian-lillard?game=432&market=player_assists
- Carter recent stats: https://www.cbssports.com/nba/players/2892260/wendell-carter-jr/game-log/2026/
- Embiid stats: https://statz.ai/nba/players/joel-embiid/rebounds
- Klay history: https://www.shoulditaketheover.com/nba/players/klay-thompson/threes/

## What to transfer from existing projects

**tredaman5/NBA-Player-Prop-Model**:
https://github.com/tredaman5/NBA-Player-Prop-Model
- Separate prediction of minutes from per-minute production.
- Rolling features are shifted by one game (avoid postgame leakage).
- Fail closed on missing slate, player/team identity mismatches or stale history.
- Require genuine, preregistered sportsbook-line backtest; project documents minimum 1,500 prospectively captured lines before a verdict. The posted ML improvements over last-5 baseline are modest, ~1% error improvement, not proof of profit.

**JoshXPart/nba-player-prop-model**:
https://github.com/JoshXPart/nba-player-prop-model
- Calibration after a lagged feature pipeline and walk-forward tests.
- Crucial anti-pattern: reported synthetic-line 67–72% win rates are inflated because lines are derived from same rolling features. Never advertise these as a real-market betting edge.

**tyrimedio/nba-predict-portfolio**:
https://github.com/tyrimedio/nba-predict-portfolio
- Benchmark against simple market and logistic baselines, not just random guessing. Strong predictive classification may still perform worse than betting-market favorites.

## Next model gate (not yet implemented)
Prospectively capture before-tip public NBA data, starters/injuries, odds snapshots (at least two sportsbooks when possible), and realized minutes; use one feature generator for training and live. Forecast minutes distribution, opportunities per minute and correlated player stats. Calibrate with chronological out-of-sample predictions and report Brier, log loss, no-vig consensus benchmarks and closing-line value. Show deployment state and all missing-data failures. For meaningful bet-edge claim require predeclared sample size, confidence bounds and bookmaker-matched outcomes.

Current implemented engine **does not generate new picks or retrain itself**; it grades entered picks and audits metrics daily. This distinction must remain visible.
