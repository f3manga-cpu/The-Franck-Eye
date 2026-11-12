#!/usr/bin/env python3
"""Read-only decoder for selected Pump.fun on-chain fee events.

Uses the official Pump public IDLs. A fee event is NOT proof of user ownership,
cash withdrawal, or bank settlement. No private keys or transaction signing.
"""
import argparse
import base64
import json
import re
import struct
import urllib.request
from pathlib import Path

from onchain_receipt_verify import fetch_transaction, valid_base58

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / ".idl_cache"
BASE = "https://raw.githubusercontent.com/pump-fun/pump-public-docs/main/idl/"
PROGRAMS = {
    "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P": "pump.json",
    "pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA": "pump_amm.json",
}
EVENT_KIND = {
    "TradeEvent": "TRADE_FEE_FIELD_UNATTRIBUTED",
    "BuyEvent": "TRADE_FEE_FIELD_UNATTRIBUTED",
    "SellEvent": "TRADE_FEE_FIELD_UNATTRIBUTED",
    "SweepBondingCurveFeeEvent": "FEE_SWEPT_TO_VAULT",
    "SweepPoolFeeEvent": "FEE_SWEPT_TO_VAULT",
    "CollectCreatorFeeEvent": "CREATOR_VAULT_CLAIM_EVENT",
    "CollectCoinCreatorFeeEvent": "CREATOR_VAULT_CLAIM_EVENT",
}
RE_INVOKE = re.compile(r"^Program ([1-9A-HJ-NP-Za-km-z]+) invoke \[[0-9]+\]$")
RE_END = re.compile(r"^Program ([1-9A-HJ-NP-Za-km-z]+) (?:success|failed:.*)$")
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def b58(b):
    n = int.from_bytes(b, "big")
    digits = ""
    while n:
        n, r = divmod(n, 58)
        digits = ALPHABET[r] + digits
    return ("1" * (len(b) - len(b.lstrip(b"\0")))) + digits

def get_idls():
    CACHE.mkdir(mode=0o700, exist_ok=True)
    result = {}
    for program, filename in PROGRAMS.items():
        path = CACHE / filename
        if not path.is_file():
            req = urllib.request.Request(BASE + filename, headers={"User-Agent": "MissionC-readonly/1.0"})
            with urllib.request.urlopen(req, timeout=15) as response:
                raw = response.read(450001)
            if len(raw) > 450000:
                raise ValueError("Official IDL exceeded allowed size")
            doc = json.loads(raw)
            if doc.get("address") != program:
                raise ValueError("IDL program address does not match official program")
            path.write_bytes(raw)
        doc = json.loads(path.read_bytes())
        if doc.get("address") != program:
            raise ValueError("Cached IDL program address mismatch")
        typed = {x["name"]: x["type"]["fields"] for x in doc["types"] if x.get("type", {}).get("kind") == "struct"}
        for event in doc["events"]:
            if event["name"] in EVENT_KIND and event["name"] in typed:
                result[(program, bytes(event["discriminator"]))] = (event["name"], typed[event["name"]])
    return result

def read_primitive(blob, offset, kind):
    numeric = {"u8":("<B",1),"u16":("<H",2),"u32":("<I",4),"u64":("<Q",8),
               "i64":("<q",8),"i128":(None,16)}
    if kind in numeric:
        fmt, length = numeric[kind]
        if offset + length > len(blob):
            raise ValueError("Event data truncated")
        b = blob[offset:offset+length]
        return (struct.unpack(fmt, b)[0] if fmt else int.from_bytes(b, "little", signed=True)), offset + length
    if kind == "pubkey":
        if offset + 32 > len(blob):
            raise ValueError("Event pubkey truncated")
        return b58(blob[offset:offset+32]), offset + 32
    if kind == "bool":
        if offset >= len(blob) or blob[offset] not in (0,1):
            raise ValueError("Invalid event boolean")
        return bool(blob[offset]), offset+1
    raise ValueError("Unsupported event field: " + str(kind)[:60])

def decode_event(blob, name, fields):
    obj = {}
    off = 8
    stop_after = "creator_fee" if name == "TradeEvent" else ("coin_creator_fee" if name in ("BuyEvent","SellEvent") else None)
    for field in fields:
        val, off = read_primitive(blob, off, field["type"])
        obj[field["name"]] = val
        if field["name"] == stop_after:
            break
    return obj

def inspect_logs(tx, idls):
    if not isinstance(tx, dict) or not isinstance(tx.get("meta"), dict):
        raise ValueError("Incomplete finalized transaction")
    if tx["meta"].get("err") is not None:
        return []
    logs = tx["meta"].get("logMessages")
    if not isinstance(logs, list):
        raise ValueError("Transaction has no program logs")
    stack, events = [], []
    for line in logs:
        if not isinstance(line, str):
            continue
        invoking = RE_INVOKE.fullmatch(line)
        ending = RE_END.fullmatch(line)
        if invoking:
            stack.append(invoking.group(1))
        elif ending:
            if stack and stack[-1] == ending.group(1):
                stack.pop()
            else:
                stack.clear()
        elif line.startswith("Program data: ") and stack:
            program = stack[-1]
            if program not in PROGRAMS:
                continue
            try:
                data = base64.b64decode(line[14:], validate=True)
                spec = idls.get((program,data[:8]))
                if not spec:
                    continue
                name, fields = spec
                decoded = decode_event(data,name,fields)
                if name.startswith("Sweep") and decoded.get("bucket") != 1:
                    continue
                amount = decoded.get("creator_fee",decoded.get("coin_creator_fee",decoded.get("amount")))
                events.append({
                    "kind": EVENT_KIND[name], "event": name, "program": program,
                    "amount_raw_quote_units": amount, "data": decoded
                })
            except (ValueError,TypeError,struct.error):
                continue
    return events

def audit(signature, fetch=fetch_transaction, idls=None):
    if not valid_base58(signature,80,90):
        raise ValueError("Invalid transaction signature")
    tx=fetch(signature)
    if tx is None:
        return {"status":"NOT_FOUND","signature":signature,"bank_settled_eur":None}
    if tx["meta"].get("err") is not None:
        return {"status":"TRANSACTION_FAILED","signature":signature,"bank_settled_eur":None}
    events=inspect_logs(tx,idls if idls is not None else get_idls())
    return {
        "status":"FINALIZED_EVENT_DATA" if events else "FINALIZED_NO_RECOGNIZED_FEE_EVENTS",
        "signature":signature,"slot":tx.get("slot"),"transaction_version":tx.get("version"),
        "events":events,"event_count":len(events),
        "proof_level":"ONE_FINALIZED_PUBLIC_SOLANA_RPC_RESPONSE_PLUS_OFFICIAL_IDL",
        "revenue_attributable_to_user":False,"bank_settled_eur":None,
        "limitations":[
            "Trade fee fields may represent holder rewards, not creator earnings.",
            "A sweep moves fees into a vault; it does not establish creator withdrawal.",
            "A claim event does not prove ownership by the operator or bank settlement.",
            "Amounts are raw smallest quote-asset units, not automatically SOL or EUR.",
            "RPC response is one public provider view, not independently cross-checked."
        ]
    }

if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("signature",help="Public Solana transaction signature")
    p.add_argument("--out",help="Optional local JSON evidence path")
    args=p.parse_args()
    report=audit(args.signature)
    output=json.dumps(report,indent=2)+"\n"
    if args.out: Path(args.out).write_text(output)
    else: print(output,end="")
    raise SystemExit(0 if report["status"] == "FINALIZED_EVENT_DATA" else 2)
