#!/usr/bin/env python3
"""Prospective, no-lookahead audit of screening cautions in spotlight observations.

A paired outcome requires an observation at least horizon_minutes after the signal.
No interpolation or price-return prediction; liquidity is a reported market snapshot.
"""
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import json
import sqlite3

DB=Path(__file__).resolve().parent/"observations.sqlite3"

def parse_time(value):
    return datetime.fromisoformat(value).timestamp()

def assess(rows,horizon_minutes=30,min_liquidity=1):
    if horizon_minutes<=0: raise ValueError("horizon must be positive")
    groups=defaultdict(list)
    for r in rows:
        x=dict(r)
        groups[x["token_address"]].append(x)
    evaluations=[]
    skipped_no_followup=0
    for address, observations in groups.items():
        items=sorted(observations,key=lambda x:parse_time(x["observed_at"]))
        # Only first signal per asset to avoid repeated correlated positives.
        if len(items)<2:continue
        first=items[0]
        if first["liquidity_usd"] is None or first["liquidity_usd"]<min_liquidity:
            continue
        first_time=parse_time(first["observed_at"])
        followup=next((x for x in items[1:] if parse_time(x["observed_at"])-first_time>=horizon_minutes*60 and x["liquidity_usd"] is not None),None)
        if followup is None:
            skipped_no_followup+=1
            continue
        # All features are from the FIRST observation only. No historical peak lookahead.
        ratio=first["volume24_usd"]/first["liquidity_usd"] if first["liquidity_usd"]>0 else None
        flagged=bool((first["boosts"] or 0)>0 or (ratio is not None and ratio>20) or first["liquidity_usd"]<10000)
        drop=(first["liquidity_usd"]-followup["liquidity_usd"])/first["liquidity_usd"]
        evaluations.append({"token_address":address,"signal_at":first["observed_at"],
          "followup_at":followup["observed_at"],"initial_liquidity_usd":round(first["liquidity_usd"],2),
          "followup_liquidity_usd":round(followup["liquidity_usd"],2),
          "relative_change_pct":round(-100*drop,2),"flagged_at_signal":flagged,
          "liquidity_decline_50pct":drop>=0.5})
    n=len(evaluations)
    positives=[x for x in evaluations if x["flagged_at_signal"]]
    negatives=[x for x in evaluations if not x["flagged_at_signal"]]
    def rate(group):
        return round(sum(x["liquidity_decline_50pct"] for x in group)/len(group),4) if group else None
    return {"status":"success","horizon_minutes":horizon_minutes,
      "eligible_assets":n,"flagged_assets":len(positives),"unflagged_assets":len(negatives),
      "flagged_decline_rate":rate(positives),"unflagged_decline_rate":rate(negatives),
      "baseline_decline_rate":rate(evaluations),"skipped_without_followup":skipped_no_followup,
      "evidence_sufficient":len(positives)>=20 and len(negatives)>=20,
      "methodology":"First-observation-only cautions, first later observation >= horizon, one observation pair per asset. Requires reported initial liquidity >= 1 USD. The 50% outcome is change in reported pool liquidity, not fraud, investor loss or price return. Spotlight-only survivorship and selection bias; missing future records excluded and counted. Never infer causality or predictive usefulness when either cohort is small.",
      "examples":evaluations[:10]}

def evaluate(db=DB,horizon_minutes=30):
    if not Path(db).exists():return {"status":"no_data"}
    con=sqlite3.connect("file:"+str(Path(db).resolve())+"?mode=ro",uri=True)
    con.row_factory=sqlite3.Row
    try:
        rows=con.execute("""SELECT observed_at,token_address,liquidity_usd,volume24_usd,boosts
          FROM observations ORDER BY token_address,observed_at""").fetchall()
        return assess(rows,horizon_minutes=horizon_minutes)
    finally:con.close()

if __name__=="__main__":
    print(json.dumps(evaluate(),ensure_ascii=False))
