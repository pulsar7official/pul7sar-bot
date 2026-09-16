#!/usr/bin/env python3
"""Prove a safe FLUX.2 CPU-offload path before loading model weights.

This preflight consumes the already-generated GPU host qualification receipt and
inspects the installed Diffusers Flux2KleinPipeline class. It performs no model
load/download, no queue mutation, no image generation, and grants no publication
or Golden authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
DEFAULT_HOST_RECEIPT = ROOT / "output" / "phase18_gpu_host" / "qualification.json"
DEFAULT_OUTPUT = ROOT / "output" / "phase18_gpu_smoke" / "flux2-offload-preflight.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_MODEL_ID
from engine.intelligence.flux2_offload_capability import Flux2OffloadCapabilityProbe


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_root(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_PATH_ESCAPES_REPOSITORY")
    return target


def _load_host(path: Path) -> dict[str, object]:
    target = _inside_root(path)
    if not target.is_file():
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_HOST_RECEIPT_MISSING")
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_HOST_RECEIPT_INVALID_JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_HOST_RECEIPT_NOT_OBJECT")
    return payload


def run(*, host_receipt: Path = DEFAULT_HOST_RECEIPT, output: Path = DEFAULT_OUTPUT) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_BRANCH_BLOCKED")
    host = _load_host(host_receipt)
    if host.get("eligible") is not True:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_HOST_NOT_ELIGIBLE")
    if host.get("model_id") != FLUX2_KLEIN_4B_MODEL_ID:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_MODEL_IDENTITY_DRIFT")
    if host.get("runtime_kind") != "local_cuda" or host.get("cuda_available") is not True:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_CUDA_NOT_PROVEN")
    if host.get("bf16_supported") is not True:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_BF16_NOT_PROVEN")
    if host.get("cost_mode") != "$0-local":
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_ZERO_COST_POLICY_DRIFT")
    total_vram = host.get("gpu_vram_gb")
    if not isinstance(total_vram, (int, float)) or isinstance(total_vram, bool) or float(total_vram) <= 0:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_TOTAL_VRAM_NOT_PROVEN")

    report = Flux2OffloadCapabilityProbe().inspect(total_vram_gb=float(total_vram))
    payload: dict[str, object] = {
        "schema": "pul7sar-phase18-flux2-offload-preflight-v1",
        "branch": EXPECTED_BRANCH,
        "ready": report.ready,
        "model_id": report.model_id,
        "diffusers_version": report.diffusers_version,
        "pipeline_available": report.pipeline_available,
        "sequential_cpu_offload_available": report.sequential_cpu_offload_available,
        "model_cpu_offload_available": report.model_cpu_offload_available,
        "gpu_vram_gb": report.total_vram_gb,
        "model_offload_minimum_total_vram_gb": report.model_offload_minimum_total_vram_gb,
        "low_vram_host": report.low_vram_host,
        "selected_safe_mode": report.selected_safe_mode,
        "reasons": list(report.reasons),
        "cost_mode": "$0-local",
        "model_loaded": False,
        "downloads_performed": False,
        "generation_authorized": False,
        "queue_mutated": False,
        "png_created": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    if not report.ready:
        raise RuntimeError("FLUX2_OFFLOAD_PREFLIGHT_BLOCKED: " + ", ".join(report.reasons))

    target = _inside_root(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Prove a safe FLUX.2 CPU-offload mode before loading model weights")
    parser.add_argument("--host-qualification", type=Path, default=DEFAULT_HOST_RECEIPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(host_receipt=args.host_qualification, output=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
