#!/usr/bin/env python3
"""Execute a PUL7SAR Golden Visual handoff batch sequentially on one CUDA host.

The command intentionally delegates each candidate to the single-request executor
so every candidate passes the same integrity, cost, readiness, provenance and
canvas-normalization path. It never parallelizes GPU inference, avoiding VRAM
contention and making failures attributable to one deterministic candidate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


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
    python_executable: str = sys.executable,
    runner=subprocess.run,
) -> list[dict[str, object]]:
    manifest = load_manifest(manifest_path)
    root = Path(manifest_path).resolve().parent
    results: list[dict[str, object]] = []

    for candidate in manifest["candidates"]:
        handoff = root / str(candidate["handoff"])
        if not handoff.is_file():
            raise FileNotFoundError(f"Golden Visual handoff is missing: {handoff}")
        command = [
            python_executable,
            "tools/phase18_flux2_execute.py",
            "--request", str(handoff),
            "--generation-dir", generation_dir,
            "--proof-dir", proof_dir,
            "--dtype", dtype,
        ]
        completed = runner(command, check=True, text=True, capture_output=True)
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"candidate {candidate['request_id']} returned non-JSON executor output") from exc
        if payload.get("status") != "REAL_VISUAL_PROOF_GENERATED":
            raise RuntimeError(f"candidate {candidate['request_id']} did not produce a real visual proof")
        if int(payload.get("seed", -1)) != int(candidate["seed"]):
            raise RuntimeError(f"candidate {candidate['request_id']} returned an unexpected seed")
        results.append({
            "candidate": candidate["candidate"],
            "seed": candidate["seed"],
            "request_id": candidate["request_id"],
            "png": payload["png"],
            "metadata": payload["metadata"],
            "native_png": payload["native_png"],
        })

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute a PUL7SAR Golden Visual GPU batch sequentially")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--generation-dir", default="output/phase18_generated")
    parser.add_argument("--proof-dir", default="output/phase18_visual_proof")
    parser.add_argument("--dtype", choices=("float16", "bfloat16", "float32"), default="bfloat16")
    parser.add_argument("--result", default="output/phase18_visual_proof/batch-execution.json")
    args = parser.parse_args()

    results = execute_batch(
        args.manifest,
        generation_dir=args.generation_dir,
        proof_dir=args.proof_dir,
        dtype=args.dtype,
    )
    output = Path(args.result)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "REAL_VISUAL_PROOF_BATCH_GENERATED",
        "cost_mode": "$0-local",
        "candidate_count": len(results),
        "candidates": results,
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
