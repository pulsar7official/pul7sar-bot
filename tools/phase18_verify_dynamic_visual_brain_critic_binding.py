#!/usr/bin/env python3
"""Replay Dynamic Visual Brain concept-to-PNG-to-critic provenance on CPU."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.dynamic_visual_brain_critic_binding import DynamicVisualBrainCriticBindingGate


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify SHA-bound Dynamic Visual Brain critic provenance")
    parser.add_argument("--concept-lock", required=True)
    parser.add_argument("--local-admission", required=True)
    parser.add_argument("--batch-manifest", required=True)
    parser.add_argument("--generation-result", required=True)
    parser.add_argument("--critic-evidence", required=True)
    parser.add_argument("--repository-root", default=".")
    parser.add_argument(
        "--output",
        default="output/phase18_visual_brain/dynamic-visual-brain-critic-binding.json",
    )
    args = parser.parse_args()

    receipt = DynamicVisualBrainCriticBindingGate.verify(
        concept_lock_path=args.concept_lock,
        local_admission_path=args.local_admission,
        batch_manifest_path=args.batch_manifest,
        generation_result_path=args.generation_result,
        critic_evidence_path=args.critic_evidence,
        repository_root=args.repository_root,
    )
    root = Path(args.repository_root).resolve()
    output = (root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output).resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise ValueError("DYNAMIC_VISUAL_BRAIN_CRITIC_BINDING_OUTPUT_ESCAPES_REPOSITORY") from exc
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
