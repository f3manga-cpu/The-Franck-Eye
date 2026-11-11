#!/usr/bin/env python3
"""Mission C: public market observation only. NO wallets, issuance, trading or transfers."""
import datetime as dt
import json
import sqlite3
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / "observations.sqlite3"
PROFILES = "https://api.dexscreener.com/token-profiles/latest/v1"
BOOSTS = "https://api.dexscreener.com/token-boosts/latest/v1"
TOKEN_PAIRS = "https://api.dexscreener.com/tokens/v1/solana/"

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Independent-ReadOnly-Research/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=12) as response:
        raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError("Oversized response")
        return json.loads(raw)

def utc_now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

def number(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0

def prepare(connection):
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("""CREATE TABLE IF NOT EXISTS cycles (
      id INTEGER PRIMARY KEY, observed_at TEXT NOT NULL, status TEXT NOT NULL,
      profiles_count INTEGER NOT NULL DEFAULT 0, solana_count INTEGER NOT NULL DEFAULT 0,
      pairs_count INTEGER NOT NULL DEFAULT 0, error TEXT NOT NULL DEFAULT '')""")
    connection.execute("""CREATE TABLE IF NOT EXISTS observations (
      observed_at TEXT NOT NULL, token_address TEXT NOT NULL, symbol TEXT NOT NULL,
      name TEXT NOT NULL, dex TEXT NOT NULL, pair_url TEXT NOT NULL,
      volume24_usd REAL NOT NULL, liquidity_usd REAL NOT NULL, buys24 INTEGER NOT NULL,
      sells24 INTEGER NOT NULL, boosts REAL NOT NULL, market_cap_usd REAL NOT NULL,
      PRIMARY KEY (observed_at, token_address))""")
    connection.commit()

def interpret(profiles, boosts, pairs):
    if not isinstance(profiles, list) or not isinstance(boosts, list) or not isinstance(pairs, list):
        raise ValueError("Bad source schema")
    ps = {}
    for x in profiles:
        if not isinstance(x, dict) or x.get("chainId") != "solana":
            continue
        address = x.get("tokenAddress", "")
        if isinstance(address, str) and 30 <= len(address) <= 60:
            ps[address] = x
    bs = {}
    for x in boosts:
        if isinstance(x, dict) and x.get("chainId") == "solana":
            a = x.get("tokenAddress")
            if a:
                bs[a] = max(bs.get(a, 0.0), number(x.get("amount")))
    pair_by_address = {}
    for pair in pairs:
        if not isinstance(pair, dict) or pair.get("chainId") != "solana":
            continue
        base = pair.get("baseToken") or {}
        address = base.get("address")
        if address not in ps:
            continue
        prior = pair_by_address.get(address)
        if prior is None or number((pair.get("liquidity") or {}).get("usd")) > number((prior.get("liquidity") or {}).get("usd")):
            pair_by_address[address] = pair
    output = []
    for address in ps:
        x = pair_by_address.get(address, {})
        base = x.get("baseToken") or {}
        txs = (x.get("txns") or {}).get("h24") or {}
        output.append({
            "token_address": address, "symbol": str(base.get("symbol") or "unknown")[:30],
            "name": str(base.get("name") or "unknown")[:90], "dex": str(x.get("dexId") or "unknown")[:45],
            "pair_url": str(x.get("url") or ps[address].get("url") or "")[:400],
            "volume24_usd": number((x.get("volume") or {}).get("h24")),
            "liquidity_usd": number((x.get("liquidity") or {}).get("usd")),
            "buys24": int(number(txs.get("buys"))), "sells24": int(number(txs.get("sells"))),
            "boosts": bs.get(address, 0.0), "market_cap_usd": number(x.get("marketCap"))
        })
    return output

def cycle():
    observed_at = utc_now()
    conn = sqlite3.connect(DB, timeout=20)
    prepare(conn)
    n_profiles = n_sol = n_pairs = 0
    try:
        profiles = get_json(PROFILES)
        boosts = get_json(BOOSTS)
        n_profiles = len(profiles)
        addresses = list(dict.fromkeys(
            x.get("tokenAddress") for x in profiles
            if isinstance(x, dict) and x.get("chainId") == "solana"
            and isinstance(x.get("tokenAddress"), str)
            and 30 <= len(x["tokenAddress"]) <= 60
        ))[:30]
        n_sol = len(addresses)
        pairs = get_json(TOKEN_PAIRS + ",".join(addresses)) if addresses else []
        n_pairs = len(pairs)
        items = interpret(profiles, boosts, pairs)
        for x in items:
            conn.execute("""INSERT OR REPLACE INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (observed_at, x["token_address"], x["symbol"], x["name"], x["dex"],
                          x["pair_url"], x["volume24_usd"], x["liquidity_usd"], x["buys24"],
                          x["sells24"], x["boosts"], x["market_cap_usd"]))
        conn.execute("INSERT INTO cycles(observed_at,status,profiles_count,solana_count,pairs_count) VALUES (?,?,?,?,?)",
                     (observed_at, "success", n_profiles, n_sol, n_pairs))
        conn.execute("DELETE FROM observations WHERE observed_at < ?", ((dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=14)).isoformat(timespec="seconds"),))
        conn.commit()
        # Ranking for review only: explicitly NOT a buy signal, safety or revenue estimate.
        ranked = sorted(items, key=lambda x:(x["volume24_usd"], x["liquidity_usd"]), reverse=True)
        output = {"observed_at": observed_at, "status": "success", "profiles_seen": n_profiles,
                  "solana_profiles": n_sol, "pairs_returned": n_pairs, "listed_market_records": len(items),
                  "top_by_observed_volume": ranked[:8],
                  "warning": "DEX Screener spotlight profiles are selected, NOT a full market sample. Boosts are paid promotion, not organic demand. Neither liquidity nor market cap is creator income. Read-only; no money spent."}
        (ROOT/"health.json").write_text(json.dumps(output, indent=2, ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps({k:output[k] for k in ("observed_at","status","profiles_seen","solana_profiles","pairs_returned","listed_market_records")}))
        return True
    except Exception as ex:
        error = type(ex).__name__+": "+str(ex)[:300]
        conn.execute("INSERT INTO cycles(observed_at,status,profiles_count,solana_count,pairs_count,error) VALUES (?,?,?,?,?,?)",
                     (observed_at, "error", n_profiles, n_sol, n_pairs, error))
        conn.commit()
        (ROOT/"health.json").write_text(json.dumps({"observed_at":observed_at,"status":"error","error":error},indent=2)+"\n")
        print(json.dumps({"observed_at": observed_at,"status":"error","error":error}),file=sys.stderr)
        return False
    finally:
        conn.close()

def status():
    if not (ROOT/"health.json").exists():
        return {"status":"never_run"}
    return json.loads((ROOT/"health.json").read_text())

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv)>1 else "once"
    if cmd == "once":
        raise SystemExit(0 if cycle() else 1)
    if cmd == "status":
        x=status()
        print(json.dumps({k:x.get(k) for k in ("observed_at","status","profiles_seen","solana_profiles","pairs_returned","listed_market_records","error")}))
    elif cmd == "loop":
        while True:
            cycle()
            time.sleep(900)
    else:
        raise SystemExit("Usage: public_market_watch.py [once|status|loop]")
