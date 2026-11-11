#!/usr/bin/env python3
"""Read-only creator-market observatory: local JSON and HTML, no wallet/trading."""
import argparse
from datetime import datetime, timezone
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from cohort_analysis import report as cohort_report
from screening import screen as screening_report
from forward_validation import evaluate as forward_evaluate
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent
DB=ROOT/"observations.sqlite3"

def snapshot(db=DB):
    if not Path(db).is_file():
        return {"status":"no_data","cycles":0,"assets":[]}
    con=sqlite3.connect(f"file:{Path(db).resolve()}?mode=ro",uri=True,timeout=4)
    con.row_factory=sqlite3.Row
    try:
        last=con.execute("SELECT observed_at,status,error FROM cycles ORDER BY id DESC LIMIT 1").fetchone()
        if not last:
            return {"status":"no_data","cycles":0,"assets":[]}
        count=con.execute("SELECT COUNT(*) FROM cycles").fetchone()[0]
        latest=con.execute("SELECT MAX(observed_at) FROM observations").fetchone()[0]
        rows=con.execute("""SELECT token_address,symbol,name,dex,pair_url,volume24_usd,liquidity_usd,
             buys24,sells24,boosts,market_cap_usd FROM observations
             WHERE observed_at=? ORDER BY volume24_usd DESC LIMIT 30""",(latest,)).fetchall() if latest else []
        assets=[]
        for r in rows:
            x=dict(r)
            v=x["volume24_usd"]; l=x["liquidity_usd"]; trades=x["buys24"]+x["sells24"]
            x["volume_liquidity_ratio"]=round(v/l,2) if l>0 else None
            x["buy_trade_fraction"]=round(x["buys24"]/trades,3) if trades else None
            flags=[]
            if l<10000: flags.append("thin-liquidity")
            if l==0: flags.append("liquidity-not-reported")
            if l>0 and v/l>20: flags.append("high-turnover-relative-to-liquidity")
            if x["boosts"]>0: flags.append("paid-boost-observed")
            if trades==0: flags.append("no-trade-count")
            x["cautions"]=flags
            assets.append(x)
        dt=datetime.fromisoformat(last["observed_at"])
        age=max(0,(datetime.now(timezone.utc)-dt).total_seconds())
        return {"status":last["status"],"last_cycle_utc":last["observed_at"],
                "last_error":last["error"],"age_seconds":round(age),
                "stale":age>2100,"cycles":count,"assets":assets,
                "latest_observation_utc":latest,
                "method":"Only DEX Screener promoted/latest profiles, not a random sample or pump.fun creator earnings.",
                "revenue_verified":False,"financial_transactions":0}
    finally:con.close()

def page(data):
    rows=[]
    for a in data["assets"]:
        url=a["pair_url"]
        if urlsplit(url).scheme not in ("https","http"):url=""
        link=f'<a href="{escape(url,quote=True)}" rel="noopener noreferrer" target="_blank">Source</a>' if url else "—"
        ratio="n/a" if a["volume_liquidity_ratio"] is None else str(a["volume_liquidity_ratio"])
        rows.append("<tr><td>"+escape(a["symbol"])+"</td><td>"+escape(a["name"])+"</td><td>"+escape(a["dex"])+"</td><td>"+f'{a["volume24_usd"]:,.0f}'+"</td><td>"+f'{a["liquidity_usd"]:,.0f}'+"</td><td>"+ratio+"</td><td>"+escape(", ".join(a["cautions"]) or "—")+"</td><td>"+link+"</td></tr>")
    status=escape(data["status"]);updated=escape(str(data.get("last_cycle_utc","unknown")))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Creator Market Observatory — Research only</title><style>
body{{font:15px system-ui,sans-serif;max-width:1200px;margin:30px auto;padding:0 18px;color:#1b2430;background:#fafbfd}}
h1{{font-size:1.6rem}} .muted{{color:#596777}} .notice{{border-left:4px solid #a45b0b;padding:12px;background:#fff8e8}}
table{{border-collapse:collapse;width:100%;font-size:13px}}th,td{{padding:9px;text-align:left;border-bottom:1px solid #d9e0e8}}
th{{background:#edf2f7}}.scroll{{overflow-x:auto}}a{{color:#1250a1}}
</style></head><body><h1>Creator Market Observatory</h1>
<p class="muted">Last cycle: {updated} UTC · State: {status} · Cycles: {data["cycles"]} · Stale: {data.get("stale",True)}</p>
<p class="notice"><strong>Independent research, not a trading recommendation.</strong> This is a biased spotlight sample. DEX volume, token market capitalization and promotional boosts are not creator earnings. No trades, wallets, tokens, or payouts are involved. Risk flags are heuristics, not fraud findings.</p>
<h2>Observed spotlight tokens ({len(data["assets"])})</h2><div class="scroll"><table><thead><tr><th>Symbol</th><th>Name</th><th>DEX</th><th>24h volume USD</th><th>Liquidity USD</th><th>Vol / liq</th><th>Caution flags</th><th>Data</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p class="muted">Read-only public DEX Screener data. <a href="/api/summary">JSON API</a> · <a href="/api/cohorts">Longitudinal cohort analysis</a> · <a href="/api/screening">Historical caution screening</a> · <a href="/api/validation">Forward signal audit</a>. Last observation: {escape(str(data.get("latest_observation_utc","unknown")))}</p></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path=self.path.split("?",1)[0]
        if path not in ("/","/api/summary","/api/cohorts","/api/screening","/api/validation","/healthz"):
            self.send_error(404);return
        data=snapshot()
        if path=="/healthz":
            code=200 if data["status"]=="success" and not data.get("stale",True) else 503
            payload=json.dumps({"status":data["status"],"stale":data.get("stale",True)}).encode()
            typ="application/json"
        elif path=="/api/cohorts":
            code=200;payload=json.dumps(cohort_report(),ensure_ascii=False).encode();typ="application/json"
        elif path=="/api/screening":
            code=200;payload=json.dumps(screening_report(),ensure_ascii=False).encode();typ="application/json"
        elif path=="/api/validation":
            code=200;payload=json.dumps(forward_evaluate(),ensure_ascii=False).encode();typ="application/json"
        elif path=="/api/summary":
            code=200;payload=json.dumps(data,ensure_ascii=False).encode();typ="application/json"
        else:
            code=200;payload=page(data).encode();typ="text/html; charset=utf-8"
        self.send_response(code)
        self.send_header("Content-Type",typ)
        self.send_header("Content-Length",str(len(payload)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Content-Security-Policy","default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers();self.wfile.write(payload)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--port",type=int,default=8765)
    p.add_argument("--host",default="127.0.0.1")
    p.add_argument("--once",action="store_true")
    args=p.parse_args()
    if args.once:
        x=snapshot();print(json.dumps({k:x[k] for k in ("status","cycles","stale","revenue_verified")}))
        return
    if args.host not in ("127.0.0.1","::1","localhost"):
        p.error("Public binding prohibited until separate security/release approval")
    server=ThreadingHTTPServer((args.host,args.port),Handler)
    print("Read-only dashboard at http://127.0.0.1:"+str(args.port),flush=True)
    server.serve_forever()

if __name__=="__main__":main()
