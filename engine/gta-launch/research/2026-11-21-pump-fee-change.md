# Pump.fun primary-source fee checkpoint — 2026-11-21

Source: https://pump.fun/docs/fees (page states updated 2026-11-16; accessed 2026-11-21).

- Coin creation: no platform creation fee; Solana network transaction fee and on-chain account deposit still required.
- SOL/USDC bonding-curve trades: creator fee 0.300% of eligible traded amount, protocol 0.95%, total 1.25%. This is **not** a guaranteed creator payout.
- Canonical PumpSwap pools: variable creator fee by market-cap tier, ranging from 0.95% in some tiers down to 0.05% in the highest SOL tier. Do not model all volume at one rate.
- NEW economic distinction: from 2026-10-17 web/mobile pump.fun trades carry an additional 0.45% platform fee without referral code or 0.40% with another user's referral code. The fee applies also to a first buy during coin creation; third-party interfaces/Terminal differ. This is paid by traders, not additional creator fee revenue.
- Custom pairs use flat creator-fee terms (0.30% on bonding curve, 0.05% canonical PumpSwap), different from SOL/USDC graduated tiers.
- Fee collection is in the quote asset, not the traded token. Claims, wallet balance, settlement and net fiat proceeds require separate verification.

**Gate/outcome:** creator-fee economics updated from official primary source; no verified token, trading volume, creator claim or bank receipt. User wallet still requires authorized session, exact transaction confirmation, funding and jurisdictional review. No issuance or spending authorized.

**Operational check:** Remote Desktop Commander reports franck-pc-portable OFFLINE, last seen ~13 hours before 2026-11-21 13:43 CET. GitHub issue #9 comments API returned 0 independent comments. GitHub Pages availability could not be verified through available web access; SIGNAL 009 publishing unconfirmed. Do not assert service/timer liveness.

**Next trigger:** when laptop reconnects inspect timers/scout and publish result; independently verify SIGNAL 009 URL; obtain legitimate authenticated social connection through owner UI. Avoid repeated dashboards.
