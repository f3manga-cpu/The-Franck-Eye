"""Offline, unsigned GTA launch-readiness validator. No wallet or RPC access."""
import json
from pathlib import Path

REQUIRED = ("name", "symbol", "description", "image_rights", "independent_disclaimer", "audience_18_plus", "mint_address")

def evaluate(metadata):
    errors = []
    for key in REQUIRED:
        if key not in metadata:
            errors.append("missing:" + key)
    if metadata.get("name") != "Greatest Token Action":
        errors.append("brand_mismatch")
    if metadata.get("symbol") != "GTA":
        errors.append("ticker_mismatch")
    if metadata.get("mint_address") not in (None, ""):
        errors.append("unverified_mint_address")
    if metadata.get("image_rights") != "original_owned":
        errors.append("image_rights_unverified")
    if metadata.get("independent_disclaimer") is not True:
        errors.append("independence_disclaimer_required")
    if metadata.get("audience_18_plus") is not True:
        errors.append("adult_audience_gate_required")
    for field in ("description",):
        value = metadata.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(field + "_empty")
    return {"offline_metadata_valid": not errors, "mainnet_launch_authorized": False,
            "errors": sorted(set(errors)), "ticker_collision_warning": "GTA is not unique; mint address must identify any future token",
            "requires_specific_approval": ["mainnet issuance", "wallet and fees", "spending cap", "live marketing"]}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata", type=Path)
    args = parser.parse_args()
    print(json.dumps(evaluate(json.loads(args.metadata.read_text(encoding="utf-8"))), indent=2))

if __name__ == "__main__":
    main()
