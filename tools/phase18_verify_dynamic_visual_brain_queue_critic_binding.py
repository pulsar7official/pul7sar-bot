#!/usr/bin/env python3
"""Replay Dynamic Visual Brain durable queue -> generation -> critic provenance.

CPU-only verification. This command never runs FLUX/Qwen, never mutates the
queue, and never grants Human, Golden, or publication authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.dynamic_visual_brain_queue_critic_binding import DynamicVisualBrainQueueCriticBindingGate


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify durable Dynamic Visual Brain queue execution against critic evidence")
    parser.add_argument("--queue-binding", required=True)
    parser.add_argument("--concept-lock", required=True)
    parser.add_argument("--local-admission", required=True)
    parser.add_argument("--batch-manifest", required=True)
    parser.add_argument("--generation-result", required=True)
    parser.add_argument("--critic-evidence", required=True)
    parser.add_argument("--receipt", default="output/phase18_dynamic_visual_brain/queue-critic-binding.json")
    parser.add_argument("--repository-root", default=".")
    args = parser.parse_args()

    root = Path(args.repository_root).resolve()
    receipt = DynamicVisualBrainQueueCriticBindingGate.verify(
        queue_binding_path=args.queue_binding,
        concept_lock_path=args.concept_lock,
        local_admission_path=args.local_admission,
        batch_manifest_path=args.batch_manifest,
        generation_result_path=args.generation_result,
        critic_evidence_path=args.critic_evidence,
        repository_root=str(root),
    )

    target = Path(args.receipt)
    resolved = target.resolve() if target.is_absolute() else (root / target).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("DYNAMIC_VISUAL_BRAIN_QUEUE_CRITIC_RECEIPT_OUTSIDE_REPOSITORY") from exc
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
