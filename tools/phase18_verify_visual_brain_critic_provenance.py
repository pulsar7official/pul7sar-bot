#!/usr/bin/env python3
"""Verify that Visual Brain critic evidence refers to the exact generated PNG."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.visual_brain_critic_provenance import VisualCriticProvenanceGate


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify PUL7SAR Visual Brain critic provenance")
    parser.add_argument("--repository-root", default=".")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--generation-result", required=True)
    parser.add_argument("--critic-evidence", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    receipt = VisualCriticProvenanceGate().verify(
        repository_root=args.repository_root,
        manifest_path=args.manifest,
        generation_result_path=args.generation_result,
        critic_evidence_path=args.critic_evidence,
    ).to_dict()
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["critic_accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
