#!/usr/bin/env python3
"""Offline, evidence-preserving reconciliation of *user-supplied* creator-fee CSV exports.
This never connects to a wallet or asserts a payment was actually made.
CSV fields: transaction_signature, token_address, timestamp_utc, fee_sol.
"""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone

REQUIRED = {"transaction_signature", "token_address", "timestamp_utc", "fee_sol"}

def reconcile(path):
    path = Path(path)
    raw = path.read_bytes()
    if len(raw) > 10_000_000:
        raise ValueError("Input exceeds 10MB limit")
    source_hash = hashlib.sha256(raw).hexdigest()
    rows = []
    seen = set()
    errors = []
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
            raise ValueError("Missing required CSV columns: " + ", ".join(sorted(REQUIRED)))
        for n, row in enumerate(reader, 2):
            if n > 100_001:
                raise ValueError("Too many rows")
            try:
                sig = (row["transaction_signature"] or "").strip()
                token = (row["token_address"] or "").strip()
                ts = (row["timestamp_utc"] or "").strip()
                amount = Decimal((row["fee_sol"] or "").strip())
                if not sig or len(sig) > 150 or not token or len(token) > 150:
                    raise ValueError("Invalid transaction/token identifier")
                when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if when.tzinfo is None:
                    raise ValueError("Timestamp must include timezone")
                if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -9:
                    raise ValueError("Invalid SOL amount (negative, nonfinite or >9 decimals)")
                if sig in seen:
                    raise ValueError("Duplicate transaction signature")
                seen.add(sig)
                rows.append((sig, token, when.astimezone(timezone.utc).isoformat(), amount))
            except (ValueError, InvalidOperation, TypeError, OverflowError) as exc:
                errors.append({"row": n, "reason": str(exc)[:120]})
    totals = defaultdict(lambda: Decimal("0"))
    for _, token, _, amount in rows:
        totals[token] += amount
    return {
        "status": "input_validated" if not errors else "requires_review",
        "source_sha256": source_hash,
        "accepted_rows": len(rows),
        "rejected_rows": len(errors),
        "rejected": errors[:100],
        "total_reported_sol": str(sum(totals.values(), Decimal("0"))),
        "by_token_reported_sol": {key: str(totals[key]) for key in sorted(totals)},
        "proof_level": "SELF_REPORTED_CSV_ONLY_NOT_ONCHAIN_VERIFIED",
        "bank_settled_eur": None,
        "limitations": [
            "CSV entries are untrusted self-reported records, not independently verified blockchain transfers.",
            "Duplicate detection uses signature alone and may reject multiple fee entries in one transaction.",
            "No conversion to EUR, creator attribution, entitlement, fees, custody or bank settlement is established.",
            "Do not use this tool as a financial or tax statement without independent verification."
        ]
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", help="Local CSV path")
    parser.add_argument("--out", help="Optional local JSON report path")
    args = parser.parse_args()
    report = reconcile(args.csv)
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0 if report["status"] == "input_validated" else 2

if __name__ == "__main__":
    raise SystemExit(main())
