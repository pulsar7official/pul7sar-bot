#!/usr/bin/env python3
"""Build Change Set 236 fresh-story gate verification contract (CPU-only)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_fresh_story_gate_verification_contract import (
    build_fresh_story_gate_verification_contract,
    verify_fresh_story_gate_verification_contract,
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
    parser.add_argument("--story-snapshot-sha256", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    preflight = _read_json(args.preflight_contract)
    manifest = _read_json(args.evidence_manifest)
    contract = build_fresh_story_gate_verification_contract(
        manifest,
        preflight,
        story_snapshot_sha256=args.story_snapshot_sha256,
        repo_root=repo_root,
    )
    verify_fresh_story_gate_verification_contract(
        contract,
        manifest,
        preflight,
        repo_root=repo_root,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(contract["fresh_story_gate_verification_contract_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
