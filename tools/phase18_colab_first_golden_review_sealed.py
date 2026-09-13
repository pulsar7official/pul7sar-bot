#!/usr/bin/env python3
"""Preferred one-command Candidate 1 staging through a verified human-review seal.

This wrapper delegates all generation/semantic work to the existing strict
`phase18_colab_first_golden_review.py`, then seals and replay-verifies every
receipt and PNG referenced by the resulting human-review packet. It never fills
the human decision template, never applies Golden scores, never authorizes
Seeds 2-4, and never grants publication authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
GPU_SMOKE = ROOT / "output" / "phase18_gpu_smoke"
PACKET = GPU_SMOKE / "first-golden-human-review-packet.json"
MANIFEST = GPU_SMOKE / "first-golden-human-review-integrity.json"
VERIFICATION = GPU_SMOKE / "first-golden-human-review-integrity-verification.json"
FINAL = GPU_SMOKE / "first-golden-human-review-sealed.json"


def _branch() -> str:
    completed = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError("SEALED_FIRST_GOLDEN_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


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


def run(*, worker_id: str, timeout_seconds: int, final_path: Path = FINAL) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("SEALED_FIRST_GOLDEN_BRANCH_BLOCKED")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    staged = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_colab_first_golden_review.py"),
            "--worker-id",
            worker_id,
            "--timeout-seconds",
            str(timeout_seconds),
            "--packet",
            str(PACKET),
        ],
        label="FIRST_GOLDEN_REVIEW_STAGING",
    )
    if staged.get("status") != "FIRST_GOLDEN_CANDIDATE_READY_FOR_HUMAN_REVIEW":
        raise RuntimeError("SEALED_FIRST_GOLDEN_STAGING_NOT_READY")
    if staged.get("candidate") != 1 or staged.get("cost_mode") != "$0-local":
        raise RuntimeError("SEALED_FIRST_GOLDEN_STAGING_IDENTITY_DRIFT")
    for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if staged.get(field) is not False:
            raise RuntimeError(f"SEALED_FIRST_GOLDEN_{field.upper()}_AUTHORITY_DRIFT")

    seal = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_seal_first_golden_review_packet.py"),
            "--packet",
            str(PACKET),
            "--manifest",
            str(MANIFEST),
            "--verification",
            str(VERIFICATION),
        ],
        label="FIRST_GOLDEN_REVIEW_SEAL",
    )
    if seal.get("status") != "FIRST_GOLDEN_REVIEW_PACKET_SEALED_AND_VERIFIED":
        raise RuntimeError("SEALED_FIRST_GOLDEN_INTEGRITY_NOT_VERIFIED")
    if seal.get("candidate") != 1 or seal.get("cost_mode") != "$0-local":
        raise RuntimeError("SEALED_FIRST_GOLDEN_SEAL_IDENTITY_DRIFT")
    for field in ("human_visual_review_approved", "golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):
        if seal.get(field) is not False:
            raise RuntimeError(f"SEALED_FIRST_GOLDEN_SEAL_{field.upper()}_AUTHORITY_DRIFT")

    payload = {
        "schema": "pul7sar-first-golden-human-review-sealed-v1",
        "status": "FIRST_GOLDEN_CANDIDATE_READY_FOR_VERIFIED_HUMAN_REVIEW",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "review_packet": str(PACKET),
        "integrity_manifest": str(MANIFEST),
        "integrity_verification": str(VERIFICATION),
        "manifest_sha256": seal["manifest_sha256"],
        "review_base_png": staged["review_base_png"],
        "review_hybrid_png": staged["review_hybrid_png"],
        "review_base_png_sha256": staged["review_base_png_sha256"],
        "review_hybrid_png_sha256": staged["review_hybrid_png_sha256"],
        "human_visual_review_required": True,
        "automatic_selection_performed": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "explicit human review of the integrity-verified SHA-bound base and Hybrid PNGs",
    }
    final_path = final_path if final_path.is_absolute() else ROOT / final_path
    final_path = final_path.resolve()
    root = ROOT.resolve()
    if final_path != root and root not in final_path.parents:
        raise RuntimeError("SEALED_FIRST_GOLDEN_OUTPUT_ESCAPES_REPOSITORY")
    final_path.parent.mkdir(parents=True, exist_ok=True)
    final_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Candidate 1 and stage a replay-verified human review packet")
    parser.add_argument("--worker-id", default="colab-first-golden-review-sealed-01")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--output", type=Path, default=FINAL)
    args = parser.parse_args()
    payload = run(worker_id=args.worker_id, timeout_seconds=args.timeout_seconds, final_path=args.output)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
