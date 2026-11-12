#!/usr/bin/env python3
"""Fail-closed PumpSwap pool quote-mint resolution from official IDL and read-only RPC."""
import base64
import json
import urllib.request
from pump_fee_event_audit import b58, read_primitive, PROGRAMS
from quote_asset_candidates import valid_solana_pubkey

RPC = "https://api.mainnet-beta.solana.com"

def decode_pool(account, idl):
    program = next(k for k,v in PROGRAMS.items() if v == "pump_amm.json")
    if not isinstance(account, dict) or account.get("owner") != program or account.get("executable") is not False:
        raise ValueError("Pool account owner/executable mismatch")
    if not isinstance(account.get("data"), list) or len(account["data"]) != 2 or account["data"][1] != "base64":
        raise ValueError("Unsupported account encoding")
    blob = base64.b64decode(account["data"][0], validate=True)
    definition = next(x for x in idl["accounts"] if x["name"] == "Pool")
    if blob[:8] != bytes(definition["discriminator"]):
        raise ValueError("Pool discriminator mismatch")
    fields = next(x["type"]["fields"] for x in idl["types"] if x["name"] == "Pool")
    offset = 8
    values = {}
    for field in fields:
        values[field["name"]], offset = read_primitive(blob, offset, field["type"])
    for key in ("base_mint", "quote_mint", "creator", "coin_creator"):
        if not valid_solana_pubkey(values[key]):
            raise ValueError("Malformed pool public key")
    return {"status":"POOL_ACCOUNT_VERIFIED", "quote_mint":values["quote_mint"],
            "base_mint":values["base_mint"],"creator":values["creator"],
            "coin_creator":values["coin_creator"],
            "is_holder_reward":values["is_holder_reward"],
            "creator_fee_bps":values["creator_fee_bps"],
            "fee_entitlement_verified":False,"receipt_verified":False}

def fetch_pool(pool, idl, rpc=RPC):
    if not valid_solana_pubkey(pool):
        raise ValueError("Invalid pool public key")
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":"getAccountInfo",
      "params":[pool,{"encoding":"base64","commitment":"finalized"}]}).encode()
    req = urllib.request.Request(rpc,data=payload,headers={"Content-Type":"application/json","User-Agent":"MissionC-readonly/1.0"})
    with urllib.request.urlopen(req,timeout=15) as response:
        result = json.load(response)
    if result.get("error") or not isinstance(result.get("result"),dict) or result["result"].get("value") is None:
        raise ValueError("Pool account unavailable")
    return decode_pool(result["result"]["value"],idl)
