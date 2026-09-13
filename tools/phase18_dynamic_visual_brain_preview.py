#!/usr/bin/env python3
"""Preview dynamic PUL7SAR visual concepts from one explicit story JSON payload."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview dynamic PUL7SAR Visual Brain concepts")
    parser.add_argument("--story-json", help="Path to a UTF-8 JSON object. If omitted, read JSON from stdin.")
    args = parser.parse_args()

    if args.story_json:
        payload = json.loads(Path(args.story_json).read_text(encoding="utf-8"))
    else:
        payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise TypeError("story JSON must be an object")

    plan = DynamicVisualBrain().plan(payload)
    result = {
        "status": "DYNAMIC_VISUAL_BRAIN_CONCEPTS_READY",
        "contract": plan.contract,
        "story_fingerprint": plan.story_fingerprint,
        "event": plan.event.value,
        "headline": plan.story.headline,
        "primary_entity": plan.story.primary_entity,
        "publication_ready": False,
        "concept_count": len(plan.concepts),
        "concepts": [
            {
                "concept_id": c.concept_id,
                "title": c.title,
                "editorial_metaphor": c.editorial_metaphor,
                "camera_language": c.camera_language,
                "focal_strategy": c.focal_strategy,
                "negative_space_strategy": c.negative_space_strategy,
                "signature_elements": list(c.signature_elements),
                "forbidden_elements": list(c.forbidden_elements),
                "preflight_score": c.preflight_score,
                "scene_prompt": c.scene_prompt,
            }
            for c in plan.concepts
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
