# 2026-11-01 — Commercial acquisition experiment: free CSV preflight → €59 audit

## Verified baseline

- GitHub Actions `Opportunity research` **ran successfully** on 2026-10-31 12:33 UTC: https://github.com/f3manga-cpu/The-Franck-Eye/actions/runs/41201640270. The bot committed `engine/data/RESEARCH.md` and `opportunities.json` at https://github.com/f3manga-cpu/The-Franck-Eye/commit/4fc3e1be7821c1fdfb0a84b428fd58ddd73b5c00. Only one completed run was visible when checked on 2026-11-01; the next daily scheduled execution was not yet confirmed. No code failure identified.
- The research queue is **not evidence of demand**: HN keywords surfaced irrelevant IKEA news and a broad creator platform. The agent therefore checked independent, official seller sources rather than treating ranked leads as viable offers.
- Connected Stripe Ømint **livemode**: exactly five succeeded PaymentIntents returned, all created before 2026-10-30. **No new succeeded payment** attributable to AUDIT-MKT-01, INSIGHTS-01, KPI-DASH-01 or the agency-reporting experiment. No payment events added to the ledger. Do not report historic physical-product revenue as new sales.
- Gmail search on 2026-11-01 for replies from the four 2026-10-30 outreach recipients and the two 2026-10-31 agency prospects returned **no matching incoming email**. Do not send a Sunday follow-up.

## Three routes compared (official seller terms; not demand proof)

| Route | Money mechanism | Fees/eligibility and settlement | Fit now | Decision |
|---|---|---|---|---|
| **Fab (Epic)** — game audio packs | Sell downloadable game assets to marketplace buyers | Creator share **88%**; publisher onboarding and third-party payout setup; payment roughly 30 days after month-end when accrued amount is at least **US$100**; below threshold rolls over | Existing audio pack may fit, but no listing or publisher onboarding confirmed; payout threshold delays first cash | **Research / hold**. No new account opened. |
| **Unity Asset Store** — game audio packs | Sell reviewed assets | Free to publish; creator retains **70%**; **US$4.99** minimum asset price; publisher registration, package preparation in Unity Editor, editorial review and tax/payout setup required | High setup and review latency, no confirmed sales; less suitable for immediate cash | **Hold** |
| **Direct B2B analytics** — low-friction self-check → paid audit | Free local CSV checker lets prospective client inspect export, then optional **€59** fixed-scope audit paid via already-live Stripe checkout | No platform listing fees or paid traffic; standard Stripe processing applies; no need to transfer CSV to server; buyers still must be reached | Existing service, expertise and checkout; faster possible conversion but currently zero qualified inbound | **Test a new conversion step, not more generic cold emails** |

Official sources (checked 2026-11-01):
- Fab publisher: https://www.fab.com/o/become-a-publisher ; payouts https://dev.epicgames.com/documentation/fab/publisher-get-started-in-fab
- Unity publishing: https://assetstore.unity.com/publishing/publish-and-sell-assets ; agreement https://unity.com/legal/provider
- itch.io payment economics for existing seller: https://itch.io/docs/creators/payments

Comparable products on Fab show that retro SFX packs are an existing product category, **not** that this pack will sell: https://www.fab.com/listings/27a17016-2127-4858-839a-967939772a86

## Executed in GitHub on 2026-11-01

Created public, **no-data-upload** HTML preflight: https://github.com/f3manga-cpu/The-Franck-Eye/blob/main/tools/marketing-csv-preflight.html

- Self-contained HTML/JS, no dependencies, external scripts or telemetry; users download/open the file locally.
- Checks header/row consistency, missing values, duplicate rows, unnamed columns and missing obvious period/date column. CSV parser handles quoted commas, embedded line breaks and escaped quotes; JS syntax and sample parsing tested in the tool runtime.
- Provides copyable findings and a clearly labelled upsell to the existing €59 Stripe checkout, with a pre-order email for unusual briefs.
- Linked from both repository README and existing white-label reporting offer. The tool is **publicly downloadable, not a hosted website**, and has no known traffic or conversions yet.
- No private customer data, keys or buyer lists committed. No payment, spend, platform signup or outreach executed.

## Measurement and decision rule

Hypothesis: a useful free privacy-respecting preflight reduces perceived risk and can create qualified conversations about paid analytics.

Primary success: a **new succeeded live Stripe payment** attributable to the €59 audit, net of fees/refunds; no payment yet. Secondary: prospect uses tool, emails qualified brief, or explicitly requests an audit. **No tracking means tool downloads and usage are unknown**; do not fabricate them.

Next acquisition action: share the tool only with a genuinely relevant consenting/warm prospect or in an appropriate community with disclosure and compliance with posting rules. No indiscriminate posting or automated relances. Evaluate after 5 working days or when qualified feedback arrives. If no distribution or intent signal, pivot to an actual buyer-intent channel instead of producing more tools.

Current state: public asset created, conversion link connected, **0 € new verified revenue**.
