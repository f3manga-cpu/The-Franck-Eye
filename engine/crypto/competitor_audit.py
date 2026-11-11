#!/usr/bin/env python3
"""Public competitor evidence, not proof of customer demand. No outreach or publishing."""
import datetime as dt
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEARCHES = {
    "token_risk": "solana token risk scanner",
    "creator_analytics": "pumpfun analytics",
    "rug_check": "solana rug checker",
    "solana_research": "solana token analytics",
}
def fetch(q, per_page=10):
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": q, "sort": "stars", "order": "desc", "per_page": per_page})
    request = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json","User-Agent":"MissionC-PublicResearch/1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)

def normalize(raw):
    if not isinstance(raw, dict) or not isinstance(raw.get("items"), list):
        raise ValueError("unexpected GitHub API schema")
    repos = []
    for r in raw["items"]:
        if not isinstance(r, dict):
            continue
        repos.append({"name": r.get("full_name"), "url": r.get("html_url"),
                      "stars": r.get("stargazers_count"), "forks": r.get("forks_count"),
                      "last_push": r.get("pushed_at"), "archived": r.get("archived"),
                      "description": str(r.get("description") or "")[:250]})
    return {"total_matches":raw.get("total_count"),"top_repositories":repos}

def main():
    result={"observed_at":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
            "source":"https://api.github.com/search/repositories",
            "method":"GitHub repository full-text query, sorted by stars; repository count is NOT buyer count, star is NOT purchase intent",
            "queries":{}, "errors":{}}
    for key,q in SEARCHES.items():
        try:result["queries"][key]={"query":q,**normalize(fetch(q))}
        except Exception as e:result["errors"][key]=type(e).__name__+": "+str(e)[:180]
    (ROOT/"competitor_evidence.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"at":result["observed_at"],"matches":{k:v["total_matches"] for k,v in result["queries"].items()},"errors":result["errors"]}))
    return 0 if len(result["queries"])>=3 else 1
if __name__=="__main__":
    raise SystemExit(main())
