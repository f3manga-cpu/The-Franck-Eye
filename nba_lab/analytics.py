#!/usr/bin/env python3
"""Audit recommendations without conflating hypothetical picks and paid wagers."""
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_jsonl(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]


def implied_probability(american):
    if american is None or american == 0:
        return None
    return abs(american) / (abs(american) + 100) if american < 0 else 100 / (american + 100)


def calculate(rows, backlog=None):
    statuses = Counter(row.get("grade_status", "unknown") for row in rows)
    verified = [x for x in rows if x.get("grade_status") in ("hit", "miss")]
    reported = [x for x in rows if x.get("grade_status") in ("reported_hit", "reported_miss")]
    by_market = defaultdict(lambda: {"hit": 0, "miss": 0})
    for x in verified:
        by_market[x.get("market", "unknown")][x["grade_status"]] += 1
    calibrated = [x for x in verified if isinstance(x.get("model_probability"), (int, float)) and
                  0 < x["model_probability"] < 1]
    brier = None
    log_loss = None
    if calibrated:
        brier = sum((x["model_probability"] - int(x["grade_status"] == "hit"))**2 for x in calibrated)/len(calibrated)
        log_loss = -sum(int(x["grade_status"] == "hit")*math.log(x["model_probability"]) +
                        int(x["grade_status"] == "miss")*math.log(1-x["model_probability"])
                        for x in calibrated)/len(calibrated)
    return {
        "recommendations_total": len(rows),
        "statuses": dict(statuses),
        "verified_sample": len(verified),
        "verified_hit_rate": (sum(x["grade_status"] == "hit" for x in verified) / len(verified)) if verified else None,
        "reported_sample_not_independently_audited": len(reported),
        "reported_hit_rate": (sum(x["grade_status"] == "reported_hit" for x in reported) / len(reported)) if reported else None,
        "historical_backlog_records": len(backlog or []),
        "by_market_verified": dict(by_market),
        "probability_scored_sample": len(calibrated),
        "brier_score": brier,
        "log_loss": log_loss,
        "actual_bet_roi": None,
        "closing_line_value": None
    }


def main():
    picks = read_jsonl(ROOT / "data" / "picks.jsonl")
    backlog = read_jsonl(ROOT / "data" / "history_backlog.jsonl")
    print(json.dumps(calculate(picks, backlog), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
