#!/usr/bin/env python3
"""Independent spotlight-cohort analysis; observational, no price or creator income claims."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parent
DB=ROOT/"observations.sqlite3"

def report(db=DB, min_hours=0.5):
    c=sqlite3.connect(f"file:{Path(db).resolve()}?mode=ro",uri=True)
    c.row_factory=sqlite3.Row
    try:
        cycles=[dict(r) for r in c.execute("SELECT observed_at,status FROM cycles ORDER BY id")]
        successful=[x["observed_at"] for x in cycles if x["status"]=="success"]
        observations=[dict(r) for r in c.execute("SELECT observed_at,token_address,symbol,volume24_usd,liquidity_usd,boosts FROM observations ORDER BY observed_at")]
        unique={x["token_address"] for x in observations}
        if not successful:
            return {"status":"no_successful_cycles","cycles":len(cycles),"unique_tokens":0}
        first=min(successful);last=max(successful)
        hours=(dt.datetime.fromisoformat(last)-dt.datetime.fromisoformat(first)).total_seconds()/3600
        grouped={}
        for x in observations:
            grouped.setdefault(x["token_address"],[]).append(x)
        # Profiles are a biased spotlight feed: repeat appearances are NOT price returns or organic demand.
        repeated=[(a,rows) for a,rows in grouped.items() if len({x["observed_at"] for x in rows})>=2]
        long_span=[]
        for address,rows in repeated:
            a,b=rows[0],rows[-1]
            gap=(dt.datetime.fromisoformat(b["observed_at"])-dt.datetime.fromisoformat(a["observed_at"])).total_seconds()/3600
            if gap>=min_hours:
                long_span.append({
                    "token_address":address,"symbol":str(b["symbol"])[:30],
                    "first_seen":a["observed_at"],"last_seen":b["observed_at"],
                    "observations":len(rows),"span_hours":round(gap,2),
                    "first_volume24_usd":round(a["volume24_usd"],2),
                    "last_volume24_usd":round(b["volume24_usd"],2),
                    "first_liquidity_usd":round(a["liquidity_usd"],2),
                    "last_liquidity_usd":round(b["liquidity_usd"],2),
                    "ever_boosted":any(x["boosts"]>0 for x in rows)})
        return {"status":"success","first_cycle_utc":first,"last_cycle_utc":last,
                "coverage_hours":round(hours,2),"successful_cycles":len(successful),
                "failed_cycles":len(cycles)-len(successful),
                "observations":len(observations),"unique_tokens":len(unique),
                "repeated_spotlight_tokens":len(repeated),
                "repeated_fraction_of_unique":round(len(repeated)/len(unique),4) if unique else None,
                "tokens_spanning_min_hours":len(long_span),"min_span_hours":min_hours,
                "long_span_examples":sorted(long_span,key=lambda x:x["span_hours"],reverse=True)[:10],
                "interpretation":"Repeated spotlight listing only. 24h volume windows overlap; DO NOT sum them. Appearance frequency is not survival, returns, safety, creator fees, or user demand. A token absent from the feed may still trade.",
                "creator_fees_verified":False,"user_adoption_verified":False}
    finally:c.close()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",default=str(DB))
    p.add_argument("--min-hours",type=float,default=0.5)
    p.add_argument("--output",default="")
    args=p.parse_args()
    if args.min_hours<0:p.error("min-hours must be >= 0")
    x=report(args.db,args.min_hours)
    data=json.dumps(x,indent=2,ensure_ascii=False)+"\n"
    if args.output:Path(args.output).write_text(data)
    print(data,end="")

if __name__=="__main__":main()
