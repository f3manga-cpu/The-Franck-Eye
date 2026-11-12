# Pump.fun verified market / launch research — 2026-11-12
Prepared for Mission C. Public research, not an authorization to issue, trade, sign, spend, or market a token.

## Verified present mission state
- As of 2026-11-12 23:15 CET, laptop user services `agentic-creator-watch.service` and `agentic-creator-dashboard.service` were active; the fee-probe systemd timer was enabled.
- Journal shows 15-minute market collection with successful updates after one transient DNS failure.
- The Mission C scheduled run at 22:45 CET reported 88 passing tests, 2 skips, 0 failures, all five public demo assets HTTP 200; no validated independent user, lead, paid client, token launch, creator-fee entitlement, or bank proceeds.
- Local Git checkout file inventory does not show a GTO-specific mint/launch config or metadata in this repository. This is not proof that none exists elsewhere.
- Prioritize external adoption evidence; extra polling and commits are not income.

## Platform economics (primary source, last updated Oct 17, 2026)
https://pump.fun/docs/fees
- Creation: no platform fee, but Solana transaction fee and on-chain account deposit apply.
- Migration to PumpSwap: 0.015 SOL, charge allocation depends on pairing/trigger.
- Bonding curve SOL/USDC creator share: 0.300% of genuine traded quote volume.
- Canonical PumpSwap SOL/USDC: creator fee tiers range from 0.05% to 0.95% by quoted cap. Custom-pair canonical pool: 0.05%.
- Holder Rewards mode routes creator fees to eligible token holders instead of creator and is not equivalent to creator cash. Creator-fee sharing and ownership changes exist.
- Creator fees are in the pool's quote asset, not an automatic bank payout. Withdrawal / off-ramp / tax stages require separate verification.
- At $100k legitimate quote volume on the bonding curve, 0.3% gross creator fee = $300 before network, other costs and taxes. This is illustrative, not forecast.

## Base rates and measurement caveats
- pumpdata.fun on-chain daily statistics: 2026-11-11 42,369 launches and 920 graduations (2.17% same-day flow ratio, NOT matched-cohort probability): https://pumpdata.fun/pump-fun-graduation-rate
- July 22–October 31 cohort: 3,917,381 launches, 108,901 graduations (2.78%) reported; 37.9% of graduates completed within two slots, including 24.4% by sole deployer buying full curve: https://pumpdata.fun/research/pump-fun-launch-to-graduation
- Aug–Oct 2026 on-chain study: fewer than 1 in 10 launches still traded 7 days later in earlier cohorts: https://jumpbit.io/en/resources/research/pump-fun-statistics-launches-graduation-rate-survival
- Some other academic estimates use different collection and event definitions and have explicit correction notices; never combine as though directly comparable.
- Bitquery on-chain study of 3,170 $100k+ tracker "wins" (Oct 2025–Aug 2026) classified only 26% of tracked amount as real independent trading profits; 51% token handoffs, 13% related-wallet wash loops. **This is NOT a creator-fee distribution estimate**: https://bitquery.io/investigations/who-got-rich-on-pumpfun

## Documented success mechanisms; selection bias and uncertainties
- Bagwork duo: press reported ~$49k creator fees after viral livestream incident in September 2025. Legal controversy makes the incident unsuitable as a playbook. https://decrypt.co/339298
- BunnyFuFuu: press reported >$130k creator fees over first 3 days but only ~$29k in next 3 months; strong initial attention did not ensure long tail. https://decrypt.co/352919/creator-capital-markets-pump-fun-streaming-twitch
- Truth Terminal/GOAT: third party launched GOAT; agent did not mint it. Cultural distribution and outside wallet donations drove valuation, not evidence of autonomous programmatic launch earnings. https://cointelegraph.com/news/ai-bot-didnt-launch-goat-memecoin-did-promote-it
- Need separately verify on-chain creator fee **claims**, independent audience and quote-asset-to-bank settlement; media numbers do not imply net bank cash.

## New 2026 technical capabilities / overlooked routes
- Official pump.fun Tokenized Agent terms: opt-in automated buyback/burn smart-contract setting, `skills.md`, hourly policy-controlled buyback; expressly **not** an AI agent by itself. Has different funding requirements; do not conflate buyback activity with model skill or holder value. https://pump.fun/docs/tokenized-agent-disclaimer
- Official public program instruction sources and SDKs: https://github.com/pump-fun/pump-public-docs ; official archived agent skills library https://github.com/pump-fun/pump-fun-skills . Use maintained docs, audit any code before execution, use local unsigned/testnet mode. Never import credential-writing code unreviewed.
- Alternative non-token revenue: creator-fee forensic proof service for independent creators; community takeover of abandoned coin and earning creator fees (requires genuine community consent and Pump approval); audience/content-led launch only after independent engagement validation. None currently has demonstrated customer demand in this mission.
- Jan 2026 platform fee-sharing and rights updates: https://www.theblock.co/news/markets/2026-01-09-pump-fun-overhauls-creator-fees-token-launches-highest-daily-september-384975

## Compliance/IP checks before any live launch
- In France/EU MiCA, public offers or admission to trading can invoke whitepaper / notification / marketing requirements; exemptions exist with conditions and may not apply if admission to trading is sought. Assess actual planned launch; do not presume any blanket memecoin exemption:
  https://www.esma.europa.eu/publications-and-data/interactive-single-rulebook/mica/article-4-offers-public-crypto-assets-other
  https://www.amf-france.org/fr/offre-au-public-de-crypto-actifs
- Disclose creator fee routing and creator-held supply; never simulate independent wallets, volume or community support. No deceptive market promotion.
- Check naming/art/trademarks against third-party comic, game and entertainment IP before public publication. Reuse only genuinely original/licensed material.

## Decision framework for next cycle
1. **Launch readiness audit**: find original metadata/art, names, ticker uniqueness and wallet handling; verify official SDK current APIs and actual minimum network costs; prototype an UNSIGNED offline transaction; no publish, signing or spend.
2. **Customer/adoption gate**: before claiming business, add permission-compliant feedback/signup to existing live Token Evidence demo or seek independent user testing through an authorized channel and record real unique replies. No invented impressions.
3. **Choose mechanism based on independent evidence**: pure meme/viral coin; content-led repeat-interest token; demonstrable useful product with transparent fees; external creator-fee services; community takeover. Discard routes lacking distribution and credible unit economics.
4. **Exact approval gate for mainnet**: chosen coin, mint/wallet recipient, fee-routing model, pair, initial buy, maximum SOL/network spend, promotion/publication scope, compliance determination. Standing harness permission does not authorize issuance.
5. Report separate stages researched -> configured -> unsigned tested -> publicly issued -> independent traders/users -> creator fees claimed -> transferable -> bank settled. A market-cap print cannot advance any fee stage.
