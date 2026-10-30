# Performance engine v1 — research is not revenue

**Goal:** persist a zero-cost research queue and a strict money-evidence ledger. Improve the number of *validated* experiments and paid outcomes, not the count of assets or emails produced.

## What runs automatically

GitHub Actions executes `python engine/performance.py discover` daily at 06:19 UTC, uses public Hacker News search-by-date results, deduplicates links, scores keywords and writes a list of **research leads** to [RESEARCH.md](data/RESEARCH.md). These are NOT validated business opportunities; the workflow cannot claim market size, profitability or legality. Run manually from the Actions tab at any time.

No account credentials, Stripe connection, mass messaging, wallet, trading or spending are required. The workflow does not open accounts or sell anything. An upstream API failure is logged to the research output.

## Ledger — money is zero until recorded with evidence

```bash
python -m unittest discover -s engine/tests -v
python engine/performance.py report
python engine/performance.py record experiment_started --experiment pilot-a
python engine/performance.py record published --experiment pilot-a
python engine/performance.py record payment_confirmed --experiment pilot-a --amount-cents 5900 --evidence 'verified live Stripe payment' --reference 'pi_REAL_ID'
python engine/performance.py report
```

Never record hypothetical transactions. Evidence strings are manually supplied, **not independently verified**. Amounts are euro cents and confirmations are deduplicated by event type/reference. For privacy, do not commit personal data, customer names, secrets, receipts or private Stripe IDs to the **public** repository. The example ID above is illustrative only. In production, keep payment evidence in a private store, or record sanitized proof/reference hashes. The automated workflow does not write to the ledger.

## Validation protocol (human/agent)

For each lead, investigate: source and date, how money actually flows to participants, terms and eligibility, fees, demand evidence, customer acquisition, repeatability, competition, legal/reputational risk, costs, capacity to deliver, and an experiment with a stop rule. Reject leads without a legal value-creation mechanism, with prohibited deception, or requiring unaffordable capital.

Allocate a small capped effort to one candidate; define paid-conversion evidence **before** building. Record the stages: research_only → validated → experiment_started → published → observed users → confirmed payments. Reports must keep those states separate. Compare net revenue with time and out-of-pocket costs. After a fixed test, stop or revise unproductive channels rather than defending past work.

## Boundaries

Automated research is only a discovery input. HN is a narrow convenience source, not the whole internet, and keyword ranking is a crude heuristic. The next engineering increment should add at least two independent platform data sources, real merchant-fee validation, experiment prioritization and private verified Stripe reconciliation. The workflow becomes active only once this branch is merged into the default branch and GitHub Actions is enabled.
