#!/usr/bin/env python3
"""Bind a durable Dynamic Visual Brain candidate to a canonical ledger case."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.dynamic_visual_brain_ledger_binding import (
    DynamicVisualBrainLedgerBindingGate,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "phase18_visual_validation" / "dynamic-ledger-binding.json"


def _inside_repo(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SystemExit("DYNAMIC_VISUAL_BRAIN_LEDGER_OUTPUT_OUTSIDE_REPOSITORY") from exc
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-id", required=True)
    parser.add_argument("--queue-critic-binding", required=True)
    parser.add_argument("--candidate-png", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    receipt = DynamicVisualBrainLedgerBindingGate.verify(
        benchmark_id=args.benchmark_id,
        queue_critic_binding_path=args.queue_critic_binding,
        candidate_png_path=args.candidate_png,
        repository_root=str(ROOT),
    )
    output = _inside_repo(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "DYNAMIC_VISUAL_BRAIN_LEDGER_BINDING_READY",
        "binding_path": str(output.relative_to(ROOT.resolve())),
        "benchmark_id": receipt.benchmark_id,
        "critic_approved": receipt.critic_approved,
        "human_visual_review_required": True,
        "golden_quality_approved": False,
        "publication_ready": False,
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
