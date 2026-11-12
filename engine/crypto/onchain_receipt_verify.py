#!/usr/bin/env python3
"""Read-only Solana RPC verification of *transaction existence and account balance deltas*.

This does NOT identify Pump.fun creator fees, entitlement, custody or bank settlement.
No private keys, wallet connections, trades, account scans or arbitrary RPC hosts.
"""
import argparse
from decimal import Decimal
import hashlib
import json
import re
import urllib.request
from pathlib import Path

RPC = "https://api.mainnet-beta.solana.com"
BASE58 = re.compile(r"^[1-9A-HJ-NP-Za-km-z]+$")
LAMPORTS = Decimal("1000000000")

def valid_base58(value, minimum, maximum):
    return isinstance(value, str) and minimum <= len(value) <= maximum and BASE58.fullmatch(value) is not None

def fetch_transaction(signature, transport=None):
    if not valid_base58(signature, 80, 90):
        raise ValueError("Invalid Solana signature")
    payload = {"jsonrpc":"2.0","id":1,"method":"getTransaction",
               "params":[signature,{"encoding":"jsonParsed","commitment":"finalized",
                                    "maxSupportedTransactionVersion":1}]}
    if transport is not None:
        result = transport(payload)
    else:
        req = urllib.request.Request(RPC, data=json.dumps(payload).encode(),
                                     headers={"Content-Type":"application/json","User-Agent":"MissionC-readonly/1.0"},
                                     method="POST")
        with urllib.request.urlopen(req, timeout=12) as response:
            raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError("Oversized RPC response")
            result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("Malformed RPC envelope")
    if "error" in result:
        raise ValueError("RPC error: "+str(result["error"])[:180])
    return result.get("result")

def verify(signature, recipient, tx):
    if not valid_base58(recipient, 32, 44):
        raise ValueError("Invalid Solana account address")
    if tx is None:
        return {"status":"NOT_FOUND_OR_NOT_FINALIZED","signature":signature,
                "recipient":recipient,"bank_settled_eur":None}
    if not isinstance(tx,dict) or not isinstance(tx.get("meta"),dict):
        raise ValueError("Incomplete transaction metadata")
    meta = tx["meta"]
    message = (tx.get("transaction") or {}).get("message") or {}
    keys = message.get("accountKeys")
    pre, post = meta.get("preBalances"), meta.get("postBalances")
    if not isinstance(keys,list) or not isinstance(pre,list) or not isinstance(post,list) or len(keys)!=len(pre) or len(keys)!=len(post):
        raise ValueError("Balance/account key lengths mismatch")
    addresses = [k.get("pubkey") if isinstance(k,dict) else k for k in keys]
    if len(addresses)!=len(set(addresses)):
        raise ValueError("Duplicate account keys")
    if meta.get("err") is not None:
        return {"status":"FAILED_TRANSACTION","signature":signature,"recipient":recipient,
                "slot":tx.get("slot"),"bank_settled_eur":None}
    if recipient not in addresses:
        return {"status":"ACCOUNT_NOT_IN_TRANSACTION","signature":signature,"recipient":recipient,
                "slot":tx.get("slot"),"bank_settled_eur":None}
    idx=addresses.index(recipient)
    if any(not isinstance(v,int) or isinstance(v,bool) or v<0 for v in (pre[idx],post[idx])):
        raise ValueError("Invalid lamport balances")
    delta=post[idx]-pre[idx]
    return {"status":"FINALIZED_ACCOUNT_DELTA_OBSERVED","signature":signature,"recipient":recipient,
            "slot":tx.get("slot"),"block_time":tx.get("blockTime"),
            "recipient_net_delta_lamports":delta,
            "recipient_net_delta_sol":str(Decimal(delta)/LAMPORTS),
            "rpc_endpoint":RPC,"proof_level":"RPC_REPORTED_ACCOUNT_NET_CHANGE_NOT_CREATOR_FEE",
            "creator_fee_attributed":False,"creator_entitlement_verified":False,
            "bank_settled_eur":None,
            "limitations":["Net balance change can combine transfers, rent and other movements.",
                           "A balance increase does not establish Pump.fun fee attribution or ownership.",
                           "RPC response is a single third-party view, not independently cross-checked.",
                           "This does not verify withdrawals, off-ramp or bank settlement."]}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("signature")
    parser.add_argument("recipient",help="Public recipient account address, NOT private key")
    parser.add_argument("--out",help="Optional local JSON report")
    args=parser.parse_args()
    result=verify(args.signature,args.recipient,fetch_transaction(args.signature))
    result["report_sha256"]=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()
    output=json.dumps(result,indent=2)+"\n"
    if args.out: Path(args.out).write_text(output)
    else: print(output,end="")
    return 0 if result["status"]=="FINALIZED_ACCOUNT_DELTA_OBSERVED" else 2

if __name__=="__main__":
    raise SystemExit(main())
