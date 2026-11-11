#!/usr/bin/env python3
"""NBA prop result grader. Stdlib-only; no sportsbook or betting actions.

Usage: python nba_lab/grade.py [--date YYYY-MM-DD] [--dry-run]
Dates refer to NBA/U.S. Eastern local game dates.
"""
import argparse
import datetime as dt
import json
import os
import sys
import unicodedata
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
PICKS = ROOT / "data" / "picks.jsonl"
API = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"


def fetch_json(url):
    req = Request(url, headers={"User-Agent": "NBA-Props-Lab/0.1 (research, no wagering)", "Accept": "application/json"})
    with urlopen(req, timeout=25) as response:
        return json.load(response)


def normal(text):
    ascii_text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    return "".join(c for c in ascii_text.lower() if c.isalnum())


def locate_event(scoreboard, team, opponent):
    for event in scoreboard.get("events", []):
        competitors = event.get("competitions", [{}])[0].get("competitors", [])
        abbreviations = {t.get("team", {}).get("abbreviation", "") for t in competitors}
        if {team, opponent} <= abbreviations:
            status = event.get("status", {}).get("type", {})
            if status.get("completed", False):
                return event
            return None
    return None


def extract_player(summary, team, player):
    for club in summary.get("boxscore", {}).get("players", []):
        if club.get("team", {}).get("abbreviation", "") != team:
            continue
        for group in club.get("statistics", []):
            labels = group.get("labels", [])
            for record in group.get("athletes", []):
                athlete = record.get("athlete", {})
                if normal(athlete.get("displayName")) != normal(player):
                    continue
                stat_strings = record.get("stats") or []
                output = {}
                for key, value in zip(labels, stat_strings):
                    key = str(key).upper()
                    if key == "3PT":
                        output["3PM"] = int(str(value).split("-")[0])
                    elif key in {"PTS", "REB", "AST"}:
                        output[key] = int(value)
                if {"PTS", "REB", "AST"}.issubset(output):
                    return output
    return None


def value_for(market, stats):
    maps = {"PTS": ["PTS"], "REB": ["REB"], "AST": ["AST"], "3PM": ["3PM"],
            "PR": ["PTS", "REB"], "PRA": ["PTS", "REB", "AST"]}
    if market not in maps:
        raise ValueError(f"Unsupported market: {market}")
    return sum(stats[key] for key in maps[market])


def read_picks(path=PICKS):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def write_picks(rows, path=PICKS):
    tmp = path.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in rows))
    os.replace(tmp, path)


def grade_day(game_date, rows, request=fetch_json):
    candidates = [row for row in rows if row["date_et"] == game_date and row.get("grade_status") == "pending"]
    if not candidates:
        return {"updated": 0, "pending": 0, "issues": []}
    scoreboard = request(f"{API}/scoreboard?dates={game_date.replace('-', '')}")
    summaries = {}
    updated = 0
    issues = []
    for row in candidates:
        event = locate_event(scoreboard, row["team"], row["opponent"])
        if event is None:
            issues.append(row["id"] + ": event not final or not found")
            continue
        event_id = str(event["id"])
        if event_id not in summaries:
            summaries[event_id] = request(f"{API}/summary?event={event_id}")
        stats = extract_player(summaries[event_id], row["team"], row["player"])
        if stats is None:
            row["grade_status"] = "manual_review"
            row["grade_note"] = "Player not found in completed game's boxscore; verify DNP, identity and ESPN feed before settlement"
            issues.append(row["id"] + ": player missing from boxscore")
            updated += 1
            continue
        observed = value_for(row["market"], stats)
        row["observed"] = observed
        row["grade_status"] = "hit" if observed >= row["threshold"] else "miss"
        row["result_source"] = f"ESPN summary event {event_id}"
        row["result_verified_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
        updated += 1
    return {"updated": updated, "pending": len(candidates) - updated, "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", help="NBA Eastern game date YYYY-MM-DD; default yesterday ET")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    today_et = dt.datetime.now(ZoneInfo("America/New_York")).date()
    target = args.date or str(today_et - dt.timedelta(days=1))
    dt.date.fromisoformat(target)
    rows = read_picks()
    result = grade_day(target, rows)
    if result["updated"] and not args.dry_run:
        write_picks(rows)
    print(json.dumps({"date_et": target, **result, "dry_run": args.dry_run}, indent=2))
    if result["issues"]:
        print("Review unresolved outcomes. No assumed wins, losses, or voids.", file=sys.stderr)


if __name__ == "__main__":
    main()
