#!/usr/bin/env python3
"""Generate a static, shareable, read-only evidence demo from observed data. No wallet or telemetry."""
import argparse
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import sqlite3
from urllib.parse import urlsplit
from portable_evidence import export

ROOT=Path(__file__).resolve().parent
DB=ROOT/"observations.sqlite3"

def safe_text(x):
    return escape(str(x),quote=True)

def choose_tokens(db,limit=3):
    con=sqlite3.connect(f"file:{Path(db).resolve()}?mode=ro",uri=True)
    try:
        rows=con.execute("""SELECT token_address,MAX(symbol) AS symbol, COUNT(*) AS n,
          MAX(volume24_usd) AS volume, MAX(liquidity_usd) AS liquidity
          FROM observations GROUP BY token_address HAVING COUNT(*)>=2
          ORDER BY n DESC, volume DESC LIMIT ?""",(limit,)).fetchall()
        return [{"address":r[0],"symbol":r[1],"observations":r[2],"volume":r[3],"liquidity":r[4]} for r in rows]
    finally:con.close()

def landing(items,generated):
    cards=[]
    for i,x in enumerate(items,1):
        cards.append(f'<article><h2>Case {i}: {safe_text(x["symbol"])}</h2><p>{int(x["observations"])} snapshots observed; max reported liquidity ${float(x["liquidity"]):,.0f}. Values are third-party observations, not financial advice.</p><a href="case-{i}.html">Open evidence report</a></article>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Token Evidence — independent research demo</title>
<meta name="description" content="A transparent demonstration of source-linked historical token observations and their limitations.">
<style>body{{font:16px/1.6 system-ui,sans-serif;max-width:860px;margin:3rem auto;padding:0 1rem;color:#172438}}h1{{font-size:2rem}}article{{padding:1rem 1.4rem;margin:1rem 0;border:1px solid #dce2ea;border-radius:10px}}a{{color:#164c95}}.note{{background:#fff8e7;border-left:4px solid #ac761a;padding:1rem}}.muted{{color:#596679}}</style></head><body>
<h1>Token Evidence</h1><p>Source-linked, reproducible market observation reports for Solana tokens. No wallet connection, trading or paid access.</p>
<p class="note"><strong>Research demonstration only.</strong> The dataset is a nonrepresentative DEX Screener spotlight sample, not a comprehensive Pump.fun feed. Risk indicators have <strong>not</strong> been validated as predictions of future losses. Reported trading volume and token capitalization are not creator revenue.</p>
<h2>Explore actual observations</h2>{''.join(cards)}
<h2>What this does not establish</h2><p>Token safety, holder distribution, smart-contract permissions, future price, true organic demand, creator-fee payouts, customer demand or willingness to pay.</p>
<p class="muted">Generated {safe_text(generated)} UTC from previously collected third-party public data. Offline static HTML; no cookies, scripts, telemetry, signup form or payment collection. Source links are included inside each case.</p></body></html>"""

def build(db,out,limit=3):
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    items=choose_tokens(db,limit)
    if not items:raise ValueError("No tokens with repeated observations")
    for i,item in enumerate(items,1):
        export(item["address"],db,out/f"case-{i}.html")
    now=datetime.now(timezone.utc).isoformat(timespec="seconds")
    (out/"index.html").write_text(landing(items,now),encoding="utf-8")
    (out/"manifest.json").write_text(json.dumps({"generated_at_utc":now,"cases":len(items),"public_sources":"DEX Screener spotlight API","external_users_verified":0,"paid_customers_verified":0,"wallet_transactions":0},indent=2)+"\n",encoding="utf-8")
    return {"directory":str(out),"cases":len(items),"files":sorted(p.name for p in out.iterdir())}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--db",default=str(DB))
    p.add_argument("--out",default=str(ROOT/"public-demo"))
    args=p.parse_args()
    print(json.dumps(build(args.db,args.out)))
