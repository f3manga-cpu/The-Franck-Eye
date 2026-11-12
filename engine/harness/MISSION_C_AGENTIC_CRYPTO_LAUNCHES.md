# Mission C — Agentic crypto builder and creator-fee research-to-execution runtime
Created 2026-11-11. User-specified third autonomous mission. This is a live operating objective, not a claim that agents or tokens are deployed.
Read OUTCOME_MISSIONS_V3.md, UNIVERSAL_OPERATOR_DIRECTIVE.md and this file each cycle.

## Objective
Use autonomous AI engineering and operating capabilities to systematically investigate, build, test, publish where authorized, distribute honestly and improve promising crypto-adjacent products and token-creator platforms, particularly the capabilities demonstrated in the user's Pump.fun / agentic-terminal video. Independent idea generation matters: do not constrain exploration to earlier suggested themes or existing brands. Aim for lawful **verified creator/platform income and usable technology**, not simulation theater, speculative profit promises, or token market-cap headlines. This mission is independent from the wider source-agnostic bank-money mission, although verified proceeds can count there with careful attribution.

## Opportunity / product factory
- Observe official platform documentation, current launch/creator fee economics, legal/tax/platform rules, market activity and demand. Record time, source, reliability, limitations and meaningful changes; avoid mirroring hype and unverified teenage earnings.
- Develop and evaluate multiple original, defensible product mechanisms (including non-token tools/integrations), looking for *actual use* and a plausible fee structure rather than merely attractive token artwork.
- Reuse open-source code and tools when license-compatible. Before any public release, verify name/IP/trademark risks, tokenomics/fee terms, smart-contract permissions, deployment process, UX, security, functioning demo and real user benefit.
- Build in safe local/testnet/paper mode first: authentic proofs of running code, integration tests, simulated or testnet transactions, verified output logs and persistent state. A static marketing site or image is not a working launchpad.
- Where agent terminals expose authenticated APIs, use read-only/testnet/sandbox first with strict credential isolation and immutable audit logs. Audit potential rug-pull and misrepresentation risk. Never split wallets to hide token concentration, wash trade, manipulate volume or impersonate existing brands.
- For real-money actions (token issue, on-chain transfers, trades, exchange deposits, production financial deployments, signing contracts, nonzero spending) obtain specific user authorization and verify balances, fees and failure modes. General authorization to run a harness is not permission to execute a financial transaction.
- If live issuance is unavailable or blocked, continue other independent product/creator-fee experiments instead of merely reporting failure. The user should not need to invent the next idea, provide prompts, or restart the engine.

## Minimum agentic execution loop
COLLECT public/legal platform and category signals -> SCORE evidence and next feasible result -> BUILD the smallest genuine capability -> TEST with automated unit and end-to-end checks -> REVIEW by independent evaluator -> RELEASE within scope -> MONITOR actual usage and attributable fees -> RECONCILE crypto, off-ramp and bank availability (if evidence accessible) -> SAVE durable state and next trigger.
Use scripts/events for deterministic steps; only invoke models where reasoning is needed. Keep incremental cost at EUR 0 unless explicitly authorized.
Measure executable builds, passing tests, user adoption and bank-settled funds; **do not** count GitHub notes, fake volume, paper profits, speculative market cap or anecdotes as commercial outcomes.

## Implementation checkpoints
1. Audit existing Pump.fun/GTO assets, repositories, installed runtimes and connectivity.
2. Create a genuinely running zero-cost public-information/creator-economics scanner with versioned stored snapshots and hard error handling.
3. Produce and test an original runnable prototype with a lawful value proposition and no wallet access in research mode.
4. Establish controlled release workflow and independently test real user interaction. Escalate exact minimal financial/public launch permission when needed.
5. Re-run on an ongoing schedule with deduplication, crash restart, stale-source detection and exception-only reports.
6. Verify outcome stages separately: researched, built, tested, deployed, used, fees earned, transferable balance, actual bank credit.

## Required honesty
This document itself is only a documented mission. An automation schedule is not a resident autonomous agent. A local research daemon is not proof of token deployment, usage, real fees or bank-settled cash.

## Verified implementation checkpoint — 2026-11-12
- Local public DEX market collector and dashboard observed running; the collector completed successful 15-minute cycles. At 02:54 CET, dashboard API returned fresh successful state, 44 cycles and zero verified revenue.
- Added live read-only Solana v1 transaction support in `engine/crypto/onchain_receipt_verify.py` after a genuine v1 RPC incompatibility was found. Validated against finalized signature `5pUYqwjevNZnUGmYkZALFEU23QgEsWc4siKKrwtgQA2NfUmmCBuU5WCtxMtXHwm33FHus7NCLYug459epBn89GTr`; account balance delta was observed, without interpreting it as a creator payment.
- Added `engine/crypto/pump_fee_event_audit.py`: official Pump/PumpSwap IDL-based decoding of finalized trade, sweep and creator claim events with program-invocation checks. A live PumpSwap BuyEvent for the signature above reported 3,419 raw quote units in the coin creator fee field. The fee beneficiary, whether a holder-rewards mode applies, the quote conversion, personal entitlement and any payout to the principal remain unverified.
- Added `engine/crypto/onchain_fee_probe.py` and corresponding systemd .service/.timer. Linux timer was enabled and active, scheduled hourly, with `Result=success`, `ExecMainStatus=0` on manual systemd invocation. It samples a biased set of current PumpSwap mints, deduplicates finalized signatures into a separate local SQLite database, and emits fail-closed health state; no wallet or tokens involved. Verified 4 stored mainnet signatures and two recognized fee events after manual executions, not attributed earnings.
- Local crypto-lab regression suite: 62 passing tests. All safe scripts, tests, and unit files committed to this repository.
- **Outstanding external outcome gate:** No verified outside human using the fee-proof tool, no paying client, no token issued, no claimable creator-fee entitlement, no bank money. Prioritize a permission-compliant public distribution/usage test, independent creator-market alternatives, or a scope-authorized launch; do not increase background polling solely to claim activity. Real token issuance, trading, wallets and nonzero spending still require specific transaction authorization. 
