#!/usr/bin/env python3
"""Conservative read-only quote-mint candidates from Solana transaction metadata.
Candidates are NOT a verified pool quote mint or fee entitlement.
"""
from collections import Counter

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def valid_solana_pubkey(value):
    """Check a canonical 32-byte Solana public key, without third-party dependencies."""
    if not isinstance(value, str) or not 32 <= len(value) <= 44:
        return False
    n = 0
    for ch in value:
        if ch not in BASE58_ALPHABET:
            return False
        n = n * 58 + BASE58_ALPHABET.index(ch)
    zeros = len(value) - len(value.lstrip('1'))
    decoded_len = zeros + ((n.bit_length() + 7) // 8)
    return decoded_len == 32

NATIVE_SOL = 'So11111111111111111111111111111111111111112'

def candidate_quote_assets(tx):
    if not isinstance(tx, dict) or not isinstance(tx.get('meta'), dict):
        return {'status':'INSUFFICIENT_METADATA','candidates':[]}
    meta = tx['meta']
    if meta.get('err') is not None:
        return {'status':'FAILED_TRANSACTION','candidates':[]}
    balances = (meta.get('preTokenBalances'),meta.get('postTokenBalances'))
    if any(not isinstance(v,list) for v in balances):
        return {'status':'INSUFFICIENT_METADATA','candidates':[]}
    seen = Counter()
    for group in balances:
        for item in group:
            if isinstance(item,dict) and isinstance(item.get('mint'),str) and isinstance(item.get('uiTokenAmount'),dict):
                mint=item['mint']; decimals=item['uiTokenAmount'].get('decimals')
                if valid_solana_pubkey(mint) and isinstance(decimals,int) and not isinstance(decimals,bool) and 0<=decimals<=18:
                    seen[(mint,decimals)]+=1
    # Conflicting decimals for one mint make monetary interpretation unsafe.
    by_mint = {}
    for mint, decimals in seen:
        by_mint.setdefault(mint, set()).add(decimals)
    conflicts = sorted(mint for mint, decimals in by_mint.items() if len(decimals) > 1)
    candidates=[{'mint':mint,'decimals':decimals,'source':'TRANSACTION_TOKEN_BALANCE_METADATA'} for mint,decimals in sorted(seen) if mint not in conflicts]
    return {'status':'CONFLICTING_MINT_DECIMALS' if conflicts else ('CANDIDATES_ONLY_NOT_ATTRIBUTED' if candidates else 'NO_TOKEN_BALANCE_CANDIDATES'),
            'conflicting_mints': conflicts,
            'candidates':candidates,'quote_mint_verified':False,'fee_entitlement_verified':False}
