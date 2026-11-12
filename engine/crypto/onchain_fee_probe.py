#!/usr/bin/env python3
"""One-shot public-chain Pump fee event sampler. No keys, trading or payouts.

The sample is ONLY from the existing biased DEX Screener spotlight database.
Fees observed on third-party coins are NOT user revenue.
"""
from datetime import datetime, timezone
import json
import sqlite3
from pathlib import Path
import urllib.request

from onchain_receipt_verify import RPC, valid_base58
from quote_asset_candidates import valid_solana_pubkey
from pump_fee_event_audit import audit, get_idls

ROOT=Path(__file__).resolve().parent
MARKET=ROOT/"observations.sqlite3"
EVIDENCE=ROOT/"chain_fee_samples.sqlite3"
STATUS=ROOT/"chain_fee_probe_status.json"

def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def latest_mints(db=MARKET):
    con=sqlite3.connect(f"file:{Path(db).resolve()}?mode=ro",uri=True,timeout=5)
    try:
        rows=con.execute("""SELECT token_address,MAX(volume24_usd) AS vol
          FROM observations WHERE observed_at=(SELECT MAX(observed_at) FROM observations)
          AND dex IN ('pumpswap','pumpfun') GROUP BY token_address
          ORDER BY vol DESC LIMIT 12""").fetchall()
        return [r[0] for r in rows if valid_solana_pubkey(r[0])]
    finally: con.close()

def signatures_for(mint):
    if not valid_solana_pubkey(mint):
        raise ValueError("Invalid mint public key")
    payload=json.dumps({"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress",
                        "params":[mint,{"limit":3,"commitment":"finalized"}]}).encode()
    req=urllib.request.Request(RPC,data=payload,
              headers={"Content-Type":"application/json","User-Agent":"MissionC-readonly/1.0"},method="POST")
    with urllib.request.urlopen(req,timeout=12) as response:
        raw=response.read(200001)
    if len(raw)>200000: raise ValueError("Oversized Solana RPC signatures response")
    result=json.loads(raw)
    if not isinstance(result,dict) or "error" in result:
        raise ValueError("Solana RPC error: "+str(result.get("error"))[:120])
    items=result.get("result")
    if not isinstance(items,list):raise ValueError("Malformed signatures response")
    return [i["signature"] for i in items if isinstance(i,dict) and i.get("err") is None
            and valid_base58(i.get("signature"),80,90)]

def init_store(db=EVIDENCE):
    con=sqlite3.connect(db,timeout=10)
    con.execute("""CREATE TABLE IF NOT EXISTS samples(
       signature TEXT PRIMARY KEY,observed_at_utc TEXT NOT NULL,
       sample_mint TEXT NOT NULL, event_count INTEGER NOT NULL,
       report_json TEXT NOT NULL)""")
    con.commit()
    return con

def collect(market=MARKET,evidence=EVIDENCE,clock=None,fetch_signatures=signatures_for,
            audit_func=audit,idls=None):
    candidates=latest_mints(market)
    if not candidates:raise RuntimeError("No recent PumpSwap mints in current market snapshot")
    hour=int((clock or datetime.now(timezone.utc)).timestamp()//3600)
    mint=candidates[hour%len(candidates)]
    signatures=fetch_signatures(mint)
    con=init_store(evidence)
    added=fee_events=0
    try:
        schemas=idls if idls is not None else get_idls()
        for sig in signatures:
            if con.execute("SELECT 1 FROM samples WHERE signature=?",(sig,)).fetchone():
                continue
            report=audit_func(sig,idls=schemas)
            count=report.get("event_count",0)
            con.execute("INSERT INTO samples VALUES (?,?,?,?,?)",
                        (sig,utcnow(),mint,count,json.dumps(report,separators=(",",":"))))
            added+=1;fee_events+=count
        con.commit()
        total=con.execute("SELECT COUNT(*) FROM samples").fetchone()[0]
    finally:con.close()
    return {"observed_at_utc":utcnow(),"status":"success","sample_mint":mint,
            "candidate_pool_count":len(candidates),"signatures_returned":len(signatures),
            "new_signatures_stored":added,"new_fee_events_observed":fee_events,
            "stored_signatures":total,"sample_is_representative":False,
            "creator_revenue_to_user_verified":False,"money_spent_eur":0}

def main():
    try:
        report=collect()
        exit_code=0
    except Exception as exc:
        report={"observed_at_utc":utcnow(),"status":"error",
                "reason":f"{type(exc).__name__}: {str(exc)[:200]}",
                "creator_revenue_to_user_verified":False,"money_spent_eur":0}
        exit_code=2
    temporary=STATUS.with_suffix(".tmp")
    temporary.write_text(json.dumps(report,indent=2)+"\n")
    temporary.replace(STATUS)
    print(json.dumps(report),flush=True)
    return exit_code

if __name__=="__main__":
    raise SystemExit(main())
