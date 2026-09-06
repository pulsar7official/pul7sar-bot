#!/usr/bin/env python3
"""Run first-Golden staging with an early, SHA-bound host-memory preflight.

This additive wrapper closes the gap between GPU/offload qualification and the
actual CPU memory pressure created by sequential offload. It proves currently
available system RAM before model work, then delegates to the existing
runtime-locked Candidate 1 path and binds both receipts by SHA-256.

It never authorizes Seeds 2-4, human acceptance, Golden approval, or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
GPU_SMOKE = ROOT / "output" / "phase18_gpu_smoke"
HOST_MEMORY = GPU_SMOKE / "host-memory-preflight.json"
RUNTIME_LOCK = GPU_SMOKE / "first-golden-runtime-locked.json"
FINAL = GPU_SMOKE / "first-golden-host-memory-locked.json"


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GOLDEN_HOST_MEMORY_LOCK_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_root(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GOLDEN_HOST_MEMORY_LOCK_PATH_ESCAPES_REPOSITORY")
    return target


def _run_json(command: list[str], *, label: str) -> dict[str, object]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout)[-4000:]
        raise RuntimeError(f"{label} failed: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} did not emit valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} emitted non-object JSON")
    return payload


def _evidence(path: Path) -> dict[str, object]:
    target = _inside_root(path)
    if not target.is_file():
        raise RuntimeError("FIRST_GOLDEN_HOST_MEMORY_LOCK_EVIDENCE_MISSING")
    return {
        "path": str(target),
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "bytes": target.stat().st_size,
    }


def _write(path: Path, payload: dict[str, object]) -> None:
    target = _inside_root(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _validate_memory(payload: dict[str, object]) -> None:
    failures: list[str] = []
    if payload.get("schema") != "pul7sar-first-golden-host-memory-preflight-v1":
        failures.append("schema_drift")
    if payload.get("branch") != EXPECTED_BRANCH:
        failures.append("branch_drift")
    if payload.get("ready") is not True:
        failures.append("host_memory_not_ready")
    if payload.get("cost_mode") != "$0-local":
        failures.append("zero_cost_drift")
    available = payload.get("available_ram_gb")
    required = payload.get("minimum_available_ram_gb")
    if not isinstance(available, (int, float)) or isinstance(available, bool):
        failures.append("available_ram_unproven")
    if not isinstance(required, (int, float)) or isinstance(required, bool) or float(required) <= 0:
        failures.append("required_ram_floor_unproven")
    elif isinstance(available, (int, float)) and not isinstance(available, bool) and float(available) < float(required):
        failures.append("available_ram_below_floor")
    for field in (
        "model_downloads_performed",
        "model_loaded",
        "generation_authorized",
        "queue_mutated",
        "png_created",
        "semantic_approved",
        "golden_quality_approved",
        "publication_ready",
    ):
        if payload.get(field) is not False:
            failures.append(f"authority_drift:{field}")
    if failures:
        raise RuntimeError("FIRST_GOLDEN_HOST_MEMORY_PREFLIGHT_BLOCKED: " + ", ".join(failures))


def _validate_runtime(payload: dict[str, object]) -> None:
    failures: list[str] = []
    if payload.get("schema") != "pul7sar-first-golden-runtime-lock-v1":
        failures.append("runtime_schema_drift")
    if payload.get("status") != "FIRST_GOLDEN_RUNTIME_LOCK_VERIFIED":
        failures.append("runtime_not_verified")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        failures.append("runtime_identity_drift")
    if payload.get("cost_mode") != "$0-local":
        failures.append("runtime_zero_cost_drift")
    if payload.get("runtime_stable_across_generation") is not True:
        failures.append("runtime_stability_unproven")
    for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if payload.get(field) is not False:
            failures.append(f"runtime_authority_drift:{field}")
    if failures:
        raise RuntimeError("FIRST_GOLDEN_HOST_MEMORY_RUNTIME_LOCK_BLOCKED: " + ", ".join(failures))


def run(*, worker_id: str, timeout_seconds: int, final_path: Path = FINAL) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GOLDEN_HOST_MEMORY_LOCK_BRANCH_BLOCKED")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    memory = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_preflight_host_memory.py"),
            "--output",
            str(HOST_MEMORY),
        ],
        label="FIRST_GOLDEN_HOST_MEMORY_PREFLIGHT",
    )
    _validate_memory(memory)
    memory_evidence = _evidence(HOST_MEMORY)

    runtime = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_colab_first_golden_runtime_locked.py"),
            "--worker-id",
            worker_id,
            "--timeout-seconds",
            str(timeout_seconds),
            "--output",
            str(RUNTIME_LOCK),
        ],
        label="FIRST_GOLDEN_RUNTIME_LOCKED_PIPELINE",
    )
    _validate_runtime(runtime)
    runtime_evidence = _evidence(RUNTIME_LOCK)

    payload: dict[str, object] = {
        "schema": "pul7sar-first-golden-host-memory-lock-v1",
        "status": "FIRST_GOLDEN_HOST_MEMORY_AND_RUNTIME_LOCK_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "host_memory_ready": True,
        "available_ram_gb_before_model_work": memory.get("available_ram_gb"),
        "minimum_available_ram_gb": memory.get("minimum_available_ram_gb"),
        "runtime_stable_across_generation": True,
        "evidence": {
            "host_memory_preflight": memory_evidence,
            "runtime_lock": runtime_evidence,
        },
        "review_base_png": runtime.get("review_base_png"),
        "review_hybrid_png": runtime.get("review_hybrid_png"),
        "review_base_png_sha256": runtime.get("review_base_png_sha256"),
        "review_hybrid_png_sha256": runtime.get("review_hybrid_png_sha256"),
        "human_visual_review_required": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "explicit human review of the sealed Candidate 1 base and Hybrid PNGs",
    }
    _write(final_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run first-Golden staging with a fail-closed host-memory preflight")
    parser.add_argument("--worker-id", default="colab-first-golden-host-memory-lock-01")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--output", type=Path, default=FINAL)
    args = parser.parse_args()
    payload = run(worker_id=args.worker_id, timeout_seconds=args.timeout_seconds, final_path=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
