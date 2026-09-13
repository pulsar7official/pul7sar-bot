#!/usr/bin/env python3
"""Execute a PUL7SAR Golden Visual handoff batch sequentially on one CUDA host.

The command intentionally delegates each candidate to the single-request executor
so every candidate passes the same integrity, cost, readiness, provenance and
canvas-normalization path. It never parallelizes GPU inference, avoiding VRAM
contention and making failures attributable to one deterministic candidate.

Batch control reads each candidate result from a dedicated JSON file rather than
parsing stdout, because real Diffusers/Transformers runtimes may emit progress or
informational text while loading model weights. `--limit 1` provides a safe first
GPU smoke proof without changing the locked four-candidate manifest.

Golden execution is precision-locked to the documented BF16 path. `--dtype auto`
means native BF16 must be proven; no silent FP16 fallback is allowed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def load_manifest(path: str) -> dict[str, object]:
    manifest_path = Path(path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("manifest_version") != "pul7sar-golden-batch-v1":
        raise ValueError("unsupported Golden Visual batch manifest")
    if data.get("cost_mode") != "$0-local":
        raise ValueError("Golden Visual batch must remain locked to $0-local")
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Golden Visual batch contains no candidates")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("invalid Golden Visual candidate entry")
        for key in ("handoff", "seed", "request_id", "payload_sha256"):
            if key not in candidate:
                raise ValueError(f"Golden Visual candidate missing {key}")
    return data


def execute_batch(
    manifest_path: str,
    *,
    generation_dir: str,
    proof_dir: str,
    dtype: str,
    limit: int | None = None,
    python_executable: str = sys.executable,
    runner=subprocess.run,
) -> list[dict[str, object]]:
    manifest = load_manifest(manifest_path)
    all_candidates = manifest["candidates"]
    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer or None")
        if limit > len(all_candidates):
            raise ValueError("limit cannot exceed Golden Visual candidate count")
        candidates = all_candidates[:limit]
    else:
        candidates = all_candidates

    root = Path(manifest_path).resolve().parent
    results: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="pul7sar-phase18-results-") as temp_results:
        result_root = Path(temp_results)
        for candidate in candidates:
            handoff = root / str(candidate["handoff"])
            if not handoff.is_file():
                raise FileNotFoundError(f"Golden Visual handoff is missing: {handoff}")
            result_file = result_root / f"{candidate['request_id']}.json"
            command = [
                python_executable,
                "tools/phase18_flux2_execute.py",
                "--request", str(handoff),
                "--generation-dir", generation_dir,
                "--proof-dir", proof_dir,
                "--dtype", dtype,
                "--result", str(result_file),
            ]
            runner(command, check=True, text=True, capture_output=True)
            if not result_file.is_file():
                raise RuntimeError(f"candidate {candidate['request_id']} did not write its executor result file")
            try:
                payload = json.loads(result_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"candidate {candidate['request_id']} wrote invalid executor result JSON") from exc
            if payload.get("status") != "REAL_VISUAL_PROOF_GENERATED":
                raise RuntimeError(f"candidate {candidate['request_id']} did not produce a real visual proof")
            if int(payload.get("seed", -1)) != int(candidate["seed"]):
                raise RuntimeError(f"candidate {candidate['request_id']} returned an unexpected seed")
            if payload.get("request_id") not in {None, candidate["request_id"]}:
                raise RuntimeError(f"candidate {candidate['request_id']} returned an unexpected request_id")
            if payload.get("resolved_dtype") not in {None, "bfloat16"}:
                raise RuntimeError(f"candidate {candidate['request_id']} escaped the Golden BF16 precision lock")
            results.append({
                "candidate": candidate["candidate"],
                "seed": candidate["seed"],
                "request_id": candidate["request_id"],
                "png": payload["png"],
                "metadata": payload["metadata"],
                "native_png": payload["native_png"],
                "requested_dtype": payload.get("requested_dtype", dtype),
                "resolved_dtype": payload.get("resolved_dtype"),
                "gpu_name": payload.get("gpu_name"),
                "gpu_vram_gb": payload.get("gpu_vram_gb"),
                "bf16_supported": payload.get("bf16_supported"),
                "compute_capability": payload.get("compute_capability"),
            })

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a PUL7SAR Golden Visual GPU batch sequentially")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--generation-dir", default="output/phase18_generated")
    parser.add_argument("--proof-dir", default="output/phase18_visual_proof")
    parser.add_argument("--dtype", choices=("auto", "bfloat16"), default="auto")
    parser.add_argument("--limit", type=int, help="Execute only the first N locked candidates; use 1 for GPU smoke proof")
    parser.add_argument("--result", default="output/phase18_visual_proof/batch-execution.json")
    args = parser.parse_args()

    results = execute_batch(
        args.manifest,
        generation_dir=args.generation_dir,
        proof_dir=args.proof_dir,
        dtype=args.dtype,
        limit=args.limit,
    )
    output = Path(args.result)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "REAL_VISUAL_PROOF_BATCH_GENERATED",
        "cost_mode": "$0-local",
        "candidate_count": len(results),
        "execution_scope": "partial" if args.limit is not None else "full",
        "requested_limit": args.limit,
        "requested_dtype": args.dtype,
        "candidates": results,
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
