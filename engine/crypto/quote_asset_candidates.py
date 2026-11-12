#!/usr/bin/env python3
"""Conservative read-only quote-mint candidates from Solana transaction metadata.
Candidates are NOT a verified pool quote mint or fee entitlement.
"""
from collections import Counter

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
                if len(mint)>=32 and isinstance(decimals,int) and not isinstance(decimals,bool) and 0<=decimals<=18:
                    seen[(mint,decimals)]+=1
    candidates=[{'mint':mint,'decimals':decimals,'source':'TRANSACTION_TOKEN_BALANCE_METADATA'} for mint,decimals in sorted(seen)]
    return {'status':'CANDIDATES_ONLY_NOT_ATTRIBUTED' if candidates else 'NO_TOKEN_BALANCE_CANDIDATES',
            'candidates':candidates,'quote_mint_verified':False,'fee_entitlement_verified':False}
