#!/usr/bin/env python3
"""Read-only, fail-closed SPL mint metadata inspection; never values token units."""
import base64
import json
import struct
import urllib.request
from quote_asset_candidates import valid_solana_pubkey

TOKEN = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
TOKEN_2022 = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
RPC = "https://api.mainnet-beta.solana.com"

def decode_mint(account):
    if not isinstance(account, dict) or account.get("owner") not in (TOKEN, TOKEN_2022):
        raise ValueError("Unrecognized mint owner")
    if account.get("executable") is not False:
        raise ValueError("Executable account is not a mint")
    data = account.get("data")
    if not isinstance(data, list) or len(data) != 2 or data[1] != "base64":
        raise ValueError("Invalid encoding")
    blob = base64.b64decode(data[0], validate=True)
    if len(blob) < 82 or blob[45] not in (0,1):
        raise ValueError("Invalid mint layout")
    decimals = blob[44]
    extensions = []
    if account["owner"] == TOKEN:
        if len(blob) != 82:
            raise ValueError("Unexpected legacy mint length")
    elif len(blob) > 82:
        if len(blob) < 166 or blob[165] != 1:
            raise ValueError("Invalid Token-2022 mint extension header")
        offset = 166
        while offset < len(blob):
            if len(blob) - offset < 4:
                raise ValueError("Truncated extension header")
            typ, length = struct.unpack_from("<HH", blob, offset)
            offset += 4
            if length > len(blob) - offset:
                raise ValueError("Truncated extension payload")
            extensions.append(typ)
            offset += length
    # Extension IDs must be evaluated against the installed canonical Token-2022 spec
    # before interpreting displayed balances or transferability.
    return {"status":"MINT_LAYOUT_VERIFIED", "token_program":account["owner"],
            "decimals":decimals, "extension_type_ids":extensions,
            "economic_value_verified":False,"transferability_verified":False,
            "fee_receipt_verified":False}

def fetch_mint(mint, rpc=RPC):
    if not valid_solana_pubkey(mint):
        raise ValueError("Invalid mint key")
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"getAccountInfo",
        "params":[mint,{"encoding":"base64","commitment":"finalized"}]}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json",
        "User-Agent":"MissionC-readonly/1.0"})
    with urllib.request.urlopen(req,timeout=15) as resp:
        response = json.load(resp)
    if response.get("error") or not isinstance(response.get("result"),dict) or response["result"].get("value") is None:
        raise ValueError("Mint account unavailable")
    return decode_mint(response["result"]["value"])
