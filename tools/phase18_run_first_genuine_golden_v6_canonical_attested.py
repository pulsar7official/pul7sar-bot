#!/usr/bin/env python3
"""Fail-closed canonical Golden v6 launcher with attested pre-GPU proof.

This wrapper is intentionally narrow. It runs the existing attested first-Golden
pre-GPU contract against an immutable source commit and only if that contract is
ready does it delegate to the existing canonical Golden v6 resource-locked entry
point. It does not weaken or replace any downstream factual, identity, sentiment,
semantic-publication, visual-quality, BF16, local-cache, or human-review gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_run_first_golden_pre_gpu_attested import run as run_attested_pre_gpu

_SHA40 = re.compile(r"^[0-9a-f]{40}$")


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


def _closed_authorities() -> dict[str, bool]:
    return {
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def run(
    *,
    expected_commit: str,
    output_path: Path,
    receipt_path: Path,
    attestation_path: Path,
    summary_path: Path,
) -> dict[str, object]:
    if _SHA40.fullmatch(expected_commit) is None:
        return {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v1",
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
    if len({output_target, receipt_target, attestation_target, summary_target}) != 4:
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
            "schema": "pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v1",
            "expected_commit": expected_commit,
            "pre_gpu_summary": str(summary_target),
            "canonical_generation_started": False,
            "ready": False,
            "blockers": blockers,
            **_closed_authorities(),
        }

    command = [
        sys.executable,
        str(ROOT / "tools/phase18_colab_first_genuine_resources_locked.py"),
        "--output",
        str(output_target),
    ]
    subprocess.run(command, cwd=ROOT, check=True)

    return {
        "schema": "pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v1",
        "expected_commit": expected_commit,
        "pre_gpu_summary": str(summary_target),
        "canonical_output": str(output_target),
        "canonical_generation_started": True,
        "ready": output_target.is_file(),
        "blockers": [] if output_target.is_file() else ["CANONICAL_OUTPUT_MISSING"],
        **_closed_authorities(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run canonical Golden v6 only after attested pre-GPU readiness")
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
    args = parser.parse_args()

    payload = run(
        expected_commit=args.expected_commit,
        output_path=args.output,
        receipt_path=args.receipt,
        attestation_path=args.attestation,
        summary_path=args.summary,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
