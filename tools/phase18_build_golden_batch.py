#!/usr/bin/env python3
"""Build a deterministic quality-first batch of Golden Visual GPU handoffs.

The batch deliberately varies only the seed. Prompt, platform, model, layout and
cost policy remain identical so later visual comparison is meaningful.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from tools.phase18_build_golden_handoff import build_request


DEFAULT_SEEDS = (7007001, 7007002, 7007003, 7007004)


def build_batch(output_dir: str, seeds: tuple[int, ...] = DEFAULT_SEEDS) -> dict[str, object]:
    if not seeds:
        raise ValueError("at least one Golden Visual seed is required")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Golden Visual seeds must be unique")
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    candidates: list[dict[str, object]] = []
    for index, seed in enumerate(seeds, start=1):
        request_id = f"golden-general-season-opener-{index:03d}"
        request = build_request(seed=seed, request_id=request_id)
        filename = f"candidate-{index:02d}-seed-{seed}.json"
        path = target / filename
        LocalGenerationHandoff.write(request, str(path))
        data = json.loads(path.read_text(encoding="utf-8"))
        target_width = int(request.metadata["target_width"])
        target_height = int(request.metadata["target_height"])
        candidates.append({
            "candidate": index,
            "seed": seed,
            "request_id": request_id,
            "handoff": filename,
            "payload_sha256": data["payload_sha256"],
            "model_id": request.model_id,
            "native_canvas": f"{request.width}x{request.height}",
            "target_canvas": f"{target_width}x{target_height}",
            "canvas_normalization_required": bool(request.metadata["canvas_normalization_required"]),
        })

    manifest = {
        "manifest_version": "pul7sar-golden-batch-v1",
        "benchmark": "golden-visual-general-season-opener-v1",
        "cost_mode": "$0-local",
        "selection_rule": "quality-first; compare visual quality after identical semantic gates, never select by seed order",
        "candidates": candidates,
    }
    manifest_path = target / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic PUL7SAR Golden Visual candidate batch")
    parser.add_argument("--output-dir", default="output/phase18_handoffs/golden-batch")
    parser.add_argument("--seeds", nargs="*", type=int, default=list(DEFAULT_SEEDS))
    args = parser.parse_args()
    manifest = build_batch(args.output_dir, tuple(args.seeds))
    print(json.dumps({
        "status": "GOLDEN_BATCH_READY",
        "output_dir": args.output_dir,
        "candidate_count": len(manifest["candidates"]),
        "cost_mode": manifest["cost_mode"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
