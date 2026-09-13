#!/usr/bin/env python3
"""Prepare CPU-only review artifacts from one genuine Golden Hybrid v5 base."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.golden_candidate_review_bundle import GoldenCandidateReviewBundleBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare non-publication Golden Candidate review bundle")
    parser.add_argument("--root", default=".")
    parser.add_argument("--summary", default="output/phase18_colab/latest.json")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--output-dir", default="output/phase18_candidate_review/candidate-01")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    payload = GoldenCandidateReviewBundleBuilder().build(
        repository_root=str(root),
        summary_path=args.summary,
        output_dir=args.output_dir,
        expected_candidate=args.candidate,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
