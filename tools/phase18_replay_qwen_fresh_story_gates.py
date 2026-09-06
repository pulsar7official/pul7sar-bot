#!/usr/bin/env python3
"""Execute Change Set 238 gate-specific fresh-story semantic replay (CPU-only).

The registry module must expose ``GATE_REPLAY_VERIFIERS`` as an insertion-ordered
mapping with exactly the six required gate IDs. This tool never loads Qwen, touches
CUDA, mutates the generation queue, or grants canonical generation authority.
"""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_fresh_story_gate_semantic_replay import (
    build_fresh_story_gate_semantic_replay,
    verify_fresh_story_gate_semantic_replay,
)


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON object required: {path}")
    return data


def _load_registry(module_name: str) -> Mapping[str, Any]:
    if not module_name or module_name.startswith("."):
        raise ValueError("Absolute verifier registry module required")
    module = importlib.import_module(module_name)
    registry = getattr(module, "GATE_REPLAY_VERIFIERS", None)
    if not isinstance(registry, Mapping):
        raise ValueError(
            f"{module_name} must expose mapping GATE_REPLAY_VERIFIERS"
        )
    return registry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-contract", type=Path, required=True)
    parser.add_argument("--evidence-manifest", type=Path, required=True)
    parser.add_argument("--verification-contract", type=Path, required=True)
    parser.add_argument("--receipt-bundle", type=Path, required=True)
    parser.add_argument("--gate-receipt", type=Path, action="append", required=True)
    parser.add_argument("--verifier-registry-module", required=True)
    parser.add_argument("--replayed-at-utc", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    preflight = _read_json(args.preflight_contract)
    manifest = _read_json(args.evidence_manifest)
    contract = _read_json(args.verification_contract)
    bundle = _read_json(args.receipt_bundle)
    receipts = [_read_json(path) for path in args.gate_receipt]
    verifiers = _load_registry(args.verifier_registry_module)

    replay = build_fresh_story_gate_semantic_replay(
        bundle,
        contract,
        manifest,
        preflight,
        receipts,
        verifiers,
        replayed_at_utc=args.replayed_at_utc,
        repo_root=repo_root,
    )
    verify_fresh_story_gate_semantic_replay(
        replay,
        bundle,
        contract,
        manifest,
        preflight,
        receipts,
        verifiers,
        repo_root=repo_root,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(replay, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(replay["fresh_story_gate_semantic_replay_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
