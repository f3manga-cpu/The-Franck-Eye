#!/usr/bin/env python3
"""Revenue harness independent gatekeeper. Read-only on external services.
It MUST NOT claim Stripe verification from manually written repo state.
No third-party libraries, account credentials or paid inference.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "engine/harness/state.json"
LEDGER = ROOT / "engine/data/events.jsonl"
OUTPUT = ROOT / "engine/harness/STATUS.md"

KNOWN_STATES = {
    "research_only", "prepared", "evidence_checked", "selected", "built",
    "distributed", "purchase_verified", "fulfilled", "scale", "closed",
}
MONEY_TYPES = {"payment_confirmed", "refund", "cost"}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must be an object")
    return value


def ledger_summary(path: Path) -> dict[str, Any]:
    events = []
    if path.exists():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid ledger line {n}") from exc
            if event.get("type") in MONEY_TYPES:
                cents = event.get("amount_cents")
                if not isinstance(cents, int) or cents <= 0:
                    raise ValueError(f"Bad money amount on ledger line {n}")
            events.append(event)
    types = {k: sum(1 for event in events if event.get("type") == k)
             for k in ("experiment_started", "published", "lead", "reply",
                       "order", "payment_confirmed", "refund", "cost")}
    manual_gross = sum(e.get("amount_cents", 0) for e in events
                       if e.get("type") == "payment_confirmed")
    return {"events": len(events), "types": types,
            "manual_gross_eur": manual_gross / 100,
            "source_of_truth": "MANUALLY_ENTERED_NOT_STRIPE_VERIFIED"}


def audit_experiment(experiment: dict[str, Any]) -> dict[str, Any]:
    issues = []
    warnings = []
    stage = experiment.get("state")
    if stage not in KNOWN_STATES:
        issues.append(f"unknown_state:{stage}")
    verified = experiment.get("purchases_verified", 0)
    gross = experiment.get("attributable_gross_eur", 0)
    net = experiment.get("attributable_net_eur")
    if not isinstance(verified, int) or verified < 0:
        issues.append("invalid_purchase_count")
    if not isinstance(gross, (float, int)) or gross < 0:
        issues.append("invalid_gross")
    if isinstance(gross, (float, int)) and gross > 0 and not verified:
        issues.append("gross_without_verified_purchase")
    if stage in {"purchase_verified", "fulfilled", "scale"} and verified == 0:
        issues.append("advanced_without_verified_payment")
    if net is not None and isinstance(gross, (float, int)) and net > gross:
        issues.append("net_exceeds_gross")
    if stage in {"built", "distributed", "purchase_verified", "fulfilled", "scale"}:
        if not experiment.get("offer_url") and not experiment.get("stripe_checkout"):
            issues.append("no_offer_or_checkout_url")
    if stage in {"distributed", "purchase_verified", "fulfilled", "scale"}:
        if not experiment.get("channel"):
            issues.append("distribution_without_channel")
    if net is None:
        warnings.append("NET_UNKNOWN_NEVER_EQUATE_GROSS_TO_NET")
    if not verified:
        warnings.append("ZERO_CONFIRMED_PURCHASES_IN_RECORDED_STATE")
    if stage == "prepared":
        warnings.append("NOT_LIVE_IN_BUYER_CHANNEL")
    return {"id": experiment.get("id", ""), "stage": stage,
            "verified_purchases_recorded": verified,
            "attributable_gross_eur_recorded": gross,
            "attributable_net_eur_recorded": net,
            "issues": issues, "warnings": warnings}


def audit_state(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("schema_version") != 2:
        raise ValueError("Unexpected schema version")
    if value.get("spend_ceiling_eur") != 0:
        raise ValueError("Zero-cost guardrail disabled: operator review required")
    experiments = value.get("experiments")
    if not isinstance(experiments, list):
        raise ValueError("experiments must be an array")
    ids = [e.get("id") for e in experiments]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate experiment ids")
    records = [audit_experiment(e) for e in experiments]
    issues = [f'{r["id"]}: {issue}' for r in records for issue in r["issues"]]
    active = value.get("active_experiment")
    if active and active not in ids:
        issues.append("active_experiment_missing")
    return {"active": active, "experiments": records, "issues": issues}


def render_report(state: dict[str, Any], ledger: dict[str, Any],
                  run_at: str) -> str:
    lines = [
        "# Revenue harness — independent validation report",
        "", f"Audit run (UTC): {run_at}", "",
        "> This is a **public, manually updated operations state**. It has no direct",
        "> access to Stripe, Gmail, bank balances or delivery confirmations.",
        "> The live Stripe connector is the source of truth for payment claims.",
        "", f"Active experiment: \`{state['active']}\`", "",
        "| Experiment | Stage | Purchases recorded | Gross recorded (€) | Net recorded (€) |",
        "|---|---|---:|---:|---:|",
    ]
    for row in state["experiments"]:
        net = row["attributable_net_eur_recorded"]
        lines.append(f"| {row['id']} | {row['stage']} | "
                     f"{row['verified_purchases_recorded']} | "
                     f"{row['attributable_gross_eur_recorded']:.2f} | "
                     f"{'unknown' if net is None else f'{net:.2f}'} |")
    lines += ["", "## Invariants and warnings", ""]
    if state["issues"]:
        lines += [f"- BLOCK: {issue}" for issue in state["issues"]]
    else:
        lines.append("- State invariants pass; **no independent payment verification performed**.")
    for row in state["experiments"]:
        lines += [f"- {row['id']}: {warn}" for warn in row["warnings"]]
    lines += ["", "## Ledger notes", "",
              f"- Existing ledger events: {ledger['events']}",
              f"- Manually recorded gross: €{ledger['manual_gross_eur']:.2f}; "
              "not independently verified from Stripe.",
              "- Model-agent/API costs: no API inference performed by this auditor.",
              "- Next decision must be supported by buyer exposure, response or payment, not file counts.",
              ""]
    return "\n".join(lines)


def main() -> None:
    state = audit_state(load_json(STATE))
    ledger = ledger_summary(LEDGER)
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    OUTPUT.write_text(render_report(state, ledger, now), encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT.relative_to(ROOT)),
                      "issues": state["issues"],
                      "experiments": len(state["experiments"])},
                     ensure_ascii=False))
    if state["issues"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
