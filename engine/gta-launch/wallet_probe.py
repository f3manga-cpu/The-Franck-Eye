#!/usr/bin/env python3
"""Read-only creator-wallet status watcher, no wallet signing or transactions.

This does not prove the user owns the specified wallet or that it is attached
to a pump.fun account. Public Solana RPC is the single mainnet data source.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
import urllib.request
import urllib.error

PRIVATE=Path('/home/franck/.config/gta-creator/owner.json')
LOG=Path('/home/franck/.config/gta-creator/wallet_observations.jsonl')
RPC='https://api.mainnet-beta.solana.com'

def check():
    config=json.loads(PRIVATE.read_text())
    pub=config['wallet_address']
    assert isinstance(pub,str) and 32 <= len(pub) <= 44
    request=urllib.request.Request(
        RPC,
        data=json.dumps({
            "jsonrpc":"2.0","id":1,"method":"getBalance",
            "params":[pub,{"commitment":"finalized"}]
        }).encode(),
        headers={"Content-Type":"application/json","User-Agent":"GTA-public-wallet-observer/0.1"},
        method="POST"
    )
    observation={
        "collected_at":datetime.now(timezone.utc).isoformat(),
        "wallet_last6":pub[-6:],
        "wallet_source":"user-provided",
        "wallet_ownership_verified":False,
        "coin_issued":False,
        "sol_balance":None,
        "source":"solana mainnet public RPC",
        "status":"ERROR",
    }
    try:
        with urllib.request.urlopen(request,timeout=12) as response:
            result=json.load(response)
        if "error" in result:
            raise RuntimeError(str(result["error"])[:300])
        lamports=result["result"]["value"]
        observation["sol_balance"]=lamports/1_000_000_000
        observation["slot"]=result["result"]["context"]["slot"]
        observation["status"]="SUCCESS"
        observation["funded_at_observation"]=lamports>0
    except Exception as exc:
        observation["error"]=f"{type(exc).__name__}: {str(exc)[:160]}"
    return observation

def main():
    value=check()
    LOG.parent.mkdir(parents=True,exist_ok=True)
    with LOG.open('a',encoding='utf-8') as out:
        out.write(json.dumps(value,separators=(',',':'))+'\n')
    LOG.chmod(0o600)
    print(json.dumps(value,indent=2))
    # Treat network failures as observed unknown, not an unfunded wallet.
    # Service remains successful so the next timer tries again.
if __name__=="__main__":
    main()
