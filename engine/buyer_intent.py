#!/usr/bin/env python3
"""Public buyer-intent scanner. Research only: no payments, outreach or paid APIs."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "engine/data/buyer_intent.json"
REPORT = ROOT / "engine/data/BUYER_INTENT.md"
QUERIES = [
    "is:issue is:open bounty in:title,body",
    'is:issue is:open "paid task" in:title,body',
    "is:issue is:open reward label:bounty",
]
PRICE = re.compile(r"(?:(?:[$€£]\s?\d{2,6}(?:[,.]\d{2})?|\b\d{2,6}\s?(?:USD|EUR|GBP)\b))", re.I)
PAYMENT = re.compile(r"\b(?:bounty|paid task|paid issue|reward|payment|commission|budget)\b", re.I)
STOP = re.compile(r"\b(?:casino|gambling|crypto pump|airdrop|token launch|exploit|phishing|adult content)\b", re.I)

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent":"FranckEyeResearch/1.0", "Accept":"application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=18) as response:
        return json.load(response)

def classify(issue, now):
    if "pull_request" in issue or issue.get("state") != "open":
        return None
    title = " ".join(str(issue.get("title") or "").split())[:200]
    body = str(issue.get("body") or "")[:6000]
    labels = [(v.get("name", "") if isinstance(v, dict) else str(v)).lower() for v in issue.get("labels", [])]
    content = title + " " + body
    if not title or STOP.search(content):
        return None
    price = PRICE.search(content)
    if not (PAYMENT.search(content) or any("bounty" in label or "paid" in label for label in labels)):
        return None
    url = issue.get("html_url", "")
    if not url.startswith("https://github.com/"):
        return None
    try:
        updated = dt.datetime.fromisoformat(issue["updated_at"].replace("Z", "+00:00"))
        if updated > now or (now - updated).days > 45:
            return None
    except (KeyError, ValueError, TypeError):
        return None
    score = (3 if price else 0) + (2 if any("bounty" in x for x in labels) else 0) + (1 if "paid" in content.lower() else 0)
    return {
        "id":hashlib.sha256(url.encode()).hexdigest()[:16],
        "title":title, "url":url, "updated_at":issue["updated_at"],
        "budget_mentioned":price.group(0) if price else None, "score":score,
        "state":"unverified_public_lead",
        "limitations":"Verify buyer, budget, eligibility, delivery scope, competition, escrow and payout timing before proceeding."
    }

def run(fetch=get, now=None, output=OUT, report=REPORT):
    now = now or dt.datetime.now(dt.timezone.utc)
    found = {}; errors = []
    for query in QUERIES:
        q = query + " updated:>=" + str((now-dt.timedelta(days=45)).date())
        url = "https://api.github.com/search/issues?" + urllib.parse.urlencode({"q":q,"per_page":50,"sort":"updated","order":"desc"})
        try:
            for item in fetch(url).get("items", []):
                candidate = classify(item, now)
                if candidate:
                    found[candidate["id"]] = candidate
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append({"query":query,"reason":str(exc)[:120]})
    ranked = sorted(found.values(), key=lambda v:(-v["score"], v["updated_at"], v["id"]))[:100]
    payload = {
        "updated_at":now.isoformat(), "source":"public GitHub issue search",
        "proven_sales":0, "candidates":ranked, "source_errors":errors,
        "notice":"Unverified research only; no authenticated buyers, payments, messages or Stripe access."
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines = ["# Buyer-intent discovery", "", "Run: "+now.isoformat(), "",
        "**Unverified public research; no paid customer has been established.**", "",
        "| Score | Open request | Posted budget |", "|---:|---|---|"]
    for item in ranked[:25]:
        title = item["title"].replace("|", "-").replace("]", "")
        lines.append(f'| {item["score"]} | [{title}]({item["url"]}) | {item["budget_mentioned"] or "Unknown"} |')
    if errors:
        lines.extend(["","## Source failures", *["- "+item["query"]+": "+item["reason"] for item in errors]])
    if not ranked:
        lines.extend(["","No matching active public requests discovered."])
    report.write_text("\n".join(lines)+"\n",encoding="utf-8")
    return payload

if __name__ == "__main__":
    result = run()
    print(json.dumps({"public_candidates":len(result["candidates"]),"source_errors":result["source_errors"]}))
