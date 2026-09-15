#!/usr/bin/env python3
"""Fail-closed canonical Golden v6 launcher with attested pre-GPU proof.

This wrapper is intentionally narrow. It runs the existing attested first-Golden
pre-GPU contract against an immutable source commit, builds and validates the
machine-readable GPU handoff from that exact attested summary, binds the exact
handoff/workflow/launcher bytes into a first-Golden GPU attempt contract, replays
those SHA-256 bindings immediately before generation, then independently replays
the produced resource-lock receipt and PNG before reporting readiness. It does
not weaken or replace any downstream factual, identity, sentiment,
semantic-publication, visual-quality, BF16, local-cache, or human-review gate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_build_first_golden_gpu_handoff import build as build_gpu_handoff
from tools.phase18_prepare_first_golden_gpu_attempt import build as build_gpu_attempt_contract
from tools.phase18_run_first_golden_pre_gpu_attested import run as run_attested_pre_gpu

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
CANONICAL_WORKFLOW = ".github/workflows/phase18-first-genuine-golden-v6.yml"
CANONICAL_LAUNCHER = "tools/phase18_run_first_genuine_golden_v6_canonical_attested.py"
ATTEMPT_SCHEMA = "pul7sar-phase18-first-golden-gpu-attempt-contract-v1"
RESOURCE_LOCK_SCHEMA = "pul7sar-first-genuine-golden-v6-resource-lock-v4"
RESOURCE_LOCK_STATUS = "FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _inside_repository(path: Path) -> Path:
    resolved = path if path.is_absolute() else ROOT / path
    resolved = resolved.resolve()
    root = ROOT.resolve()
    if resolved != root and root not in resolved.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_CANONICAL_OUTPUT_ESCAPES_REPOSITORY")
    return resolved


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _closed_authorities() -> dict[str, bool]:
    return {
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _attempt_contract_blockers(
    *,
    attempt: dict[str, object],
    expected_commit: str,
    handoff_target: Path,
) -> list[str]:
    blockers: list[str] = []
    if attempt.get("schema") != ATTEMPT_SCHEMA:
        blockers.append("GPU_ATTEMPT_SCHEMA_DRIFT")
    if attempt.get("expected_commit") != expected_commit:
        blockers.append("GPU_ATTEMPT_COMMIT_DRIFT")
    if attempt.get("branch_required") != "phase18/story-intelligence":
        blockers.append("GPU_ATTEMPT_BRANCH_DRIFT")
    if attempt.get("cost_mode_required") != "$0-local":
        blockers.append("GPU_ATTEMPT_COST_MODE_DRIFT")
    if attempt.get("offline_required") is not True:
        blockers.append("GPU_ATTEMPT_OFFLINE_POLICY_DRIFT")
    if attempt.get("attempt_contract_ready") is not True:
        blockers.append("GPU_ATTEMPT_NOT_READY")
    if attempt.get("blockers") != []:
        blockers.append("GPU_ATTEMPT_BLOCKERS_REMAIN")
    if attempt.get("workflow_dispatch_performed") is not False or attempt.get("png_created") is not False:
        blockers.append("GPU_ATTEMPT_PREEXECUTION_STATE_DRIFT")
    for field in (
        "authoritative_gate",
        "network_download_authorized",
        "generation_authorized",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if attempt.get(field) is not False:
            blockers.append(f"GPU_ATTEMPT_AUTHORITY_DRIFT_{field.upper()}")

    workflow_target = ROOT / CANONICAL_WORKFLOW
    launcher_target = ROOT / CANONICAL_LAUNCHER
    expected_hashes = {
        "source_handoff_sha256": _sha256(handoff_target),
        "canonical_workflow_sha256": _sha256(workflow_target),
        "canonical_launcher_sha256": _sha256(launcher_target),
    }
    for field, actual in expected_hashes.items():
        if attempt.get(field) != actual:
            blockers.append(f"GPU_ATTEMPT_CONTENT_DRIFT_{field.upper()}")
    return blockers


def _canonical_output_blockers(*, output_target: Path) -> tuple[list[str], dict[str, object] | None]:
    blockers: list[str] = []
    if not output_target.is_file():
        return ["CANONICAL_OUTPUT_MISSING"], None
    try:
        payload = json.loads(output_target.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return ["CANONICAL_OUTPUT_INVALID_JSON"], None
    if not isinstance(payload, dict):
        return ["CANONICAL_OUTPUT_INVALID_PAYLOAD"], None

    if payload.get("schema") != RESOURCE_LOCK_SCHEMA:
        blockers.append("CANONICAL_OUTPUT_SCHEMA_DRIFT")
    if payload.get("status") != RESOURCE_LOCK_STATUS:
        blockers.append("CANONICAL_OUTPUT_STATUS_DRIFT")
    if payload.get("branch") != "phase18/story-intelligence":
        blockers.append("CANONICAL_OUTPUT_BRANCH_DRIFT")
    if payload.get("candidate") != 1:
        blockers.append("CANONICAL_OUTPUT_CANDIDATE_DRIFT")
    if payload.get("cost_mode") != "$0-local":
        blockers.append("CANONICAL_OUTPUT_COST_MODE_DRIFT")
    if payload.get("gpu_eligible") is not True or payload.get("native_bf16_proven") is not True:
        blockers.append("CANONICAL_OUTPUT_GPU_BF16_UNPROVEN")
    if payload.get("network_download_authorized") is not False or payload.get("local_files_only") is not True:
        blockers.append("CANONICAL_OUTPUT_LOCAL_ONLY_DRIFT")
    if payload.get("semantic_preflight_bound") is not True or payload.get("runtime_stable_across_generation") is not True:
        blockers.append("CANONICAL_OUTPUT_SEMANTIC_RUNTIME_UNBOUND")
    if payload.get("human_visual_review_required") is not True or payload.get("human_visual_review_approved") is not False:
        blockers.append("CANONICAL_OUTPUT_HUMAN_REVIEW_STATE_DRIFT")
    if payload.get("golden_quality_approved") is not False:
        blockers.append("CANONICAL_OUTPUT_GOLDEN_QUALITY_AUTHORITY_DRIFT")
    if payload.get("publication_ready") is not False:
        blockers.append("CANONICAL_OUTPUT_PUBLICATION_AUTHORITY_DRIFT")
    if payload.get("seeds_2_to_4_authorized") is not False:
        blockers.append("CANONICAL_OUTPUT_SEEDS_AUTHORITY_DRIFT")

    png_value = payload.get("png")
    if not isinstance(png_value, str) or not png_value.strip():
        blockers.append("CANONICAL_OUTPUT_PNG_PATH_MISSING")
        return blockers, payload
    try:
        png_target = _inside_repository(Path(png_value))
    except RuntimeError:
        blockers.append("CANONICAL_OUTPUT_PNG_PATH_INVALID")
        return blockers, payload
    if not png_target.is_file():
        blockers.append("CANONICAL_OUTPUT_PNG_MISSING")
        return blockers, payload
    try:
        with png_target.open("rb") as handle:
            signature = handle.read(8)
    except OSError:
        blockers.append("CANONICAL_OUTPUT_PNG_UNREADABLE")
        return blockers, payload
    if signature != PNG_SIGNATURE:
        blockers.append("CANONICAL_OUTPUT_PNG_SIGNATURE_INVALID")
        return blockers, payload

    png_sha = _sha256(png_target)
    if payload.get("png_sha256") != png_sha:
        blockers.append("CANONICAL_OUTPUT_PNG_SHA_DRIFT")
    png_bytes = payload.get("png_bytes")
    if isinstance(png_bytes, bool) or not isinstance(png_bytes, int) or png_bytes <= 8:
        blockers.append("CANONICAL_OUTPUT_PNG_BYTES_INVALID")
    elif png_bytes != png_target.stat().st_size:
        blockers.append("CANONICAL_OUTPUT_PNG_SIZE_DRIFT")
    return blockers, payload


def run(
    *,
    expected_commit: str,
    output_path: Path,
    receipt_path: Path,
    attestation_path: Path,
    summary_path: Path,
    handoff_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-gpu-handoff.json"),
    attempt_contract_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-gpu-attempt-contract.json"),
) -> dict[str, object]:
    if _SHA40.fullmatch(expected_commit) is None:
        return {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v4",
            "expected_commit": expected_commit,
            "canonical_generation_started": False,
            "ready": False,
            "blockers": ["EXPECTED_COMMIT_INVALID"],
            **_closed_authorities(),
        }

    output_target = _inside_repository(output_path)
    receipt_target = _inside_repository(receipt_path)
    attestation_target = _inside_repository(attestation_path)
    summary_target = _inside_repository(summary_path)
    handoff_target = _inside_repository(handoff_path)
    attempt_target = _inside_repository(attempt_contract_path)
    if len({output_target, receipt_target, attestation_target, summary_target, handoff_target, attempt_target}) != 6:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_CANONICAL_OUTPUT_PATH_COLLISION")

    pre_gpu = run_attested_pre_gpu(
        expected_commit=expected_commit,
        receipt_path=receipt_target,
        attestation_path=attestation_target,
    )
    _write_json(summary_target, pre_gpu)

    blockers: list[str] = []
    if pre_gpu.get("expected_commit") != expected_commit:
        blockers.append("ATTESTED_PRE_GPU_COMMIT_DRIFT")
    if pre_gpu.get("ready_for_authoritative_golden_preflight") is not True:
        blockers.append("ATTESTED_PRE_GPU_NOT_READY")
    if pre_gpu.get("receipt_attested") is not True:
        blockers.append("ATTESTED_PRE_GPU_RECEIPT_NOT_ATTESTED")
    if pre_gpu.get("blockers") != []:
        blockers.append("ATTESTED_PRE_GPU_BLOCKERS_REMAIN")
    for field in (
        "authoritative_gate",
        "network_download_authorized",
        "generation_authorized",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if pre_gpu.get(field) is not False:
            blockers.append(f"ATTESTED_PRE_GPU_AUTHORITY_DRIFT_{field.upper()}")

    if blockers:
        return {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v4",
            "expected_commit": expected_commit,
            "pre_gpu_summary": str(summary_target),
            "canonical_generation_started": False,
            "ready": False,
            "blockers": blockers,
            **_closed_authorities(),
        }

    handoff = build_gpu_handoff(
        expected_commit=expected_commit,
        attested_summary_path=summary_target,
    )
    _write_json(handoff_target, handoff)

    handoff_blockers: list[str] = []
    if handoff.get("expected_commit") != expected_commit:
        handoff_blockers.append("GPU_HANDOFF_COMMIT_DRIFT")
    if handoff.get("branch_required") != "phase18/story-intelligence":
        handoff_blockers.append("GPU_HANDOFF_BRANCH_DRIFT")
    if handoff.get("cost_mode_required") != "$0-local":
        handoff_blockers.append("GPU_HANDOFF_COST_MODE_DRIFT")
    if handoff.get("offline_required") is not True:
        handoff_blockers.append("GPU_HANDOFF_OFFLINE_POLICY_DRIFT")
    if handoff.get("eligible_for_authoritative_golden_preflight") is not True:
        handoff_blockers.append("GPU_HANDOFF_NOT_ELIGIBLE")
    if handoff.get("blockers") != []:
        handoff_blockers.append("GPU_HANDOFF_BLOCKERS_REMAIN")
    for field in (
        "authoritative_gate",
        "network_download_authorized",
        "generation_authorized",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if handoff.get(field) is not False:
            handoff_blockers.append(f"GPU_HANDOFF_AUTHORITY_DRIFT_{field.upper()}")

    if handoff_blockers:
        return {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v4",
            "expected_commit": expected_commit,
            "pre_gpu_summary": str(summary_target),
            "gpu_handoff": str(handoff_target),
            "canonical_generation_started": False,
            "ready": False,
            "blockers": handoff_blockers,
            **_closed_authorities(),
        }

    attempt = build_gpu_attempt_contract(expected_commit=expected_commit, handoff_path=handoff_target)
    _write_json(attempt_target, attempt)
    attempt_blockers = _attempt_contract_blockers(
        attempt=attempt,
        expected_commit=expected_commit,
        handoff_target=handoff_target,
    )
    if attempt_blockers:
        return {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v4",
            "expected_commit": expected_commit,
            "pre_gpu_summary": str(summary_target),
            "gpu_handoff": str(handoff_target),
            "gpu_attempt_contract": str(attempt_target),
            "canonical_generation_started": False,
            "ready": False,
            "blockers": attempt_blockers,
            **_closed_authorities(),
        }

    command = [
        sys.executable,
        str(ROOT / "tools/phase18_colab_first_genuine_resources_locked.py"),
        "--output",
        str(output_target),
    ]
    subprocess.run(command, cwd=ROOT, check=True)

    output_blockers, output_payload = _canonical_output_blockers(output_target=output_target)
    return {
        "schema": "pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v4",
        "expected_commit": expected_commit,
        "pre_gpu_summary": str(summary_target),
        "gpu_handoff": str(handoff_target),
        "gpu_attempt_contract": str(attempt_target),
        "canonical_output": str(output_target),
        "canonical_output_sha256": _sha256(output_target) if output_target.is_file() else None,
        "canonical_png": output_payload.get("png") if output_payload is not None else None,
        "canonical_png_sha256": output_payload.get("png_sha256") if output_payload is not None else None,
        "canonical_generation_started": True,
        "ready": not output_blockers,
        "blockers": output_blockers,
        **_closed_authorities(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run canonical Golden v6 only after attested pre-GPU readiness, immutable GPU handoff, content-bound GPU attempt replay, and canonical output replay")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-receipt.json"),
    )
    parser.add_argument(
        "--attestation",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-attestation.json"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-summary.json"),
    )
    parser.add_argument(
        "--handoff",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-gpu-handoff.json"),
    )
    parser.add_argument(
        "--attempt-contract",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-gpu-attempt-contract.json"),
    )
    args = parser.parse_args()

    payload = run(
        expected_commit=args.expected_commit,
        output_path=args.output,
        receipt_path=args.receipt,
        attestation_path=args.attestation,
        summary_path=args.summary,
        handoff_path=args.handoff,
        attempt_contract_path=args.attempt_contract,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
