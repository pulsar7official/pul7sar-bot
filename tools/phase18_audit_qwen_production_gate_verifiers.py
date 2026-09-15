#!/usr/bin/env python3
"""Audit and optionally persist the canonical Phase 18 production-verifier readiness receipt.

This tool is CPU-only. It never executes story semantics, loads model weights, runs
Qwen inference, mutates publication queues, or grants generation/publication authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_production_gate_verifier_readiness import (
    audit_production_gate_verifier_readiness,
    verify_production_gate_verifier_readiness,
)
from engine.intelligence.qwen_image_production_gate_verifier_registry import (
    GATE_REPLAY_VERIFIERS,
)


def build_readiness_receipt() -> dict:
    """Build and immediately replay-verify the live canonical registry/source bytes."""
    receipt = audit_production_gate_verifier_readiness(GATE_REPLAY_VERIFIERS)
    verify_production_gate_verifier_readiness(receipt, GATE_REPLAY_VERIFIERS)
    return receipt


def write_readiness_receipt(receipt: dict, output: Path) -> None:
    """Persist deterministic UTF-8 JSON only after live replay verification succeeds."""
    if not isinstance(output, Path):
        raise TypeError("output must be pathlib.Path")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit whether all six production fresh-story replay verifiers are bound. "
            "This command never executes gate semantics, loads model weights, runs Qwen "
            "inference, or grants canonical-generation/publication authority."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for a replay-verified deterministic readiness receipt JSON.",
    )
    args = parser.parse_args()

    receipt = build_readiness_receipt()
    if args.output is not None:
        write_readiness_receipt(receipt, args.output)
    print(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if receipt["all_production_verifiers_bound"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
