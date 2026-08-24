#!/usr/bin/env python3
"""Build a review template directly from a real Golden Visual execution report.

The template prevents reviewers from mistyping request IDs/seeds and enumerates
every approved scoring dimension and hard blocker. Scores are intentionally null:
PUL7SAR never fabricates visual judgments before someone actually inspects PNGs.
"""

from __future__ import annotations

import argparse
from dataclasses import fields
import json
from pathlib import Path

from engine.intelligence.golden_visual_quality import GoldenVisualBlockers, GoldenVisualScores
from tools.phase18_review_golden_batch import REVIEW_VERSION


SCORE_FIELDS = tuple(item.name for item in fields(GoldenVisualScores))
BLOCKER_FIELDS = tuple(item.name for item in fields(GoldenVisualBlockers))


def build_template(execution_report: str) -> dict[str, object]:
    data = json.loads(Path(execution_report).read_text(encoding="utf-8"))
    if data.get("status") != "REAL_VISUAL_PROOF_BATCH_GENERATED":
        raise ValueError("execution report is not a completed real visual proof batch")
    if data.get("cost_mode") != "$0-local":
        raise ValueError("execution report must remain locked to $0-local")
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("execution report contains no candidates")

    seen: set[str] = set()
    review_candidates: list[dict[str, object]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("invalid execution candidate entry")
        request_id = str(candidate.get("request_id") or "")
        if not request_id or request_id in seen:
            raise ValueError("execution report request IDs must be non-empty and unique")
        seen.add(request_id)
        seed = candidate.get("seed")
        if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
            raise ValueError(f"invalid seed for {request_id}")
        png = candidate.get("png")
        metadata = candidate.get("metadata")
        if not isinstance(png, str) or not png.strip():
            raise ValueError(f"missing proof PNG path for {request_id}")
        if not isinstance(metadata, str) or not metadata.strip():
            raise ValueError(f"missing proof metadata path for {request_id}")
        review_candidates.append({
            "request_id": request_id,
            "seed": seed,
            "png": png,
            "metadata": metadata,
            "scores": {field: None for field in SCORE_FIELDS},
            "blockers": {field: False for field in BLOCKER_FIELDS},
            "review_note": "",
        })

    return {
        "review_version": REVIEW_VERSION,
        "instructions": (
            "Inspect each real PNG before editing scores. Enter 0-10 for every score. "
            "Mark every observed hard blocker true. Do not delete candidates or alter request_id/seed."
        ),
        "candidates": review_candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a PUL7SAR Golden Visual review template")
    parser.add_argument("--execution-report", required=True)
    parser.add_argument("--output", default="output/phase18_visual_proof/golden-review.json")
    args = parser.parse_args()
    template = build_template(args.execution_report)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(template, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": "GOLDEN_REVIEW_TEMPLATE_READY",
        "output": str(output),
        "candidate_count": len(template["candidates"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
