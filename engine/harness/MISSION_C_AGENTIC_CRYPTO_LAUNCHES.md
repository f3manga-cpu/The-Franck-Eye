# Mission C — Agentic crypto builder and creator-fee research-to-execution runtime
Created 2026-11-11. User-specified third autonomous mission. This is a live operating objective, not a claim that agents or tokens are deployed.
Read OUTCOME_MISSIONS_V3.md, UNIVERSAL_OPERATOR_DIRECTIVE.md and this file each cycle.

## Geographic and creator-wallet correction — 2026-11-13
- User reports that they are **currently based in Austin, Texas, USA**, and asks that French-location assumptions be set aside. For now use **U.S. federal / Texas** rules in the GTA launch review, not an automatic French/MiCA default. This statement establishes a reported current location only, not tax residence, legal issuer domicile, or an exemption from other jurisdictions.
- The user gave their proposed pump.fun creator **public Solana address** privately in chat, and explicitly designated their existing pump.fun account as the GTA creator/fee-recipient. The address is saved only in a permission-restricted local file at `/home/franck/.config/gta-creator/owner.json`; do not copy that wallet-account association or authentication material into this public repository.
- 2026-11-13 read-only Solana mainnet verification: the reported wallet had **0 SOL**, no account data, and zero recent signatures. This does not independently confirm control of the account; public keys do not sign transactions.
- The official pump.fun SDK `createV2Instruction` produced a valid **unsigned** GTA instruction using the owner-supplied address and staged metadata; that does not create an onchain coin. There is no authority to spend SOL, purchase a token, or access/export keys.
- Monitor SOL balance read-only and identify the next real blocker. Pump.fun's creation UI supports free *off-chain* draft creation, but an actual public on-chain token requires a qualifying first buy. Always verify live fees directly and obtain owner-controlled approval of the exact transaction.
- Regulatory basis to check: SEC March 17, 2026 interpretive release (effective March 23), digital collectible/memecoin vs investment-contract analysis; Texas State Securities Board's marketing and enforcement rules; pump.fun Terms and restricted jurisdictions. Avoid promising purchaser profit or presenting creator-managed future price appreciation as a return. Separate legal analysis from financial authorization; consult qualified U.S. counsel if issuance classification is uncertain.
- The older French/MiCA launch gating remains a contextual historical note and **is not a standing Austin-based gate** absent evidence that the issuer or offering triggers it.

## Active user-directed launch identity — 2026-11-12
**Current working brand is Greatest Token Action (GTA)**; this replaces Gotham Fifth Overbet (GTO) and any suggestion to use Greatest Token Arcade. Read `engine/harness/GTA_GREATEST_TOKEN_ACTION_BRIEF_2026-11-12.md` every cycle and direct meaningful execution toward original content-world creation, launch-readiness technical checks (unsigned only), distribution verification and a real launch decision. Do not spend entire cycles merely expanding generic market telemetry. Ticker is provisional; a distinct coin named Greatest Token Alive is already present as GTA. Avoid Rockstar IP, game affiliation implications, deceptive hype or targeting minors. No on-chain mint, signing, financial transactions or unauthorized public promotion. Log actual progress against launch gating and independently proven organic participation.

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

## Current verified Pump.fun market research
Read `engine/harness/PUMPFUN_RESEARCH_2026-11-12.md` before choosing launch or distribution work. It records primary-source fee rules as of October 2026, documented creator case studies, cohort failure rates, official tokenized-agent limitations, France/EU compliance checks and an evidence-based launch readiness gate. Treat it as research, not a transaction authorization. Validate changing platform terms again before any live action.

## Implementation checkpoints
1. Audit existing Pump.fun/GTO assets, repositories, installed runtimes and connectivity.
2. Create a genuinely running zero-cost public-information/creator-economics scanner with versioned stored snapshots and hard error handling.
3. Produce and test an original runnable prototype with a lawful value proposition and no wallet access in research mode.
4. Establish controlled release workflow and independently test real user interaction. Escalate exact minimal financial/public launch permission when needed.
5. Re-run on an ongoing schedule with deduplication, crash restart, stale-source detection and exception-only reports.
6. Verify outcome stages separately: researched, built, tested, deployed, used, fees earned, transferable balance, actual bank credit.

## Verifiable launch-preparation deliverable — 2026-11-12
- **Actual project:** `engine/gta-launch/`, using official `@pump-fun/pump-sdk@4.1.0` and Solana web3.js on the online laptop. `npm test` passed three tests; real SDK `createV2Instruction` produced a nonbroadcasting 16-account instruction with 157 bytes when given the verified staging metadata URL.
- **Original artwork + metadata:** `docs/gta-staging/logo.png` (512×512) and `metadata.json`; both were verified HTTP 200 via GitHub Pages. No token issued. This GitHub Pages staging URI is mutable, not final immutable IPFS metadata.
- **No wallet credentials/signing:** no Solana CLI wallet or detected browser wallet extension in common laptop profile paths. The script generates an ephemeral unsigned preview mint key; its address is not a live coin and no secret is retained.
- **Irreducible live gates:** owner-controlled creator/payer wallet and enough SOL for actual account rent/fees; immutable verified metadata; applicable France/EU token offering/admission/marketing compliance determination; explicit per-transaction authorization. The default additional spending authorization remains €0.
- Do not represent the preparation as a launch or keep expanding generic dashboards in place of identifying/removing the exact gate. Next cycle should address legitimate safe gating steps and real creator distribution mechanisms with independent evidence.

## Required honesty
This document itself is only a documented mission. An automation schedule is not a resident autonomous agent. A local research daemon is not proof of token deployment, usage, real fees or bank-settled cash.

## Verified implementation checkpoint — 2026-11-12
- Local public DEX market collector and dashboard observed running; the collector completed successful 15-minute cycles. At 02:54 CET, dashboard API returned fresh successful state, 44 cycles and zero verified revenue.
- Added live read-only Solana v1 transaction support in `engine/crypto/onchain_receipt_verify.py` after a genuine v1 RPC incompatibility was found. Validated against finalized signature `5pUYqwjevNZnUGmYkZALFEU23QgEsWc4siKKrwtgQA2NfUmmCBuU5WCtxMtXHwm33FHus7NCLYug459epBn89GTr`; account balance delta was observed, without interpreting it as a creator payment.
- Added `engine/crypto/pump_fee_event_audit.py`: official Pump/PumpSwap IDL-based decoding of finalized trade, sweep and creator claim events with program-invocation checks. A live PumpSwap BuyEvent for the signature above reported 3,419 raw quote units in the coin creator fee field. The fee beneficiary, whether a holder-rewards mode applies, the quote conversion, personal entitlement and any payout to the principal remain unverified.
- Added `engine/crypto/onchain_fee_probe.py` and corresponding systemd .service/.timer. Linux timer was enabled and active, scheduled hourly, with `Result=success`, `ExecMainStatus=0` on manual systemd invocation. It samples a biased set of current PumpSwap mints, deduplicates finalized signatures into a separate local SQLite database, and emits fail-closed health state; no wallet or tokens involved. Verified 4 stored mainnet signatures and two recognized fee events after manual executions, not attributed earnings.
- Local crypto-lab regression suite: 62 passing tests. All safe scripts, tests, and unit files committed to this repository.
- **Outstanding external outcome gate:** No verified outside human using the fee-proof tool, no paying client, no token issued, no claimable creator-fee entitlement, no bank money. Prioritize a permission-compliant public distribution/usage test, independent creator-market alternatives, or a scope-authorized launch; do not increase background polling solely to claim activity. Real token issuance, trading, wallets and nonzero spending still require specific transaction authorization. 
