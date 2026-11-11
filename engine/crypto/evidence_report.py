"""Source-linked due diligence reports; no investment advice or fraud verdicts."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

def report(token, db):
    if not isinstance(token,str) or len(token)>90 or not token or not token.isascii() or not token.isalnum():
        raise ValueError("Invalid token identifier")
    if not Path(db).exists():
        return None
    con=sqlite3.connect(f"file:{Path(db).resolve()}?mode=ro",uri=True,timeout=4)
    con.row_factory=sqlite3.Row
    try:
        rows=con.execute("""SELECT observed_at,token_address,symbol,name,dex,pair_url,volume24_usd,
            liquidity_usd,buys24,sells24,boosts,market_cap_usd FROM observations
            WHERE token_address=? ORDER BY observed_at ASC LIMIT 1000""",(token,)).fetchall()
        if not rows:return None
        first,last=dict(rows[0]),dict(rows[-1])
        def safe(x):
            return {"observed_at":x["observed_at"],"volume24_usd":x["volume24_usd"],
                    "liquidity_usd":x["liquidity_usd"],"buys24":x["buys24"],
                    "sells24":x["sells24"],"paid_boost_amount_reported":x["boosts"]}
        flags=[]
        if last["liquidity_usd"]<=0:flags.append("liquidity-not-reported")
        elif last["liquidity_usd"]<10000:flags.append("thin-reported-liquidity")
        if last["boosts"]>0:flags.append("paid-promotion-reported")
        if first["liquidity_usd"]>0 and last["liquidity_usd"]<first["liquidity_usd"]*0.5:
            flags.append("reported-liquidity-down-more-than-half-since-first-observation")
        return {"schema":"creator-observatory-evidence-v1","generated_at_utc":datetime.now(timezone.utc).isoformat(),
                "chain":"solana","token_address":token,"symbol_latest":last["symbol"],
                "name_latest":last["name"],"observation_count":len(rows),
                "first_observed_utc":first["observed_at"],"last_observed_utc":last["observed_at"],
                "first_observation":safe(first),"last_observation":safe(last),
                "caution_indicators":flags,
                "evidence":{"source":"DEX Screener public API","source_url":last["pair_url"],
                            "market_api":"https://api.dexscreener.com/token-profiles/latest/v1",
                            "source_type":"third-party reported market data; unverified on-chain"},
                "limitations":["Biased promoted/latest spotlight sample, not representative of all tokens.",
                               "Snapshot 24h volume is a rolling window; do not sum snapshots.",
                               "Boosts reflect paid promotion, not organic demand.",
                               "Reported liquidity is not proof of recoverable value.",
                               "No on-chain wallet/holder/contract/security verification performed.",
                               "Caution indicators are not predictive risk scores or allegations of fraud.",
                               "No creator fee, revenue, transaction, payout or bank settlement verified."],
                "investment_recommendation":False,"creator_revenue_verified":False}
    finally:con.close()
