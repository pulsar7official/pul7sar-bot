#!/usr/bin/env python3
"""Run the strict first-Golden Colab path with pre/post software fingerprinting.

This wrapper repairs the runtime once, captures the exact software stack, then
runs the existing strict Candidate 1 bootstrap with --skip-repair. After the
sealed review packet is produced it captures the runtime again and fails closed
unless the fingerprint is byte-for-byte equivalent at the contract level.

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
PRE = GPU_SMOKE / "generation-runtime-fingerprint-pre.json"
POST = GPU_SMOKE / "generation-runtime-fingerprint-post.json"
STRICT_BOOTSTRAP = GPU_SMOKE / "first-golden-colab-bootstrap.json"
FINAL = GPU_SMOKE / "first-golden-runtime-locked.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.intelligence.generation_runtime_fingerprint import (
    capture_generation_runtime_fingerprint,
    verify_matching_runtime_fingerprints,
)
import tools.phase18_colab_bootstrap as runtime_bootstrap


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_root(value: Path) -> Path:
    target = value if value.is_absolute() else ROOT / value
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_PATH_ESCAPES_REPOSITORY")
    return target


def _write_json(path: Path, payload: dict[str, object]) -> None:
    target = _inside_root(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _evidence_record(path: Path) -> dict[str, object]:
    target = _inside_root(path)
    if not target.is_file():
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_EVIDENCE_MISSING")
    return {
        "path": str(target),
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "bytes": target.stat().st_size,
    }


def _run_strict_bootstrap(*, worker_id: str, timeout_seconds: int) -> dict[str, object]:
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_colab_first_golden_bootstrap.py"),
            "--worker-id",
            worker_id,
            "--timeout-seconds",
            str(timeout_seconds),
            "--skip-repair",
            "--output",
            str(STRICT_BOOTSTRAP),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout)[-4000:]
        raise RuntimeError(f"FIRST_GOLDEN_RUNTIME_LOCK_STRICT_BOOTSTRAP_FAILED: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_STRICT_BOOTSTRAP_INVALID_JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_STRICT_BOOTSTRAP_NOT_OBJECT")
    return payload


def run(*, worker_id: str, timeout_seconds: int, final_path: Path = FINAL) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_BRANCH_BLOCKED")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    # Repair once in the parent process, then freeze the resolved environment.
    runtime_bootstrap._repair_runtime()
    before = capture_generation_runtime_fingerprint()
    _write_json(PRE, before)

    staged = _run_strict_bootstrap(worker_id=worker_id, timeout_seconds=timeout_seconds)
    if staged.get("status") != "FIRST_GOLDEN_COLAB_REVIEW_PACKET_READY":
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_REVIEW_NOT_READY")
    if staged.get("branch") != EXPECTED_BRANCH or staged.get("candidate") != 1:
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_IDENTITY_DRIFT")
    if staged.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GOLDEN_RUNTIME_LOCK_COST_MODE_DRIFT")
    for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if staged.get(field) is not False:
            raise RuntimeError(f"FIRST_GOLDEN_RUNTIME_LOCK_AUTHORITY_DRIFT:{field}")

    after = capture_generation_runtime_fingerprint()
    _write_json(POST, after)
    fingerprint_sha = verify_matching_runtime_fingerprints(before, after)

    evidence = {
        "runtime_fingerprint_pre": _evidence_record(PRE),
        "runtime_fingerprint_post": _evidence_record(POST),
        "strict_bootstrap": _evidence_record(STRICT_BOOTSTRAP),
    }
    payload: dict[str, object] = {
        "schema": "pul7sar-first-golden-runtime-lock-v1",
        "status": "FIRST_GOLDEN_RUNTIME_LOCK_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "runtime_fingerprint_sha256": fingerprint_sha,
        "runtime_stable_across_generation": True,
        "runtime_fingerprint_pre": str(PRE),
        "runtime_fingerprint_post": str(POST),
        "strict_bootstrap": str(STRICT_BOOTSTRAP),
        "evidence": evidence,
        "review_base_png": staged.get("review_base_png"),
        "review_hybrid_png": staged.get("review_hybrid_png"),
        "review_base_png_sha256": staged.get("review_base_png_sha256"),
        "review_hybrid_png_sha256": staged.get("review_hybrid_png_sha256"),
        "human_visual_review_required": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "explicit human review of the sealed Candidate 1 base and Hybrid PNGs",
    }
    _write_json(final_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the strict first-Golden path with immutable software-runtime fingerprinting")
    parser.add_argument("--worker-id", default="colab-first-golden-runtime-lock-01")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--output", type=Path, default=FINAL)
    args = parser.parse_args()
    payload = run(worker_id=args.worker_id, timeout_seconds=args.timeout_seconds, final_path=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
