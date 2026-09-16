#!/usr/bin/env python3
"""Build Change Set 237 fresh-story gate receipt bundle admission (CPU-only)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_fresh_story_gate_receipt_bundle import (
    build_fresh_story_gate_receipt_bundle,
    verify_fresh_story_gate_receipt_bundle,
)


def _read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON object required: {path}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-contract", type=Path, required=True)
    parser.add_argument("--evidence-manifest", type=Path, required=True)
    parser.add_argument("--verification-contract", type=Path, required=True)
    parser.add_argument("--gate-receipt", type=Path, action="append", required=True)
    parser.add_argument("--evaluated-at-utc", required=True)
    parser.add_argument("--max-gate-age-seconds", type=int, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    preflight = _read_json(args.preflight_contract)
    manifest = _read_json(args.evidence_manifest)
    contract = _read_json(args.verification_contract)
    receipts = [_read_json(path) for path in args.gate_receipt]

    bundle = build_fresh_story_gate_receipt_bundle(
        contract,
        manifest,
        preflight,
        receipts,
        evaluated_at_utc=args.evaluated_at_utc,
        max_gate_age_seconds=args.max_gate_age_seconds,
        repo_root=repo_root,
    )
    verify_fresh_story_gate_receipt_bundle(
        bundle,
        contract,
        manifest,
        preflight,
        receipts,
        repo_root=repo_root,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(bundle["fresh_story_gate_receipt_bundle_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
