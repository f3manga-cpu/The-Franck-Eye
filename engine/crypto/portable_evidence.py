#!/usr/bin/env python3
"""Create a portable, self-contained, source-linked evidence report. No network or transactions."""
import argparse
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit
from evidence_report import report

def html_report(item):
    if not item:
        raise ValueError("No observed evidence")
    esc=lambda x:escape(str(x),quote=True)
    url=item["evidence"]["source_url"]
    parts=urlsplit(url)
    valid=(parts.scheme=="https" and parts.hostname in ("dexscreener.com","www.dexscreener.com"))
    source=f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">View original market source</a>' if valid else "Source URL unavailable or not allowlisted"
    first=item["first_observation"]; last=item["last_observation"]
    rows=[("Token",item["symbol_latest"]),("Chain",item["chain"]),("Address",item["token_address"]),
          ("First seen (UTC)",item["first_observed_utc"]),("Last seen (UTC)",item["last_observed_utc"]),
          ("Observed snapshots",item["observation_count"]),
          ("First reported liquidity (USD)",f'{first["liquidity_usd"]:,.2f}'),
          ("Last reported liquidity (USD)",f'{last["liquidity_usd"]:,.2f}'),
          ("Latest rolling 24h volume (USD)",f'{last["volume24_usd"]:,.2f}'),
          ("Paid boost reported",last["paid_boost_amount_reported"])]
    table="".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k,v in rows)
    cautions="".join(f"<li>{esc(x)}</li>" for x in item["caution_indicators"]) or "<li>No listed caution flags; this does not imply safety.</li>"
    limits="".join(f"<li>{esc(x)}</li>" for x in item["limitations"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Independent token evidence — {esc(item['symbol_latest'])}</title>
<style>body{{font:16px system-ui,sans-serif;max-width:820px;margin:3rem auto;padding:0 1rem;color:#182533;line-height:1.55}}h1{{font-size:1.7rem}}.sub{{color:#5b6674}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;border-bottom:1px solid #ddd;padding:.65rem;overflow-wrap:anywhere}}th{{width:48%}}.warning{{padding:1rem;border-left:4px solid #a56a16;background:#fff8e9}}li{{margin:.4rem 0}}a{{color:#174b90}}</style></head><body>
<h1>Independent token evidence: {esc(item['symbol_latest'])}</h1><p class="sub">Generated {esc(item['generated_at_utc'])} · Snapshot data from DEX Screener</p>
<p class="warning"><strong>Not investment advice or a fraud verdict.</strong> This report contains third-party observations from a nonrepresentative spotlight sample. No wallet security, holder distribution, contract behavior, creator fees or revenue were verified.</p>
<h2>Observed evidence</h2><table>{table}</table><p>{source}</p><h2>Indicators to investigate</h2><ul>{cautions}</ul>
<h2>Limitations</h2><ul>{limits}</ul><p class="sub">Offline, self-contained HTML report. No JavaScript, tracking, external fonts, remote images, trading or wallet connections.</p></body></html>"""

def export(token, db, output):
    item=report(token,db)
    if item is None:
        raise ValueError("Token has no recorded observations")
    out=Path(output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(html_report(item),encoding="utf-8")
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--token",required=True)
    p.add_argument("--db",default=str(Path(__file__).resolve().parent/"observations.sqlite3"))
    p.add_argument("--out",required=True)
    args=p.parse_args()
    print(export(args.token,args.db,args.out))
