#!/usr/bin/env python3
"""Build a SHA-bound human visual-review template for Candidate 1 Hybrid proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from engine.intelligence.hybrid_human_review_decision import HybridHumanReviewDecisionGate

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
DEFAULT_BUNDLE = ROOT / "output" / "phase18_gpu_smoke" / "hybrid-human-review-bundle.json"
DEFAULT_TEMPLATE = ROOT / "output" / "phase18_gpu_smoke" / "hybrid-human-review-template.json"


def _branch() -> str:
    completed = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError("HYBRID_HUMAN_TEMPLATE_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def run(*, bundle_path: Path = DEFAULT_BUNDLE, output_path: Path = DEFAULT_TEMPLATE) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("HYBRID_HUMAN_TEMPLATE_BRANCH_BLOCKED")
    gate = HybridHumanReviewDecisionGate(root=ROOT)
    payload = gate.build_template(bundle_path=bundle_path)
    output_path = output_path.resolve()
    root = ROOT.resolve()
    if output_path != root and root not in output_path.parents:
        raise RuntimeError("HYBRID_HUMAN_TEMPLATE_OUTPUT_ESCAPES_REPOSITORY")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact Candidate 1 Hybrid human-review decision template")
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args()
    payload = run(bundle_path=args.bundle, output_path=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
