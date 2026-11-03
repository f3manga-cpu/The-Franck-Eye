# Revenue Harness — operating contract (v2)

## Objective
Produce **verified new net cash from independently sourced internet demand**. Distribution is mandatory: an item that has not reached a relevant buyer is a prototype, not a commercial experiment. Prefer an existing buying channel or demonstrated conversion path over building a new storefront. No unpaid speculative development by inertia.

## Execution environments and truthful boundary
- **ChatGPT Automations (controller):** an active daily agentic run, with connected Gmail, GitHub, web and Stripe tools when those are actually available. It is the only current component authorized to access those connected accounts. Its steps are NOT magically separate independent model agents.
- **GitHub Actions (read-only research and metrics):** scheduled Python workloads; it cannot use the authenticated ChatGPT Gmail or Stripe connectors. Never assume the ChatGPT plan gives an OpenAI API key to GitHub Actions.
- **Codex/Agents SDK (optional specialist runtime):** requires a separately provisioned OpenAI API key, budget, permission scope, and approvals. Disabled by default. No model/API spending to be silently activated.

## Specialist responsibilities — independently challenge assumptions
1. **Scout (discovery):** survey at least three genuinely distinct demand mechanisms (buyer-posted work, application/plugin-store demand, organic commercial search, B2B purchase-intent signals, marketplace categories). Produce 3 evidence records; challenge novelty bias and earlier projects.
2. **Underwriter (independent veto):** for each demand record, inspect the buyer, whether money actually changes hands, fees and payout timing, competition, compliance, time-to-deliver, and cost of acquiring one buyer. Reject unverifiable revenue claims and unsupported opportunity-size arguments. No misleading claims.
3. **Builder (Codex / GitHub):** implement ONLY the smallest deliverable to test a validated offer; require verifiable tests and an accessible offer/checkout route. No full application until proof of demand.
4. **Distributor (actual channel operation):** publish where buyers are already looking; confirm live listing, working user journey, and external visibility. If using email, contact relevant legitimate B2B prospects with personalization and stop rules; no bulk spam. Record only messages SENT, not inbox delivery or sales.
5. **Cash controller:** query **live Stripe** for the exact payment link/product created for an experiment, then reconcile charge success, refunds, fees, cash available and payouts without counting historic unrelated physical orders. Never treat a link, session, open checkout or sent email as revenue. Do not publish private IDs or customer details.
6. **Skeptic / auditor:** independently test the commercial claim before reporting; stop after fixed evidence windows; compare new actual net receipts against effort and costs, not activity volume. Repeat/scale only if actual conversion evidence supports it.

## Shared state and approval
State machine:
\`research_only -> evidence_checked -> selected -> built -> distributed -> purchase_verified -> fulfilled -> scale\`
Reject/close from any stage. The **buyer and distribution path must be identified before the build step**, and source evidence must be dated. A Stripe checkout that exists but is not distributed is \`built\`, not \`distributed\`.
- Money events require primary-source verification, unique reference and a recorded conversion attribution. The public GitHub ledger is NOT itself a primary source of revenue; it stores sanitized aggregates only.
- Individual contact details, bank data, payment IDs, private customer files and secrets stay out of public GitHub.
- Purchases, spend, account changes, external mass communications, production deployments, refunds, and contractual commitments use their own authorization/guardrails.
- 0 EUR additional infrastructure spend without explicit authorization. Do not quietly consume billable OpenAI API usage.
- Limit simultaneous *commercial* experiments to one active unless there is a clear independently validated reason to expand.

## Every daily controller run must execute
1. Read \`engine/harness/OPERATING_CONTRACT.md\` and \`engine/harness/state.json\`, along with the latest evidence/ledger.
2. Verify that today's and yesterday's research jobs have produced evidence. Distinguish a successful GitHub commit from a verified external outcome.
3. Scout 3 independent paid-demand opportunities (not ideas already picked by the user). Underwriter independently rejects weak candidates; prioritize one.
4. Continue one selected experiment *through its next missing commercial gate*: real buyer channel, publication, functional checkout, distribution, buyer response, or verified payment. Use connected tools to do the action, not just draft instructions.
5. Query live Stripe for new payments attributed to that experiment and report separate gross, fees/refunds, and paid-out cash when available; unknown values must remain unknown.
6. Persist sanitized evidence and decisions. If there are no verified new buyers after a precommitted interval, close or revise with a clear reason rather than adding products.
7. Report succinctly: what changed externally, live link / receipt, attributable new gross, attributable new net known or unknown, next blocker. Never say "the business runs automatically" unless jobs, credentials, and transactions are verified.

## Stop rules
- After 5 working days of a live listing or 25 targeted relevant buyer exposures (whichever is later), if there is no qualified response, revise the buyer proposition or distribution channel; do not manufacture more collateral.
- Without known stock, legal fulfillment ability or completed service capability, do not solicit or accept prepaid orders for delivery.
- No undisclosed financial gain or guaranteed sales; no scraping behind authentication; no spamming; no unconsented personal-data use.
- Each experiment must include a payable path, a measurable buyer path and a timestamped decision.
