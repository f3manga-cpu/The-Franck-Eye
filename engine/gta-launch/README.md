# Greatest Token Action — live SDK launch preparation
Status: **token not issued**. This directory contains a working, non-custodial, offline `create_v2` instruction builder using pump.fun's official SDK 4.1.0.

## Execute on Linux
```bash
cd engine/gta-launch
npm ci --ignore-scripts
npm test
npm run preview
# With owner-controlled public address and a durable HTTPS metadata URL:
node launch.mjs --dry-run --creator YOUR_PUBLIC_SOLANA_ADDRESS --metadata-uri https://your-domain.example/metadata.json
```

The preview intentionally generates an ephemeral mint keypair and discards the secret. The printed preview mint address is **not a launched coin** and cannot later be used as a real mint. There is no signing, key handling, RPC broadcast, private-key import, account access, or trade capability. No secrets belong in this repository.

Token name: Greatest Token Action. Proposed ticker: GTA (nonunique). Default SOL pair, creator fee mode on, holder rewards off, mayhem mode off. No initial buy proposed or authorized. Staging metadata and original image are now publicly served at `https://f3manga-cpu.github.io/The-Franck-Eye/gta-staging/metadata.json` and `/logo.png` (both HTTP 200 verified on 2026-11-12). This is an editable staging endpoint and **not a permanent IPFS URI for a live coin**. Metadata template in `token.json` includes an independent/no-affiliation statement. Image is generated via `make_logo.py` in `assets/logo.png`; public permanent metadata/image pinning is outstanding.

## Honest launch gating
1. Confirm the identity/rights and uniqueness (other GTA ticker coins already exist), artwork and social links. Keep independent from Rockstar IP and make no official affiliation claims.
2. Review US federal and Texas laws for the reported Austin-based launch; confirm actual issuer structure and any cross-border exposure. Do not infer a blanket memecoin exemption.
3. Publish immutable metadata/image URI on a suitable host (IPFS preferred) after authorized scope check. The older pump.fun/api/ipfs upload endpoint is deprecated.
4. User-owned wallet public key and controlled Solana signing required. Confirm remaining SOL for account rent, tx fees and optional initial buy.
5. Rebuild and inspect instruction with final owner and metadata, simulate/estimate fees on Solana, obtain explicit authorization for the exact live transaction.
6. Separate outcomes: metadata hosted -> instruction prepared -> transaction signed -> confirmed mint -> organic independent interactions -> claimable creator fee -> payout settled.
For official create_v2 API see https://github.com/pump-fun/pump-public-docs/blob/main/docs/instructions/COIN_CREATION.md and https://pump.fun/docs/fees.

**No live token is created by these commands.**

## Ongoing independent editorial and audience processes
- `publish.py --publish --push`: one story becomes public when its queued date arrives; auto-publish does not create financial offers, send social posts or mint a coin. See `content_queue.json`.
- `gta-editorial-publisher.timer`: scheduled daily 12:05 Europe/Paris, with persistent catch-up after reboot.
- `collect_metrics.py`: independent community issue #9 and site availability checks, storing timestamped snapshots locally under `data/`. GitHub repository view counts are not the website pageview metric.
- `gta-audience-monitor.timer`: runs four times a day. No fake site traffic claims or unknown wallet earnings.
- Public community-feedback issue: https://github.com/f3manga-cpu/The-Franck-Eye/issues/9 (requires GitHub sign-in).
- Publishing to pump.fun or social networks remains blocked pending account session and connected network; the hosted stories are separate.

## Current owner-wallet binding (local, not published)
The user-provided creator address and self-reported current Austin, Texas location are stored in a chmod-600 local record: `/home/franck/.config/gta-creator/owner.json`. That record contains only a public address and non-secret preferences. It is not ownership verification and never authorizes signing. Local hourly `gta-wallet-observer.timer` records read-only finalized SOL balance; no transfers or automated launch. To run owner-bound preview, use `--creator` with the public key. The repo does not include that key as an address-to-user identity binding. At the first check the address was unfunded (0 SOL).
