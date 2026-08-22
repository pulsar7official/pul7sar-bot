#!/usr/bin/env python3
"""Verify a Golden Visual handoff batch without CUDA or model downloads.

This command is the transport/preflight boundary between CI and a GPU runtime.
It validates the manifest, every v2 handoff SHA-256, request/seed/model identity,
zero-cost policy, canvas contract, and one-to-one file coverage before expensive
model loading begins.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


def verify_batch(manifest_path: str) -> dict[str, object]:
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("manifest_version") != "pul7sar-golden-batch-v1":
        raise ValueError("unsupported Golden Visual batch manifest version")
    if manifest.get("cost_mode") != "$0-local":
        raise ValueError("Golden Visual batch must remain locked to $0-local")
    candidates = manifest.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Golden Visual batch manifest contains no candidates")

    root = path.resolve().parent
    seen_ids: set[str] = set()
    seen_seeds: set[int] = set()
    seen_files: set[str] = set()
    verified: list[dict[str, object]] = []

    for item in candidates:
        if not isinstance(item, dict):
            raise ValueError("invalid Golden Visual candidate manifest entry")
        request_id = str(item.get("request_id") or "")
        seed = item.get("seed")
        handoff_name = str(item.get("handoff") or "")
        declared_hash = str(item.get("payload_sha256") or "")
        if not request_id or request_id in seen_ids:
            raise ValueError("candidate request IDs must be non-empty and unique")
        if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0 or seed in seen_seeds:
            raise ValueError("candidate seeds must be unique non-negative integers")
        if not handoff_name or handoff_name in seen_files or Path(handoff_name).name != handoff_name:
            raise ValueError("candidate handoff filenames must be unique simple filenames")
        seen_ids.add(request_id)
        seen_seeds.add(seed)
        seen_files.add(handoff_name)

        handoff_path = root / handoff_name
        if not handoff_path.is_file():
            raise FileNotFoundError(f"Golden Visual handoff is missing: {handoff_name}")
        raw = json.loads(handoff_path.read_text(encoding="utf-8"))
        if raw.get("payload_sha256") != declared_hash:
            raise ValueError(f"manifest/handoff SHA-256 mismatch for {request_id}")
        request = LocalGenerationHandoff.read(str(handoff_path))
        if request.request_id != request_id:
            raise ValueError(f"request ID mismatch for {handoff_name}")
        if request.seed != seed:
            raise ValueError(f"seed mismatch for {request_id}")
        if request.provider_id != FLUX2_KLEIN_4B_LOCAL.provider_id:
            raise ValueError(f"unexpected provider for {request_id}")
        if request.model_id != FLUX2_KLEIN_4B_LOCAL.model_id:
            raise ValueError(f"unexpected model for {request_id}")
        if request.backend != "diffusers":
            raise ValueError(f"unexpected backend for {request_id}")
        if request.metadata.get("cost_mode") != "$0-local":
            raise ValueError(f"candidate {request_id} escaped $0-local mode")
        target_width = request.metadata.get("target_width")
        target_height = request.metadata.get("target_height")
        expected_target = item.get("target_canvas")
        actual_target = f"{target_width}x{target_height}"
        if expected_target != actual_target:
            raise ValueError(f"target canvas mismatch for {request_id}")
        if item.get("native_canvas") != f"{request.width}x{request.height}":
            raise ValueError(f"native canvas mismatch for {request_id}")

        verified.append({
            "request_id": request_id,
            "seed": seed,
            "payload_sha256": declared_hash,
            "native_canvas": f"{request.width}x{request.height}",
            "target_canvas": actual_target,
        })

    json_files = {entry.name for entry in root.glob("candidate-*.json") if entry.is_file()}
    if json_files != seen_files:
        extras = sorted(json_files - seen_files)
        missing = sorted(seen_files - json_files)
        details = []
        if extras:
            details.append("unmanifested=" + ",".join(extras))
        if missing:
            details.append("missing=" + ",".join(missing))
        raise ValueError("candidate file coverage mismatch: " + "; ".join(details))

    return {
        "status": "GOLDEN_BATCH_INTEGRITY_VERIFIED",
        "cost_mode": "$0-local",
        "candidate_count": len(verified),
        "candidates": verified,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a PUL7SAR Golden Visual batch before GPU execution")
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    result = verify_batch(args.manifest)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
