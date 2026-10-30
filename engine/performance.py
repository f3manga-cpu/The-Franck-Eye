#!/usr/bin/env python3
"""Performance engine: real-source discovery, deduplication, ranked candidates, evidence ledger.
No payments, trading, outbound messages, or secrets. Python standard library only.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "engine" / "data"
OPPORTUNITIES = DATA / "opportunities.json"
EVENTS = DATA / "events.jsonl"
SOURCES = [
    ("creator monetization", "https://hn.algolia.com/api/v1/search_by_date?query=creator%20monetization&tags=story&hitsPerPage=40"),
    ("payment platform", "https://hn.algolia.com/api/v1/search_by_date?query=payment%20platform&tags=story&hitsPerPage=40"),
    ("digital products", "https://hn.algolia.com/api/v1/search_by_date?query=digital%20products&tags=story&hitsPerPage=40"),
    ("marketplace launch", "https://hn.algolia.com/api/v1/search_by_date?query=marketplace%20launch&tags=story&hitsPerPage=40"),
]
WORDS = {
    "creator": 3, "monetiz": 4, "marketplace": 4, "payments": 2,
    "stripe": 2, "revenue": 3, "affiliate": 2, "launch": 1,
    "distribution": 4, "api": 2, "fee": 1, "sales": 2, "customer": 1,
}
BLACKLIST = {"gambling", "ponzi", "rug pull", "exploit", "hacking"}
EVENT_TYPES = {"hypothesis", "experiment_started", "published", "lead", "reply", "order", "payment_confirmed", "refund", "cost", "closed"}
def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
def read_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))
def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()[:400]
def rank(text):
    t = text.lower()
    if any(k in t for k in BLACKLIST):
        return -100
    return sum(weight for word,weight in WORDS.items() if word in t)
def discover(fetch=None):
    if fetch is None:
        def fetch(url):
            request = urllib.request.Request(url, headers={"User-Agent": "OpportunityResearchBot/1.0 (+public research)"})
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.load(response)
    saved = read_json(OPPORTUNITIES, {"candidates": []})
    prior = {item["id"]:item for item in saved["candidates"]}
    errors=[]
    today=dt.datetime.now(dt.timezone.utc)
    for theme, url in SOURCES:
        try:
            hits=fetch(url).get("hits", [])
        except (OSError,ValueError,KeyError) as e:
            errors.append({"theme":theme,"error":str(e)[:120]})
            continue
        for hit in hits:
            title=clean(hit.get("title"))
            link=hit.get("url") or ("https://news.ycombinator.com/item?id="+str(hit.get("objectID","")))
            published=hit.get("created_at") or ""
            try:
                age=(today-dt.datetime.fromisoformat(published.replace("Z","+00:00"))).days
            except ValueError:
                continue
            if not title or not link.startswith("https://") or age<0 or age>30:
                continue
            score=rank(title+" "+clean(hit.get("story_text")))
            if score<=0:
                continue
            identifier=hashlib.sha256(link.encode()).hexdigest()[:16]
            if identifier not in prior:
                prior[identifier]={
                    "id":identifier,"first_seen":now(),"date":published,
                    "theme":theme,"title":title,"url":link,
                    "score":score,"status":"research_only",
                    "evidence":"HN submission; commercial terms and revenue NOT verified",
                    "next_validation":"Check actual payment mechanics, fees, eligibility, unit economics and acquisition source"
                }
    candidates=sorted(prior.values(),key=lambda v:(-v["score"],v["first_seen"],v["id"]))[:250]
    atomic_write(OPPORTUNITIES,json.dumps({"updated_at":now(),"candidates":candidates,"errors":errors},ensure_ascii=False,indent=2)+"\n")
    lines=["# Opportunity research queue","",f"Updated (UTC): {now()}","",
           "**These are leads for research, not verified opportunities, income claims or recommendations.**","",
           "| Score | Research lead | Source | Next step |","|---:|---|---|---|"]
    for entry in candidates[:20]:
        title=entry["title"].replace("|","-").replace("[","").replace("]","")
        lines.append(f'| {entry["score"]} | [{title}]({entry["url"]}) | {entry["theme"]} | Verify fees, eligibility, demand |')
    if errors:
        lines.extend(["","## Source failures",*["- "+e["theme"]+": "+e["error"] for e in errors]])
    atomic_write(DATA/"RESEARCH.md","\n".join(lines)+"\n")
    return {"candidates":len(candidates),"errors":errors}
def record(kind, experiment, amount=0, currency="EUR", evidence="", reference=""):
    if kind not in EVENT_TYPES:
        raise ValueError("unsupported event type")
    if amount<0 or currency!="EUR":
        raise ValueError("amount must be non-negative EUR cents")
    if kind in {"payment_confirmed","refund","cost"} and (amount<=0 or not evidence or not reference):
        raise ValueError("money events require positive EUR cents, evidence, and unique reference")
    if kind not in {"payment_confirmed","refund","cost"} and amount:
        raise ValueError("only money events may carry amounts")
    event={"at":now(),"type":kind,"experiment":experiment,"amount_cents":amount,
           "currency":currency,"evidence":evidence,"reference":reference}
    DATA.mkdir(parents=True,exist_ok=True)
    old=EVENTS.read_text(encoding="utf-8").splitlines() if EVENTS.exists() else []
    if reference and any(json.loads(s).get("reference")==reference and json.loads(s).get("type")==kind for s in old if s.strip()):
        raise ValueError("duplicate event reference and type")
    with EVENTS.open("a",encoding="utf-8") as f:
        f.write(json.dumps(event,ensure_ascii=False)+"\n")
    return event
def report():
    events=[json.loads(s) for s in EVENTS.read_text(encoding="utf-8").splitlines() if s.strip()] if EVENTS.exists() else []
    totals={k:sum(e["amount_cents"] for e in events if e["type"]==k) for k in ("payment_confirmed","refund","cost")}
    counts={k:sum(e["type"]==k for e in events) for k in EVENT_TYPES}
    net=totals["payment_confirmed"]-totals["refund"]-totals["cost"]
    return {"gross_confirmed_eur":totals["payment_confirmed"]/100,
            "net_after_recorded_refunds_costs_eur":net/100,
            "counts":counts,"ledger_events":len(events),
            "caution":"Manually supplied evidence; does NOT independently verify Stripe payments"}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="action",required=True)
    sub.add_parser("discover");sub.add_parser("report")
    rec=sub.add_parser("record")
    rec.add_argument("kind",choices=sorted(EVENT_TYPES))
    rec.add_argument("--experiment",required=True)
    rec.add_argument("--amount-cents",type=int,default=0)
    rec.add_argument("--evidence",default="")
    rec.add_argument("--reference",default="")
    args=parser.parse_args()
    if args.action=="discover": result=discover()
    elif args.action=="report": result=report()
    else: result=record(args.kind,args.experiment,args.amount_cents,evidence=args.evidence,reference=args.reference)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
