# Signal-to-outcome lessons — 11 Nov 2026
Status: research synthesis / design guidance, not a running deployment, customer contract, revenue proof, or permission expansion.
Sources: two user-provided YouTube transcripts, one on Salim Jernite/Fountain and the autonomous company, one on AI-built memecoin launches and agentic trading. Anecdotal claims remain unverified unless independently identified below. Paraphrased; no transcript reproduced.

## Operating insight
The shared advantage is not "more agents"; it is compressing the interval between an external signal, a correctly chosen action, and independently verified results. Distribution and authorization remain bottlenecks. Existing outcome missions and permissions supersede this note.

## Transferable practices from the Fountain interview
1. **Signal engine.** Continuously collect permitted public/connected indicators with source, observed_at, target entity, event type, evidence URL/ID, freshness, confidence, anticipated economic value and deadline. Deduplicate, expire stale signals, and separate a weak inference from a verified need. Examples: published hiring surge, job reposting, interviewer changes, procurement tenders, product incidents, specific buyer requirements, verified open paid assignments. Do not infer private HR problems from a single complaint.
2. **Opportunity scoring before work.** Rank by verified payer/decision-maker, reachable distribution, demand proof, fit/fulfillment, cash timing, incremental cost, permissions and failure risk. A signal is not qualified demand.
3. **Customer-development gate.** For a new product, prefer short discovery interviews, a clickable mockup and explicit purchase interest from multiple independent buyers before substantial engineering. Fountain's account of five beta customers and three "would buy" responses is an *illustrative gate*, not proof of product-market fit or an invariant sample threshold. Signed paid pilots are stronger evidence.
4. **Factory with explicit stages.** SIGNAL -> TRIAGE -> QUALIFY -> SPEC -> BUILD/DELIVER -> INDEPENDENT QA -> PUBLISH/SEND (where authorized) -> MEASURE -> RECORD. Artifacts have versioned IDs, owners, testable acceptance criteria, rollback and next trigger.
5. **Structured handoffs.** Agent A writes an event/task to durable state; Agent B consumes with idempotency key and bounded retries. Prefer event triggers to expensive repeated full-context polling. Keep skills, tool schemas, failures and rationale in versioned, portable text. Model/router changes should not erase state.
6. **Automated verification.** Add separate code review, executable tests, visual/user-flow QA and outcome reconciliation. Human approval remains necessary for irreversible/financial/regulated actions and any action outside granted scope.
7. **Production rules.** No critique without a better alternative; minimize the burden of requesting time/clarification; treat trusted relationships as earned; prohibit sending raw unreviewed AI-generated communications. Translate this into evidence-rich, concise machine reports.
8. **Economic accounting.** Track tokens, tool calls, real incremental cost and money gained/saved. More model throughput is not automatically net value. The interview is from an enterprise with substantial staff and financial resources; do not imitate its agent count or spend.

## Transferable practices from the memecoin video
1. The developer-fee mechanism means revenue can depend on transaction *volume*, not necessarily an upfront product purchase. Verify fee schedule, actual executed volume, attributed wallet receipts, asset price, transfers, costs, off-ramp and bank availability.
2. Fast AI prototyping, visual identity, social distribution and API-accessible launch/trade tooling are real capabilities; never confuse a polished demo with a functional, lawful product.
3. The account offers several very high claimed earnings, but no adequate audit trail for independent verification. It exhibits survivorship bias and overlooks fees, failed launches, trader losses, liquidity and legal exposure. A promoted 1.5% fee would require $6.2m in eligible gross volume for $93k before costs.
4. Wallet splitting to conceal concentration, deceptive project branding, wash trading, manipulated volume and misleading performance claims are not legitimate growth tactics. No token issue, purchase, trade, real-currency transfer or spending is authorized by this research.
5. Candle and similar tools may support sandbox, public research and paper-mode experiments. Distinguish platform documentation from an independently tested live integration; no assumption of profit.
6. Explore the more general analogy instead: outcome-priced legitimate services, transaction/usage-based software for verified customers and embedded buyer distribution. Fees are an economic model, **not** distribution.

## What changes for existing missions
### Mission A: paid work
- Monitor genuine employer-trigger signals (new role published, hiring manager/new department, repeated/reopened posting, credible referral/introduction, direct employer response).
- Qualify on match, truthful suitability, reachability, application channel, probability/time to income.
- Generate one evidence-backed, individually tailored application or follow-up; send only via already-authorized verified channels; verify sent and response state; avoid duplicate outreach.
- Score outcomes by legitimate response, interview, offer, first paid work, and first settled pay, not outreach volume.

### Mission B: net bank-available funds
- Seek an *existing payer* or validated willingness to pay **before** additional software production. Track a diversified funnel of authorized routes, including outstanding receivables, legitimate paid assignments, existing marketplaces, direct B2B service need, and potentially usage/outcome priced work.
- For a prospective product: specific buyer pain -> accessible buyer -> demonstration/pilot -> paid commitment -> fulfillment -> processor/bank reconciliation. Avoid unpaid product factories with no distribution.
- Treat speculative tokens as research topics, not presumed fast-cash channels. Never substitute token capitalization/creator fees/crypto balance for verified bank-settled money.

### Harness design
- First inspect and reuse existing runtime, state and permissions. Minimum viable structure: event collector -> eligibility/scoring -> task queue -> tool worker -> independent verifier -> audit ledger, with explicit state transitions.
- Start with at most one fully evidenced workflow per mission; add parallel agents only when bottleneck data demonstrates value.
- Compare baseline to experiment with defined metric, cost ceiling, rollback and quality checks.
- Existing ChatGPT automation, GitHub Actions and an always-powered laptop do not constitute a tested unified autonomous runtime without shared credentials, verified liveness, recovery and durable state.

## Verified external references (as of 11 Nov 2026)
- Fountain's published autonomous-company thesis (self-description, not an independent audit): https://www.fountain.com/posts/the-autonomous-company
- Fountain Cue launch announcement: https://www.fountain.com/news/fountain-launches-cue-to-run-frontline-hiring-and-workforce-operations
- Notion Custom Agents triggers and Slack integrations: https://www.notion.com/help/custom-agents
- Notion credit costs: https://www.notion.com/help/buy-and-track-notion-credits-for-custom-agents
- Pump.fun October 2026 fee schedule (may change): https://pump.fun/docs/fees
- Candle agent tools, paper mode, pricing and risk-limiting affordances (provider claims): https://candle.tv/
- Robinhood Chain technical information: https://docs.robinhood.com/chain/connecting/

## Acceptance criteria for eventual engineering work
Do not count this research note as implementation. A signal-to-outcome workflow is only operational after (1) live signal collected and independently cited, (2) valid eligibility and permission check, (3) real action completed and receipt captured, (4) accurate outcome state recorded and deduplicated, (5) second cycle/restart tested, and (6) external results distinguished from hypotheses and forecasts.
