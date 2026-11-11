#!/usr/bin/env python3
"""Read-only token screening evidence: conservative, reproducible historical red flags.
No fraud accusation, investment advice, creator income claim, or token launch.
"""
import json
import sqlite3
from pathlib import Path
DB=Path(__file__).resolve().parent/"observations.sqlite3"

def screen(db=DB, min_points=2):
    if min_points<2: raise ValueError("min_points must be >= 2")
    if not Path(db).is_file(): return {"status":"no_data","candidates":[]}
    con=sqlite3.connect("file:"+str(Path(db).resolve())+"?mode=ro",uri=True)
    con.row_factory=sqlite3.Row
    try:
        rows=con.execute("""SELECT observed_at,token_address,symbol,liquidity_usd,
            volume24_usd,boosts,buys24,sells24 FROM observations
            ORDER BY token_address,observed_at""").fetchall()
        grouped={}
        for r in rows: grouped.setdefault(r["token_address"],[]).append(dict(r))
        out=[]
        for addr,items in grouped.items():
            if len(items)<min_points:continue
            first,last=items[0],items[-1]
            peak=max(x["liquidity_usd"] for x in items)
            floor=min(x["liquidity_usd"] for x in items)
            decline=(peak-last["liquidity_usd"])/peak if peak>0 else None
            flags=[]
            if peak==0:flags.append("liquidity-unavailable")
            if decline is not None and decline>=0.8:flags.append("observed-liquidity-down-80pct-from-sample-peak")
            if peak>0 and floor/peak<=0.2:flags.append("observed-liquidity-trough-below-20pct-of-sample-peak")
            if any(x["boosts"]>0 for x in items):flags.append("paid-promotion-observed")
            if last["liquidity_usd"]>0 and last["volume24_usd"]/last["liquidity_usd"]>20:
                flags.append("24h-volume-to-current-liquidity-over-20")
            out.append({"token_address":addr,"symbol":last["symbol"],
                "observations":len(items),"first_seen":first["observed_at"],"last_seen":last["observed_at"],
                "peak_liquidity_usd":round(peak,2),"latest_liquidity_usd":round(last["liquidity_usd"],2),
                "decline_from_observed_peak_pct":round(100*decline,1) if decline is not None else None,
                "cautions":flags,"caution_count":len(flags)})
        out.sort(key=lambda x:(-x["caution_count"],-(x["decline_from_observed_peak_pct"] or 0),x["token_address"]))
        return {"status":"success","sampled_assets":len(grouped),"assets_with_repeats":len(out),
            "flagged_assets":sum(bool(x["cautions"]) for x in out),
            "methodology":"Historical snapshots of a promotional/latest-profile convenience sample. Peak is the observed peak only, not lifetime peak. 24h volume is rolling, NOT volume generated between snapshots. Missing liquidity is not proof of zero. Flags are heuristics, NOT evidence of fraud or predictions. No on-chain verification.",
            "candidates":out}
    finally:con.close()

if __name__=="__main__":print(json.dumps(screen(),ensure_ascii=False))
