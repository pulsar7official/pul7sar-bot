#!/usr/bin/env python3
"""Lock one Dynamic Visual Brain concept before any renderer is allowed to run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.dynamic_visual_brain import DynamicVisualBrain
from engine.intelligence.dynamic_visual_brain_lock import DynamicVisualBrainConceptLock


def _inside_repo(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("DYNAMIC_VISUAL_BRAIN_LOCK_OUTPUT_OUTSIDE_REPOSITORY") from exc
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description="Lock one PUL7SAR Dynamic Visual Brain concept before rendering")
    parser.add_argument("--story-json", required=True, help="UTF-8 story JSON object")
    parser.add_argument("--concept-id", required=True, help="Exact concept_id returned by the Dynamic Visual Brain")
    parser.add_argument(
        "--output",
        default="output/phase18_visual_brain/dynamic-concept-lock.json",
        help="Repository-relative JSON receipt path",
    )
    args = parser.parse_args()

    story_path = _inside_repo(Path(args.story_json) if Path(args.story_json).is_absolute() else ROOT / args.story_json)
    payload = json.loads(story_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("story JSON must be an object")

    plan = DynamicVisualBrain().plan(payload)
    receipt = DynamicVisualBrainConceptLock.lock(plan, args.concept_id)

    output = _inside_repo(Path(args.output) if Path(args.output).is_absolute() else ROOT / args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": receipt.status,
        "contract": receipt.contract,
        "story_fingerprint": receipt.story_fingerprint,
        "competition_sha256": receipt.competition_sha256,
        "selected_concept_id": receipt.selected_concept_id,
        "selected_concept_sha256": receipt.selected_concept_sha256,
        "scene_prompt_sha256": receipt.scene_prompt_sha256,
        "publication_ready": receipt.publication_ready,
        "output": str(output.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
