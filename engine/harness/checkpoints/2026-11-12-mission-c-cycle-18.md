# Mission C — cycle 18 — 2026-11-12 10:48 CET
Stage: verified read-only mainnet account inspection; NOT creator income.

- Read all three authoritative mission/directive documents. Linux Remote Desktop Commander device online.
- Reused the previously documented finalized mainnet PumpSwap transaction signature `5pUYqwjevNZnUGmYkZALFEU23QgEsWc4siKKrwtgQA2NfUmmCBuU5WCtxMtXHwm33FHus7NCLYug459epBn89GTr`.
- Called Solana `getTransaction` (53 account keys), `getMultipleAccounts` for those keys, and decoded PumpSwap-owned accounts using official cached PumpSwap IDL and existing `decode_pool`.
- **Real canonical pool resolved:** `2ULaeaUQWkid31cVKyFEujx9ReF7cdGepPxuoptz57m5`, owned by `pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA`; valid Pool discriminator. Base mint `4xgqefa5WcdHWKXzqvM9MRJqWYGaHVEUnpUL4Vq5pump`; quote mint `Xsc9qvGR1efVDFGLrVsmkzv3qi45LTBjeUKSPmx9qEh`; creator fee bps 30; `is_holder_reward=true`. Two other PumpSwap-owned accounts were correctly rejected for mismatched discriminator.
- Called finalized `getAccountInfo` with `jsonParsed` on quote mint: owner `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb` (Token-2022), decimals **8**. This mint has extensions including `scaledUiAmountConfig`, `permanentDelegate`, `confidentialTransferMint`, and `pausableConfig`; do not assume raw integer / 10^8 represents economically transferable or unscaled UI value. Never treat fee field as wallet income.
- Regression: `python3 -m unittest discover -s engine/crypto -p 'test_*.py' -q` => 77 tests, OK, 2 skipped.
- Codex private creator scout file exists and keys inspected; unverified proposals not treated as outcome. No private contents published.
- Zero additional spend, no signing, trading, issuance, transfers, or promotions.
- No verified outside users, fee entitlement, receipts, or bank settlement.
- Next trigger: create read-only quote-mint metadata validation and extension-aware warning in exported fee evidence, then test against this mainnet pool; pursue an authorized external user journey.
