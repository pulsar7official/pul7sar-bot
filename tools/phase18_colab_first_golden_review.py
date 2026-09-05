#!/usr/bin/env python3
"""Run Candidate 1 through the current Golden Hybrid path up to human review.

This is a strict orchestration wrapper for a compatible CUDA/BF16 Colab or
self-hosted GPU runtime. It does not implement a new generator, does not choose
a visual automatically, and never grants Golden or publication authority.

The command intentionally stops after preparing the exact SHA-bound human-review
bundle and its decision template:

Original Scene admission -> Candidate 1 -> provenance -> Hybrid handoff ->
BASE_SCENE/HYBRID_SURFACE QA -> human-review bundle -> human-review template.

Seeds 2-4 are never requested by this tool.
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
COLAB_SUMMARY = ROOT / "output" / "phase18_colab" / "latest.json"
ORIGINAL_SCENE_ADMISSION = GPU_SMOKE / "original-scene-runtime-admission.json"
CONTINUATION = GPU_SMOKE / "hybrid-semantic-continuation.json"
REVIEW_BUNDLE = GPU_SMOKE / "hybrid-human-review-bundle.json"
REVIEW_TEMPLATE = GPU_SMOKE / "hybrid-human-review-template.json"
PACKET = GPU_SMOKE / "first-golden-human-review-packet.json"


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _inside_root(path: Path) -> Path:
    resolved = path if path.is_absolute() else ROOT / path
    resolved = resolved.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_PATH_ESCAPES_REPOSITORY")
    return resolved


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_json(command: list[str], *, label: str) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout)[-4000:]
        raise RuntimeError(f"{label} failed: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{label} did not emit valid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{label} emitted a non-object JSON payload")
    return payload


def _require_false(payload: dict[str, object], *fields: str, label: str) -> None:
    for field in fields:
        if payload.get(field) is not False:
            raise RuntimeError(f"{label}_{field.upper()}_AUTHORITY_DRIFT")


def _write_receipt(path: Path, payload: dict[str, object]) -> None:
    path = _inside_root(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _require_original_scene_receipt_binding(original_scene_run: dict[str, object], receipt_path: Path) -> tuple[str, int]:
    if original_scene_run.get("original_scene_admission_replayed") is not True:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_NOT_REPLAYED")
    recorded_path = original_scene_run.get("original_scene_admission_receipt")
    if not isinstance(recorded_path, str) or not recorded_path.strip():
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_RECEIPT_PATH_MISSING")
    if _inside_root(Path(recorded_path)) != receipt_path:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_RECEIPT_PATH_DRIFT")
    recorded_sha = original_scene_run.get("original_scene_admission_sha256")
    recorded_bytes = original_scene_run.get("original_scene_admission_bytes")
    if not isinstance(recorded_sha, str) or len(recorded_sha) != 64:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_SHA_MISSING")
    if not isinstance(recorded_bytes, int) or recorded_bytes <= 0:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_SIZE_MISSING")
    if not receipt_path.is_file():
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_RECEIPT_MISSING")
    if _sha256(receipt_path) != recorded_sha or receipt_path.stat().st_size != recorded_bytes:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_REPLAY_BINDING_FAILED")
    return recorded_sha, recorded_bytes


def run(*, worker_id: str, timeout_seconds: int, packet_path: Path = PACKET) -> dict[str, object]:
    if _branch() != EXPECTED_BRANCH:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_BRANCH_BLOCKED")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    GPU_SMOKE.mkdir(parents=True, exist_ok=True)

    # 1) Admit the measured local runtime for the provider-neutral Original Scene
    # contract, then generate/reuse Candidate 1 through the already hardened
    # first-PNG path. The wrapper preserves repository integrity, CUDA/BF16,
    # Qwen preflight, FLUX snapshot locks and provenance postflight.
    original_scene_run = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_first_png_original_scene.py"),
            "--admission-receipt",
            str(ORIGINAL_SCENE_ADMISSION),
            "--worker-id",
            worker_id,
            "--timeout-seconds",
            str(timeout_seconds),
        ],
        label="FIRST_GOLDEN_ORIGINAL_SCENE_CANDIDATE",
    )
    if original_scene_run.get("status") != "FIRST_GOLDEN_PNG_ORIGINAL_SCENE_PATH_COMPLETE":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_PATH_NOT_COMPLETE")
    admission = original_scene_run.get("original_scene_admission")
    first_png = original_scene_run.get("first_png")
    if not isinstance(admission, dict) or not isinstance(first_png, dict):
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_EVIDENCE_MISSING")
    if admission.get("status") != "GOLDEN_ORIGINAL_SCENE_RUNTIME_ADMITTED":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_NOT_ADMITTED")
    if admission.get("candidate") != 1 or admission.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_IDENTITY_DRIFT")
    if admission.get("resolved_dtype") != "bfloat16" or admission.get("runtime_ready") is not True:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_RUNTIME_DRIFT")
    _require_false(
        admission,
        "generation_authorized",
        "queue_mutated",
        "png_created",
        "semantic_approved",
        "golden_quality_approved",
        "publication_ready",
        label="FIRST_GOLDEN_ORIGINAL_SCENE_ADMISSION",
    )
    admission_receipt = _inside_root(ORIGINAL_SCENE_ADMISSION)
    admission_sha256, admission_bytes = _require_original_scene_receipt_binding(original_scene_run, admission_receipt)
    if first_png.get("candidate") != 1:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_CANDIDATE_DRIFT")
    if first_png.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_COST_MODE_DRIFT")
    _require_false(first_png, "publication_ready", label="FIRST_GOLDEN_CANDIDATE")
    _write_receipt(GPU_SMOKE / "first-png-result.json", first_png)

    # 2) Bridge the provenance-bound Candidate 1 bytes into the canonical v5
    # semantic path without re-running FLUX.
    handoff = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_build_first_png_hybrid_handoff.py"),
            "--output",
            str(COLAB_SUMMARY),
        ],
        label="FIRST_GOLDEN_HYBRID_HANDOFF",
    )
    if handoff.get("status") != "FIRST_GOLDEN_PNG_HYBRID_HANDOFF_READY":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_HANDOFF_NOT_READY")
    if handoff.get("candidate") != 1 or handoff.get("manifest_version") != "pul7sar-golden-batch-v5":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_HANDOFF_IDENTITY_DRIFT")
    _require_false(
        handoff,
        "semantic_layer_gate_approved",
        "hybrid_semantic_review_approved",
        "golden_quality_approved",
        "publication_ready",
        label="FIRST_GOLDEN_HANDOFF",
    )
    _write_receipt(GPU_SMOKE / "first-png-hybrid-handoff.json", handoff)

    # 3) Run strict BASE_SCENE ownership QA, deterministic football composition,
    # artifact-integrity replay and HYBRID_SURFACE semantic/alignment QA.
    continuation = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_continue_hybrid_from_first_png.py"),
            "--candidate",
            "1",
            "--handoff",
            str(COLAB_SUMMARY),
            "--output",
            str(CONTINUATION),
        ],
        label="FIRST_GOLDEN_HYBRID_SEMANTIC_CONTINUATION",
    )
    if continuation.get("status") != "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_HYBRID_SEMANTIC_NOT_READY")
    if continuation.get("candidate") != 1:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_CONTINUATION_CANDIDATE_DRIFT")
    if continuation.get("semantic_layer_gate_approved") is not True:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_BASE_SEMANTIC_GATE_BLOCKED")
    if continuation.get("hybrid_semantic_review_approved") is not True:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_HYBRID_SEMANTIC_GATE_BLOCKED")
    _require_false(continuation, "golden_quality_approved", "publication_ready", label="FIRST_GOLDEN_CONTINUATION")

    # 4) Copy exactly the approved base/Hybrid bytes into a stable human-review
    # directory and record their SHA-256 values.
    bundle = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_prepare_hybrid_human_review.py"),
            "--continuation",
            str(CONTINUATION),
            "--receipt",
            str(REVIEW_BUNDLE),
        ],
        label="FIRST_GOLDEN_HUMAN_REVIEW_BUNDLE",
    )
    if bundle.get("status") != "HYBRID_HUMAN_REVIEW_BUNDLE_READY":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_BUNDLE_NOT_READY")
    if bundle.get("human_visual_review_required") is not True or bundle.get("automatic_selection_performed") is not False:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_HUMAN_AUTHORITY_DRIFT")
    _require_false(bundle, "golden_quality_approved", "publication_ready", label="FIRST_GOLDEN_REVIEW_BUNDLE")

    # 5) Build, but never fill or evaluate, the human-decision template.
    template = _run_json(
        [
            sys.executable,
            str(ROOT / "tools" / "phase18_build_hybrid_human_review_template.py"),
            "--bundle",
            str(REVIEW_BUNDLE),
            "--output",
            str(REVIEW_TEMPLATE),
        ],
        label="FIRST_GOLDEN_HUMAN_REVIEW_TEMPLATE",
    )
    if template.get("status") != "HYBRID_HUMAN_REVIEW_DECISION_TEMPLATE":
        raise RuntimeError("FIRST_GOLDEN_REVIEW_TEMPLATE_NOT_READY")
    if template.get("decision") is not None:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_AUTOMATIC_DECISION_FORBIDDEN")
    _require_false(template, "golden_quality_approved", "publication_ready", label="FIRST_GOLDEN_REVIEW_TEMPLATE")

    review_base = _inside_root(Path(str(bundle["review_base_png"])))
    review_hybrid = _inside_root(Path(str(bundle["review_hybrid_png"])))
    for value, label in ((review_base, "BASE"), (review_hybrid, "HYBRID")):
        if not value.is_file() or value.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"FIRST_GOLDEN_REVIEW_{label}_PNG_INVALID")

    # The packet must carry the exact admission digest that was proven both
    # before and after Candidate 1 generation by the Original Scene wrapper.
    if _sha256(admission_receipt) != admission_sha256 or admission_receipt.stat().st_size != admission_bytes:
        raise RuntimeError("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_DRIFT_BEFORE_PACKET")

    payload: dict[str, object] = {
        "schema": "pul7sar-first-golden-human-review-packet-v2",
        "status": "FIRST_GOLDEN_CANDIDATE_READY_FOR_HUMAN_REVIEW",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "original_scene_runtime_admission": str(admission_receipt),
        "original_scene_runtime_admission_sha256": admission_sha256,
        "original_scene_runtime_admission_bytes": admission_bytes,
        "original_scene_runtime_admission_replayed": True,
        "first_png_result": str(GPU_SMOKE / "first-png-result.json"),
        "hybrid_handoff": str(GPU_SMOKE / "first-png-hybrid-handoff.json"),
        "hybrid_semantic_continuation": str(CONTINUATION),
        "human_review_bundle": str(REVIEW_BUNDLE),
        "human_review_template": str(REVIEW_TEMPLATE),
        "review_base_png": str(review_base),
        "review_hybrid_png": str(review_hybrid),
        "review_base_png_sha256": _sha256(review_base),
        "review_hybrid_png_sha256": _sha256(review_hybrid),
        "human_visual_review_required": True,
        "automatic_selection_performed": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
        "next_gate": "explicit human review of the exact SHA-bound base and Hybrid PNGs",
    }
    _write_receipt(packet_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Candidate 1 through Original Scene admission and stage the exact Golden Hybrid proof for explicit human review"
    )
    parser.add_argument("--worker-id", default="colab-first-golden-review-01")
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--packet", type=Path, default=PACKET)
    args = parser.parse_args()
    payload = run(worker_id=args.worker_id, timeout_seconds=args.timeout_seconds, packet_path=args.packet)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
