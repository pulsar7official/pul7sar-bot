#!/usr/bin/env python3
"""Apply the PUL7SAR Golden Visual scorecard to a generated candidate batch.

The command consumes the batch execution report plus explicit review scores. It
cannot infer visual quality by itself; it only enforces the approved thresholds,
hard blockers, seed/request identity and quality-first selection semantics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.golden_visual_quality import (
    GoldenVisualBlockers,
    GoldenVisualEvaluation,
    GoldenVisualQualitySelector,
    GoldenVisualScores,
)


_SCORE_FIELDS = (
    "editorial_realism",
    "composition_hierarchy",
    "stadium_depth",
    "controlled_lighting",
    "protected_zone_cleanliness",
    "platform_crop_strength",
)
_BLOCKER_FIELDS = (
    "fantasy_or_monumental_staging",
    "fake_logo_or_crest",
    "pseudo_text_or_gibberish",
    "invented_result_or_winner",
    "cluttered_collage",
    "broken_geometry_or_anatomy",
)


def _load_json(path: str) -> dict[str, object]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("review input must be a JSON object")
    return data


def evaluate(execution_report: str, review_file: str) -> dict[str, object]:
    execution = _load_json(execution_report)
    review = _load_json(review_file)
    if execution.get("status") != "REAL_VISUAL_PROOF_BATCH_GENERATED":
        raise ValueError("execution report is not a completed real visual proof batch")
    if execution.get("cost_mode") != "$0-local":
        raise ValueError("execution report is not locked to $0-local")
    generated = execution.get("candidates")
    reviews = review.get("candidates")
    if not isinstance(generated, list) or not generated:
        raise ValueError("execution report contains no candidates")
    if not isinstance(reviews, list) or not reviews:
        raise ValueError("review file contains no candidates")

    generated_by_id = {str(item["request_id"]): item for item in generated if isinstance(item, dict) and "request_id" in item}
    if len(generated_by_id) != len(generated):
        raise ValueError("execution report request IDs must be unique and complete")

    evaluations: list[GoldenVisualEvaluation] = []
    seen: set[str] = set()
    for item in reviews:
        if not isinstance(item, dict):
            raise ValueError("invalid review candidate entry")
        request_id = str(item.get("request_id") or "")
        if not request_id or request_id in seen:
            raise ValueError("review request IDs must be non-empty and unique")
        seen.add(request_id)
        generated_item = generated_by_id.get(request_id)
        if generated_item is None:
            raise ValueError(f"review references unknown generated candidate: {request_id}")
        seed = int(item.get("seed", -1))
        if seed != int(generated_item["seed"]):
            raise ValueError(f"review seed mismatch for {request_id}")

        scores_data = item.get("scores")
        blockers_data = item.get("blockers", {})
        if not isinstance(scores_data, dict):
            raise ValueError(f"review scores missing for {request_id}")
        if not isinstance(blockers_data, dict):
            raise ValueError(f"review blockers invalid for {request_id}")
        missing_scores = [field for field in _SCORE_FIELDS if field not in scores_data]
        if missing_scores:
            raise ValueError(f"review scores incomplete for {request_id}: {', '.join(missing_scores)}")

        scores = GoldenVisualScores(**{field: float(scores_data[field]) for field in _SCORE_FIELDS})
        blockers = GoldenVisualBlockers(**{field: bool(blockers_data.get(field, False)) for field in _BLOCKER_FIELDS})
        evaluations.append(GoldenVisualEvaluation(request_id, seed, scores, blockers))

    if seen != set(generated_by_id):
        missing = sorted(set(generated_by_id) - seen)
        raise ValueError("review file does not cover every generated candidate: " + ", ".join(missing))

    selection = GoldenVisualQualitySelector().select(tuple(evaluations))
    ranked = [{
        "request_id": item.request_id,
        "seed": item.seed,
        "weighted_score": item.scores.weighted_score,
        "approved": item.approved,
        "blockers": list(item.blockers.active),
        "png": generated_by_id[item.request_id]["png"],
        "metadata": generated_by_id[item.request_id]["metadata"],
    } for item in selection.ranked]
    selected = None
    if selection.selected is not None:
        item = selection.selected
        selected = {
            "request_id": item.request_id,
            "seed": item.seed,
            "weighted_score": item.scores.weighted_score,
            "png": generated_by_id[item.request_id]["png"],
            "metadata": generated_by_id[item.request_id]["metadata"],
        }

    return {
        "status": "GOLDEN_VISUAL_SELECTED" if selected else "NO_GOLDEN_VISUAL_APPROVED",
        "selected": selected,
        "ranked": ranked,
        "rejected_request_ids": list(selection.rejected_request_ids),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Review and select a PUL7SAR Golden Visual candidate")
    parser.add_argument("--execution-report", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--output", default="output/phase18_visual_proof/golden-selection.json")
    args = parser.parse_args()
    result = evaluate(args.execution_report, args.review)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["selected"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
