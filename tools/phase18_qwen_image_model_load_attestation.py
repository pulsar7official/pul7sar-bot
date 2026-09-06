#!/usr/bin/env python3
"""Attempt and record a local-only Qwen-Image model load for Phase 18."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_model_load_attestation import attempt_qwen_image_model_load


def _inside_repo(path: Path) -> Path:
    root = Path.cwd().resolve()
    resolved = path.expanduser().resolve()
    if resolved != root and root not in resolved.parents:
        raise SystemExit(f"output path must stay inside repository: {resolved}")
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-path", required=True, help="Already-local immutable Hugging Face snapshots/<revision> directory")
    parser.add_argument("--output", default="output/phase18_gpu_host/qwen-image-model-load-attestation.json")
    parser.add_argument("--require-loaded", action="store_true", help="Return non-zero unless the genuine model load succeeded")
    args = parser.parse_args()

    result = attempt_qwen_image_model_load(snapshot_path=args.snapshot_path)
    payload = result.to_dict()
    output = _inside_repo(Path(args.output))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.require_loaded and not (result.model_loaded and result.sequential_cpu_offload_enabled):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
