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

Token name: Greatest Token Action. Proposed ticker: GTA (nonunique). Default SOL pair, creator fee mode on, holder rewards off, mayhem mode off. No initial buy proposed or authorized. Metadata template in `token.json` includes an independent/no-affiliation statement. Image is generated via `make_logo.py` in `assets/logo.png`; public permanent metadata/image pinning is outstanding.

## Honest launch gating
1. Confirm the identity/rights and uniqueness (other GTA ticker coins already exist), artwork and social links. Keep independent from Rockstar IP and make no official affiliation claims.
2. Assess EU/French MiCA obligations for intended public launch and marketing; do not infer an automatic exemption.
3. Publish immutable metadata/image URI on a suitable host (IPFS preferred) after authorized scope check. The older pump.fun/api/ipfs upload endpoint is deprecated.
4. User-owned wallet public key and controlled Solana signing required. Confirm remaining SOL for account rent, tx fees and optional initial buy.
5. Rebuild and inspect instruction with final owner and metadata, simulate/estimate fees on Solana, obtain explicit authorization for the exact live transaction.
6. Separate outcomes: metadata hosted -> instruction prepared -> transaction signed -> confirmed mint -> organic independent interactions -> claimable creator fee -> payout settled.
For official create_v2 API see https://github.com/pump-fun/pump-public-docs/blob/main/docs/instructions/COIN_CREATION.md and https://pump.fun/docs/fees.

**No live token is created by these commands.**
