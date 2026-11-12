#!/usr/bin/env python3
"""Read-only, evidence-labeled GTA audience monitor; never fabricates pageviews."""
from datetime import datetime, timezone
from pathlib import Path
import json
import subprocess
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"data"/"audience_pulse.jsonl"
PAGE="https://f3manga-cpu.github.io/The-Franck-Eye/gta/"
STORY=PAGE+"signal-001.html"
REPO="f3manga-cpu/The-Franck-Eye"

def http_status(url):
    try:
        with urlopen(Request(url,headers={"User-Agent":"GTA-original-newsroom-availability-monitor/0.1"}),timeout=12) as r: return r.status
    except HTTPError as e: return e.code
    except (URLError,TimeoutError): return None

def gh_api(path):
    proc=subprocess.run(["gh","api",path],capture_output=True,text=True,timeout=20)
    if proc.returncode: return None,proc.stderr[-500:]
    return json.loads(proc.stdout),None

def collect():
    comment_data,comment_error=gh_api(f"repos/{REPO}/issues/9/comments?per_page=100")
    if isinstance(comment_data,list):
        authors={c.get("user",{}).get("login") for c in comment_data
                 if c.get("user",{}).get("login")
                 and c["user"]["login"].casefold()!="f3manga-cpu"
                 and c.get("user",{}).get("type")!="Bot"}
        comments=len(comment_data)
        independent=len(authors)
    else:
        comments=None
        independent=None
    traffic,traffic_error=gh_api(f"repos/{REPO}/traffic/views")
    traffic_valid=isinstance(traffic,dict) and "uniques" in traffic
    return {
        "collected_at":datetime.now(timezone.utc).isoformat(),
        "brand":"Greatest Token Action",
        "mint_status":"NOT_ISSUED",
        "pages_http_status":http_status(PAGE),
        "first_dispatch_http_status":http_status(STORY),
        "github_issue_9_comments_total":comments,
        "github_issue_9_unique_nonowner_human_accounts":independent,
        "github_issue_9_status":"unavailable" if comment_error else "read_ok",
        "github_repo_14day_views":traffic.get("count") if traffic_valid else None,
        "github_repo_14day_unique_visitors":traffic.get("uniques") if traffic_valid else None,
        "github_repo_views_are_NOT_website_pageviews":True,
        "social_views":None,
        "social_followers":None,
        "creator_fee_earned":None,
        "bank_money_verified":None,
        "note":"Availability is not engagement. GitHub issue counts require GitHub login; unique accounts are not verified unique people."
    }

if __name__=="__main__":
    x=collect()
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("a",encoding="utf8") as f: f.write(json.dumps(x,ensure_ascii=False)+"\n")
    print(json.dumps(x,indent=2))
